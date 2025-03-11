from typing import Optional
from urllib.parse import urlparse, urlunparse
import re

import httpx
from pydantic import BaseModel, HttpUrl

from stash.models.links import ContentType, ProcessingStatus, Link


class LinkMetadata(BaseModel):
    """Metadata extracted from a link during the quick processing phase."""
    url: HttpUrl
    final_url: Optional[HttpUrl] = None
    content_type: ContentType = ContentType.UNKNOWN
    title: Optional[str] = None
    error: Optional[str] = None


class LinkService:
    def __init__(self, http_client: httpx.AsyncClient):
        self.http_client = http_client

    def _clean_url(self, url: str) -> str:
        """Clean and normalize a URL.
        
        - Ensures scheme is present
        - Removes common tracking parameters
        - Normalizes to standard format
        """
        # Add scheme if missing
        if not url.startswith(('http://', 'https://')):
            url = f'https://{url}'

        # Parse URL into components
        parsed = urlparse(url)
        
        # Common tracking parameters to remove
        tracking_params = {
            # Generic
            'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
            'source', 'ref', 'referrer', 'ref_src', 'ref_url',
            # Social media
            'fbclid', 'igshid', 'twclid', '_ga',
            # Amazon
            'tag', 'linkId', 'pd_rd_r', 'pd_rd_w', 'pd_rd_wg',
            # Others
            'gclid', 'dclid', 'affiliate', 'zanpid', 'mc_cid', 'mc_eid'
        }
        
        # Filter out tracking parameters
        if parsed.query:
            params = dict(param.split('=') for param in parsed.query.split('&') if '=' in param)
            clean_params = {k: v for k, v in params.items() if k.lower() not in tracking_params}
            query = '&'.join(f'{k}={v}' for k, v in clean_params.items())
        else:
            query = ''
        
        # Reconstruct URL in normalized form
        clean = urlunparse((
            parsed.scheme,
            parsed.netloc.lower(),
            parsed.path,
            parsed.params,
            query,
            ''  # Remove fragments
        ))
        
        return clean

    def _detect_content_type(self, url: str, headers: Optional[dict] = None) -> ContentType:
        """Detect content type from URL pattern and/or headers."""
        url_lower = url.lower()
        
        # Check URL patterns
        if 'youtube.com/watch' in url_lower or 'youtu.be/' in url_lower:
            return ContentType.YOUTUBE
        elif 'open.spotify.com' in url_lower:
            return ContentType.SPOTIFY
        elif 'github.com' in url_lower:
            return ContentType.GITHUB
        elif 'twitter.com' in url_lower or 't.co' in url_lower or 'x.co' in url_lower or 'x.com' in url_lower:
            return ContentType.TWITTER
        elif url_lower.endswith('.pdf'):
            return ContentType.PDF
            
        # Check content-type header
        if headers and 'content-type' in headers:
            content_type = headers['content-type'].lower()
            if 'pdf' in content_type:
                return ContentType.PDF
                
        return ContentType.WEBPAGE

    async def process_new_link(self, url: str) -> LinkMetadata:
        """Quick process a new link to extract basic metadata.
        
        This is meant to be fast and run during the HTTP request.
        More detailed processing happens in enrich_link.
        """
        try:
            # Clean and normalize URL
            clean_url = self._clean_url(url)
            
            # Do a GET request to:
            # - Follow redirects
            # - Get content type
            # - Check if accessible
            # - Get quick title
            r = await self.http_client.get(
                clean_url,
                follow_redirects=True,
                timeout=5.0
            )
            r.raise_for_status()
            
            # Get final URL after redirects
            final_url = str(r.url)
            
            # Detect content type
            content_type = self._detect_content_type(
                final_url,
                r.headers
            )

            # Quick title extraction if it's HTML
            title = None
            if 'html' in r.headers.get('content-type', '').lower():
                # Look for title in first 8KB of response to keep it fast
                # Use streaming to avoid loading the entire response
                chunk = ""
                async with self.http_client.stream("GET", final_url, timeout=5.0) as stream:
                    # Read just the first 8KB
                    async for data in stream.aiter_text(chunk_size=8192):
                        chunk = data
                        break  # Only read the first chunk
                
                # Try OpenGraph title first
                og_match = re.search(r'<meta\s+property="og:title"\s+content="([^"]+)"', chunk)
                if og_match:
                    title = og_match.group(1)
                else:
                    # Fall back to title tag
                    title_match = re.search(r'<title[^>]*>([^<]+)</title>', chunk)
                    if title_match:
                        title = title_match.group(1).strip()
            
            return LinkMetadata(
                url=clean_url,
                final_url=final_url,
                content_type=content_type,
                title=title
            )
            
        except httpx.TimeoutException:
            return LinkMetadata(
                url=clean_url,
                error="Request timed out"
            )
        except httpx.HTTPStatusError as e:
            return LinkMetadata(
                url=clean_url,
                error=f"HTTP error: {e.response.status_code}"
            )
        except Exception as e:
            return LinkMetadata(
                url=clean_url,
                error=str(e)
            )

    async def enrich_link(self, link: Link) -> None:
        """Enrich a link with additional metadata.
        
        This is meant to run in the background and can take longer.
        It will update the link record when done.
        """
        try:
            # Update status
            link.processing_status = ProcessingStatus.PROCESSING
            
            # Get full page content
            r = await self.http_client.get(
                link.url,
                follow_redirects=True,
                timeout=10.0
            )
            r.raise_for_status()
            
            # TODO: Extract metadata based on content type
            # For now, just get title from content-type
            content_type = r.headers.get('content-type', '')
            if 'html' in content_type.lower():
                # TODO: Parse HTML and get proper title
                link.title = link.url
            
            link.processing_status = ProcessingStatus.COMPLETE
            
        except Exception as e:
            link.processing_status = ProcessingStatus.ERROR
            link.processing_error = str(e)

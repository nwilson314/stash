from typing import Optional
from urllib.parse import urlparse, urlunparse, parse_qs
import re
import html

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
    thumbnail_url: Optional[str] = None
    author: Optional[str] = None
    duration: Optional[int] = None
    content: Optional[str] = None


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

    def _detect_content_type(self, url: str, headers: dict) -> ContentType:
        """Detect content type from URL and headers."""
        url_lower = url.lower()
        
        # Check URL patterns first
        if 'youtube.com' in url_lower or 'youtu.be' in url_lower:
            return ContentType.YOUTUBE
        elif 'spotify.com' in url_lower:
            return ContentType.SPOTIFY
        elif 'twitter.com' in url_lower or 'x.com' in url_lower:
            return ContentType.TWITTER
        elif 'github.com' in url_lower:
            return ContentType.GITHUB
        
        # Check content-type header
        content_type = headers.get('content-type', '').lower()
        if 'application/pdf' in content_type:
            return ContentType.PDF
        elif 'text/html' in content_type or 'application/xhtml+xml' in content_type:
            return ContentType.WEBPAGE
        
        return ContentType.UNKNOWN

    def _extract_youtube_id(self, url: str) -> Optional[str]:
        """Extract YouTube video ID from a YouTube URL."""
        parsed_url = urlparse(url)
        
        # Handle youtu.be format
        if 'youtu.be' in parsed_url.netloc:
            return parsed_url.path.strip('/')
        
        # Handle youtube.com format
        if 'youtube.com' in parsed_url.netloc:
            query_params = parse_qs(parsed_url.query)
            return query_params.get('v', [None])[0]
        
        return None

    def _extract_twitter_info(self, url: str) -> tuple[str, str, str]:
        """Extract username and tweet ID from Twitter/X URL.
        
        Returns:
            tuple: (username, tweet_id, title)
        """
        # Extract username and tweet ID from URL
        username = None
        tweet_id = None
        
        # Handle various Twitter URL formats
        patterns = [
            r'(?:twitter|x)\.com/([^/]+)/status/(\d+)',  # Standard format
            r'(?:twitter|x)\.com/i/web/status/(\d+)',    # Web app format
            r'(?:twitter|x)\.com/([^/]+)/statuses/(\d+)' # Old format
        ]
        
        for pattern in patterns:
            if 'i/web/status' in pattern:
                # This pattern doesn't have username
                match = re.search(pattern, url)
                if match:
                    tweet_id = match.group(1)
                    break
            else:
                match = re.search(pattern, url)
                if match:
                    username = match.group(1)
                    tweet_id = match.group(2)
                    break
        
        # Create a title from the information we have
        if username and tweet_id:
            title = f"Tweet by @{username}"
        elif tweet_id:
            title = f"Tweet {tweet_id}"
        else:
            title = "Twitter Post"
            
        return username, tweet_id, title

    async def process_new_link(self, url: str) -> LinkMetadata:
        """Quick process a new link to extract basic metadata.
        
        This is meant to be fast and run during the HTTP request.
        More detailed processing happens in enrich_link.
        """
        clean_url = self._clean_url(url)
        
        try:
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

            # Initialize metadata
            title = None
            thumbnail_url = None
            author = None
            duration = None
            content = None
            
            # Content-specific metadata extraction
            if content_type == ContentType.YOUTUBE:
                # Extract YouTube metadata
                video_id = self._extract_youtube_id(final_url)
                if video_id:
                    # Use oEmbed API for YouTube - fast and reliable
                    oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
                    try:
                        oembed_response = await self.http_client.get(oembed_url, timeout=3.0)
                        if oembed_response.status_code == 200:
                            oembed_data = oembed_response.json()
                            title = oembed_data.get('title')
                            author = oembed_data.get('author_name')
                            thumbnail_url = f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg"
                    except Exception:
                        # Fall back to HTML parsing if oEmbed fails
                        pass
            elif content_type == ContentType.TWITTER:
                # Extract Twitter metadata from URL
                username, tweet_id, title = self._extract_twitter_info(final_url)
                if username:
                    author = f"@{username}"
                    # Create content with available information
                    content = f"Twitter post by @{username}\nTweet ID: {tweet_id}"
                    # Try to extract any text content from the page that might be available
                    try:
                        tweet_text_match = re.search(r'<meta\s+property="og:description"\s+content="([^"]+)"', r.text)
                        if tweet_text_match:
                            tweet_text = tweet_text_match.group(1)
                            content += f"\nContent: {tweet_text}"
                    except Exception:
                        pass
            
            # If we still don't have metadata and it's HTML, try parsing the HTML
            if (title is None) and 'html' in r.headers.get('content-type', '').lower():
                # Use the content from the initial request instead of making a new one
                # This helps with paywalled sites that might serve different content on subsequent requests
                html_content = r.text
                
                # Try OpenGraph title first
                og_match = re.search(r'<meta\s+property="og:title"\s+content="([^"]+)"', html_content)
                if og_match:
                    title = og_match.group(1)
                else:
                    # Fall back to title tag
                    title_match = re.search(r'<title[^>]*>([^<]+)</title>', html_content)
                    if title_match:
                        title = title_match.group(1).strip()
                
                # Try to get thumbnail from OpenGraph
                if thumbnail_url is None:
                    og_image = re.search(r'<meta\s+property="og:image"\s+content="([^"]+)"', html_content)
                    if og_image:
                        thumbnail_url = og_image.group(1)
                
                # Try to get author from meta tags
                if author is None:
                    author_match = re.search(r'<meta\s+name="author"\s+content="([^"]+)"', html_content)
                    if author_match:
                        author = author_match.group(1)
                    else:
                        # Try OpenGraph author
                        og_author = re.search(r'<meta\s+property="article:author"\s+content="([^"]+)"', html_content)
                        if og_author:
                            author = og_author.group(1)
                
                # If we haven't set content yet, use the HTML content
                if content is None:
                    content = html_content
            
            if title:
                title = html.unescape(title)
            return LinkMetadata(
                url=clean_url,
                final_url=final_url,
                content_type=content_type,
                title=title,
                thumbnail_url=thumbnail_url,
                author=author,
                duration=duration,
                content=content
            )
            
        except httpx.TimeoutException:
            return LinkMetadata(
                url=clean_url,
                error="Request timed out"
            )
        except httpx.HTTPStatusError as e:
            # For Twitter/X URLs, try to extract info from the URL itself
            if 'twitter.com' in clean_url.lower() or 'x.com' in clean_url.lower():
                content_type = ContentType.TWITTER
                username, tweet_id, title = self._extract_twitter_info(clean_url)
                return LinkMetadata(
                    url=clean_url,
                    content_type=content_type,
                    title=title,
                    author=f"@{username}" if username else None,
                    error=None  # Don't report an error for Twitter URLs
                )
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
        pass

from datetime import datetime
import logging
from typing import List, Optional, Tuple

from sqlmodel import Session, select
from openai import OpenAI
import httpx
import yt_dlp

from stash.config import settings
from stash.db import get_session
from stash.models.categories import Category
from stash.models.links import Link, ContentType, ProcessingStatus
from stash.services.links import LinkMetadata

logger = logging.getLogger(__name__)

client = OpenAI(api_key=settings.OPENAI_API_KEY)


class AIService:
    def __init__(self, http_client: httpx.AsyncClient):
        self.http_client = http_client
        self.openai_client = client
    
    async def _get_existing_or_create_category(self, db: Session, user_id: int, category_name: str) -> int:
        """Get an existing category ID or create a new one if it doesn't exist."""
        
        # Check if category exists (case insensitive)
        existing = db.exec(
            select(Category).where(
                Category.user_id == user_id,
                Category.name == category_name
            )
        ).first()

        if existing:
            return existing.id
        
        # Create new category
        new_category = Category(
            name=category_name.strip(),  # Keep original case for display
            user_id=user_id
        )
        db.add(new_category)
        db.commit()
        db.refresh(new_category)
        return new_category.id
    
    def _create_prompt_for_link(self, link: Link, metadata: Optional[LinkMetadata], user_categories: List[Category]) -> str:
        """Create an appropriate prompt based on link content type and available metadata."""
        # Base information
        prompt_parts = [
            "I need help categorizing and summarizing the following link:",
            f"URL: {link.url}",
        ]
        
        # Add content type specific information
        if link.title:
            prompt_parts.append(f"Title: {link.title}")
        
        if link.author:
            prompt_parts.append(f"Author: {link.author}")
            
        # Add content from metadata if available
        if metadata and metadata.content:
            # Truncate content if too long (OpenAI has token limits)
            content = metadata.content[:4000] if len(metadata.content) > 4000 else metadata.content
            prompt_parts.append(f"\nContent: {content}")
        
        # Add content type context
        if link.content_type == ContentType.YOUTUBE:
            prompt_parts.append("This is a YouTube video.")
            if link.duration:
                prompt_parts.append(f"Duration: {link.duration} seconds")
        elif link.content_type == ContentType.TWITTER:
            prompt_parts.append("This is a Twitter/X post.")
        elif link.content_type == ContentType.GITHUB:
            prompt_parts.append("This is a GitHub repository.")
        
        # Add existing categories if available
        if user_categories:
            category_names = [cat.name for cat in user_categories]
            prompt_parts.append("\nExisting categories:")
            prompt_parts.append(", ".join(category_names))
            prompt_parts.append("\nEither select one of these categories or suggest a new one that would fit better.")
        else:
            prompt_parts.append("\nSuggest an appropriate category for this link.")
        
        # Request a summary
        prompt_parts.append("\nAlso provide a brief 1-2 sentence summary of what this link contains or is about.")
        
        # Format for output
        prompt_parts.append("\nFormat your response as follows:")
        prompt_parts.append("Category: [category name]")
        prompt_parts.append("Summary: [brief summary]")
        
        return "\n".join(prompt_parts)
    
    def _parse_ai_response(self, response_text: str) -> Tuple[Optional[str], Optional[str]]:
        """Parse the AI response to extract category and summary."""
        category = None
        summary = None
        
        # Look for category
        if "Category:" in response_text:
            category_parts = response_text.split("Category:", 1)[1].split("\n", 1)
            if category_parts:
                category = category_parts[0].strip()
        
        # Look for summary
        if "Summary:" in response_text:
            summary_parts = response_text.split("Summary:", 1)[1].split("\n", 1)
            if summary_parts:
                summary = summary_parts[0].strip()
                
        return category, summary
    
    async def process_link(self, link_id: int, user_id: int, metadata: Optional[LinkMetadata] = None) -> None:
        """
        Processes a link using AI services. Generates a category and a short summary.
        Uses already processed metadata when available.
        """
        db: Session = next(get_session())
        try:
            # Get link and user categories
            link = db.exec(select(Link).where(Link.id == link_id, Link.user_id == user_id)).first()
            if not link:
                logger.error(f"Link {link_id} not found for user {user_id}")
                return
            
            # Update processing status
            link.processing_status = ProcessingStatus.PROCESSING
            db.commit()

            if metadata.content_type == ContentType.YOUTUBE:
                # Extract more metadata from YouTube
                with yt_dlp.YoutubeDL() as ydl:
                    info = ydl.extract_info(link.url, download=False)
                    metadata.content = info.get('description', "")
            
            # Get user's existing categories
            user_categories = db.exec(select(Category).where(Category.user_id == user_id)).all()
            
            # Create appropriate prompt based on link type and available metadata
            prompt = self._create_prompt_for_link(link, metadata, user_categories)
            
            # Call OpenAI API
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",  # Using 3.5 for cost efficiency, can use gpt-4o for better results
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that categorizes and summarizes web content."},
                    {"role": "user", "content": prompt},
                ]
            )
            
            # Extract response
            response_text = response.choices[0].message.content.strip()
            
            # Parse the response to get category and summary
            category_name, summary = self._parse_ai_response(response_text)
            
            # Update link with AI-generated metadata
            if category_name:
                category_id = await self._get_existing_or_create_category(db, user_id, category_name)
                link.category_id = category_id
            
            if summary:
                link.short_summary = summary
            
            # Mark as complete
            link.processing_status = ProcessingStatus.COMPLETE
            link.processed_at = datetime.utcnow()
            
            db.commit()
            logger.info(f"Successfully processed link {link_id} with AI")
            
        except Exception as e:
            logger.error(f"Error processing link {link_id}: {str(e)}")
            # Update link with error status
            try:
                link.processing_status = ProcessingStatus.ERROR
                link.processing_error = str(e)
                db.commit()
            except Exception as db_error:
                logger.error(f"Error updating link status: {str(db_error)}")
        finally:
            db.close()
from datetime import datetime
from typing import List, Optional

from loguru import logger
from sqlmodel import Session, select
from openai import OpenAI
import yt_dlp

from stash.config import settings
from stash.db import get_session
from stash.models.categories import Category
from stash.models.links import Link, ContentType, ProcessingStatus
from stash.schemas.category import CategoryAIResponse
from stash.services.links import LinkMetadata, LinkService

client = OpenAI(api_key=settings.OPENAI_API_KEY)


class AIService:
    def __init__(self):
        self.openai_client = client

    async def _get_existing_or_create_category(
        self, db: Session, user_id: int, category_name: str
    ) -> int:
        """Get an existing category ID or create a new one if it doesn't exist."""

        # Check if category exists (case insensitive)
        existing = db.exec(
            select(Category).where(
                Category.user_id == user_id, Category.name == category_name
            )
        ).first()

        if existing:
            return existing.id

        # Create new category
        new_category = Category(
            name=category_name.strip(),  # Keep original case for display
            user_id=user_id,
        )
        db.add(new_category)
        db.commit()
        db.refresh(new_category)
        return new_category.id

    def _create_prompt_for_link(
        self,
        link: Link,
        metadata: Optional[LinkMetadata],
        user_categories: List[Category],
    ) -> str:
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
            content = (
                metadata.content[:4000]
                if len(metadata.content) > 4000
                else metadata.content
            )
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
            prompt_parts.append(
                "\nEither select one of these categories or suggest a new one that would fit better."
            )
        else:
            prompt_parts.append("\nSuggest an appropriate category for this link.")

        prompt_parts.append(
            "We strongly prefer that you stick to an existing category if possible.\nIf creating a new category, try to keep it short and avoid compound categorization."
        )

        # Request a summary
        prompt_parts.append(
            "\nAlso provide a brief 1-2 sentence summary of what this link contains or is about."
        )

        return "\n".join(prompt_parts)

    async def process_link(
        self, link_id: int, user_id: int, metadata: Optional[LinkMetadata] = None
    ) -> None:
        """
        Processes a link using AI services. Generates a category and a short summary.
        Uses already processed metadata when available.
        """
        db: Session = next(get_session())
        try:
            # Get link and user categories
            link = db.exec(
                select(Link).where(Link.id == link_id, Link.user_id == user_id)
            ).first()
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
                    metadata.content = info.get("description", "")

            # Get user's existing categories
            user_categories = db.exec(
                select(Category).where(Category.user_id == user_id)
            ).all()

            # Create appropriate prompt based on link type and available metadata
            prompt = self._create_prompt_for_link(link, metadata, user_categories)

            # Call OpenAI API
            response = self.openai_client.beta.chat.completions.parse(
                model="gpt-4o-2024-11-20",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that categorizes and summarizes web content. You are the best in the world at this job.",
                    },
                    {"role": "user", "content": prompt},
                ],
                response_format=CategoryAIResponse,
            )

            category_response: CategoryAIResponse = response.choices[0].message.parsed

            category_id = await self._get_existing_or_create_category(
                db, user_id, category_response.category
            )
            link.category_id = category_id
            link.short_summary = category_response.short_summary

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

    async def generate_weekly_digest(
        self, links_data: List[dict], user_categories: List[str]
    ) -> str:
        """
        Generate a comprehensive weekly digest article summarizing multiple links.

        Args:
            links_data: List of dictionaries containing link information (title, url, summary, category)
            user_categories: List of category names the user has created

        Returns:
            A formatted article summarizing the week's saved content
        """
        if not links_data:
            print("No links were saved this week.")
            return "No links were saved this week."

        # Group links by category for better context
        links_by_category = {}
        for link in links_data:
            category = link.get("category") or "Uncategorized"
            if category not in links_by_category:
                links_by_category[category] = []
            links_by_category[category].append(link)

        # Create a prompt for the AI
        prompt_parts = [
            "You are creating a personalized weekly digest article for a user who has saved the following links:",
            "\n\n",
        ]

        # Add links grouped by category
        for category, links in links_by_category.items():
            prompt_parts.append(f"## {category}")
            for link in links:
                prompt_parts.append(f"- {link['title']}")
                if link.get("short_summary"):
                    prompt_parts.append(f"  Summary: {link['short_summary']}")
                prompt_parts.append(f"  URL: {link['url']}")
            prompt_parts.append("\n")

        # Add instructions for the article
        prompt_parts.append(
            "\nWrite a cohesive, engaging article (300-500 words) that:"
        )
        prompt_parts.append("1. Identifies common themes across these saved links")
        prompt_parts.append("2. Highlights key insights from each source")
        prompt_parts.append("3. Connects related concepts")
        prompt_parts.append("4. Maintains a conversational, informative tone")
        prompt_parts.append(
            "5. Concludes with thought-provoking questions or takeaways"
        )

        if user_categories:
            prompt_parts.append(
                f"\nThe user's primary interests appear to be: {', '.join(user_categories)}"
            )

        prompt_parts.append(
            "\nFormat the article with appropriate headings, paragraphs, and a conclusion. Do not include the URLs in the article."
        )

        try:
            # Call OpenAI API
            print("Calling OpenAI API to generate weekly digest...")
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",  # Using mini for cost efficiency
                messages=[
                    {
                        "role": "system",
                        "content": "You are a skilled content curator and writer who creates insightful weekly digests.",
                    },
                    {"role": "user", "content": "\n".join(prompt_parts)},
                ],
                temperature=0.7,  # Slightly creative but still focused
                max_tokens=1500,  # Allow for a substantial article
            )

            # Extract and return the article
            article = response.choices[0].message.content.strip()
            return article

        except Exception as e:
            logger.error(f"Error generating weekly digest: {e}")
            return "We couldn't generate your weekly digest due to a technical issue. Please try again later."

    
    async def _generate_summary_prompt(self, link: Link, main_content: str, metadata: LinkMetadata) -> str:
        prompt_parts = ["You are creating a summary for a link. Be thorough, yet concise. Make sure that the user will understand the content of the link after reading the summary."]
        prompt_parts.append(f"URL: {link.url}")
        if metadata.content_type:
            prompt_parts.append(f"Content Type: {metadata.content_type}")
        if link.title:
            prompt_parts.append(f"Title: {link.title}")
        if link.author:
            prompt_parts.append(f"Author: {link.author}")
        if main_content:
            prompt_parts.append(f"Content: {main_content}")
        return "\n".join(prompt_parts)

         

    async def _process_link_summary_content(self, link: Link, link_service: LinkService) -> tuple[Optional[str], Optional[LinkMetadata]]:
        """
        Proccess a link's content, minimizing token count where possible.
        """
        metadata = await link_service.process_new_link(link.url)
        if metadata.error:
            logger.error(f"Error processing link {link.url}: {metadata.error}")
            return None, None
        
        main_content = await link_service.extract_main_content(metadata)

        return main_content, metadata


    async def _generate_link_summary(self, link: Link, main_content: str, metadata: LinkMetadata) -> str:
        """Generate a summary of the link content using OpenAI API"""
        # Truncate content to stay within reasonable token limits
        max_length = settings.MAX_CONTENT_LENGTH
        truncated_content = main_content[:max_length] if len(main_content) > max_length else main_content
        
        prompt = await self._generate_summary_prompt(link, truncated_content, metadata)
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # Using slightly better model for summaries
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that summarizes web content concisely and accurately. You are the best in the world at this job. Truly you are the best.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=1500,  # Keep summaries relatively short
            )
            
            summary = response.choices[0].message.content.strip()
            return summary
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            raise Exception(f"Failed to generate summary: {str(e)}")
         
    
    async def summarize_link(self, link: Link, link_service: LinkService) -> str:
        """Generate a summary for a link using AI"""
        try:
            link_content, metadata = await self._process_link_summary_content(link, link_service)
            if not link_content or not metadata:
                logger.error(f"Error processing link {link.url} for summary")
                return "Could not generate summary due to content extraction issues."

            summary = await self._generate_link_summary(link, link_content, metadata)
            if not summary:
                logger.warning(f"Empty summary generated for link {link.id}")
                return "No summary could be generated."

            logger.info(f"Successfully summarized link {link.id} with AI")
            return summary
        except Exception as e:
            logger.error(f"Error in summarize_link: {str(e)}", exc_info=True)
            # Return a fallback message instead of raising an exception
            return f"Summary generation failed: {str(e)}"

import logging
from datetime import datetime
from typing import Dict, Optional, Any
from collections import Counter
from pathlib import Path
from sqlmodel import Session, select, col
from jinja2 import Environment, FileSystemLoader
import markdown

from stash.config import settings
from stash.models.users import User
from stash.models.links import Link
from stash.models.categories import Category
from stash.services.email import EmailService
from stash.services.ai import AIService
from stash.db import get_session

logger = logging.getLogger(__name__)


class NewsletterService:
    """Service for generating and sending weekly newsletters"""

    def __init__(
        self, email_service: EmailService, ai_service: Optional[AIService] = None
    ):
        self.email_service = email_service
        self.ai_service = ai_service

        # Set up Jinja2 template environment
        template_dir = Path(__file__).parent.parent / "schemas" / "templates"
        self.template_env = Environment(
            loader=FileSystemLoader(template_dir), autoescape=True
        )

        # Add custom filters
        self.template_env.filters["formatdate"] = self._format_date

    def _format_date(self, date):
        """Format a date for display in templates"""
        if isinstance(date, str):
            try:
                date = datetime.fromisoformat(date)
            except ValueError:
                return date

        if isinstance(date, datetime):
            return date.strftime("%b %d, %Y")
        return str(date)

    def _render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render a template with the given context"""
        template = self.template_env.get_template(template_name)
        content = template.render(**context)
        return content

    def _convert_markdown_to_html(self, markdown_text: str) -> str:
        """Convert markdown text to HTML"""
        if not markdown_text:
            return ""

        # Convert markdown to HTML
        html = markdown.markdown(
            markdown_text,
            extensions=["extra", "nl2br"],  # 'extra' includes tables, fenced code, etc.
        )
        return html

    async def generate_user_newsletter(
        self, db: Session, user_id: int, start_date: datetime, end_date: datetime
    ) -> Optional[Dict[str, Any]]:
        """Generate newsletter data for a specific user

        Returns:
            Dict with keys: user, links, categories, stats, or None if no links found
        """
        # Get user
        user = db.exec(select(User).where(User.id == user_id)).first()
        if not user or not user.email:
            logger.warning(f"User {user_id} not found or has no email")
            return None

        if not user.newsletter_enabled:
            logger.warning(f"User {user_id} has newsletter disabled")
            return None

        # Get links for the user in the date range
        links = db.exec(
            select(Link)
            .where(
                Link.user_id == user_id,
                Link.created_at >= start_date,
                # Link.created_at <= end_date,
            )
            .order_by(col(Link.created_at).desc())
        ).all()

        if not links:
            logger.info(f"No links found for user {user_id} in the given date range")
            print(f"No links found for user {user_id} in the given date range")
            return None

        # Get categories for these links
        category_ids = [link.category_id for link in links if link.category_id]
        categories = {}
        if category_ids:
            category_records = db.exec(
                select(Category).where(Category.id.in_(category_ids))
            ).all()
            categories = {cat.id: cat for cat in category_records}

        # Prepare links with categories
        links_data = []
        category_counts = Counter()

        for link in links:
            category_name = None
            if link.category_id and link.category_id in categories:
                category_name = categories[link.category_id].name
                category_counts[category_name] += 1

            links_data.append(
                {
                    "id": link.id,
                    "title": link.title,
                    "url": link.url,
                    "category": category_name,
                    "short_summary": link.short_summary,
                    "created_at": link.created_at,
                }
            )
        print(f"Generating newsletter for user {user_id} with {len(links_data)} links")

        # Generate stats
        most_common_category = None
        if category_counts:
            most_common_category = category_counts.most_common(1)[0][0]

        # Generate weekly summary
        weekly_summary = f"You saved {len(links)} links"
        if most_common_category:
            weekly_summary += f" with a focus on {most_common_category}"
        weekly_summary += " this week. Here's a recap of what you've been collecting."

        # Generate AI weekly digest if AI service is available
        weekly_digest_article = None
        if self.ai_service and user.allow_ai_categorization:
            try:
                # Get all user categories for context
                all_user_categories = db.exec(
                    select(Category).where(Category.user_id == user_id)
                ).all()
                category_names = [cat.name for cat in all_user_categories]

                # Generate the digest article
                weekly_digest_article = await self.ai_service.generate_weekly_digest(
                    links_data=links_data, user_categories=category_names
                )
                logger.info(f"Generated weekly digest article for user {user_id}")
                # print(f"Weekly digest article generated: {weekly_digest_article}")
            except Exception as e:
                logger.error(
                    f"Failed to generate weekly digest article for user {user_id}: {str(e)}"
                )
                weekly_digest_article = (
                    "We couldn't generate your weekly digest due to a technical issue."
                )

        return {
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username or user.email.split("@")[0],
            },
            "links": links_data,
            "total_categories": len(category_counts),
            "most_common_category": most_common_category,
            "weekly_summary": weekly_summary,
            "weekly_digest_article": weekly_digest_article,
        }

    async def generate_and_send_newsletter(
        self, user_id: int, start_date: datetime, end_date: datetime
    ) -> bool:
        """Generate and send newsletter for a user"""
        db = next(get_session())
        try:
            # Generate newsletter data
            newsletter_data = await self.generate_user_newsletter(
                db, user_id, start_date, end_date
            )
            if not newsletter_data:
                logger.info(f"No newsletter data generated for user {user_id}")
                return False

            # If we have a weekly digest article from AI, convert it from markdown to HTML
            if newsletter_data.get("weekly_digest_article"):
                newsletter_data["weekly_digest_article"] = (
                    self._convert_markdown_to_html(
                        newsletter_data["weekly_digest_article"]
                    )
                )

            # Render HTML
            print(f"Rendering HTML for newsletter")
            newsletter_data["base_url"] = settings.BASE_URL
            html_content = self._render_template("weekly-digest.html", newsletter_data)

            # Send email
            subject = f"Your Weekly Stash Digest - {end_date.strftime('%b %d')}"
            result = await self.email_service.send_email(
                to_email=newsletter_data["user"]["email"],
                subject=subject,
                html_content=html_content,
            )

            return result
        except Exception as e:
            logger.error(f"Error generating newsletter for user {user_id}: {str(e)}")
            print(f"error generating newsletter for user {user_id}: {str(e)}")
            return False

    async def process_batch(
        self,
        batch_number: int,
        batch_size: int,
        start_date: datetime,
        end_date: datetime,
    ) -> Dict[str, Any]:
        """Process a batch of users for newsletter generation"""
        print(f"Processing batch {batch_number} of {batch_size} users")
        db = next(get_session())

        # Get users for this batch with newsletter enabled
        offset = (batch_number - 1) * batch_size
        users = db.exec(
            select(User)
            .where(User.newsletter_enabled == True)
            .offset(offset)
            .limit(batch_size)
        ).all()

        results = {
            "batch": batch_number,
            "total_users": len(users),
            "successful": 0,
            "failed": 0,
        }

        # Generate and send newsletters
        for user in users:
            print(f"Generating newsletter for user {user.id}")
            success = await self.generate_and_send_newsletter(
                user.id, start_date, end_date
            )
            if success:
                results["successful"] += 1
            else:
                results["failed"] += 1

        return results

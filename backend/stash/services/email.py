import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional, Dict, Any

from stash.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails"""

    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.FROM_EMAIL

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
    ):
        """Send an email with HTML and optional plain text content"""
        print(f"Sending email to {to_email} with subject: {subject}")
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = self.from_email
        message["To"] = to_email

        # Add plain text version if provided, otherwise create a simple version
        if text_content is None:
            # Very basic HTML to text conversion
            text_content = html_content.replace("<div>", "\n").replace("</div>", "")
            text_content = text_content.replace("<p>", "\n").replace("</p>", "\n")
            text_content = text_content.replace("<br>", "\n").replace("<br/>", "\n")
            # Remove all other HTML tags
            import re

            text_content = re.sub(r"<[^>]*>", "", text_content)

        # Attach parts
        part1 = MIMEText(text_content, "plain")
        part2 = MIMEText(html_content, "html")
        message.attach(part1)
        message.attach(part2)

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.sendmail(self.from_email, to_email, message.as_string())
            print(f"Email sent to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False

    async def send_batch(self, emails: List[Dict[str, Any]]):
        """Send a batch of emails

        Args:
            emails: List of email dicts with keys: to_email, subject, html_content, text_content (optional)
        """
        results = []
        for email in emails:
            result = await self.send_email(
                email["to_email"],
                email["subject"],
                email["html_content"],
                email.get("text_content"),
            )
            results.append(result)

        return results

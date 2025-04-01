from pydantic import BaseModel
from typing import Optional


class NewsletterPreferences(BaseModel):
    """Schema for updating user newsletter preferences"""

    enabled: bool
    frequency: str  # weekly, biweekly, monthly

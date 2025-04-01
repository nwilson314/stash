from typing import Optional, TYPE_CHECKING, List

from pydantic import EmailStr
from sqlmodel import SQLModel, Relationship, Field

if TYPE_CHECKING:
    from .links import Link
    from .categories import Category


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    username: Optional[str] = Field(nullable=True)
    email: EmailStr = Field(index=True, nullable=False)
    hashed_password: str = Field(nullable=False)

    # AI preferences
    allow_ai_categorization: bool = Field(default=True)
    allow_ai_create_categories: bool = Field(default=False)
    ai_confidence_threshold: float = Field(default=0.8)

    # Newsletter preferences
    newsletter_enabled: bool = Field(default=False)
    newsletter_frequency: str = Field(default="weekly")  # weekly, biweekly, monthly

    # Relationships
    links: List["Link"] = Relationship(back_populates="user")
    categories: List["Category"] = Relationship(back_populates="user")

from datetime import datetime
from enum import Enum
from typing import Optional, Dict

from sqlmodel import SQLModel, Field, Relationship, JSON

from stash.models.users import User
from stash.models.categories import Category


class ContentType(str, Enum):
    WEBPAGE = "webpage"
    YOUTUBE = "youtube"
    SPOTIFY = "spotify"
    TWITTER = "twitter"
    GITHUB = "github"
    PDF = "pdf"
    UNKNOWN = "unknown"


class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETE = "complete"
    ERROR = "error"


class Link(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    url: str = Field(index=True)
    original_url: Optional[str] = Field(default=None)  # Store pre-redirect URL
    title: Optional[str] = Field(default=None)
    short_summary: Optional[str] = Field(default=None)
    note: Optional[str] = Field(default=None)
    read: bool = Field(default=False)
    
    # Content metadata
    content_type: Optional[ContentType] = Field(nullable=True, default=ContentType.UNKNOWN)
    author: Optional[str] = Field(default=None, nullable=True)
    duration: Optional[int] = Field(default=None, nullable=True)  # Duration in seconds for media content
    thumbnail_url: Optional[str] = Field(default=None)
    raw_metadata: Optional[Dict] = Field(default=None, sa_type=JSON)
    
    # Processing status
    processing_status: ProcessingStatus = Field(default=ProcessingStatus.PENDING)
    processing_error: Optional[str] = Field(default=None)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = Field(default=None)

    # Relationships
    user_id: int = Field(foreign_key="user.id", index=True)
    user: User = Relationship(back_populates="links")
    
    category_id: Optional[int] = Field(default=None, foreign_key="category.id", index=True)
    category: Optional[Category] = Relationship(back_populates="links")

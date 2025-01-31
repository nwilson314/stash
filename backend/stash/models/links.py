from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field, Relationship

from stash.models.users import User


class Link(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    url: str = Field(index=True)
    note: Optional[str] = Field(default=None)
    read: bool = Field(default=False)

    timestamp: datetime = Field(default_factory=datetime.utcnow)

    user_id: int | None = Field(default=None, foreign_key="user.id")
    user: User | None = Relationship(back_populates="links")

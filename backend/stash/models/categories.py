from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship

from stash.models.users import User

if TYPE_CHECKING:
    from .links import Link


class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    name: str = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    user_id: int = Field(foreign_key="user.id", index=True)
    user: User = Relationship(back_populates="categories")

    links: List["Link"] = Relationship(back_populates="category")

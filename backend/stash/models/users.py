from typing import Optional, TYPE_CHECKING

from pydantic import EmailStr
from sqlmodel import SQLModel, Relationship, Field

if TYPE_CHECKING:
    from .links import Link

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    username: Optional[str] = Field(nullable=True)
    email: EmailStr = Field(index=True, nullable=False)
    hashed_password: str = Field(nullable=False)

    links: list["Link"] = Relationship(back_populates="user")

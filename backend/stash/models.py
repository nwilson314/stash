from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class Link(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    url: str = Field(index=True)
    note: Optional[str] = Field(default=None)
    read: bool = Field(default=False)

    timestamp: datetime = Field(default_factory=datetime.utcnow)

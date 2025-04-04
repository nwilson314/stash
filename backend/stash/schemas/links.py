from pydantic import BaseModel


class LinkCreate(BaseModel):
    url: str
    note: str = None


class LinkActivity(BaseModel):
    days: dict[str, int]

from pydantic import BaseModel


class CategoryCreate(BaseModel):
    name: str


class CategoryAIResponse(BaseModel):
    category: str
    short_summary: str

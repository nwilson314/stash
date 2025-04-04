from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str | None = None
    email: EmailStr
    password: str


class UserPassword(BaseModel):
    password: str
    new_password: str


class UserUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    allow_ai_categorization: bool | None = None
    allow_ai_create_categories: bool | None = None
    ai_confidence_threshold: float | None = None
    newsletter_enabled: bool | None = None
    newsletter_frequency: str | None = None


class UserResponse(BaseModel):
    id: int
    username: str | None = None
    email: EmailStr

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str | None = None
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    username: str | None = None
    email: EmailStr

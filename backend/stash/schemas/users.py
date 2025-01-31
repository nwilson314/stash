from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str | None = None
    email: EmailStr
    password: str

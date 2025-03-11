from pydantic import BaseModel
from stash.schemas.users import UserResponse


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AuthResponse(BaseModel):
    token: Token
    user: UserResponse

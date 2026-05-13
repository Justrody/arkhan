from datetime import datetime

from typing import Optional, Any
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBase(BaseModel):
    username: str = Field(
        ..., min_length=3, max_length=16, pattern=r"^[a-zA-Z0-9_-]+$"
    )
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int

    username: str
    role: str = "user"


class UserProfile(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int

    username: str
    email: EmailStr

    role: str = "user"
    is_active: bool = True

    created_at: datetime

    paper_count: int = 0
    votes_received: int = 0
    reputation_points: int = 0


class PublicUserProfile(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int

    username: str

    role: str = "user"

    created_at: datetime

    paper_count: int = 0
    votes_received: int = 0
    reputation_points: int = 0


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

    user: UserResponse


class TokenData(BaseModel):
    user_id: Optional[int] = None
    username: Optional[str] = None


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)

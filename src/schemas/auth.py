from typing import Any, Dict, Optional
from pydantic import BaseModel, EmailStr, Field

class UserRegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=6, max_length=72)

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=72)

class GoogleAuthRequest(BaseModel):
    access_token: Optional[str] = None
    id_token: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    picture: Optional[str] = None
    auth_provider: str
    created_at: Optional[str] = None

    @classmethod
    def from_record(cls, user: Dict[str, Any]) -> "UserResponse":
        return cls(
            id=str(user["id"]),
            email=user["email"],
            name=user["name"],
            picture=user.get("picture"),
            auth_provider=user.get("auth_provider", "local"),
            created_at=str(user["created_at"]) if user.get("created_at") else None,
        )

class AuthResponse(BaseModel):
    user: UserResponse
    access_token: str
    token_type: str = "bearer"

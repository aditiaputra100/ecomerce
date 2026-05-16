from pydantic import BaseModel, EmailStr, ConfigDict, Field, field_validator
from typing import Optional


class UserBase(BaseModel):
    username: str
    email: EmailStr
    has_shop: bool = False


class UserCreate(UserBase):
    password: str
    disable: bool = False

    @field_validator('password')
    def check_password(cls, value):
        value = str(value)

        if len(value) < 8:
            raise ValueError('Password must have at least 8 characters')
        
        return value


class User(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AuthSession(Token):
    user: User

class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: list[str] = Field(default_factory=list)

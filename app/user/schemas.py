from pydantic import BaseModel, EmailStr, ConfigDict, field_validator
from typing import Optional


class UserBase(BaseModel):
    username: str
    email: EmailStr


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
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: list[str] = []

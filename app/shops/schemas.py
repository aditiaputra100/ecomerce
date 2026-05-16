from pydantic import BaseModel, ConfigDict
from typing import TYPE_CHECKING, Optional
from app.user.schemas import User


class ShopCreate(BaseModel):
    name: str
    description: Optional[str] = None


class Shop(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    logo_url: Optional[str] = None
    owner: User

    model_config = ConfigDict(from_attributes=True)

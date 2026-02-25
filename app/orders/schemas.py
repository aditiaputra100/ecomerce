from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime
from app.user.schemas import User

class OrderItemBase(BaseModel):
    product_id: int
    quantity: int

class OrderItemCreate(OrderItemBase):
    pass

class OrderItem(OrderItemBase):
    id: int
    price: float

    model_config = ConfigDict(from_attributes=True)

class OrderCreate(BaseModel):
    items: List[OrderItemCreate]

class OrderUpdate(BaseModel):
    status: str

class Order(BaseModel):
    id: int
    user_id: int
    total_price: float
    status: str
    created_at: datetime
    items: List[OrderItem]
    owner: User  # Buyer details

    model_config = ConfigDict(from_attributes=True)

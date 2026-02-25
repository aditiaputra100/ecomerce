from pydantic import BaseModel, ConfigDict
from typing import Optional


class ProductBase(BaseModel):
    name: str
    description: str
    price: float
    stock: int


class ProductOwner(ProductBase):
    id: int
    is_publish: bool
    image_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
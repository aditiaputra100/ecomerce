from pydantic import BaseModel, ConfigDict
from typing import Optional
from app.categories.schemas import Category as CategorySchema


class ProductBase(BaseModel):
    name: str
    description: str
    price: float
    stock: int


class ProductHomePage(BaseModel):
    pass


class ProductOwner(ProductBase):
    id: int
    is_publish: bool
    image_url: Optional[str] = None
    category: Optional[CategorySchema] = None

    model_config = ConfigDict(from_attributes=True)

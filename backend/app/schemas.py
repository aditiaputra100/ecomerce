# Global schemas

from pydantic import BaseModel, ConfigDict
from typing import Optional
from app.products.schemas import ProductBase
from app.user.schemas import User
from app.categories.schemas import Category as CategorySchema


class SuccessResponse[T, S](BaseModel):
    message: str
    data: Optional[T] = None
    metadata: Optional[S] = None


class Product(ProductBase):
    id: int
    owner: User
    image_url: Optional[str]
    slug: str

    model_config = ConfigDict(from_attributes=True)


class ProductsOnShop(ProductBase):
    id: int
    image_url: Optional[str] = None
    category: Optional[CategorySchema] = None

    model_config = ConfigDict(from_attributes=True)


class ProductShop(BaseModel):
    owner: User
    products: list[ProductsOnShop]

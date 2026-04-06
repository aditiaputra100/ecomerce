# Global schemas

from pydantic import BaseModel, ConfigDict
from typing import Any, Optional, Generic, TypeVar
from fastapi.responses import JSONResponse
from app.products.schemas import ProductBase
from app.user.schemas import User
from app.categories.schemas import Category as CategorySchema

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """Global API response wrapper for consistency across all endpoints"""
    success: bool
    message: str
    data: Optional[T] = None

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Success",
                "data": {}
            }
        }
    )


from datetime import datetime, date


def _serialize_data(obj, visited=None, _exclude_relationships=None):
    """Convert various types to JSON-serializable formats"""
    if visited is None:
        visited = set()
    if _exclude_relationships is None:
        _exclude_relationships = set()
    
    # Prevent circular references
    obj_id = id(obj)
    if obj_id in visited:
        return None
    
    if isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    elif isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: _serialize_data(v, visited, _exclude_relationships) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [_serialize_data(item, visited, _exclude_relationships) for item in obj]
    elif hasattr(obj, 'model_dump'):
        return _serialize_data(obj.model_dump(), visited, _exclude_relationships)
    elif hasattr(obj, '__dict__'):
        return {k: _serialize_data(v, visited, _exclude_relationships) for k, v in obj.__dict__.items() 
                if not k.startswith('_')}
    else:
        return str(obj)


def success_response(data: Any = None, message: str = "Success", status_code: int = 200) -> JSONResponse:
    """Create a standardized success response"""
    response_data = {
        "success": True,
        "message": message,
        "data": _serialize_data(data)
    }
    
    return JSONResponse(
        content=response_data,
        status_code=status_code
    )


def error_response(message: str = "Error", status_code: int = 400, data: Any = None) -> JSONResponse:
    """Create a standardized error response"""
    response_data = {
        "success": False,
        "message": message,
        "data": _serialize_data(data)
    }
    
    return JSONResponse(
        content=response_data,
        status_code=status_code
    )


class Product(ProductBase):
    id: int
    owner: User
    image_url: Optional[str]
    category: Optional[CategorySchema]

    model_config = ConfigDict(from_attributes=True)


class ProductsOnShop(ProductBase):
    id: int
    image_url: Optional[str] = None
    category: Optional[CategorySchema] = None

    model_config = ConfigDict(from_attributes=True)


class ProductShop(BaseModel):
    owner: User
    products: list[ProductsOnShop]

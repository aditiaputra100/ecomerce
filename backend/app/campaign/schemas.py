from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class CampaignCreate(BaseModel):
    name: str
    start_time: Optional[datetime] = None
    end_time: datetime
    is_active: bool = False


class CampaignUpdate(BaseModel):
    name: str
    start_time: Optional[datetime] = None
    end_time: datetime
    is_active: bool = True


class CampaignProductResponse(BaseModel):
    """Informasi produk ringkas yang ditampilkan dalam campaign"""
    name: str
    price: float
    image_url: Optional[str] = None
    slug: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CampaignItemResponse(BaseModel):
    """Item campaign yang berisi produk dan harga spesial"""
    product_id: int
    special_price: float
    stock_limit: int
    stock_sold: int
    product: CampaignProductResponse

    model_config = ConfigDict(from_attributes=True)


class CampaignResponse(BaseModel):
    id: int
    name: str
    start_time: datetime
    end_time: datetime
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CampaignWithItemsResponse(CampaignResponse):
    """Response campaign yang menyertakan daftar produk"""
    items: list[CampaignItemResponse] = []

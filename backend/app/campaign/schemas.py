from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class CampaignCreate(BaseModel):
    name: str
    start_time: Optional[datetime] = None
    end_time: datetime
    is_active: bool = True


class CampaignUpdate(BaseModel):
    name: str
    start_time: Optional[datetime] = None
    end_time: datetime
    is_active: bool = True


class CampaignResponse(BaseModel):
    id: int
    name: str
    start_time: datetime
    end_time: datetime
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

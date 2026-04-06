from typing import Annotated, List
from fastapi import APIRouter, Depends, Security, status, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.user.dependencies import get_current_user
from app.user.models import User
from app.schemas import SuccessResponse
from app.exceptions import NotFoundError
from . import schemas, service

router = APIRouter(prefix="/campaign", tags=["Campaign"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=SuccessResponse[schemas.CampaignResponse, None])
def create_campaign(
    payload: schemas.CampaignCreate,
    current_user: Annotated[User, Security(get_current_user, scopes=["shopowner"])],
    db: Session = Depends(get_db),
):
    try:
        campaign = service.create_campaign(
            db,
            name=payload.name,
            start_time=payload.start_time,
            end_time=payload.end_time,
            is_active=payload.is_active,
        )
        campaign_data = schemas.CampaignResponse.model_validate(campaign)
        return SuccessResponse(message="Campaign created successfully", data=campaign_data)
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err))


@router.get("/active", response_model=SuccessResponse[list[schemas.CampaignResponse], None])
def get_active_campaigns(db: Session = Depends(get_db)):
    try:
        campaigns = service.get_active_campaign(db)
        campaigns_data = [
            schemas.CampaignResponse.model_validate(c)
            for c in campaigns
        ]
        return SuccessResponse(message="", data=campaigns_data)
    except RuntimeError as err:
        raise HTTPException(status_code=500, detail=str(err))


@router.put("/{campaign_id}", response_model=SuccessResponse[schemas.CampaignResponse, None])
def update_campaign(
    campaign_id: int,
    payload: schemas.CampaignUpdate,
    current_user: Annotated[User, Security(get_current_user, scopes=["shopowner"])],
    db: Session = Depends(get_db),
):
    try:
        campaign = service.update_campaign(
            db,
            id=campaign_id,
            name=payload.name,
            start_time=payload.start_time,
            end_time=payload.end_time,
            is_active=payload.is_active,
        )
        campaign_data = schemas.CampaignResponse.model_validate(campaign)
        return SuccessResponse(message="Campaign updated successfully", data=campaign_data)
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err))
    except NotFoundError as err:
        raise HTTPException(status_code=404, detail=str(err.name))


@router.patch("/{campaign_id}/active", response_model=SuccessResponse[schemas.CampaignResponse, None])
def toggle_campaign_active(
    campaign_id: int,
    current_user: Annotated[User, Security(get_current_user, scopes=["shopowner"])],
    db: Session = Depends(get_db),
):
    try:
        campaign = service.change_active_campaign(db, id=campaign_id)
        action = "activated" if campaign.is_active else "deactivated"
        campaign_data = schemas.CampaignResponse.model_validate(campaign)
        return SuccessResponse(message=f"Campaign {action} successfully", data=campaign_data)
    except NotFoundError as err:
        raise HTTPException(status_code=404, detail=str(err.name))


@router.delete("/{campaign_id}", response_model=SuccessResponse[None, None])
def delete_campaign(
    campaign_id: int,
    current_user: Annotated[User, Security(get_current_user, scopes=["shopowner"])],
    db: Session = Depends(get_db),
):
    try:
        service.delete_campaign(db, id=campaign_id)
        return SuccessResponse(message="Campaign deleted successfully", data=None)
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err))
    except NotFoundError as err:
        raise HTTPException(status_code=404, detail=str(err.name))

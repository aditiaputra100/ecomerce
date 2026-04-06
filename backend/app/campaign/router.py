from typing import Annotated, List
from fastapi import APIRouter, Depends, Security, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.user.dependencies import get_current_user
from app.user.models import User
from app.exceptions import NotFoundError
from . import schemas, service

router = APIRouter(prefix="/campaign", tags=["Campaign"])


@router.post("/", status_code=status.HTTP_201_CREATED)
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
        return {
            "message": "Campaign created successfully",
            "data": schemas.CampaignResponse.model_validate(campaign).model_dump(),
        }
    except ValueError as err:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": str(err)},
        )


@router.get("/active")
def get_active_campaigns(db: Session = Depends(get_db)):
    try:
        campaigns = service.get_active_campaign(db)
        return {
            "data": [
                schemas.CampaignResponse.model_validate(c).model_dump()
                for c in campaigns
            ],
        }
    except RuntimeError as err:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": str(err)},
        )


@router.put("/{campaign_id}")
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
        return {
            "message": "Campaign updated successfully",
            "data": schemas.CampaignResponse.model_validate(campaign).model_dump(),
        }
    except ValueError as err:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": str(err)},
        )
    except NotFoundError as err:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": str(err.name)},
        )


@router.patch("/{campaign_id}/active")
def toggle_campaign_active(
    campaign_id: int,
    current_user: Annotated[User, Security(get_current_user, scopes=["shopowner"])],
    db: Session = Depends(get_db),
):
    try:
        campaign = service.change_active_campaign(db, id=campaign_id)
        action = "activated" if campaign.is_active else "deactivated"
        return {
            "message": f"Campaign {action} successfully",
            "data": schemas.CampaignResponse.model_validate(campaign).model_dump(),
        }
    except NotFoundError as err:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": str(err.name)},
        )


@router.delete("/{campaign_id}")
def delete_campaign(
    campaign_id: int,
    current_user: Annotated[User, Security(get_current_user, scopes=["shopowner"])],
    db: Session = Depends(get_db),
):
    try:
        service.delete_campaign(db, id=campaign_id)
        return {
            "message": "Campaign deleted successfully",
            "id": campaign_id,
        }
    except ValueError as err:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": str(err)},
        )
    except NotFoundError as err:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": str(err.name)},
        )

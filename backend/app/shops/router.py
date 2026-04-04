from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, Security, Form
from sqlalchemy.orm import Session
from typing import Annotated, Optional
from app.database import get_db
from app.user.dependencies import get_current_user
from app.user.models import User
from . import schemas, service

router = APIRouter(prefix="/shops", tags=["Shops"])


@router.post("/", response_model=schemas.Shop, status_code=201)
async def open_shop(
    current_user: Annotated[User, Security(get_current_user, scopes=["me"])],
    db: Session = Depends(get_db),
    name: str = Form(...),
    description: Optional[str] = Form(None),
    logo: Optional[UploadFile] = File(None),
):
    if current_user.shop:
        raise HTTPException(status_code=400, detail="You already own a shop")

    logo_url = None
    if logo:
        try:
            logo_url = service.save_logo(logo)
        except Exception:
            raise HTTPException(status_code=500, detail="Failed to upload logo")

    payload = schemas.ShopCreate(name=name, description=description)
    shop = service.create_shop(db, current_user.id, payload, logo_url)
    return shop


@router.get("/me", response_model=schemas.Shop)
def get_my_shop(
    current_user: Annotated[User, Security(get_current_user, scopes=["me"])],
    db: Session = Depends(get_db),
):
    shop = service.get_shop_by_owner(db, current_user.id)
    if not shop:
        raise HTTPException(status_code=404, detail="You do not own a shop")
    return shop


@router.get("/{username}", response_model=schemas.Shop)
def get_shop(username: str, db: Session = Depends(get_db)):
    return service.get_shop_by_username(db, username)

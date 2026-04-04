import os
import uuid
from typing import Optional
from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.exceptions import DuplicateEntryError, NotFoundError
from app.user import models as user_models
from . import models, schemas

UPLOAD_DIR = "app/static/uploads/shops"


def _ensure_upload_dir():
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR, exist_ok=True)


def save_logo(file: UploadFile) -> str:
    _ensure_upload_dir()
    _, ext = os.path.splitext(file.filename or "")
    ext = ext or ".png"
    filename = f"{uuid.uuid4()}{ext}"
    path = os.path.join(UPLOAD_DIR, filename)
    with open(path, "wb") as buffer:
        buffer.write(file.file.read())
    return f"/static/uploads/shops/{filename}"


def get_shop_by_owner(db: Session, owner_id: int) -> models.Shop | None:
    return db.query(models.Shop).filter(models.Shop.owner_id == owner_id).first()


def get_shop_by_name(db: Session, name: str) -> models.Shop | None:
    return db.query(models.Shop).filter(models.Shop.name == name).first()


def create_shop(db: Session, owner_id: int, payload: schemas.ShopCreate, logo_url: Optional[str] = None):
    if get_shop_by_owner(db, owner_id):
        raise DuplicateEntryError(name="Shop already exists for this user")
    if get_shop_by_name(db, payload.name):
        raise DuplicateEntryError(name="Shop name already taken")

    shop = models.Shop(
        name=payload.name,
        description=payload.description,
        logo_url=logo_url,
        owner_id=owner_id,
    )
    db.add(shop)
    db.commit()
    db.refresh(shop)
    return shop


def get_shop_by_username(db: Session, username: str):
    shop = (
        db.query(models.Shop)
        .join(user_models.User, models.Shop.owner_id == user_models.User.id)
        .filter(user_models.User.username == username)
        .first()
    )
    if not shop:
        raise NotFoundError(name=f"Shop owned by {username} not found")
    return shop

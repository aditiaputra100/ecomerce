from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, Security, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.user.dependencies import get_current_user
from app.user.models import User
from app.schemas import success_response, error_response
from . import schemas, service

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("/")
def list_categories(db: Session = Depends(get_db)):
    categories = service.list_categories(db)
    return success_response(data=[schemas.Category.model_validate(c) for c in categories], message="Categories retrieved successfully")


@router.get("/{category_id}")
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = service.get_category(db, category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return success_response(data=schemas.Category.model_validate(category), message="Category retrieved successfully")


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_category(
    payload: schemas.CategoryCreate,
    current_user: Annotated[User, Security(get_current_user, scopes=["shopowner"])],
    db: Session = Depends(get_db),
):
    try:
        category = service.create_category(db, payload)
        return success_response(data=schemas.Category.model_validate(category), message="Category created successfully", status_code=201)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))


@router.put("/{category_id}")
def update_category(
    category_id: int,
    payload: schemas.CategoryUpdate,
    current_user: Annotated[User, Security(get_current_user, scopes=["shopowner"])],
    db: Session = Depends(get_db),
):
    try:
        category = service.update_category(db, category_id, payload)
        return success_response(data=schemas.Category.model_validate(category), message="Category updated successfully")
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))


@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    current_user: Annotated[User, Security(get_current_user, scopes=["shopowner"])],
    db: Session = Depends(get_db),
):
    service.delete_category(db, category_id)
    return success_response(data=None, message="Category deleted successfully")

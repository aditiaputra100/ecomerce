from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Security, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.user.dependencies import get_current_user
from app.user.models import User
from app.schemas import SuccessResponse
from . import schemas, service

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("/", response_model=SuccessResponse[list[schemas.Category], None])
def list_categories(db: Session = Depends(get_db)):
    categories = service.list_categories(db)
    return SuccessResponse(message="Categories retrieved successfully", data=[schemas.Category.model_validate(c) for c in categories])


@router.get("/{category_id}", response_model=SuccessResponse[schemas.Category, None])
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = service.get_category(db, category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return SuccessResponse(message="Category retrieved successfully", data=schemas.Category.model_validate(category))


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=SuccessResponse[schemas.Category, None])
def create_category(
    payload: schemas.CategoryCreate,
    current_user: Annotated[User, Security(get_current_user, scopes=["shopowner"])],
    db: Session = Depends(get_db),
):
    try:
        category = service.create_category(db, payload)
        return SuccessResponse(message="Category created successfully", data=schemas.Category.model_validate(category))
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))


@router.put("/{category_id}", response_model=SuccessResponse[schemas.Category, None])
def update_category(
    category_id: int,
    payload: schemas.CategoryUpdate,
    current_user: Annotated[User, Security(get_current_user, scopes=["shopowner"])],
    db: Session = Depends(get_db),
):
    try:
        category = service.update_category(db, category_id, payload)
        return SuccessResponse(message="Category updated successfully", data=schemas.Category.model_validate(category))
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))


@router.delete("/{category_id}", response_model=SuccessResponse[None, None])
def delete_category(
    category_id: int,
    current_user: Annotated[User, Security(get_current_user, scopes=["shopowner"])],
    db: Session = Depends(get_db),
):
    service.delete_category(db, category_id)
    return SuccessResponse(message="Category deleted successfully", data=None)

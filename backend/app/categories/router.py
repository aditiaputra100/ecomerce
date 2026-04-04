from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, Security, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.user.dependencies import get_current_user
from app.user.models import User
from . import schemas, service

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("/", response_model=List[schemas.Category])
def list_categories(db: Session = Depends(get_db)):
    return service.list_categories(db)


@router.get("/{category_id}", response_model=schemas.Category)
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = service.get_category(db, category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category


@router.post("/", response_model=schemas.Category, status_code=status.HTTP_201_CREATED)
def create_category(
    payload: schemas.CategoryCreate,
    current_user: Annotated[User, Security(get_current_user, scopes=["shopowner"])],
    db: Session = Depends(get_db),
):
    try:
        return service.create_category(db, payload)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))


@router.put("/{category_id}", response_model=schemas.Category)
def update_category(
    category_id: int,
    payload: schemas.CategoryUpdate,
    current_user: Annotated[User, Security(get_current_user, scopes=["shopowner"])],
    db: Session = Depends(get_db),
):
    try:
        return service.update_category(db, category_id, payload)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    current_user: Annotated[User, Security(get_current_user, scopes=["shopowner"])],
    db: Session = Depends(get_db),
):
    service.delete_category(db, category_id)

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, DatabaseError

from app.exceptions import NotFoundError, DuplicateEntryError
from . import models, schemas


def list_categories(db: Session) -> list[models.Category]:
    try:
        return (
            db.query(models.Category)
            .order_by(models.Category.name.asc())
            .all()
        )
    except DatabaseError as err:
        db.rollback()
        raise RuntimeError(f"Failed to fetch categories: {err}")


def get_category(db: Session, category_id: int) -> models.Category | None:
    return db.query(models.Category).filter(models.Category.id == category_id).first()


def create_category(db: Session, payload: schemas.CategoryCreate) -> models.Category:
    if not payload.name or payload.name.strip() == "":
        raise ValueError("Name cannot be empty")

    category = models.Category(**payload.model_dump())

    try:
        db.add(category)
        db.commit()
        db.refresh(category)
    except IntegrityError:
        db.rollback()
        raise DuplicateEntryError(name=payload.name)
    except DatabaseError as err:
        db.rollback()
        raise RuntimeError(f"Failed to create category: {err}")

    return category


def update_category(
    db: Session, category_id: int, payload: schemas.CategoryUpdate
) -> models.Category:
    category = get_category(db, category_id)
    if not category:
        raise NotFoundError(name=f"Category with ID {category_id} not found")

    data = payload.model_dump(exclude_unset=True)

    if "name" in data and (not data["name"] or data["name"].strip() == ""):
        raise ValueError("Name cannot be empty")

    for key, value in data.items():
        setattr(category, key, value)

    try:
        db.commit()
        db.refresh(category)
    except IntegrityError:
        db.rollback()
        raise DuplicateEntryError(name=data.get("name", ""))
    except DatabaseError as err:
        db.rollback()
        raise RuntimeError(f"Failed to update category: {err}")

    return category


def delete_category(db: Session, category_id: int) -> None:
    category = get_category(db, category_id)
    if not category:
        raise NotFoundError(name=f"Category with ID {category_id} not found")

    try:
        for product in category.products:
            product.category_id = None

        db.delete(category)
        db.commit()
    except DatabaseError as err:
        db.rollback()
        raise RuntimeError(f"Failed to delete category: {err}")

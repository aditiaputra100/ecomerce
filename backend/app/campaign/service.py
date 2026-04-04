from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import DatabaseError, IntegrityError
from datetime import datetime, timezone
from . import models
from ..exceptions import NotFoundError, DuplicateEntryError

def __validation_flash_sale(db: Session, name: str, start_time: datetime, end_time: datetime, exclude_id: int = None):
    if name.strip() == "":
        raise ValueError("Name cannot be empty")
    
    if start_time.date() < datetime.now().date():
        raise ValueError("Start time cannot be earlier than today")

    if end_time.date() <= start_time.date():
        raise ValueError("End time cannot be earlier or equal than start time")
    
    try:
        query = (db.query(models.FlashSale)
                 .filter(models.FlashSale.start_time < end_time)
                 .filter(models.FlashSale.end_time > start_time))
        if exclude_id is not None:
            query = query.filter(models.FlashSale.id != exclude_id)
        overlapping = query.first()
    except DatabaseError as err:
        db.rollback()
        raise RuntimeError(f"Failed to check overlapping flash sales: {err}")

    if overlapping:
        raise ValueError(
            f"Flash sale '{name}' overlaps with existing flash sale '{overlapping.name}' "
            f"({overlapping.start_time} - {overlapping.end_time})"
        )

def get_active_flash_sale(db: Session):
    now = datetime.now()

    try:
        flash_sale = (db.query(models.FlashSale)
                      .filter(models.FlashSale.start_time <= now)
                      .filter(models.FlashSale.end_time >= now)
                      .first())
    except DatabaseError as err:
        db.rollback()
        raise RuntimeError(f"Failed to fetch active flash sale: {err}")

    if not flash_sale:
        raise NotFoundError(name="No active flash sale found")

    return flash_sale

def create_flash_sale(db: Session, name: str, end_time: datetime, start_time: datetime = datetime.now(timezone.utc), is_active: bool = True) -> None:
    __validation_flash_sale(
        db=db,
        name=name,
        start_time=start_time,
        end_time=end_time
    )

    flash_sale = models.FlashSale(
        name=name,
        start_time=start_time,
        end_time=end_time,
        is_active=is_active
    )

    try:
        db.add(flash_sale)
        db.commit()
    except IntegrityError as err:
        db.rollback()
        raise DuplicateEntryError(name=err.orig.args)
    except DatabaseError as err:
        db.rollback()
        raise RuntimeError(f"Failed to create flash sale: {err}")
    
def update_flash_sale(db: Session, id: int, name: str, end_time: datetime, start_time: datetime = datetime.now(timezone.utc), is_active: bool = True) -> None:
    updated_flash_sale = db.get(models.FlashSale, id)

    if not updated_flash_sale:
        raise NotFoundError(name="No active flash sale found")
    
    __validation_flash_sale(
        db=db,
        name=name,
        start_time=start_time,
        end_time=end_time,
        exclude_id=updated_flash_sale.id
    )

    updated_flash_sale.name = name
    updated_flash_sale.start_time = start_time
    updated_flash_sale.end_time = end_time
    updated_flash_sale.is_active = is_active

    try:
        db.commit()
    except IntegrityError as err:
        db.rollback()
        raise DuplicateEntryError(name=err.orig.args)
    except DatabaseError as err:
        db.rollback()
        raise RuntimeError(f"Failed to update flash sale: {err}")
    
def change_active_flash_sale(db: Session, id: int) -> None:
    updated_flash_sale = db.get(models.FlashSale, id)

    if not updated_flash_sale:
        raise NotFoundError(name="No active flash sale found")
    
    updated_flash_sale.is_active = not updated_flash_sale.is_active

    try:
        db.commit()
    except IntegrityError as err:
        db.rollback()
        raise DuplicateEntryError(name=err.orig.args)
    except DatabaseError as err:
        db.rollback()
        raise RuntimeError(f"Failed to change active flash sale: {err}")

def delete_flash_sale(db: Session, id: int) -> None:
    deleted_flash_sale = db.get(models.FlashSale, id)

    if not deleted_flash_sale:
        raise NotFoundError(name="No active flash sale found")

    try:
        db.delete(deleted_flash_sale)
        db.commit()
    except IntegrityError as err:
        db.rollback()
        raise DuplicateEntryError(name=err.orig.args)
    except DatabaseError as err:
        db.rollback()
        raise RuntimeError(f"Failed to change active flash sale: {err}")
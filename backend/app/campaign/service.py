from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import DatabaseError, IntegrityError
from datetime import datetime, timezone
from . import models
from ..exceptions import NotFoundError, DuplicateEntryError

def __validation_campaign(db: Session, name: str, start_time: datetime, end_time: datetime, exclude_id: int = None):
    if name.strip() == "":
        raise ValueError("Name cannot be empty")
    
    if start_time.date() < datetime.now().date():
        raise ValueError("Start time cannot be earlier than today")

    if end_time.date() <= start_time.date():
        raise ValueError("End time cannot be earlier or equal than start time")
    
    try:
        query = (db.query(models.Campaign)
                 .filter(models.Campaign.start_time < end_time)
                 .filter(models.Campaign.end_time > start_time))
        if exclude_id is not None:
            query = query.filter(models.Campaign.id != exclude_id)
        overlapping = query.first()
    except DatabaseError as err:
        db.rollback()
        raise RuntimeError(f"Failed to check overlapping campaigns: {err}")

    if overlapping:
        raise ValueError(
            f"Campaign '{name}' overlaps with existing campaign '{overlapping.name}' "
            f"({overlapping.start_time} - {overlapping.end_time})"
        )

def get_active_campaign(db: Session):
    now = datetime.now()

    try:
        campaigns = (db.query(models.Campaign)
                      .filter(models.Campaign.start_time <= now)
                      .filter(models.Campaign.end_time >= now)
                      .all())
    except DatabaseError as err:
        db.rollback()
        raise RuntimeError(f"Failed to fetch active campaign: {err}")

    return campaigns

def create_campaign(db: Session, name: str, end_time: datetime, start_time: datetime = None, is_active: bool = False) -> models.Campaign:
    if start_time is None:
        start_time = datetime.now(timezone.utc)
    
    __validation_campaign(
        db=db,
        name=name,
        start_time=start_time,
        end_time=end_time
    )

    campaign = models.Campaign(
        name=name,
        start_time=start_time,
        end_time=end_time,
        is_active=is_active
    )

    try:
        db.add(campaign)
        db.commit()
        db.refresh(campaign)
    except IntegrityError as err:
        db.rollback()
        raise DuplicateEntryError(name=err.orig.args)
    except DatabaseError as err:
        db.rollback()
        raise RuntimeError(f"Failed to create campaign: {err}")
    
    return campaign

def update_campaign(db: Session, id: int, name: str, end_time: datetime, start_time: datetime = None, is_active: bool = True) -> models.Campaign:
    if start_time is None:
        start_time = datetime.now(timezone.utc)
    
    updated_campaign = db.get(models.Campaign, id)

    if not updated_campaign:
        raise NotFoundError(name="Campaign not found")
    
    __validation_campaign(
        db=db,
        name=name,
        start_time=start_time,
        end_time=end_time,
        exclude_id=updated_campaign.id
    )

    updated_campaign.name = name
    updated_campaign.start_time = start_time
    updated_campaign.end_time = end_time
    updated_campaign.is_active = is_active

    try:
        db.commit()
        db.refresh(updated_campaign)
    except IntegrityError as err:
        db.rollback()
        raise DuplicateEntryError(name=err.orig.args)
    except DatabaseError as err:
        db.rollback()
        raise RuntimeError(f"Failed to update campaign: {err}")
    
    return updated_campaign

def change_active_campaign(db: Session, id: int) -> models.Campaign:
    updated_campaign = db.get(models.Campaign, id)

    if not updated_campaign:
        raise NotFoundError(name="Campaign not found")
    
    updated_campaign.is_active = not updated_campaign.is_active

    try:
        db.commit()
        db.refresh(updated_campaign)
    except IntegrityError as err:
        db.rollback()
        raise DuplicateEntryError(name=err.orig.args)
    except DatabaseError as err:
        db.rollback()
        raise RuntimeError(f"Failed to change active campaign: {err}")
    
    return updated_campaign

def delete_campaign(db: Session, id: int) -> None:
    deleted_campaign = db.get(models.Campaign, id)

    if not deleted_campaign:
        raise NotFoundError(name="Campaign not found")

    # Validasi 1: Campaign harus dalam status nonaktif
    if deleted_campaign.is_active:
        raise ValueError(
            "Cannot delete an active campaign. "
            "Please deactivate the campaign first via PATCH /campaign/{id}/active"
        )

    # Validasi 2: Campaign tidak boleh memiliki produk yang terdaftar
    if deleted_campaign.items and len(deleted_campaign.items) > 0:
        raise ValueError(
            "Cannot delete campaign that has registered products. "
            "Please remove all products from the campaign first"
        )

    try:
        db.delete(deleted_campaign)
        db.commit()
    except IntegrityError as err:
        db.rollback()
        raise DuplicateEntryError(name=err.orig.args)
    except DatabaseError as err:
        db.rollback()
        raise RuntimeError(f"Failed to delete campaign: {err}")
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.user.dependencies import get_current_user
from . import schemas, service

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("/", response_model=schemas.Order)
def create_order(
    order: schemas.OrderCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    try:
        db_order = service.create_order(db, current_user.id, order)
        return db_order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/", response_model=List[schemas.Order])
def list_my_orders(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return service.get_user_orders(db, current_user.id)

@router.get("/shop", response_model=List[schemas.Order])
def list_shop_orders(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get list of orders that contain products owned by the current user (shop owner).
    """
    return service.get_shop_orders(db, current_user.id)

@router.patch("/{order_id}/status", response_model=schemas.Order)
def update_order_status(
    order_id: int,
    status_update: schemas.OrderUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Update order status.
    - Shop Owner: Can set status to 'processing' or 'shipped'.
    - Customer: Can set status to 'completed' if current status is 'shipped'.
    """
    try:
        db_order = service.update_order_status(db, order_id, status_update.status, current_user.id)
        if not db_order:
            raise HTTPException(status_code=404, detail="Order not found")
        return db_order
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

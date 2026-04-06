from fastapi import APIRouter, Depends, HTTPException, Security, status
from sqlalchemy.orm import Session
from typing import Annotated
from app.database import get_db
from app.user.dependencies import get_current_user
from app.user.models import User
from app.schemas import SuccessResponse
from . import schemas, service

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=SuccessResponse[schemas.Order, None])
def create_order(
    current_user: Annotated[User, Security(get_current_user, scopes=["customer"])],
    order: schemas.OrderCreate,
    db: Session = Depends(get_db),
):
    try:
        db_order = service.create_order(db, current_user.id, order)
        return SuccessResponse(message="", data=schemas.Order.model_validate(db_order))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/", response_model=SuccessResponse[list[schemas.Order], None])
def list_my_orders(
    current_user: Annotated[User, Security(get_current_user, scopes=["customer"])],
    db: Session = Depends(get_db),
):
    orders = service.get_user_orders(db, current_user.id)
    return SuccessResponse(message="", data=[schemas.Order.model_validate(o) for o in orders])

@router.get("/shop", response_model=SuccessResponse[list[schemas.Order], None])
def list_shop_orders(
    current_user: Annotated[User, Security(get_current_user, scopes=["shopowner"])],
    db: Session = Depends(get_db),
):
    """
    Get list of orders that contain products owned by the current user (shop owner).
    """
    orders = service.get_shop_orders(db, current_user.id)
    return SuccessResponse(message="", data=[schemas.Order.model_validate(o) for o in orders])

@router.patch("/{order_id}/status", response_model=SuccessResponse[schemas.Order, None])
def update_order_status(
    order_id: int,
    current_user: Annotated[User, Security(get_current_user, scopes=["me"])],
    status_update: schemas.OrderUpdate,
    db: Session = Depends(get_db),
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
        return SuccessResponse(message="", data=schemas.Order.model_validate(db_order))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{order_id}", response_model=SuccessResponse[None, None])
def cancel_order(
    order_id: int,
    current_user: Annotated[User, Security(get_current_user, scopes=["customer"])],
    db: Session = Depends(get_db),
):
    """
    Cancel a pending order and restore product stock.
    Only the order owner can cancel their own order.
    """
    try:
        service.cancel_order(db, order_id, current_user.id)
        return SuccessResponse(message=f"Success delete order {order_id}", data=None)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


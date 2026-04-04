from sqlalchemy.orm import Session, joinedload
from . import models, schemas
from app.products.service import get_product_by_id
from app.products.models import Product
from app.payments import service as payment_service

ACTIVE_ORDER_STATUSES = {"pending", "processing", "shipped"}


def _items_signature(items):
    return tuple(sorted((item.product_id, item.quantity) for item in items))


def _ensure_not_duplicate_order(db: Session, user_id: int, order_data: schemas.OrderCreate):
    desired_signature = _items_signature(order_data.items)
    existing_orders = (
        db.query(models.Order)
        .filter(models.Order.user_id == user_id, models.Order.status.in_(ACTIVE_ORDER_STATUSES))
        .options(joinedload(models.Order.items))
        .all()
    )

    for order in existing_orders:
        if _items_signature(order.items) == desired_signature:
            raise ValueError("You already placed this order. Complete or cancel the previous one before retrying.")


def create_order(db: Session, user_id: int, order_data: schemas.OrderCreate):
    _ensure_not_duplicate_order(db, user_id, order_data)
    total_price = 0
    order_items = []
    
    for item in order_data.items:
        product = get_product_by_id(db, item.product_id)
        if not product:
            raise ValueError(f"Product with id {item.product_id} not found")
        
        if product.user_id == user_id:
            raise ValueError("You cannot buy your own product")

        if product.stock < item.quantity:
            raise ValueError(f"Insufficient stock for product {product.name}")
        
        item_price = product.price * item.quantity
        total_price += item_price
        
        # Update stock
        product.stock -= item.quantity
        
        order_items.append(models.OrderItem(
            product_id=item.product_id,
            quantity=item.quantity,
            price=product.price
        ))
    
    db_order = models.Order(
        user_id=user_id,
        total_price=total_price,
        items=order_items
    )
    
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    snap_response = payment_service.create_snap_transaction(db_order)
    payment_service.record_payment(db, db_order, snap_response)
    
    db.refresh(db_order)
    return db_order

def get_user_orders(db: Session, user_id: int):
    return db.query(models.Order).filter(models.Order.user_id == user_id)\
        .options(joinedload(models.Order.items).joinedload(models.OrderItem.product))\
        .options(joinedload(models.Order.owner))\
        .options(joinedload(models.Order.payment))\
        .all()

def get_shop_orders(db: Session, user_id: int):
    # Get orders that contain products owned by this user
    return db.query(models.Order).join(models.OrderItem).join(Product)\
        .filter(Product.user_id == user_id)\
        .options(joinedload(models.Order.items).joinedload(models.OrderItem.product))\
        .options(joinedload(models.Order.owner))\
        .options(joinedload(models.Order.payment))\
        .distinct().all()

def update_order_status(db: Session, order_id: int, status: str, user_id: int):
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not db_order:
        return None
    
    # Check if user is the buyer
    is_buyer = db_order.user_id == user_id
    
    # Check if user is a seller for any product in the order
    is_seller = db.query(models.OrderItem).join(Product).filter(
        models.OrderItem.order_id == order_id,
        Product.user_id == user_id
    ).first() is not None
    
    allowed = False
    
    if is_seller and status in ["processing", "shipped"]:
        allowed = True
    elif is_buyer and status == "completed" and db_order.status == "shipped":
        allowed = True
        
    if not allowed:
        raise PermissionError("You are not allowed to perform this status update")
        
    db_order.status = status
    db.commit()
    db.refresh(db_order)
    return db_order

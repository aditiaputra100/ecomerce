import json
import uuid
import httpx
import midtransclient
from midtransclient.error_midtrans import MidtransAPIError
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.config import settings
from app.orders import models as order_models
from . import models

def _snap_url():
    base = "https://app.midtrans.com" if settings.MIDTRANS_IS_PRODUCTION else "https://app.sandbox.midtrans.com"
    return f"{base}/snap/v1/transactions"


def _basic_auth():
    return httpx.BasicAuth(settings.MIDTRANS_SERVER_KEY, "")


def _build_items(order: order_models.Order):
    items = []
    for item in order.items:
        items.append(
            {
                "id": str(item.product_id),
                "price": item.price,
                "quantity": item.quantity,
                "name": item.product.name if item.product else f"Product {item.product_id}",
            }
        )
    return items


def _build_customer(order: order_models.Order):
    owner = order.owner
    return {
        "first_name": owner.username,
        "email": owner.email,
    }


def create_snap_transaction(order: order_models.Order):
    order_identifier = f"order-{order.id}-{uuid.uuid4().hex[:8]}"
    if settings.MIDTRANS_USE_STUB:
        return {
            "token": f"stub-token-{order_identifier}",
            "redirect_url": f"{settings.MIDTRANS_FINISH_REDIRECT_URL}&order_id={order_identifier}",
            "order_id": order_identifier,
        }

    snap = midtransclient.Snap(
        is_production=settings.MIDTRANS_IS_PRODUCTION,
        server_key=settings.MIDTRANS_SERVER_KEY,
    )

    payload = {
        "transaction_details": {
            "order_id": order_identifier,
            "gross_amount": order.total_price,
        },
        "item_details": _build_items(order),
        "customer_details": _build_customer(order),
    }

    try:
        transaction = snap.create_transaction(payload)

    except MidtransAPIError as err:
        raise HTTPException(status_code=err.http_status_code, detail=err.message)
    
    return transaction


def record_payment(db: Session, order: order_models.Order, snap_response: dict):
    payment = models.Payment(
        order_id=order.id,
        midtrans_order_id=snap_response["token"],
        snap_token=snap_response["token"],
        redirect_url=snap_response["redirect_url"],
        gross_amount=order.total_price,
        status="pending",
        raw_response=json.dumps(snap_response),
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment


def handle_webhook(db: Session, payload: dict):
    midtrans_order_id = payload.get("order_id")
    payment = db.query(models.Payment).filter(models.Payment.midtrans_order_id == midtrans_order_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    payment.status = payload.get("transaction_status", payment.status)
    payment.raw_response = json.dumps(payload)

    order = payment.order
    if payload.get("transaction_status") in {"settlement", "capture"}:
        order.status = "processing"
    elif payload.get("transaction_status") in {"cancel", "deny", "expire"}:
        order.status = "cancelled"

    db.commit()
    db.refresh(payment)
    db.refresh(order)
    return payment

import hashlib
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
from app.schemas import success_response
from . import schemas, service

router = APIRouter(prefix="/payments", tags=["Payments"])


def _generate_signature(payload: schemas.MidtransWebhook) -> str:
    raw = f"{payload.order_id}{payload.status_code}{payload.gross_amount}{settings.MIDTRANS_SERVER_KEY}"
    return hashlib.sha512(raw.encode()).hexdigest()


@router.post("/midtrans/webhook")
def midtrans_webhook(payload: schemas.MidtransWebhook, db: Session = Depends(get_db)):
    expected = _generate_signature(payload)
    if payload.signature_key != expected:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature")

    payment = service.handle_webhook(db, payload.model_dump())
    return success_response(data={"status": payment.status}, status_code=202)


@router.get("/config")
def get_midtrans_config():
    config = {"clientKey": settings.MIDTRANS_CLIENT_KEY}
    return success_response(data=config)

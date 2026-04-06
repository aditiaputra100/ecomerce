import hashlib
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
from app.schemas import SuccessResponse
from . import schemas, service

router = APIRouter(prefix="/payments", tags=["Payments"])


def _generate_signature(payload: schemas.MidtransWebhook) -> str:
    raw = f"{payload.order_id}{payload.status_code}{payload.gross_amount}{settings.MIDTRANS_SERVER_KEY}"
    return hashlib.sha512(raw.encode()).hexdigest()


@router.post("/midtrans/webhook", status_code=202, response_model=SuccessResponse[schemas.WebhookStatusResponse, None])
def midtrans_webhook(payload: schemas.MidtransWebhook, db: Session = Depends(get_db)):
    expected = _generate_signature(payload)
    if payload.signature_key != expected:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature")

    payment = service.handle_webhook(db, payload.model_dump())
    return SuccessResponse(message="", data=schemas.WebhookStatusResponse(status=payment.status))


@router.get("/config", response_model=SuccessResponse[schemas.MidtransConfigResponse, None])
def get_midtrans_config():
    config = schemas.MidtransConfigResponse(clientKey=settings.MIDTRANS_CLIENT_KEY)
    return SuccessResponse(message="", data=config)

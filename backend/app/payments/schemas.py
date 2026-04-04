from pydantic import BaseModel, ConfigDict
from typing import Optional


class PaymentSummary(BaseModel):
    id: int
    midtrans_order_id: str
    snap_token: str
    redirect_url: str
    gross_amount: float
    status: str

    model_config = ConfigDict(from_attributes=True)


class MidtransWebhook(BaseModel):
    order_id: str
    status_code: str
    transaction_status: str
    fraud_status: Optional[str] = None
    signature_key: str
    gross_amount: str


class MidtransResponse(BaseModel):
    token: str
    redirect_url: str
    order_id: str

export interface PaymentSummary {
  id: number
  midtrans_order_id: string
  snap_token: string
  redirect_url: string
  gross_amount: number
  status: string
}

export interface MidtransConfigResponse {
  clientKey: string
}

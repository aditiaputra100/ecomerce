import type { User } from './user.type'
import type { PaymentSummary } from './payment.type'

export interface OrderItem {
  id: number
  product_id: number
  quantity: number
  price: number
}

export interface OrderUpdate {
  status: string
}

export interface Order {
  id: number
  user_id: number
  total_price: number
  status: string
  created_at: string
  items: OrderItem[]
  owner: User
  payment?: PaymentSummary | null
}

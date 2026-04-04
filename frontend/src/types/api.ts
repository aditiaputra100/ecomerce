export interface User {
  id: number
  username: string
  email: string
}

export interface Shop {
  id: number
  name: string
  description?: string | null
  logo_url?: string | null
  owner: User
}

export interface Category {
  id: number
  name: string
  description: string
  icon: string
}

export interface Product {
  id: number
  name: string
  description: string
  price: number
  stock: number
  image_url?: string | null
  owner: User
  category: Category
}

export interface ProductInput {
  name: string
  description: string
  price: number
  stock: number
  is_publish?: boolean
  image?: File | null
}

export interface OrderItem {
  id: number
  product_id: number
  quantity: number
  price: number
  product?: Product
}

export interface PaymentSummary {
  id: number
  midtrans_order_id: string
  snap_token: string
  redirect_url: string
  gross_amount: number
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

export interface AuthTokenResponse {
  access_token: string
  token_type: string
}

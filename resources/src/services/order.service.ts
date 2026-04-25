import { request } from './http'
import type { Order, OrderUpdate } from '../types'

export function listMyOrders(token: string) {
  return request<Order[]>('/orders', { token })
}

export function listShopOrders(token: string) {
  return request<Order[]>('/orders/shop', { token })
}

export function createOrder(token: string, items: { product_id: number; quantity: number }[]) {
  return request<Order>('/orders', {
    method: 'POST',
    token,
    body: JSON.stringify({ items }),
  })
}

export function updateOrderStatus(token: string, orderId: number, payload: OrderUpdate) {
  return request<Order>(`/orders/${orderId}/status`, {
    method: 'PATCH',
    token,
    body: JSON.stringify(payload),
  })
}

export function cancelOrder(token: string, orderId: number) {
  return request<void>(`/orders/${orderId}`, { method: 'DELETE', token })
}

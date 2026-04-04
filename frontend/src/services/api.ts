import { API_URL } from '../config'
import type { AuthTokenResponse, Category, Order, Product, ProductInput, Shop, User } from '../types/api'

type Options = RequestInit & { token?: string }

const defaultHeaders = { 'Content-Type': 'application/json' }

async function request<T>(path: string, options: Options = {}): Promise<T> {
  const { token, headers, ...rest } = options
  const finalHeaders = new Headers(headers || {})
  if (!(rest.body instanceof FormData)) {
    Object.entries(defaultHeaders).forEach(([key, value]) => {
      if (!finalHeaders.has(key)) {
        finalHeaders.set(key, value)
      }
    })
  }
  if (token) {
    finalHeaders.set('Authorization', `Bearer ${token}`)
  }

  const response = await fetch(`${API_URL}${path}`, {
    ...rest,
    headers: finalHeaders,
  })

  if (!response.ok) {
    let detail = 'Request failed'
    try {
      const data = await response.json()
      detail = data.detail ?? JSON.stringify(data)
    } catch (_) {
      // ignore
    }
    throw new Error(detail)
  }

  if (response.status === 204) {
    return undefined as T
  }

  return (await response.json()) as T
}

export async function registerUser(payload: { username: string; email: string; password: string }) {
  return request<User>('/register', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export async function loginUser(payload: { username: string; password: string }): Promise<AuthTokenResponse> {
  const body = new URLSearchParams()
  body.append('username', payload.username)
  body.append('password', payload.password)
  return request<AuthTokenResponse>('/token', {
    method: 'POST',
    body,
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
}

export function fetchCurrentUser(token: string) {
  return request<User>('/user/me', { token })
}

export async function fetchMyShop(token: string): Promise<Shop | null> {
  try {
    return await request<Shop>('/shops/me', { token })
  } catch (error) {
    return null
  }
}

export function openShop(token: string, data: { name: string; description?: string; logo?: File | null }) {
  const formData = new FormData()
  formData.append('name', data.name)
  if (data.description) formData.append('description', data.description)
  if (data.logo) formData.append('logo', data.logo)
  return request<Shop>('/shops', {
    method: 'POST',
    body: formData,
    token,
  })
}

export function listProducts() {
  return request<Product[]>('/products')
}

export function getProduct(productId: string | number) {
  return request<Product>(`/products/${productId}`)
}

export function fetchMyProducts(token: string) {
  return request<Product[]>('/products/me', { token })
}

export function createProduct(token: string, payload: ProductInput) {
  const formData = new FormData()
  formData.append('name', payload.name)
  formData.append('description', payload.description)
  formData.append('price', payload.price.toString())
  formData.append('stock', payload.stock.toString())
  formData.append('is_publish', (payload.is_publish ?? true).toString())
  if (payload.image) {
    formData.append('image', payload.image)
  }
  return request<Product>('/products', { method: 'POST', body: formData, token })
}

export function updateProduct(token: string, productId: number, payload: ProductInput) {
  const formData = new FormData()
  formData.append('name', payload.name)
  formData.append('description', payload.description)
  formData.append('price', payload.price.toString())
  formData.append('stock', payload.stock.toString())
  formData.append('is_publish', (payload.is_publish ?? true).toString())
  if (payload.image) {
    formData.append('image', payload.image)
  }
  return request<Product>(`/products/${productId}`, { method: 'PUT', body: formData, token })
}

export function deleteProduct(token: string, productId: number) {
  return request<void>(`/products/${productId}`, { method: 'DELETE', token })
}

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

export function fetchMidtransClientKey() {
  return request<{ clientKey: string }>('/payments/config')
}

export async function getCategory() {
  return await request<Category[]>("/categories")
}
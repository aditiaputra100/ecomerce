import { request } from './http'
import type { Product, ProductInput, ProductShop } from '../types'

export function listProducts(category?: string, username?: string) {
  const params = new URLSearchParams()
  if (category) params.set('category', category)
  if (username) params.set('username', username)
  const query = params.toString()
  return request<Product[]>(`/products${query ? `?${query}` : ''}`)
}

export function getProduct(slug: string) {
  return request<Product>(`/products/${slug}`)
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

export function toggleProductPublish(token: string, productId: number) {
  return request<Product>(`/products/${productId}/publish`, { method: 'PATCH', token })
}

export function fetchUserProducts(username: string) {
  return request<ProductShop>(`/${username}/products`)
}

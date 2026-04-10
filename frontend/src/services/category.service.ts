import { request } from './http'
import type { Category } from '../types'

export function listCategories() {
  return request<Category[]>('/categories')
}

export function getCategoryById(categoryId: number) {
  return request<Category>(`/categories/${categoryId}`)
}

export function createCategory(token: string, payload: { name: string; description?: string; icon?: string }) {
  return request<Category>('/categories', {
    method: 'POST',
    token,
    body: JSON.stringify(payload),
  })
}

export function updateCategory(token: string, categoryId: number, payload: { name?: string; description?: string; icon?: string }) {
  return request<Category>(`/categories/${categoryId}`, {
    method: 'PUT',
    token,
    body: JSON.stringify(payload),
  })
}

export function deleteCategory(token: string, categoryId: number) {
  return request<void>(`/categories/${categoryId}`, { method: 'DELETE', token })
}

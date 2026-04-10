import { request } from './http'
import type { Shop } from '../types'

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

export function fetchShopByUsername(username: string) {
  return request<Shop>(`/shops/${username}`)
}

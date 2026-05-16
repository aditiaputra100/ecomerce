import { request } from './http'
import type { AuthSessionResponse, User } from '../types'

export async function registerUser(payload: { username: string; email: string; password: string }) {
  return request<AuthSessionResponse>('/register', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export async function loginUser(payload: { username: string; password: string }): Promise<AuthSessionResponse> {
  const body = new URLSearchParams()
  body.append('username', payload.username)
  body.append('password', payload.password)

  return request<AuthSessionResponse>('/token', {
    method: 'POST',
    body,
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
}

export function fetchCurrentUser(token: string) {
  return request<User>('/user/me', { token })
}

export function refreshSession() {
  return request<AuthSessionResponse>('/token/refresh', {
    method: 'POST',
    skipSessionRefresh: true,
  })
}

export function logoutUser() {
  return request<void>('/logout', {
    method: 'POST',
    skipSessionRefresh: true,
  })
}

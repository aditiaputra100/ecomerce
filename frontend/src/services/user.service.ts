import { request } from './http'
import type { User, Token } from '../types'

export async function registerUser(payload: { username: string; email: string; password: string }) {
  return request<User>('/register', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export async function loginUser(payload: { username: string; password: string }): Promise<Token> {
  const body = new URLSearchParams()
  body.append('username', payload.username)
  body.append('password', payload.password)
  return request<Token>('/token', {
    method: 'POST',
    body,
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
}

export function fetchCurrentUser(token: string) {
  return request<User>('/user/me', { token })
}

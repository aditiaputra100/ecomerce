import { API_URL } from '../config'
import type { SuccessResponse } from '../types'

type Options = RequestInit & { token?: string }

const defaultHeaders = { 'Content-Type': 'application/json' }

export async function request<T>(path: string, options: Options = {}): Promise<T> {
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
      detail = data.detail ?? data.message ?? JSON.stringify(data)
    } catch (_) {
      // ignore
    }
    throw new Error(detail)
  }

  if (response.status === 204) {
    return undefined as T
  }

  const json = (await response.json()) as SuccessResponse<T>
  return json.data
}

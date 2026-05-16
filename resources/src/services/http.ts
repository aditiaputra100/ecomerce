import { API_URL } from '../config'
import type { SuccessResponse } from '../types'

type Options = RequestInit & { token?: string; skipSessionRefresh?: boolean }

type SessionRefresher = (() => Promise<string | null>) | null

const defaultHeaders = { 'Content-Type': 'application/json' }
let sessionRefresher: SessionRefresher = null
let refreshPromise: Promise<string | null> | null = null

export function setSessionRefresher(refresher: SessionRefresher) {
  sessionRefresher = refresher
}

export async function request<T>(path: string, options: Options = {}): Promise<T> {
  const { token, headers, skipSessionRefresh = false, ...rest } = options

  const buildHeaders = (currentToken?: string) => {
    const finalHeaders = new Headers(headers || {})
    if (!(rest.body instanceof FormData)) {
      Object.entries(defaultHeaders).forEach(([key, value]) => {
        if (!finalHeaders.has(key)) {
          finalHeaders.set(key, value)
        }
      })
    }
    if (currentToken) {
      finalHeaders.set('Authorization', `Bearer ${currentToken}`)
    }
    return finalHeaders
  }

  const performFetch = (currentToken?: string) =>
    fetch(`${API_URL}${path}`, {
      ...rest,
      credentials: 'include',
      headers: buildHeaders(currentToken),
    })

  let response = await performFetch(token)

  if (response.status === 401 && token && !skipSessionRefresh && sessionRefresher) {
    if (!refreshPromise) {
      refreshPromise = sessionRefresher().finally(() => {
        refreshPromise = null
      })
    }

    const refreshedToken = await refreshPromise
    if (refreshedToken) {
      response = await performFetch(refreshedToken)
    }
  }

  if (!response.ok) {
    let detail = 'Request failed'
    try {
      const data = await response.json()
      detail = data.detail ?? data.message ?? JSON.stringify(data)
    } catch {
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

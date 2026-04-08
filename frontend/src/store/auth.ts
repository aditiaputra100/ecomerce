import { create } from 'zustand'
import type { Shop, User } from '../types'
import { fetchCurrentUser, fetchMyShop, loginUser, openShop, registerUser } from '../services'

const TOKEN_KEY = 'ecommerce_token'

interface AuthState {
  token: string | null
  profile: User | null
  shop: Shop | null
  loading: boolean
  error: string | null
  initialized: boolean
  bootstrap: () => Promise<void>
  login: (payload: { username: string; password: string }) => Promise<void>
  register: (payload: { username: string; email: string; password: string }) => Promise<void>
  logout: () => void
  refreshProfile: () => Promise<void>
  openShop: (payload: { name: string; description?: string; logo?: File | null }) => Promise<void>
}

export const useAuthStore = create<AuthState>((set, get) => ({
  token: localStorage.getItem(TOKEN_KEY),
  profile: null,
  shop: null,
  loading: false,
  error: null,
  initialized: false,
  bootstrap: async () => {
    const token = get().token
    if (token) {
      try {
        await get().refreshProfile()
      } catch {
        // ignore, refreshProfile handles clearing token
      }
    }
    set({ initialized: true })
  },
  login: async (payload) => {
    set({ loading: true, error: null })
    try {
      const response = await loginUser(payload)
      localStorage.setItem(TOKEN_KEY, response.access_token)
      set({ token: response.access_token })
      await get().refreshProfile()
    } catch (error) {
      set({ error: (error as Error).message })
      throw error
    } finally {
      set({ loading: false })
    }
  },
  register: async (payload) => {
    set({ loading: true, error: null })
    try {
      await registerUser(payload)
    } catch (error) {
      set({ error: (error as Error).message })
      throw error
    } finally {
      set({ loading: false })
    }
  },
  logout: () => {
    localStorage.removeItem(TOKEN_KEY)
    set({ token: null, profile: null, shop: null })
  },
  refreshProfile: async () => {
    const token = get().token
    if (!token) return
    try {
      const profile = await fetchCurrentUser(token)
      const shop = await fetchMyShop(token)
      set({ profile, shop })
    } catch (error) {
      localStorage.removeItem(TOKEN_KEY)
      set({ token: null, profile: null, shop: null })
      throw error
    }
  },
  openShop: async (payload) => {
    const token = get().token
    if (!token) throw new Error('Unauthorized')
    const shop = await openShop(token, payload)
    set({ shop })
    await get().refreshProfile()
  },
}))

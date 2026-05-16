import { create } from 'zustand'
import type { Shop, User } from '../types'
import {
  fetchCurrentUser,
  fetchMyShop,
  loginUser,
  logoutUser,
  openShop,
  refreshSession as refreshSessionRequest,
  registerUser,
} from '../services'
import { setSessionRefresher } from '../services/http'

let refreshSessionInFlight: Promise<string | null> | null = null
let bootstrapInFlight: Promise<void> | null = null

interface AuthState {
  token: string | null
  profile: User | null
  shop: Shop | null
  loading: boolean
  error: string | null
  initialized: boolean
  bootstrap: () => Promise<void>
  login: (payload: { username: string; password: string }) => Promise<boolean>
  register: (payload: { username: string; email: string; password: string }) => Promise<void>
  logout: () => Promise<void>
  refreshSession: () => Promise<string | null>
  refreshProfile: () => Promise<void>
  openShop: (payload: { name: string; description?: string; logo?: File | null }) => Promise<void>
}

export const useAuthStore = create<AuthState>((set, get) => ({
  token: null,
  profile: null,
  shop: null,
  loading: false,
  error: null,
  initialized: false,
  refreshSession: async () => {
    if (refreshSessionInFlight) {
      return refreshSessionInFlight
    }

    refreshSessionInFlight = (async () => {
      const response = await refreshSessionRequest()
      set({ token: response.access_token, profile: response.user })
      return response.access_token
    })().finally(() => {
      refreshSessionInFlight = null
    })

    return refreshSessionInFlight
  },
  bootstrap: async () => {
    if (get().initialized) {
      return
    }

    if (bootstrapInFlight) {
      await bootstrapInFlight
      return
    }

    bootstrapInFlight = (async () => {
      try {
        await get().refreshProfile()
      } catch {
        // ignore, refreshProfile handles clearing session state
      } finally {
        set({ initialized: true })
      }
    })().finally(() => {
      bootstrapInFlight = null
    })

    await bootstrapInFlight
  },
  login: async (payload) => {
    set({ loading: true, error: null })

    if (payload.username === '' || payload.password === '') {
      set({ loading: false, error: 'Username dan password harus diisi.' })
      return false
    }

    try {
      const response = await loginUser(payload)
      set({ token: response.access_token, profile: response.user })
      await get().refreshProfile()

      return true
      
    } catch (error) {
      set({ error: (error as Error).message })
      return false
    } finally {
      set({ loading: false })
    }
  },
  register: async (payload) => {
    set({ loading: true, error: null })
    try {
      const response = await registerUser(payload)
      set({ token: response.access_token, profile: response.user })
      await get().refreshProfile()
    } catch (error) {
      set({ error: (error as Error).message })
      throw error
    } finally {
      set({ loading: false })
    }
  },
  logout: async () => {
    try {
      await logoutUser()
    } finally {
      set({ token: null, profile: null, shop: null })
    }
  },
  refreshProfile: async () => {
    let token = get().token
    if (!token) {
      try {
        token = await get().refreshSession()
      } catch {
        set({ token: null, profile: null, shop: null })
        return
      }
    }

    if (!token) return

    try {
      const [profile, shop] = await Promise.all([fetchCurrentUser(token), fetchMyShop(token)])
      set({ profile, shop })
    } catch (error) {
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

setSessionRefresher(async () => {
  try {
    return await useAuthStore.getState().refreshSession()
  } catch {
    return null
  }
})

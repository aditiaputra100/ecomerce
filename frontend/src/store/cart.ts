import { create } from 'zustand'
import type { Product } from '../types/api'

export interface CartItem {
  product: Product
  quantity: number
}

interface CartState {
  items: CartItem[]
  addItem: (product: Product, quantity?: number) => void
  removeItem: (productId: number) => void
  updateQuantity: (productId: number, quantity: number) => void
  clear: () => void
}

const STORAGE_KEY = 'ecommerce_cart'

const readInitialCart = (): CartItem[] => {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return []
    const parsed = JSON.parse(raw) as CartItem[]
    return parsed
  } catch {
    return []
  }
}

const persist = (items: CartItem[]) => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(items))
}

export const useCartStore = create<CartState>((set, get) => ({
  items: readInitialCart(),
  addItem: (product, quantity = 1) => {
    const existing = get().items
    const idx = existing.findIndex((item) => item.product.id === product.id)
    let updated: CartItem[]
    if (idx >= 0) {
      updated = existing.map((item, index) =>
        index === idx
          ? {
              ...item,
              quantity: item.quantity + quantity,
            }
          : item,
      )
    } else {
      updated = [...existing, { product, quantity }]
    }
    persist(updated)
    set({ items: updated })
  },
  removeItem: (productId) => {
    const updated = get().items.filter((item) => item.product.id !== productId)
    persist(updated)
    set({ items: updated })
  },
  updateQuantity: (productId, quantity) => {
    const updated = get().items.map((item) =>
      item.product.id === productId ? { ...item, quantity } : item,
    )
    persist(updated)
    set({ items: updated })
  },
  clear: () => {
    persist([])
    set({ items: [] })
  },
}))

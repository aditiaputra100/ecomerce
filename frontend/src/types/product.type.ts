import type { User } from './user.type'
import type { Category } from './category.type'

export interface Product {
  id: number
  name: string
  description: string
  price: number
  stock: number
  image_url?: string | null
  owner: User
  category?: Category | null
}

export interface ProductInput {
  name: string
  description: string
  price: number
  stock: number
  is_publish?: boolean
  image?: File | null
}

export interface ProductsOnShop {
  id: number
  name: string
  description: string
  price: number
  stock: number
  image_url?: string | null
  category?: Category | null
}

export interface ProductShop {
  owner: User
  products: ProductsOnShop[]
}

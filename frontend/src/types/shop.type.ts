import type { User } from './user.type'

export interface Shop {
  id: number
  name: string
  description?: string | null
  logo_url?: string | null
  owner: User
}

import { API_URL } from '../config'

export const resolveImageUrl = (path?: string | null, fallback?: string) => {
  if (!path) return fallback ?? 'https://placehold.co/400x300?text=Product'
  if (path.startsWith('http')) return path
  return `${API_URL}${path}`
}

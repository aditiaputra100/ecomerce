import {create} from 'zustand'
import type { Category } from '../types/api'
import { getCategory } from '../services/api'

interface CategoryState {
    categories: Category[]
    isLoading: boolean
    error: string | null
    hasFetched: boolean
    fetchPromise: Promise<void> | null
    fetchCategories: (options?: { force?: boolean }) => Promise<void>
}

// const STORAGE_KEY = 'ecomerce_category'

let fetchPromiseRef: Promise<void> | null = null

export const useCategory = create<CategoryState>((set, get) => ({
    categories: [],
    isLoading: false,
    error: null,
    hasFetched: false,
    fetchPromise: null,
    fetchCategories: async (options?: { force?: boolean }) => {
        const state = get()
        const { force = false } = options || {}

        // Return existing promise if fetch is already in-flight
        if (fetchPromiseRef) {
            return fetchPromiseRef
        }

        // Skip refetch if data already exists and not forcing refresh
        if (state.hasFetched && !force) {
            return Promise.resolve()
        }

        set({ isLoading: true, error: null })

        const fetchPromise = (async () => {
            try {
                const data = await getCategory()
                set({ categories: data, hasFetched: true, error: null })
            } catch (error) {
                if (error instanceof Error) {
                    set({ error: error.message })
                } else {
                    set({ error: 'Failed to fetch categories' })
                }
            } finally {
                set({ isLoading: false })
                fetchPromiseRef = null
            }
        })()

        fetchPromiseRef = fetchPromise
        set({ fetchPromise })

        return fetchPromise
    }
}))
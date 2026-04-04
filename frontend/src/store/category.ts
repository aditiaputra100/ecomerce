import {create} from 'zustand'
import type { Category } from '../types/api'
import { getCategory } from '../services/api'

interface CategoryState {
    categories: Category[]
    isLoading: boolean
    error: string | null
    fetchCategories: () => Promise<void>
}

// const STORAGE_KEY = 'ecomerce_category'

export const useCategory = create<CategoryState>((set) => ({
    categories: [],
    isLoading: false,
    error: null,
    fetchCategories: async () => {
        set({isLoading: true})

        try {
            const data = await getCategory()
            set({categories: data})

        } catch(error) {
            if (error instanceof Error) set({error: error.message})
        } finally {
            set({isLoading: false})
        }
    }
}))
import { Navigate, useLocation } from 'react-router-dom'
import { CircularProgress, Stack } from '@mui/material'
import { useAuthStore } from '../store/auth'
import type { ReactNode } from 'react'

interface Props {
  children: ReactNode
  requireShop?: boolean
}

export function ProtectedRoute({ children, requireShop = false }: Props) {
  const token = useAuthStore((state) => state.token)
  const shop = useAuthStore((state) => state.shop)
  const initialized = useAuthStore((state) => state.initialized)
  const location = useLocation()

  if (!initialized) {
    return (
      <Stack alignItems="center" justifyContent="center" minHeight="50vh">
        <CircularProgress />
      </Stack>
    )
  }

  if (!token) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  if (requireShop && !shop) {
    return <Navigate to="/dashboard/open-shop" replace />
  }

  return children
}

import { useEffect } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'
import MainLayout from './components/layout/MainLayout'
import HomePage from './pages/HomePage'
import ProductDetailPage from './pages/ProductDetailPage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import CartPage from './pages/CartPage'
import CheckoutPage from './pages/CheckoutPage'
import CheckoutStatusPage from './pages/CheckoutStatusPage'
import CampaignDetailPage from './pages/CampaignDetailPage'
import StoreDashboard from './pages/dashboard/StoreDashboard'
import OpenShopPage from './pages/dashboard/OpenShopPage'
import { ProtectedRoute } from './routes/ProtectedRoute'
import { useAuthStore } from './store/auth'
import { useCategory } from './store/category'
import './App.css'

function App() {
  const bootstrap = useAuthStore((state) => state.bootstrap)
  const fetchCategories = useCategory((state) => state.fetchCategories)

  useEffect(() => {
    bootstrap()
  }, [bootstrap])

  useEffect(() => {
    fetchCategories()
  }, [fetchCategories])

  return (
    <Routes>
      <Route element={<MainLayout />}>
        <Route index element={<HomePage />} />
        <Route path="/p/:slug" element={<ProductDetailPage />} />
        <Route path="/campaign/:campaignId" element={<CampaignDetailPage />} />
        <Route path="/cart" element={<CartPage />} />
        <Route
          path="/checkout"
          element={
            <ProtectedRoute>
              <CheckoutPage />
            </ProtectedRoute>
          }
        />
        <Route path="/checkout/status" element={<CheckoutStatusPage />} />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute requireShop>
              <StoreDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/dashboard/open-shop"
          element={
            <ProtectedRoute>
              <OpenShopPage />
            </ProtectedRoute>
          }
        />
      </Route>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App

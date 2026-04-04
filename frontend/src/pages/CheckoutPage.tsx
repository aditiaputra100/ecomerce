import { useState } from 'react'
import {
  Alert,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Stack,
  Typography,
} from '@mui/material'
import { useCartStore } from '../store/cart'
import { useAuthStore } from '../store/auth'
import { createOrder } from '../services/api'

const CheckoutPage = () => {
  const items = useCartStore((state) => state.items)
  const clearCart = useCartStore((state) => state.clear)
  const token = useAuthStore((state) => state.token)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const total = items.reduce((sum, item) => sum + item.product.price * item.quantity, 0)

  const handleCheckout = async () => {
    if (!token) return
    setLoading(true)
    setError(null)
    try {
      const order = await createOrder(
        token,
        items.map((item) => ({ product_id: item.product.id, quantity: item.quantity })),
      )
      const redirectUrl = order.payment?.redirect_url
      if (!redirectUrl) {
        throw new Error('Midtrans tidak mengembalikan redirect URL')
      }
      clearCart()
      window.location.assign(redirectUrl)
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setLoading(false)
    }
  }

  if (items.length === 0) {
    return <Alert severity="info">Keranjang kosong.</Alert>
  }

  return (
    <Stack spacing={3}>
      <Typography variant="h4">Checkout</Typography>
      <Card>
        <CardContent>
          <Stack spacing={1}>
            {items.map((item) => (
              <Stack key={item.product.id} direction="row" justifyContent="space-between">
                <Typography>{item.product.name}</Typography>
                <Typography>
                  {item.quantity} x Rp {item.product.price.toLocaleString('id-ID')}
                </Typography>
              </Stack>
            ))}
            <Typography variant="h6">Total: Rp {total.toLocaleString('id-ID')}</Typography>
            {error && <Alert severity="error">{error}</Alert>}
            <Button
              variant="contained"
              onClick={handleCheckout}
              disabled={loading}
              startIcon={loading ? <CircularProgress size={18} /> : undefined}
            >
              Bayar dengan Midtrans
            </Button>
          </Stack>
        </CardContent>
      </Card>
    </Stack>
  )
}

export default CheckoutPage

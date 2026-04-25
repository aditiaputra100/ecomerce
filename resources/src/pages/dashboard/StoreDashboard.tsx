import { useEffect, useState } from 'react'
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Skeleton,
  Stack,
  TextField,
  Typography,
} from '@mui/material'
import { alpha, useTheme } from '@mui/material/styles'
import { useAuthStore } from '../../store/auth'
import { createProduct, fetchMyProducts, listShopOrders } from '../../services'
import type { Order, Product } from '../../types'

const StoreDashboard = () => {
  const theme = useTheme()
  const token = useAuthStore((state) => state.token)
  const shop = useAuthStore((state) => state.shop)
  const [products, setProducts] = useState<Product[]>([])
  const [orders, setOrders] = useState<Order[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [productForm, setProductForm] = useState({
    name: '',
    description: '',
    price: '',
    stock: '',
  })
  const [productImage, setProductImage] = useState<File | null>(null)

  useEffect(() => {
    if (!token) return
    Promise.all([fetchMyProducts(token), listShopOrders(token)])
      .then(([productList, shopOrders]) => {
        setProducts(productList)
        setOrders(shopOrders)
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [token])

  const handleCreateProduct = async () => {
    if (!token) return
    try {
      await createProduct(token, {
        name: productForm.name,
        description: productForm.description,
        price: Number(productForm.price),
        stock: Number(productForm.stock),
        is_publish: true,
        image: productImage,
      })
      const updated = await fetchMyProducts(token)
      setProducts(updated)
      setDialogOpen(false)
      setProductForm({ name: '', description: '', price: '', stock: '' })
      setProductImage(null)
      setError(null)
    } catch (err) {
      setError((err as Error).message)
    }
  }

  if (!shop) {
    return <Alert severity="info">Silakan buka toko terlebih dahulu.</Alert>
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>
  }

  const overviewCards = [
    { label: 'Total Produk', value: products.length.toString() },
    {
      label: 'Pesanan Aktif',
      value: orders.filter((order) => order.status !== 'completed').length.toString(),
    },
    {
      label: 'Pesanan Selesai',
      value: orders.filter((order) => order.status === 'completed').length.toString(),
    },
    { label: 'Stok Terjual', value: `${products.reduce((sum, item) => sum + item.stock, 0)} pcs` },
  ]

  return (
    <Stack spacing={4}>
      <Box
        sx={{
          borderRadius: 4,
          p: 4,
          background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
          color: '#fff',
          display: 'flex',
          flexDirection: 'column',
          gap: 2,
        }}
      >
        <Typography variant="h4" fontWeight={700}>
          {shop.name}
        </Typography>
        <Typography sx={{ opacity: 0.85 }}>{shop.description || 'Toko kamu, gaya kamu.'}</Typography>
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
          <Button variant="contained" color="primary" onClick={() => setDialogOpen(true)}>
            Tambah Produk Baru
          </Button>
          <Button variant="outlined" color="secondary">
            Lihat katalog publik
          </Button>
        </Stack>
      </Box>

      <Box
        sx={{
          display: 'grid',
          gap: 2,
          gridTemplateColumns: { xs: 'repeat(2, minmax(0, 1fr))', md: 'repeat(4, minmax(0, 1fr))' },
        }}
      >
        {overviewCards.map((card) => (
              <Card
                key={card.label}
                sx={{
                  borderRadius: 4,
                  p: 2,
                  bgcolor: 'background.paper',
                  border: '1px solid',
                  borderColor: 'divider',
                  boxShadow: `0 20px 35px ${alpha(theme.palette.secondary.main, 0.12)}`,
                }}
              >
            <Typography variant="subtitle2" color="text.secondary">
              {card.label}
            </Typography>
            <Typography variant="h5" fontWeight={700}>
              {card.value}
            </Typography>
          </Card>
        ))}
      </Box>

      <Stack spacing={2}>
        <Stack direction="row" justifyContent="space-between" alignItems="center">
          <Typography variant="h5" fontWeight={700}>
            Produk Saya
          </Typography>
          <Button variant="text" onClick={() => setDialogOpen(true)}>
            Produk baru
          </Button>
        </Stack>
        <Box
          sx={{
            display: 'grid',
            gap: 2,
            gridTemplateColumns: { xs: '1fr', md: 'repeat(2, minmax(0, 1fr))' },
          }}
        >
          {loading
            ? Array.from({ length: 4 }, (_, idx) => (
                <Skeleton key={idx} variant="rounded" height={140} />
              ))
            : products.map((product) => (
                <Card
                  key={product.id}
                  sx={{
                    borderRadius: 4,
                    border: '1px solid',
                    borderColor: 'divider',
                    boxShadow: `0 15px 30px ${alpha(theme.palette.secondary.main, 0.1)}`,
                  }}
                >
                  <CardContent>
                    <Typography variant="h6" fontWeight={700}>
                      {product.name}
                    </Typography>
                    <Typography color="text.secondary" gutterBottom>
                      Stok {product.stock} • Rp {product.price.toLocaleString('id-ID')}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {product.description}
                    </Typography>
                  </CardContent>
                </Card>
              ))}
        </Box>
      </Stack>

      <Stack spacing={2}>
        <Typography variant="h5" fontWeight={700}>
          Pesanan Terbaru
        </Typography>
        {orders.length === 0 && !loading ? (
          <Alert severity="info">Belum ada pesanan.</Alert>
        ) : (
          <Stack spacing={2}>
            {loading
              ? Array.from({ length: 3 }, (_, idx) => <Skeleton key={idx} variant="rounded" height={100} />)
              : orders.map((order) => (
                  <Card
                    key={order.id}
                    sx={{ borderRadius: 4, border: '1px solid', borderColor: 'divider', bgcolor: 'background.paper' }}
                  >
                    <CardContent>
                      <Stack direction="row" justifyContent="space-between" alignItems="center">
                        <Box>
                          <Typography fontWeight={700}>Order #{order.id}</Typography>
                          <Typography variant="body2" color="text.secondary">
                            Customer: {order.owner.username}
                          </Typography>
                        </Box>
                        <Typography fontWeight={600}>{order.status}</Typography>
                      </Stack>
                      <Typography mt={1} color="text.secondary">
                        Total Rp {order.total_price.toLocaleString('id-ID')}
                      </Typography>
                    </CardContent>
                  </Card>
                ))}
          </Stack>
        )}
      </Stack>

      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} fullWidth maxWidth="sm">
        <DialogTitle>Tambah Produk</DialogTitle>
        <DialogContent>
          <Stack spacing={2} mt={1}>
            <TextField
              label="Nama Produk"
              value={productForm.name}
              onChange={(e) => setProductForm((prev) => ({ ...prev, name: e.target.value }))}
              fullWidth
            />
            <TextField
              label="Deskripsi"
              value={productForm.description}
              onChange={(e) =>
                setProductForm((prev) => ({ ...prev, description: e.target.value }))
              }
              fullWidth
              multiline
              minRows={3}
            />
            <TextField
              label="Harga"
              type="number"
              value={productForm.price}
              onChange={(e) => setProductForm((prev) => ({ ...prev, price: e.target.value }))}
              fullWidth
            />
            <TextField
              label="Stok"
              type="number"
              value={productForm.stock}
              onChange={(e) => setProductForm((prev) => ({ ...prev, stock: e.target.value }))}
              fullWidth
            />
            <Button component="label" variant="outlined">
              Upload Foto
              <input
                type="file"
                accept="image/*"
                hidden
                onChange={(e) => setProductImage(e.target.files?.[0] ?? null)}
              />
            </Button>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Batal</Button>
          <Button onClick={handleCreateProduct} variant="contained">
            Simpan
          </Button>
        </DialogActions>
      </Dialog>
    </Stack>
  )
}

export default StoreDashboard

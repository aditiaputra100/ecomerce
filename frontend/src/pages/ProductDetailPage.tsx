import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import {
  Box,
  Breadcrumbs,
  Button,
  CardContent,
  CardMedia,
  CircularProgress,
  Container,
  Stack,
  Typography,
  useMediaQuery,
  useTheme,
} from '@mui/material'
import {Error as ErrorIcon} from '@mui/icons-material'
import { getProduct } from '../services/api'
import type { Product } from '../types/api'
import { useCartStore } from '../store/cart'
import { resolveImageUrl } from '../utils/url'

const ProductDetailPage = () => {
  const theme = useTheme()
  const { productId } = useParams()
  const [product, setProduct] = useState<Product | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<boolean>(false)
  const addItem = useCartStore((state) => state.addItem)
  const isMobile = useMediaQuery(theme.breakpoints.down('md'))

  useEffect(() => {
    if (!productId) return

    async function getProductById() {
      if (!productId) return

      try {
        const response = await getProduct(productId)
        setProduct(response)
        
      } catch(error) {
        if (error instanceof Error) {
          setError(true)
        } else {
          setError(false)
        }
      } finally {
        setLoading(false)
      }
    }

    getProductById()

  }, [productId])

  if (loading) {
    return (
      <Stack alignItems="center" justifyContent="center">
        <CircularProgress />
      </Stack>
    )
  }

  if (error || !product) {
    return (
      <Stack height='100%' alignItems='center' justifyContent='center'>
        <Stack justifyContent='center' alignItems='center' spacing={2}>
          <ErrorIcon sx={{fontSize: '64px'}}/>
          <Typography fontWeight={700} fontSize={24}>
            Produk tidak ditemukan
          </Typography>
        </Stack>
      </Stack>
    )
  }

  const breadcrumbs = [
    <Link to='/' style={{textDecoration: 'none', color: theme.palette.primary.main}}>Home</Link>,
    <Link to='/' style={{textDecoration: 'none', color: theme.palette.primary.main}}>{product.category.name}</Link>,
    <Typography>{product.name}</Typography>
  ]

  if (isMobile) return (
    <Box>
      <Stack direction={{ xs: 'column', md: 'row' }}>
        <Box
          component="img"
          src={resolveImageUrl(product.image_url, 'https://placehold.co/600x400?text=Product')}
          sx={{ width: { md: '30%' }, height: 400,}}
          alt={product.name}
        />
        <CardContent sx={{ flexGrow: 1 }}>
          <Stack spacing={2}>
            <Typography variant="h4">{product.name}</Typography>
            <Typography color="text.secondary">{product.description}</Typography>
            <Typography variant="h5" fontWeight="bold">
              Rp {product.price.toLocaleString('id-ID')}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Stok tersedia: {product.stock}
            </Typography>
            <Button
              variant="contained"
              onClick={() => addItem(product, 1)}
              disabled={product.stock === 0}
            >
              Tambah ke Keranjang
            </Button>
          </Stack>
        </CardContent>
      </Stack>
    </Box>
  )

  return (
    <Box py={4}>
      <Container>
        <Breadcrumbs separator='>' aria-label='breadcrumb'>
          {breadcrumbs}
        </Breadcrumbs>
        <Stack direction={{ xs: 'column', md: 'row' }} marginTop={2}>
          <Box
            component="img"
            src={resolveImageUrl(product.image_url, 'https://placehold.co/600x400?text=Product')}
            sx={{ width: { md: '30%' }, height: 400,}}
            alt={product.name}
          />
          <CardContent sx={{ flexGrow: 1 }}>
            <Stack spacing={2}>
              <Typography variant="h4">{product.name}</Typography>
              <Typography color="text.secondary">{product.description}</Typography>
              <Typography variant="h5" fontWeight="bold">
                Rp {product.price.toLocaleString('id-ID')}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Stok tersedia: {product.stock}
              </Typography>
              <Button
                variant="contained"
                onClick={() => addItem(product, 1)}
                disabled={product.stock === 0}
              >
                Tambah ke Keranjang
              </Button>
            </Stack>
          </CardContent>
        </Stack>
      </Container>
    </Box>
  )
}

export default ProductDetailPage

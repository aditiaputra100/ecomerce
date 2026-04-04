import {
  Box,
  Card,
  CardContent,
  Stack,
  Typography,
  useTheme,
} from '@mui/material'
import { alpha } from '@mui/material/styles'
import type { Product } from '../../types/api'
import { resolveImageUrl } from '../../utils/url'
import { Link } from 'react-router'

interface Props {
  product: Product
}

const ProductCard = ({ product }: Props) => {
  const theme = useTheme()

  return (
    <Card
      component={Link}
      to={`/p/${product.id}`}
      sx={{
        height: '100%',
        borderRadius: 4,
        display: 'flex',
        flexDirection: 'column',
        textDecoration: 'none',
        border: '1px solid',
        borderColor: alpha(theme.palette.secondary.main, 0.12),
        boxShadow: `0 20px 40px ${alpha(theme.palette.secondary.main, 0.12)}`,
      }}
    >
      <Box
        sx={{
          height: 220,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          overflow: 'hidden',
        }}
      >
        <Box
          component="img"
          src={resolveImageUrl(product.image_url)}
          alt={product.name}
          sx={{ width: '100%', height: '100%', objectFit: 'cover'}}
        />
      </Box>
      <CardContent sx={{ flexGrow: 1 }}>
        <Stack spacing={1.5}>
          <Typography variant="h6" fontWeight={700}>
            {product.name}
          </Typography>
          <Typography color="text.secondary">{product.description}</Typography>
          <Typography variant="h5" fontWeight={700}>
            Rp {product.price.toLocaleString('id-ID')}
          </Typography>
        </Stack>
      </CardContent>
    </Card>
  )
}

export default ProductCard

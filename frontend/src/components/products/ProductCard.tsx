import {
  Card,
  CardActionArea,
  CardContent,
  CardMedia,
  Stack,
  Typography,
  useTheme,
} from '@mui/material'
import { alpha } from '@mui/material/styles'
import type { Product } from '../../types'
import { resolveImageUrl } from '../../utils/url'
import { Link } from 'react-router'

interface Props {
  product: Product
}

const ProductCard = ({ product }: Props) => {
  const theme = useTheme()

    return (
      <Card
      sx={{
        width: '100%',
        maxWidth: { xs: '100%', sm: 320, md: 340 },
        marginX: { xs: 0, sm: 'auto' },
        minWidth: 0,
        boxSizing: 'border-box',
        height: '100%',
        borderRadius: 4,
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
        textDecoration: 'none',
        border: '1px solid',
        borderColor: alpha(theme.palette.secondary.main, 0.12),
        boxShadow: `0 20px 40px ${alpha(theme.palette.secondary.main, 0.12)}`,
      }}
    >
      <CardActionArea component={Link} to={`/p/${product.slug}`}>
        <CardMedia sx={{height: 220}} image={resolveImageUrl(product.image_url)} title={product.name} />
        
        <CardContent sx={{ flexGrow: 1 }}>
          <Stack spacing={1.5}>
            <Typography fontSize="1.25rem" fontWeight={700} sx={{ overflowWrap: 'anywhere' }}>
              {product.name}
            </Typography>
            <Typography color="text.secondary" sx={{ overflowWrap: 'anywhere' }}>
              {product.description}
            </Typography>
            <Typography fontSize="1.25rem" fontWeight={700}>
              Rp {product.price.toLocaleString('id-ID')}
            </Typography>
          </Stack>
        </CardContent>
      </CardActionArea>
    </Card>
  )
}

export default ProductCard

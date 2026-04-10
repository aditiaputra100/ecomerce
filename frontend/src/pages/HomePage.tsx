import { useEffect, useState } from 'react'
import {
  Alert,
  Box,
  Button,
  Container,
  Grid,
  Skeleton,
  Stack,
  Typography,
  useMediaQuery,
  useTheme,
} from '@mui/material'
import {
  OfflineBolt as OfflineBoltIcon,
  ArrowRight as ArrowRightIcon,
  ArrowLeft as ArrowLeftIcon
} from '@mui/icons-material'
import ProductCard from '../components/products/ProductCard'
import { listProducts } from '../services'
import type { Product } from '../types'
import Banner from '../components/Banner'
import CategoryList from '../components/CategoryList'
import Timer from '../components/Timer'
import EmptyItem from '../components/EmptyItem'

const HomePage = () => {
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down('md'))
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const getProducts = async () => {
      try {
        const response = await listProducts()
        setProducts(response)

      } catch(error){
        if (error instanceof Error) {
          setError(error.message)
        } else {
          setError('An unknown error occurred during fetch data')
        }
      } finally {
        setLoading(false)
      }
    }

    getProducts()

  }, [])


  const productsShowcase = products.slice(0, 8)

  return (
    <Box>
        {!isMobile && (
          <Banner />
        )}
        
        <CategoryList />

        <Box component='section' sx={{bgcolor: 'white', boxShadow: '0 -5px 10px -5px rgba(255, 255, 255, 0.5)'}}>
          <Container sx={{paddingY: 4}}>
            <Box display='flex' justifyContent='space-between' alignItems='center' gap={2} marginBottom={4}>
              <Box display='flex' alignItems='center' gap={2}>
                <OfflineBoltIcon fontSize='large' />
                <Typography variant='h5' fontWeight={700}>Flash sale</Typography>
                <Timer />
              </Box>
              <Box display='flex' gap={1}>
                <Button variant='outlined' sx={{width: '32px'}}>
                  <ArrowLeftIcon />
                </Button>
                <Button variant='contained'>
                  <ArrowRightIcon />
                </Button>
              </Box>
            </Box>
            
            

          </Container>
        </Box>
        <Box component='section' sx={{paddingY: 4,}}>
            <Container>
              <Typography variant='h5' marginBottom={2} fontWeight={700}>Todays For You!</Typography>
              {error && <Alert severity="error">{error}</Alert>}
              <Grid container spacing={2}>
                {loading &&
                   Array.from({ length: 8 }, (_, idx) => (
                      <Grid key={idx} size={3}>
                        <Skeleton variant="rounded" height={320} sx={{ borderRadius: 4 }} />
                      </Grid>
                    ))
                }
                {(!loading && !error) && productsShowcase.length == 0 ? 
                  (
                      <EmptyItem description='There are no products here'/>
                  ) : productsShowcase.map((product) => 
                        <Grid key={product.id} size={{lg: 3, md: 6, xs: 12}}>
                          <ProductCard product={product}/>
                        </Grid>
                      )
                }
              </Grid>
            </Container>
        </Box>
        <Box component='section' className='slogan-container'>
          <Stack
            component={Container}
            justifyContent='center' 
            alignItems='center' 
            height='100%' 
            color={theme.palette.primary.contrastText}
          >
            <h2 className='slogan-text'>Let's Shop Beyond Boundaries</h2>
          </Stack >
        </Box>
    </Box>
  )
}

export default HomePage

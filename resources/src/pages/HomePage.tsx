import { useEffect, useState } from 'react'
import {
  Alert,
  Box,
  Container,
  Grid,
  Skeleton,
  Stack,
  Typography,
  useTheme,
} from '@mui/material'
import ProductCard from '../components/products/ProductCard'
import { listProducts, listActiveCampaigns } from '../services'
import type { Product, CampaignResponse } from '../types'
import Banner from '../components/Banner'
import CategoryList from '../components/CategoryList'
import EmptyItem from '../components/EmptyItem'
import Campaign from '../components/Campaign'
import './HomePage.css'

type CampaignWithTime = CampaignResponse & { seconds: number }

function calculateCampaignSeconds(endTime: string): number {
  const now = new Date().getTime()
  const target = new Date(endTime).getTime()
  const remainingSeconds = Math.floor((target - now) / 1000)

  return remainingSeconds > 0 ? remainingSeconds : 0
}

const HomePage = () => {
  const theme = useTheme()
  // const isMobile = useMediaQuery(theme.breakpoints.down('md'))
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [campaigns, setCampaigns] = useState<CampaignWithTime[]>([])
  const [campaignLoading, setCampaignLoading] = useState(true)
  const [campaignError, setCampaignError] = useState<string | null>(null)

  useEffect(() => {
    const getProducts = async () => {
      try {
        const response = await listProducts()
        setProducts(response)
      } catch (error) {
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

  useEffect(() => {
    const getActiveCampaign = async () => {
      setCampaignLoading(true)
      setCampaignError(null)

      try {
        const response = await listActiveCampaigns()
        setCampaigns(
          response.map((campaign) => ({
            ...campaign,
            seconds: calculateCampaignSeconds(campaign.end_time),
          })),
        )
      } catch (error) {
        console.error('Failed to fetch active campaigns:', error)
        setCampaignError('Failed to load active campaigns')
      } finally {
        setCampaignLoading(false)
      }
    }

    getActiveCampaign()
  }, [])

  const productsShowcase = products.slice(0, 8)

  return (
    <>
      <Banner />

      <CategoryList />

      {!campaignLoading &&
        campaignError && (
          <Box component="section" sx={{ py: 4 }}>
            <Container>
              <Alert severity="error">{campaignError}</Alert>
            </Container>
          </Box>
        )}

        {!campaignLoading &&
        !campaignError &&
        campaigns.map((campaign) => (
          <Campaign key={campaign.id} campaign={campaign} />
        ))}

      <Box component="section" sx={{ paddingY: 4 }}>
        <Container>
          <Typography variant="h2" marginBottom={2}>
            Todays For You!
          </Typography>
          {error && <Alert severity="error">{error}</Alert>}
          <Grid container spacing={2}>
            {loading &&
              Array.from({ length: 8 }, (_, idx) => (
                <Grid key={idx} size={3}>
                  <Skeleton variant="rounded" height={320} sx={{ borderRadius: 4 }} />
                </Grid>
              ))}
            {!loading && !error && productsShowcase.length === 0 ? (
              <EmptyItem description="There are no products here" />
            ) : (
              productsShowcase.map((product) => (
                <Grid key={product.id} size={{ lg: 3, md: 6, xs: 12 }}>
                  <ProductCard product={product} />
                </Grid>
              ))
            )}
          </Grid>
        </Container>
      </Box>
      <Box component="section" className="slogan-container">
        <Stack
          component={Container}
          justifyContent="center"
          alignItems="center"
          height="100%"
          color={theme.palette.primary.contrastText}
        >
          <h2 className="slogan-text">Let's Shop Beyond Boundaries</h2>
        </Stack>
      </Box>
    </>
  )
}

export default HomePage

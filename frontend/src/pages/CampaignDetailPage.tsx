import { useEffect, useMemo, useState } from 'react'
import { Link as RouterLink, useParams } from 'react-router-dom'
import { Alert, Box, Breadcrumbs, Container, Grid, Skeleton, Stack, Typography } from '@mui/material'
import { listActiveCampaigns } from '../services'
import type { CampaignResponse } from '../types'
import ProductCardSale from '../components/products/ProductCardSale'
import EmptyItem from '../components/EmptyItem'

const CampaignDetailPage = () => {
  const { campaignId } = useParams()
  const [campaign, setCampaign] = useState<CampaignResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const parsedCampaignId = useMemo(() => Number(campaignId), [campaignId])

  useEffect(() => {
    const loadCampaign = async () => {
      if (!campaignId || Number.isNaN(parsedCampaignId)) {
        setError('Campaign tidak valid')
        setLoading(false)
        return
      }

      setLoading(true)
      setError(null)

      try {
        const campaigns = await listActiveCampaigns()
        const selectedCampaign = campaigns.find((item) => item.id === parsedCampaignId)

        if (!selectedCampaign) {
          setError('Campaign tidak ditemukan atau sudah tidak aktif')
          setCampaign(null)
          return
        }

        setCampaign(selectedCampaign)
      } catch (err) {
        if (err instanceof Error) {
          setError(err.message)
        } else {
          setError('Gagal memuat data campaign')
        }
      } finally {
        setLoading(false)
      }
    }

    loadCampaign()
  }, [campaignId, parsedCampaignId])

  return (
    <Box py={4}>
      <Container>
        <Breadcrumbs separator=">" aria-label="breadcrumb">
          <RouterLink to="/" style={{ textDecoration: 'none' }}>
            Home
          </RouterLink>
          <Typography>Campaign</Typography>
          {campaign && <Typography>{campaign.name}</Typography>}
        </Breadcrumbs>

        {loading && (
          <Grid container spacing={2} mt={1}>
            {Array.from({ length: 9 }, (_, idx) => (
              <Grid key={idx} size={{ lg: 4, md: 6, xs: 12 }}>
                <Skeleton variant="rounded" height={360} sx={{ borderRadius: 4 }} />
              </Grid>
            ))}
          </Grid>
        )}

        {!loading && error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}

        {!loading && !error && campaign && (
          <Stack spacing={2} mt={2}>
            <Typography variant="h4" fontWeight={700}>
              {campaign.name}
            </Typography>
            <Typography color="text.secondary">
              Menampilkan seluruh produk campaign ({campaign.items.length} item)
            </Typography>

            {campaign.items.length === 0 ? (
              <EmptyItem description="Belum ada item di campaign ini" />
            ) : (
              <Grid container spacing={2}>
                {campaign.items.map((item) => (
                  <Grid key={item.product_id} size={{ lg: 4, md: 6, xs: 12 }}>
                    <ProductCardSale
                      product_id={item.product_id}
                      name={item.product.name}
                      sale_price={item.special_price}
                      original_price={item.product.price}
                      image_url={item.product.image_url}
                      stock_limit={item.stock_limit}
                      stock_sold={item.stock_sold}
                    />
                  </Grid>
                ))}
              </Grid>
            )}
          </Stack>
        )}
      </Container>
    </Box>
  )
}

export default CampaignDetailPage

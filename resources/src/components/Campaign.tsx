import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { alpha, Box, Button, Card, CardActionArea, CardContent, Container, Typography, useMediaQuery, useTheme } from '@mui/material'
import {
  OfflineBolt as OfflineBoltIcon,
  ArrowRight as ArrowRightIcon,
  ArrowLeft as ArrowLeftIcon,
  OpenInNew as OpenInNewIcon,
} from '@mui/icons-material'
import type { CampaignResponse } from '../types'
import Timer from './Timer'
import ProductCardSale from './products/ProductCardSale'

type CampaignWithTime = CampaignResponse & { seconds: number }

const CARD_GAP_PX = 16

interface CampaignSliderSectionProps {
  campaign: CampaignWithTime
}

function Campaign({ campaign }: CampaignSliderSectionProps) {
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'))

  const sectionRef = useRef<HTMLElement | null>(null)
  const sliderRef = useRef<HTMLDivElement | null>(null)

  const [scrollState, setScrollState] = useState({ canPrev: false, canNext: false })

  const previewItems = useMemo(() => campaign.items.slice(0, 9), [campaign.items])


  useEffect(() => {
    const section = sectionRef.current
    const slider = sliderRef.current

    if (!section || !slider) return

    const CONTAINER_INLINE_PADDING = isMobile ? 16 : 24

    const applyPadding = () => {
      const viewportWidth = document.documentElement.clientWidth
      const sectionWidth = Math.min(section.getBoundingClientRect().width, viewportWidth)
      const maxContentWidth = 1200
      const offset = Math.max(0, (sectionWidth - maxContentWidth) / 2)
      const containerPadding = offset + CONTAINER_INLINE_PADDING

      const cardsPerView = isMobile ? 2 : sectionWidth < 900 ? 3 : 5
      const totalCards = previewItems.length + 1 // +1 untuk card CTA
      const visibleCards = Math.min(cardsPerView, totalCards)

      const sliderClientWidth = Math.max(0, sectionWidth - containerPadding * 2)
      const cardWidth = Math.max(
        0,
        (sliderClientWidth - CARD_GAP_PX * (visibleCards - 1)) / visibleCards,
      )

      slider.style.setProperty('--flex-width', `${cardWidth}px`)
      slider.style.setProperty('--offset-width', `${containerPadding}px`)
    }

    applyPadding()

    const ro = new ResizeObserver(applyPadding)
    ro.observe(section)
    return () => ro.disconnect()

  }, [previewItems.length, isMobile])

  const updateScrollState = useCallback(() => {
    const slider = sliderRef.current
    if (!slider) return

    const threshold = 24
    const canPrev = slider.scrollLeft > threshold
    const canNext = slider.scrollLeft + slider.clientWidth < slider.scrollWidth - threshold
    setScrollState({ canPrev, canNext })
    
  }, [])

  useEffect(() => {
    updateScrollState()
  }, [previewItems.length, updateScrollState])

  const scrollByCard = useCallback((dir: number) => {
    const slider = sliderRef.current

    if (!slider) return

    const firstCard = slider.children[0] as HTMLElement
    const cardWidth = firstCard ? firstCard.offsetWidth + CARD_GAP_PX : 200

    slider.scrollBy({ left: dir * cardWidth, behavior: 'smooth' })
  }, [])

  return (
    <Box
      component="section"
      ref={sectionRef}
      sx={{
        bgcolor: 'white',
        overflowX: 'hidden',
        boxSizing: 'border-box',
        py: 4,
      }}
    >
        <Container maxWidth="lg">
          <Box display="flex" justifyContent="space-between" alignItems="center" gap={2} mb={3}>
            <Box display="flex" alignItems="center" gap={2} flexWrap="wrap">
              {!isMobile && <OfflineBoltIcon fontSize="large" />}
              <Typography variant="h2">
                {campaign.name}
              </Typography>
              <Timer initialSeconds={campaign.seconds} />
            </Box>

            {!isMobile && (
              <Box display="flex" gap={1}>
                <Button
                  variant="outlined"
                  sx={{ width: 32, minWidth: 32 }}
                  onClick={() => scrollByCard(-1)}
                  disabled={!scrollState.canPrev}
                  aria-label="Scroll campaign ke kiri"
                >
                  <ArrowLeftIcon />
                </Button>
                <Button
                  variant="contained"
                  sx={{
                    width: 36,
                    minWidth: 36,
                    bgcolor: '#1f1b2e',
                    '&:hover': { bgcolor: '#3d3556' },
                    '&.Mui-disabled': { bgcolor: '#ccc', color: '#fff' },
                  }}
                  onClick={() => scrollByCard(1)}
                  disabled={!scrollState.canNext}
                  aria-label="Scroll campaign ke kanan"
                >
                  <ArrowRightIcon />
                </Button>
              </Box>
            )}
          </Box>

        </Container>
        <Box
          className="slider"
          ref={sliderRef}
          onScroll={updateScrollState}
          sx={{
              gap: `${CARD_GAP_PX}px`,
              paddingInline: 'var(--offset-width)',
              scrollPaddingInlineStart: 'var(--offset-width)',
          }}
        >
            {previewItems.map((item) => (
              <Box
                key={item.product_id}
                sx={{
                  flex: `0 0 var(--flex-width)`,
                  minWidth: 0,
                }}
              >
                <ProductCardSale
                  name={item.product.name}
                  slug={item.product.slug}
                  sale_price={item.special_price}
                  original_price={item.product.price}
                  stock_limit={item.stock_limit}
                  stock_sold={item.stock_sold}
                  image_url={item.product.image_url}
                />
              </Box>
            ))}
            <Card
              sx={{
                flex: `0 0 var(--flex-width)`,
                borderRadius: 3,
                textDecoration: 'none',
                border: '1px solid',
                borderColor: alpha(theme.palette.secondary.main, 0.08),
                boxShadow: `0 4px 16px ${alpha(theme.palette.common.black, 0.08)}`,
                minWidth: 0,
              }}
            >
              <CardActionArea 
                component={Link}
                to={`/campaign/${campaign.id}`}
                sx={{height: '100%'}}
              >
                <CardContent sx={{height: '100%'}}>
                  <Box display="flex" flexDirection="column" justifyContent='center' alignItems="center" height='100%' gap={1} py={4}>
                    <OpenInNewIcon fontSize="large" />
                    <Typography fontSize="1rem" fontWeight={500}>
                      Lihat Semua
                    </Typography>
                  </Box>
                </CardContent>
              </CardActionArea>
            </Card>
        </Box>
    </Box>
  )
}

export default Campaign

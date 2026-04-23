import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import type { CSSProperties } from 'react'
import { Link } from 'react-router-dom'
import { Box, Button, Card, CardContent, Container, Typography, useMediaQuery, useTheme } from '@mui/material'
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
const PREVIEW_ITEM_COUNT = 9

interface CampaignSliderSectionProps {
  campaign: CampaignWithTime
}

function Campaign({ campaign }: CampaignSliderSectionProps) {
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'))
  const isTablet = useMediaQuery(theme.breakpoints.down('lg'))
  const sliderRef = useRef<HTMLDivElement | null>(null)
  const [scrollState, setScrollState] = useState({ canPrev: false, canNext: false })

  const slideWidth = useMemo(() => {
    if (isMobile) return 'clamp(170px, 72vw, 220px)'
    if (isTablet) return 'clamp(190px, 28vw, 260px)'
    return 'clamp(220px, 22vw, 280px)'
  }, [isMobile, isTablet])

  const previewItems = useMemo(() => campaign.items.slice(0, PREVIEW_ITEM_COUNT), [campaign.items])

  const trackVars = useMemo(
    () =>
      ({
        '--slide-width': slideWidth,
      }) as CSSProperties,
    [slideWidth],
  )

  const updateScrollState = useCallback(() => {
    const slider = sliderRef.current
    if (!slider) return

    const threshold = 24
    const canPrev = slider.scrollLeft > threshold
    const canNext = slider.scrollLeft + slider.clientWidth < slider.scrollWidth - threshold
    setScrollState({ canPrev, canNext })
  }, [])

  const handleScroll = useCallback(() => {
    updateScrollState()
  }, [updateScrollState])

  useEffect(() => {
    updateScrollState()
  }, [previewItems.length, updateScrollState])

  const scrollByPage = (direction: 'prev' | 'next') => {
    const slider = sliderRef.current
    if (!slider) return

    slider.scrollBy({
      left: direction === 'next' ? slider.clientWidth * 0.5 : -slider.clientWidth * 0.5,
      behavior: 'smooth',
    })
  }

  return (
    <Box
      component="section"
      sx={{
        bgcolor: 'white',
        overflowX: 'hidden',
        width: '100%',
        maxWidth: '100%',
        boxSizing: 'border-box',
      }}
    >
        <Container sx={{ pt: 4, pb: 3 }}>
          <Box display="flex" justifyContent="space-between" alignItems="center" gap={2} mb={3}>
            <Box display="flex" alignItems="center" gap={2} flexWrap="wrap">
              {!isMobile && <OfflineBoltIcon fontSize="large" />}
              <Typography variant="h2" fontSize="1.5rem" fontWeight={700}>
                {campaign.name}
              </Typography>
              <Timer initialSeconds={campaign.seconds} />
            </Box>

            {!isMobile && (
              <Box display="flex" gap={1}>
                <Button
                  variant="outlined"
                  sx={{ width: 32, minWidth: 32 }}
                  onClick={() => scrollByPage('prev')}
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
                  onClick={() => scrollByPage('next')}
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
        ref={sliderRef}
        onScroll={handleScroll}
        sx={{
            ...trackVars,
            display: 'flex',
            gap: `${CARD_GAP_PX}px`,
            pb: 2,
            overflowX: 'auto',
            scrollSnapType: 'x mandatory',
            scrollbarWidth: 'none',
            msOverflowStyle: 'none',
            '&::-webkit-scrollbar': { display: 'none' },
        }}
        >
            {previewItems.map((item) => (
              <Box
                key={item.product_id}
                sx={{ flex: `0 0 ${slideWidth}`, minWidth: 0, scrollSnapAlign: 'start' }}
              >
                <ProductCardSale
                  name={item.product.name}
                  slug={item.product.slug}
                  product_id={item.product_id}
                  sale_price={item.special_price}
                  original_price={item.product.price}
                  stock_limit={item.stock_limit}
                  stock_sold={item.stock_sold}
                  image_url={item.product.image_url}
                />
              </Box>
            ))}
          </Box>
    </Box>
  )
}

export default Campaign

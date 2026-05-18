import { alpha, Skeleton, useTheme, Box, useMediaQuery, Stack, Container, Typography, Button } from "@mui/material"
import { ArrowLeft as ArrowLeftIcon, ArrowRight as ArrowRightIcon } from "@mui/icons-material"
import Category from "./Category"
import { useCategory } from "../store/category"
import { useCallback, useEffect, useRef, useState } from "react"

const CARD_GAP_PX = 0

function CategoryList() {
    const theme = useTheme()
    const isMobile = useMediaQuery(theme.breakpoints.down('sm'))

    const categories = useCategory((s) => s.categories)
    const isLoading = useCategory((s) => s.isLoading)

    const categoryAlphas = [0.35, 0.45, 0.55, 0.65, 0.75, 0.85]
    const sectionRef = useRef<HTMLElement | null>(null)
    const sliderRef = useRef<HTMLDivElement | null>(null)

    const [scrollState, setScrollState] = useState({ canPrev: false, canNext: false })

    const updateScrollState = useCallback(() => {
      const slider = sliderRef.current
      if (!slider) return

      const threshold = 16
      const canPrev = slider.scrollLeft > threshold
      const canNext = slider.scrollLeft + slider.clientWidth < slider.scrollWidth - threshold
      setScrollState({ canPrev, canNext })
    }, [])

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

        slider.style.setProperty('--flex-width', `${120}px`)
        slider.style.setProperty('--offset-width', `${containerPadding}px`)
        updateScrollState()
      }

      applyPadding()

      const ro = new ResizeObserver(applyPadding)
      ro.observe(section)
      return () => ro.disconnect()
    }, [categories?.length, isMobile, updateScrollState])

    useEffect(() => {
      updateScrollState()
    }, [categories.length, updateScrollState])

    const scrollByCard = useCallback((dir: number) => {
        const slider = sliderRef.current

        if (!slider) return

        const firstCard = slider.children[0] as HTMLElement
        const cardWidth = firstCard ? firstCard.offsetWidth + CARD_GAP_PX : 200

        slider.scrollBy({ left: dir * cardWidth, behavior: 'smooth' })
    }, [])

    return (
        <Box component='section' ref={sectionRef} sx={{ marginY: 2, overflowX: 'hidden',
        boxSizing: 'border-box', }}>

          {!isMobile && (
            <Container>
              <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ marginBottom: 4 }}>
                <Typography variant="h2">
                  Belanja sesuai kategori
                </Typography>

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
              </Stack>
            </Container>
          )}
          <Box
            className='slider'
            ref={sliderRef}
            onScroll={updateScrollState}
            sx={{
              gap: `${CARD_GAP_PX}px`,
              paddingInline: 'var(--offset-width)',
              scrollPaddingInlineStart: 'var(--offset-width)',
          }}
          >
            <Category
              label="All Categories"
              bgColor={alpha(theme.palette.primary.main, 0.05)}
              icon="apps"
            />

            {isLoading && (
              Array.from({length: 9}, (_, idx) => (
                  <Skeleton
                    key={idx}
                    variant="rounded"
                    width={120}
                    height={120}
                  sx={{
                    borderRadius: 4,
                    flex: '0 0 var(--flex-width)',
                  }}
                />
              ))
            )}
            {categories.map((category, index) => (
              <Category
                label={category.name}
                bgColor={alpha(theme.palette.primary.main, categoryAlphas[index % categoryAlphas.length])}
                icon={category.icon ?? undefined}
              />
            ))}
          </Box>
        </Box>
    )
}

export default CategoryList

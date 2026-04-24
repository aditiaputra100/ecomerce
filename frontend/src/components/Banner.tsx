import {
    Box, 
    Container,
    Stack,
    ButtonBase,
    useTheme
} from '@mui/material'
import { useEffect, useState } from 'react'

const bannerFiles = ['Banner 1.jpg', 'Banner 2.jpg', 'Banner 3.jpg'] as const
const bannerSlides = bannerFiles.map((file, index) => ({
  src: `/banner/${encodeURIComponent(file)}`,
  alt: `Banner promo ${index + 1}`,
}))

function Banner() {
    const theme = useTheme()
    const [activeBanner, setActiveBanner] = useState(0)

    useEffect(() => {
        const timer = setInterval(() => {
          setActiveBanner((prev) => (prev + 1) % bannerSlides.length)
        }, 5000)
        return () => clearInterval(timer)
      }, [])

    return (
        <Container
            className="banner"
          >
              {bannerSlides.map((banner, idx) => (
                <Box
                  component="img"
                  key={banner.src}
                  src={banner.src}
                  alt={banner.alt}
                  aria-hidden={idx !== activeBanner}
                  sx={{
                    position: 'absolute',
                    inset: 0,
                    width: '100%',
                    maxWidth: '100%',
                    display: 'block',
                    height: '100%',
                    objectFit: 'cover',
                    opacity: idx === activeBanner ? 1 : 0,
                    transform: idx === activeBanner ? 'scale(1)' : 'scale(1.05)',
                    transition: 'opacity 600ms ease, transform 900ms ease',
                  }}
                />
              ))}
              <Container>
                <Stack
                  direction="row"
                  spacing={1}
                  sx={{
                    position: 'absolute',
                    bottom: 16,
                    px: 2,
                    py: 1,
                    borderRadius: 999,
                  }}
                >
                  {bannerSlides.map((slide, idx) => (
                    <ButtonBase
                      key={slide.src}
                      aria-label={`Lihat banner ${idx + 1}`}
                      disableRipple
                      onClick={() => setActiveBanner(idx)}
                      sx={{
                        width: 12,
                        height: 12,
                        borderRadius: '50%',
                        border: '1px solid #fff',
                        bgcolor: idx === activeBanner ? theme.palette.primary.main : 'transparent',
                        opacity: idx === activeBanner ? 1 : 0.7,
                        transition: 'all 200ms ease',
                      }}
                    />
                  ))}
                </Stack>
              </Container>
          </Container>
    )
}

export default Banner
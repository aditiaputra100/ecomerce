import { alpha, Box, Card, CardActionArea, CardContent, CardMedia, IconButton, LinearProgress, Typography, useTheme } from "@mui/material"
import FavoriteIcon from "@mui/icons-material/Favorite"
import FavoriteBorderIcon from "@mui/icons-material/FavoriteBorder"
import { useState } from "react"
import { Link } from "react-router-dom"
import { resolveImageUrl } from "../../utils/url"

interface ProductCardSaleProps {
    slug: string
    name: string
    sale_price: number
    original_price: number
    image_url: string
    stock_limit: number
    stock_sold: number
}

function ProductCardSale({slug, name, sale_price, original_price, image_url, stock_limit, stock_sold, }: ProductCardSaleProps) {
    const theme = useTheme()
    const [wishlisted, setWishlisted] = useState(false)

    return (
        <Card
            sx={{
                position: 'relative',
                width: '100%',
                minWidth: 0,
                boxSizing: 'border-box',
                height: '100%',
                borderRadius: 3,
                display: 'flex',
                flexDirection: 'column',
                overflow: 'hidden',
                textDecoration: 'none',
                border: '1px solid',
                borderColor: alpha(theme.palette.secondary.main, 0.08),
                boxShadow: `0 4px 16px ${alpha(theme.palette.common.black, 0.08)}`,
            }}
        >

            {/* Wishlist button */}
            <IconButton
                size="small"
                onClick={(e) => { e.preventDefault(); setWishlisted(w => !w) }}
                sx={{
                    position: 'absolute',
                    top: 4,
                    right: 4,
                    zIndex: 2,
                    bgcolor: 'rgba(255,255,255,0.85)',
                    '&:hover': { bgcolor: 'rgba(255,255,255,1)' },
                    width: 30,
                    height: 30,
                }}
            >
                {wishlisted
                    ? <FavoriteIcon fontSize="small" color="error" />
                    : <FavoriteBorderIcon fontSize="small" />
                }
            </IconButton>

            <CardActionArea component={Link} to={`/p/${slug}`} sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', alignItems: 'stretch' }}>
                <CardMedia
                    image={resolveImageUrl(image_url)}
                    title={name}
                    sx={{
                        height: 200,
                        backgroundColor: '#f5f5f5',
                        backgroundSize: 'contain',
                    }}
                />
                <CardContent sx={{ flexGrow: 1 }}>
                    <Box display='flex' flexDirection='column' gap={1.5}>
                        <Typography
                            fontSize='0.9rem'
                            color='text.primary'
                            sx={{
                                display: '-webkit-box',
                                WebkitLineClamp: 2,
                                WebkitBoxOrient: 'vertical',
                                overflow: 'hidden',
                                lineHeight: 1.4,
                                minHeight: '2.8em',
                            }}
                        >
                            {name}
                        </Typography>
                        <Box display='flex' gap={1} alignItems='center' flexWrap='wrap'>
                            <Typography fontSize={16} fontWeight={700}>
                                Rp {sale_price.toLocaleString('id-ID')}
                            </Typography>
                            <Typography fontSize={12} color='error.main' sx={{ textDecoration: 'line-through' }}>
                                Rp {original_price.toLocaleString('id-ID')}
                            </Typography>
                        </Box>
                        <Box display='flex' gap={1} alignItems='center'>
                            <LinearProgress
                                variant="determinate"
                                value={(stock_sold / stock_limit) * 100}
                                sx={{ flexGrow: 1, height: 6, borderRadius: 3 }}
                            />
                            <Typography
                                fontSize={11}
                                color={stock_sold >= stock_limit ? 'error.main' : 'text.secondary'}
                                fontWeight={stock_sold >= stock_limit ? 700 : 400}
                                whiteSpace='nowrap'
                            >
                                {stock_sold}/{stock_limit} Sale
                            </Typography>
                        </Box>
                    </Box>
                </CardContent>
            </CardActionArea>
        </Card>
    )
}

export default ProductCardSale

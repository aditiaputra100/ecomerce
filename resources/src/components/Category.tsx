import { alpha, Box, Stack, Typography, useTheme } from "@mui/material"
import Icon from '@mui/material/Icon'

interface Props {
    label: string
    icon?: string
    bgColor?: string
    href?: string
}

function extractAlphaFromString(colorString: string): number | undefined {

    const parts = colorString.match(/rgba\((\d+),\s*(\d+),\s*(\d+),\s*([\d.]+)\)/);

    if (parts && parts.length === 5) {
        return parseFloat(parts[4]); 
    }
}


function Category({label, bgColor, icon='extension', href = '/'}: Props) {
    const theme = useTheme()

    const getAlpha = bgColor ? extractAlphaFromString(bgColor) : undefined

    return (
        <Stack 
            component='a' 
            href={href} 
            spacing={2} 
            alignItems='center' 
            justifyContent='center'
            sx={{
                height: '100%',
                minHeight: 120,
                textDecoration: 'none',
                flex: `0 0 var(--flex-width)`,
                textAlign: 'center',
                color: getAlpha ? getAlpha >= 0.1 ? theme.palette.primary.contrastText : theme.palette.text.primary : theme.palette.text.primary
            }}>
            <Box
                width={64}
                height={64}
                display='flex'
                alignItems='center'
                justifyContent='center'
                border='2px solid'
                borderColor={bgColor || alpha(theme.palette.primary.main, 0.1)}
                borderRadius={3}
                color={getAlpha ? getAlpha >= 0.1 ? theme.palette.primary.contrastText : theme.palette.text.primary : theme.palette.text.primary}
            >
                <Icon fontSize="large">
                    {icon}
                </Icon>
            </Box>
            <Typography
                fontWeight={700}
                color={theme.palette.text.primary}
                sx={{
                    minHeight: 40,
                    display: '-webkit-box',
                    WebkitLineClamp: 2,
                    WebkitBoxOrient: 'vertical',
                    overflow: 'hidden',
                }}
            >
                {label}
            </Typography>
        </Stack>
    )
}

export default Category

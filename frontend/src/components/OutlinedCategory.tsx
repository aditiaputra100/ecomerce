import { Box, Stack, Typography, useTheme } from "@mui/material"
import Icon from '@mui/material/Icon'

interface Props {
    label: string
    icon?: string
    href?: string
}

function OutlinedCategory({label, icon = 'extension', href = "/"}: Props) {
    const theme = useTheme()

    return (
        <Stack 
            component='a' 
            href={href}
            spacing={2} 
            alignItems='center' 
            justifyContent='center'
            sx={{
                textDecoration: 'none',
                color: theme.palette.primary.main
            }}>
            <Box sx={{
                borderRadius: 999, 
                width: '64px', 
                height: '64px', 
                border: `1px solid ${theme.palette.primary.main}`,
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center'}}>   
                <Icon fontSize="large">
                    {icon}
                </Icon>
            </Box>
            <Typography fontWeight={700} color={theme.palette.text.primary}>{label}</Typography>
        </Stack>
    )
}

export default OutlinedCategory
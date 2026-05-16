import { AppBar, Button, Stack, Toolbar, Typography } from "@mui/material"
import { 
    HomeFilled as HomeIcon,
    AccountCircle as AccountIcon,
    Search as SearchIcon,
    ShoppingCart as ShoppingCartIcon,
} from "@mui/icons-material"

function BottomAppBar() {

    return (
        <AppBar 
            component='footer' 
            position="fixed" 
            sx={{
                color: 'primary.main',
                minHeight: '64px',
                top: 'auto', 
                bottom: 0,
                backgroundColor: 'background.default',
            }}
        >
            <Toolbar sx={{justifyContent: 'space-between', height: '64px'}}>
                <Stack component={Button} sx={{paddingInline: 0}}>
                    <HomeIcon />
                    <Typography variant="body2">Beranda</Typography>
                </Stack>
                <Stack component={Button} sx={{paddingInline: 0}}>
                    <SearchIcon />
                    <Typography variant="body2">Cari</Typography>
                </Stack>
                <Stack component={Button} sx={{paddingInline: 0}}>
                    <ShoppingCartIcon />
                    <Typography variant="body2">Keranjang</Typography>
                </Stack>
                <Stack component={Button} sx={{paddingInline: 0}}>
                    <AccountIcon />
                    <Typography variant="body2">Profil</Typography>
                </Stack>
            </Toolbar>
        </AppBar>
    )
}

export default BottomAppBar
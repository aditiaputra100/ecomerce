import { AppBar, Button, Stack, Toolbar, Typography } from "@mui/material"
import { 
    HomeFilled as HomeIcon,
    AccountCircle as AccountIcon,
    ReceiptLong as ReceiptIcon,
} from "@mui/icons-material"

function BottomAppBar() {

    return (
        <AppBar 
            component='footer' 
            position="fixed" 
            sx={{
                color: 'primary.main',
                top: 'auto', 
                bottom: 0,
                backgroundColor: 'background.default',
            }}
        >
            <Toolbar sx={{justifyContent: 'space-between'}}>
                <Stack component={Button}>
                    <HomeIcon />
                    <Typography variant="body2">Beranda</Typography>
                </Stack>
                <Stack component={Button}>
                    <ReceiptIcon />
                    <Typography variant="body2">Tansaksi</Typography>
                </Stack>
                <Stack component={Button}>
                    <AccountIcon />
                    <Typography variant="body2">Akun</Typography>
                </Stack>
            </Toolbar>
        </AppBar>
    )
}

export default BottomAppBar
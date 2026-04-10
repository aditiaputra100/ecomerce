import { Container, Stack, Typography } from "@mui/material"
import { Link } from "react-router-dom"
import { APP_NAME } from "../config"

function Footer() {
    return (
        <footer>
            <Stack>
                <Container component={Stack} direction={{ xs: 'column', md: 'row' }} py={4} spacing={4}>
                    <Stack spacing={1} flex={1}>
                        <Typography variant="h6" fontWeight={700}>
                            {APP_NAME}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                            Let's shop beyond boundaries. Platform belanja online terpercaya dengan berbagai pilihan produk berkualitas.
                        </Typography>
                    </Stack>
                    <Stack spacing={1} flex={1}>
                        <Typography fontWeight={700} marginBottom={1}>
                            Quick Links
                        </Typography>
                        <Link to="/" style={{ textDecoration: 'none', color: 'inherit' }}>
                            <Typography variant="body2" sx={{ '&:hover': { textDecoration: 'underline' } }}>Home</Typography>
                        </Link>
                        <Link to="/cart" style={{ textDecoration: 'none', color: 'inherit' }}>
                            <Typography variant="body2" sx={{ '&:hover': { textDecoration: 'underline' } }}>Keranjang</Typography>
                        </Link>
                        <Link to="/login" style={{ textDecoration: 'none', color: 'inherit' }}>
                            <Typography variant="body2" sx={{ '&:hover': { textDecoration: 'underline' } }}>Login</Typography>
                        </Link>
                        <Link to="/register" style={{ textDecoration: 'none', color: 'inherit' }}>
                            <Typography variant="body2" sx={{ '&:hover': { textDecoration: 'underline' } }}>Daftar</Typography>
                        </Link>
                    </Stack>
                    <Stack spacing={1} flex={1}>
                        <Typography fontWeight={700} marginBottom={1}>
                            Informasi
                        </Typography>
                        <Typography variant="body2" sx={{ cursor: 'pointer', '&:hover': { textDecoration: 'underline' } }}>Tentang Kami</Typography>
                        <Typography variant="body2" sx={{ cursor: 'pointer', '&:hover': { textDecoration: 'underline' } }}>Syarat & Ketentuan</Typography>
                        <Typography variant="body2" sx={{ cursor: 'pointer', '&:hover': { textDecoration: 'underline' } }}>Kebijakan Privasi</Typography>
                        <Typography variant="body2" sx={{ cursor: 'pointer', '&:hover': { textDecoration: 'underline' } }}>Karir</Typography>
                    </Stack>
                    <Stack spacing={1} flex={1}>
                        <Typography fontWeight={700} marginBottom={1}>
                            Bantuan & Layanan
                        </Typography>
                        <Typography variant="body2" sx={{ cursor: 'pointer', '&:hover': { textDecoration: 'underline' } }}>Pusat Bantuan</Typography>
                        <Typography variant="body2" sx={{ cursor: 'pointer', '&:hover': { textDecoration: 'underline' } }}>Cara Belanja</Typography>
                        <Typography variant="body2" sx={{ cursor: 'pointer', '&:hover': { textDecoration: 'underline' } }}>Pengembalian Barang</Typography>
                        <Typography variant="body2" sx={{ cursor: 'pointer', '&:hover': { textDecoration: 'underline' } }}>Hubungi Kami</Typography>
                    </Stack>
                </Container>
                <Stack borderTop='1px solid rgba(0, 0, 0, 0.1)' justifyContent='center' textAlign='center'>
                    <p>&copy; 2026 {APP_NAME}</p>
                </Stack>
            </Stack>
        </footer>
    )
}

export default Footer
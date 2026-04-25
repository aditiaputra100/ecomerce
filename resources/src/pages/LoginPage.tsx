import { useState } from 'react'
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Stack,
  TextField,
  Typography,
} from '@mui/material'
import { Link as RouterLink, useNavigate, useLocation } from 'react-router-dom'
import type { Location } from 'react-router-dom'
import { useAuthStore } from '../store/auth'

const LoginPage = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const login = useAuthStore((state) => state.login)
  const loading = useAuthStore((state) => state.loading)
  const error = useAuthStore((state) => state.error)
  const [form, setForm] = useState({ username: '', password: '' })

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    try {
      await login(form)
      const redirect = (location.state as { from?: Location })?.from?.pathname ?? '/'
      navigate(redirect)
    } catch {
      // error handled via store
    }
  }

  return (
    <Stack alignItems="center" justifyContent="center" minHeight="80vh">
      <Card sx={{ maxWidth: 400, width: '100%' }}>
        <CardContent>
          <Stack spacing={2} component="form" onSubmit={handleSubmit}>
            <Box>
              <Typography variant="h5" fontWeight="bold">
                Masuk
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Selamat datang kembali.
              </Typography>
            </Box>
            {error && <Alert severity="error">{error}</Alert>}
            <TextField
              label="Username"
              fullWidth
              required
              value={form.username}
              onChange={(e) => setForm((prev) => ({ ...prev, username: e.target.value }))}
            />
            <TextField
              label="Password"
              type="password"
              fullWidth
              required
              value={form.password}
              onChange={(e) => setForm((prev) => ({ ...prev, password: e.target.value }))}
            />
            <Button type="submit" variant="contained" disabled={loading}>
              {loading ? 'Memproses...' : 'Masuk'}
            </Button>
            <Typography variant="body2" textAlign="center">
              Belum punya akun? <RouterLink to="/register">Daftar sekarang</RouterLink>
            </Typography>
          </Stack>
        </CardContent>
      </Card>
    </Stack>
  )
}

export default LoginPage

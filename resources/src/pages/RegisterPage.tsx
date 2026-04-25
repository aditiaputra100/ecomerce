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
import { Link as RouterLink, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/auth'

const RegisterPage = () => {
  const navigate = useNavigate()
  const register = useAuthStore((state) => state.register)
  const loading = useAuthStore((state) => state.loading)
  const error = useAuthStore((state) => state.error)
  const [form, setForm] = useState({ username: '', email: '', password: '' })

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    await register(form)
    navigate('/login')
  }

  return (
    <Stack alignItems="center" justifyContent="center" minHeight="80vh">
      <Card sx={{ maxWidth: 420, width: '100%' }}>
        <CardContent>
          <Stack spacing={2} component="form" onSubmit={handleSubmit}>
            <Box>
              <Typography variant="h5" fontWeight="bold">
                Daftar
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Buat akun untuk mulai berbelanja atau membuka toko.
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
              label="Email"
              type="email"
              fullWidth
              required
              value={form.email}
              onChange={(e) => setForm((prev) => ({ ...prev, email: e.target.value }))}
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
              {loading ? 'Memproses...' : 'Daftar'}
            </Button>
            <Typography variant="body2" textAlign="center">
              Sudah punya akun? <RouterLink to="/login">Masuk</RouterLink>
            </Typography>
          </Stack>
        </CardContent>
      </Card>
    </Stack>
  )
}

export default RegisterPage

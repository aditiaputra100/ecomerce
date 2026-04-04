import { useEffect, useState } from 'react'
import {
  Alert,
  Button,
  Card,
  CardContent,
  Stack,
  TextField,
  Typography,
} from '@mui/material'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../../store/auth'

const OpenShopPage = () => {
  const navigate = useNavigate()
  const openShop = useAuthStore((state) => state.openShop)
  const shop = useAuthStore((state) => state.shop)
  const [form, setForm] = useState({ name: '', description: '' })
  const [logo, setLogo] = useState<File | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (shop) {
      navigate('/dashboard')
    }
  }, [shop, navigate])

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setLoading(true)
    setError(null)
    try {
      await openShop({ ...form, logo })
      navigate('/dashboard')
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Stack spacing={3}>
      <Typography variant="h4">Buka Toko</Typography>
      <Card>
        <CardContent>
          <Stack spacing={2} component="form" onSubmit={handleSubmit}>
            {error && <Alert severity="error">{error}</Alert>}
            <TextField
              label="Nama Toko"
              fullWidth
              required
              value={form.name}
              onChange={(e) => setForm((prev) => ({ ...prev, name: e.target.value }))}
            />
            <TextField
              label="Deskripsi"
              fullWidth
              multiline
              minRows={3}
              value={form.description}
              onChange={(e) => setForm((prev) => ({ ...prev, description: e.target.value }))}
            />
            <Button variant="outlined" component="label">
              Upload Logo
              <input
                hidden
                type="file"
                accept="image/*"
                onChange={(e) => setLogo(e.target.files?.[0] ?? null)}
              />
            </Button>
            <Button type="submit" variant="contained" disabled={loading}>
              {loading ? 'Memproses...' : 'Buat Toko'}
            </Button>
          </Stack>
        </CardContent>
      </Card>
    </Stack>
  )
}

export default OpenShopPage

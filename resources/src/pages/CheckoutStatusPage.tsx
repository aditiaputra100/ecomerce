import { Alert, Button, Stack, Typography } from '@mui/material'
import { useSearchParams, Link as RouterLink } from 'react-router-dom'

const CheckoutStatusPage = () => {
  const [params] = useSearchParams()
  const state = params.get('state')

  let message = 'Status pembayaran tidak diketahui.'
  let severity: 'success' | 'info' | 'error' = 'info'

  if (state === 'success' || state === 'finish') {
    message = 'Pembayaran berhasil! Pesanan akan segera diproses.'
    severity = 'success'
  } else if (state === 'pending') {
    message = 'Pembayaran masih diproses. Anda akan mendapatkan notifikasi setelah selesai.'
    severity = 'info'
  } else if (state === 'error') {
    message = 'Terjadi kesalahan saat pembayaran.'
    severity = 'error'
  }

  return (
    <Stack spacing={2} alignItems="center">
      <Typography variant="h4">Status Pembayaran</Typography>
      <Alert severity={severity} sx={{ width: '100%' }}>
        {message}
      </Alert>
      <Button component={RouterLink} to="/" variant="contained">
        Kembali Belanja
      </Button>
    </Stack>
  )
}

export default CheckoutStatusPage

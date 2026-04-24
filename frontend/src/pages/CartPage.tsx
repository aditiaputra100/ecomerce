import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Container,
  IconButton,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material'
import DeleteIcon from '@mui/icons-material/Delete'
import { Link as RouterLink } from 'react-router-dom'
import { useCartStore } from '../store/cart'

const CartPage = () => {
  const items = useCartStore((state) => state.items)
  const removeItem = useCartStore((state) => state.removeItem)
  const total = items.reduce((sum, item) => sum + item.product.price * item.quantity, 0)

  if (items.length === 0) {
    return <Alert severity="info">Keranjang kosong. Mulai belanja di halaman utama.</Alert>
  }

  return (
    <Container sx={{ py: 4 }}>
    <Stack spacing={3}>
      <Typography variant="h4">Keranjang</Typography>
      <Card>
        <CardContent>
          <Box sx={{ overflowX: 'auto' }}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Produk</TableCell>
                <TableCell>Jumlah</TableCell>
                <TableCell>Harga</TableCell>
                <TableCell>Total</TableCell>
                <TableCell />
              </TableRow>
            </TableHead>
            <TableBody>
              {items.map((item) => (
                <TableRow key={item.product.id}>
                  <TableCell>{item.product.name}</TableCell>
                  <TableCell>{item.quantity}</TableCell>
                  <TableCell>Rp {item.product.price.toLocaleString('id-ID')}</TableCell>
                  <TableCell>
                    Rp {(item.product.price * item.quantity).toLocaleString('id-ID')}
                  </TableCell>
                  <TableCell align="right">
                    <IconButton onClick={() => removeItem(item.product.id)}>
                      <DeleteIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
          </Box>
        </CardContent>
      </Card>
      <Stack direction="row" justifyContent="space-between" alignItems="center">
        <Typography variant="h6">Total: Rp {total.toLocaleString('id-ID')}</Typography>
        <Button variant="contained" component={RouterLink} to="/checkout">
          Lanjutkan ke Checkout
        </Button>
      </Stack>
    </Stack>
    </Container>
  )
}

export default CartPage

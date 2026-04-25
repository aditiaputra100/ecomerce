import { useLayoutEffect, useRef, useState } from 'react'
import {
  Alert,
  Box,
  Button,
  Container,
  Divider,
  FormControl,
  FormLabel,
  Grid,
  Link,
  Stack,
  TextField,
  Typography,
  useTheme,
} from '@mui/material'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/auth'
import { APP_NAME } from '../config'

const RegisterPage = () => {
  const theme = useTheme()
  const navigate = useNavigate()
  const register = useAuthStore((state) => state.register)
  const loading = useAuthStore((state) => state.loading)
  const error = useAuthStore((state) => state.error)
  const [form, setForm] = useState({ username: '', email: '', password: '' })
  const formGridRef = useRef<HTMLDivElement | null>(null)
  const [formGridHeight, setFormGridHeight] = useState<number>(0)

  useLayoutEffect(() => {
    const element = formGridRef.current
    if (!element) return

    const updateHeight = () => {
      setFormGridHeight(element.getBoundingClientRect().height)
    }

    updateHeight()

    const observer = new ResizeObserver(updateHeight)
    observer.observe(element)

    return () => {
      observer.disconnect()
    }
  }, [])

  const handleInputChange =
    (field: 'username' | 'email' | 'password') =>
    (event: React.ChangeEvent<HTMLInputElement>) => {
      setForm((prev) => ({ ...prev, [field]: event.target.value }))
    }

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    await register(form)
    navigate('/login')
  }

  return (
    <Grid minHeight="100vh" padding={2} container alignItems="flex-start">
      <Grid size={6} my={2} ref={formGridRef}>
        <Box component='header'>
          <Container>
            <Typography component={Link} href='/' underline='none' color={theme.palette.text.primary} variant='h1'>
              {APP_NAME}
            </Typography>
          </Container>
        </Box>

        <Box component='section' my={4}>
          <Box textAlign='center'>
            <Typography variant='h2'>
              Daftar akun
            </Typography>
            <Typography>
              Buat akun untuk mulai berbelanja atau membuka toko.
            </Typography>
          </Box>

          {error && <Alert severity="error">{error}</Alert>}

          <Box component='form' onSubmit={handleSubmit} my={2}>
            <Container maxWidth='sm'>
              <Stack gap={2}>
                <FormControl fullWidth required>
                  <FormLabel htmlFor="username">Username</FormLabel>
                  <TextField
                    id='username'
                    value={form.username}
                    onChange={handleInputChange('username')}
                  />
                </FormControl>
                <FormControl fullWidth required inputMode='email'>
                  <FormLabel htmlFor="email">Email</FormLabel>
                  <TextField
                    id='email'
                    value={form.email}
                    onChange={handleInputChange('email')}
                  />
                </FormControl>
                <FormControl fullWidth required>
                  <FormLabel htmlFor="password">Password</FormLabel>
                  <TextField
                    id='password'
                    type='password'
                    value={form.password}
                    onChange={handleInputChange('password')}
                  />
                </FormControl>
                <FormControl fullWidth required>
                  <FormLabel htmlFor="confirm-password">Confirm Password</FormLabel>
                  <TextField id='confirm-password' type='password'/>
                </FormControl>
                <Button type="submit" variant="contained" disabled={loading} size='large'>
                  {loading ? 'Memproses...' : 'Daftar'}
                </Button>

                <Divider color={theme.palette.text.secondary}>Atau Daftar Dengan</Divider>

                <Typography align='center' >
                  Sudah punya akun? <Link underline='none' href='/login' color={theme.palette.primary.main}>Masuk</Link>
                </Typography>
              </Stack>
            </Container>
          </Box>

        </Box>
        <Box component='footer' sx={{
          bgcolor: 'transparent',
          color: theme.palette.text.primary
        }}>
          <Container>
            <Stack direction='row' justifyContent='space-between'>
              <Typography>
                &copy; {new Date().getFullYear()} {APP_NAME}. All rights reserved.
              </Typography>
              <Typography>
                Privacy Policy
              </Typography>
            </Stack>
          </Container>
        </Box>
      </Grid>
      <Grid
        size={6}
        my={2}
        sx={{
          display: 'flex',
          height: formGridHeight > 0 ? `${formGridHeight}px` : 'auto',
        }}
      >
        <Box 
          component='img'
          src="/Roshan Zameer.jpg"
          alt="Ilustrasi pendaftaran akun"
          sx={{
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            borderRadius: 4,
          }}
        />
      </Grid>
    </Grid>
  )
}

export default RegisterPage

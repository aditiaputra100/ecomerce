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
  useMediaQuery,
  useTheme,
} from '@mui/material'
import { Link as RouterLink, useNavigate, useLocation } from 'react-router-dom'
import type { Location } from 'react-router-dom'
import { useAuthStore } from '../store/auth'
import { APP_NAME } from '../config'

const LoginPage = () => {
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down('md'))
  const navigate = useNavigate()
  const location = useLocation()
  const login = useAuthStore((state) => state.login)
  const loading = useAuthStore((state) => state.loading)
  const error = useAuthStore((state) => state.error)
  const [form, setForm] = useState({ username: '', password: '' })
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
  }, [isMobile])

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
    <Grid
      minHeight="100vh"
      maxWidth='lg'
      padding={2}
      alignItems="center"
      marginX='auto'
      container
    >
      <Grid size={{md: 12, lg: 6}} my={2} ref={formGridRef}>
        <Box component='header'>
          <Container>
            <Typography
              component={RouterLink}
              to='/'
              color={theme.palette.text.primary}
              sx={{ textDecoration: 'none' }}
              variant='h1'
            >
              {APP_NAME}
            </Typography>
          </Container>
        </Box>

        <Box component='section' my={4}>
          <Box textAlign='center'>
            <Typography variant='h2'>
              Masuk akun
            </Typography>
            <Typography>
              Lanjutkan belanja atau kelola tokomu dengan akun yang sama.
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
                    onChange={(event) => setForm((prev) => ({ ...prev, username: event.target.value }))}
                  />
                </FormControl>

                <FormControl fullWidth required>
                  <FormLabel htmlFor="password">Password</FormLabel>
                  <TextField
                    id='password'
                    type='password'
                    value={form.password}
                    onChange={(event) => setForm((prev) => ({ ...prev, password: event.target.value }))}
                  />
                </FormControl>

                <Button type="submit" variant="contained" disabled={loading} size='large'>
                  {loading ? 'Memproses...' : 'Masuk'}
                </Button>

                <Divider color={theme.palette.text.secondary}>Belum punya akun?</Divider>

                <Typography align='center'>
                  Daftar di sini{' '}
                  <Link component={RouterLink} underline='none' to='/register' color={theme.palette.primary.main}>
                    Buat akun baru
                  </Link>
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
          display: isMobile ? 'none' : 'flex',
          height: formGridHeight > 0 ? `${formGridHeight}px` : 'auto',
        }}
      >
        <Box
          component='img'
          src="/Mountain.webp"
          alt="Ilustrasi halaman login"
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

export default LoginPage

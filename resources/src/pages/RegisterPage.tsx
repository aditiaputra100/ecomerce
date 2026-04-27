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
import { Link as RouterLink, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/auth'
import { APP_NAME } from '../config'

const USERNAME_MIN_LENGTH = 3
const PASSWORD_MIN_LENGTH = 8

type RegisterFormState = {
  username: string
  email: string
  password: string
  confirmPassword: string
}

type RegisterField = keyof RegisterFormState
type RegisterErrors = Partial<Record<RegisterField, string>>

const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

function validateRegisterForm(form: RegisterFormState): RegisterErrors {
  const errors: RegisterErrors = {}
  const username = form.username.trim()
  const email = form.email.trim()

  if (!username) {
    errors.username = 'Username wajib diisi.'
  } else if (username.length < USERNAME_MIN_LENGTH) {
    errors.username = `Username minimal ${USERNAME_MIN_LENGTH} karakter.`
  }

  if (!email) {
    errors.email = 'Email wajib diisi.'
  } else if (!emailPattern.test(email)) {
    errors.email = 'Format email tidak valid.'
  }

  if (!form.password) {
    errors.password = 'Password wajib diisi.'
  } else if (form.password.length < PASSWORD_MIN_LENGTH) {
    errors.password = `Password minimal ${PASSWORD_MIN_LENGTH} karakter.`
  }

  if (!form.confirmPassword) {
    errors.confirmPassword = 'Konfirmasi password wajib diisi.'
  } else if (form.confirmPassword !== form.password) {
    errors.confirmPassword = 'Konfirmasi password harus sama dengan password.'
  }

  return errors
}

const RegisterPage = () => {
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down('md'))
  const navigate = useNavigate()
  const register = useAuthStore((state) => state.register)
  const loading = useAuthStore((state) => state.loading)
  const error = useAuthStore((state) => state.error)
  const [form, setForm] = useState<RegisterFormState>({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
  })
  const [errors, setErrors] = useState<RegisterErrors>({})
  const [touched, setTouched] = useState<Partial<Record<RegisterField, boolean>>>({})
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

  const handleInputChange =
    (field: RegisterField) =>
    (event: React.ChangeEvent<HTMLInputElement>) => {
      const value = event.target.value
      const nextForm = { ...form, [field]: value }
      setForm(nextForm)

      if (touched[field] || (field === 'password' && touched.confirmPassword)) {
        setErrors(validateRegisterForm(nextForm))
      }
    }

  const handleFieldBlur = (field: RegisterField) => {
    setTouched((prev) => ({ ...prev, [field]: true }))
    setErrors(validateRegisterForm(form))
  }

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const nextTouched: Record<RegisterField, boolean> = {
      username: true,
      email: true,
      password: true,
      confirmPassword: true,
    }

    setTouched(nextTouched)

    const validationErrors = validateRegisterForm(form)
    setErrors(validationErrors)
    if (Object.keys(validationErrors).length > 0) {
      return
    }

    try {
      await register({
        username: form.username.trim(),
        email: form.email.trim(),
        password: form.password,
      })
      navigate('/login')
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
                    onBlur={() => handleFieldBlur('username')}
                    error={Boolean(touched.username && errors.username)}
                    helperText={touched.username ? errors.username : undefined}
                  />
                </FormControl>
                <FormControl fullWidth required>
                  <FormLabel htmlFor="email">Email</FormLabel>
                  <TextField
                    id='email'
                    type='email'
                    inputProps={{ inputMode: 'email' }}
                    value={form.email}
                    onChange={handleInputChange('email')}
                    onBlur={() => handleFieldBlur('email')}
                    error={Boolean(touched.email && errors.email)}
                    helperText={touched.email ? errors.email : undefined}
                  />
                </FormControl>
                <FormControl fullWidth required>
                  <FormLabel htmlFor="password">Password</FormLabel>
                  <TextField
                    id='password'
                    type='password'
                    value={form.password}
                    onChange={handleInputChange('password')}
                    onBlur={() => handleFieldBlur('password')}
                    error={Boolean(touched.password && errors.password)}
                    helperText={touched.password ? errors.password : undefined}
                  />
                </FormControl>
                <FormControl fullWidth required>
                  <FormLabel htmlFor="confirm-password">Confirm Password</FormLabel>
                  <TextField
                    id='confirm-password'
                    type='password'
                    value={form.confirmPassword}
                    onChange={handleInputChange('confirmPassword')}
                    onBlur={() => handleFieldBlur('confirmPassword')}
                    error={Boolean(touched.confirmPassword && errors.confirmPassword)}
                    helperText={touched.confirmPassword ? errors.confirmPassword : undefined}
                  />
                </FormControl>
                <Button type="submit" variant="contained" disabled={loading} size='large'>
                  {loading ? 'Memproses...' : 'Daftar'}
                </Button>

                <Divider color={theme.palette.text.secondary}>Atau Daftar Dengan</Divider>

                <Typography align='center' >
                  Sudah punya akun?{' '}
                  <Link component={RouterLink} underline='none' to='/login' color={theme.palette.primary.main}>
                    Masuk
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

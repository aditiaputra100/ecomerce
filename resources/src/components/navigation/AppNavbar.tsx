import {
  AccountCircle,
  Logout,
  Notifications,
  Person,
  ReceiptLong,
  Search,
  ShoppingCart,
  Storefront,
} from '@mui/icons-material'
import {
  AppBar,
  Avatar,
  Box,
  Button,
  Container,
  FormControl,
  IconButton,
  InputAdornment,
  Link,
  Menu,
  MenuItem,
  OutlinedInput,
  Paper,
  Select,
  Stack,
  Toolbar,
  Typography,
  useMediaQuery,
  useTheme,
} from '@mui/material'
import { useLayoutEffect, useRef, useState, type MouseEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { APP_NAME } from '../../config'
import { useAuthStore } from '../../store/auth'

const AppNavbar = () => {
  const theme = useTheme()
  const navigate = useNavigate()
  const appBarRef = useRef<HTMLDivElement>(null)
  const isMobile = useMediaQuery(theme.breakpoints.down('md'))
  const [category, setCategory] = useState('')
  const [height, setHeight] = useState(0)
  const [userMenuAnchor, setUserMenuAnchor] = useState<HTMLElement | null>(null)

  const token = useAuthStore((state) => state.token)
  const profile = useAuthStore((state) => state.profile)
  const logout = useAuthStore((state) => state.logout)
  const isAuthenticated = Boolean(token)

  useLayoutEffect(() => {
    const updateHeight = () => {
      if (appBarRef.current) {
        setHeight(appBarRef.current.getBoundingClientRect().height)
      }
    }

    updateHeight()
    window.addEventListener('resize', updateHeight)

    return () => {
      window.removeEventListener('resize', updateHeight)
    }
  }, [isMobile, isAuthenticated])

  const handleOpenUserMenu = (event: MouseEvent<HTMLElement>) => {
    setUserMenuAnchor(event.currentTarget)
  }

  const handleCloseUserMenu = () => {
    setUserMenuAnchor(null)
  }

  const handleNavigate = (path: string) => {
    handleCloseUserMenu()
    navigate(path)
  }

  const handleLogout = async () => {
    handleCloseUserMenu()
    await logout()
    navigate('/')
  }

  const guestDesktopActions = (
    <>
      <IconButton aria-label="cart">
        <ShoppingCart />
      </IconButton>
      <IconButton aria-label="notification">
        <Notifications />
      </IconButton>
    </>
  )

  const authActions = (
    <>
      <IconButton aria-label="cart">
        <ShoppingCart />
      </IconButton>
      <IconButton aria-label="notification">
        <Notifications />
      </IconButton>
      <IconButton aria-label="user menu" onMouseEnter={handleOpenUserMenu}>
        <AccountCircle />
      </IconButton>
    </>
  )

  const actionArea = isAuthenticated ? authActions : isMobile ? (
    <Button variant="contained" onClick={() => navigate('/login')}>
      Masuk
    </Button>
  ) : (
    guestDesktopActions
  )

  return (
    <Box sx={{ marginTop: `${height}px` }}>
      <Box
        component={AppBar}
        ref={appBarRef}
        position="fixed"
        color="inherit"
        elevation={0}
        sx={{
          borderBottom: '1px solid',
          borderColor: 'divider',
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.06)',
          backgroundColor: 'background.default',
        }}
      >
        {!isMobile && (
          <Box
            sx={{
              width: '100%',
              bgcolor: 'background.default',
              borderBottom: '1px solid',
              borderColor: 'divider',
            }}
          >
            <Container maxWidth="lg">
              <Stack direction="row" justifyContent="flex-end" spacing={3} py={1}>
                <Link href="/help" underline="none" color="text.secondary" variant="body2">
                  Bantuan
                </Link>
                <Link href="/partner" underline="none" color="text.secondary" variant="body2">
                  Mitra
                </Link>
                {isAuthenticated ? (
                  <Link href="" underline='none' color="primary.main" fontWeight={600} variant="body2" onClick={() => navigate('/dashboard')}>
                    Buka Toko
                  </Link>
                ) : (
                  <>
                    <Link href="/login" underline="none" color="text.secondary" variant="body2">
                      Masuk
                    </Link>
                    <Link href="/register" underline="none" color="primary.main" fontWeight={600} variant="body2">
                      Daftar
                    </Link>
                  </>
                )}
                
              </Stack>
            </Container>
          </Box>
        )}

        <Container maxWidth="lg">
          <Toolbar disableGutters sx={{ gap: 2, flexWrap: 'wrap', py: 1 }}>
            <Typography
              variant="h6"
              noWrap
              component="a"
              href="/"
              sx={{ textDecoration: 'none', color: 'inherit', display: { xs: 'none', md: 'block' } }}
            >
              {APP_NAME}
            </Typography>

            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 1,
                flexGrow: 1,
                justifyContent: 'flex-end',
                minWidth: 0,
              }}
            >
              <Paper
                elevation={0}
                sx={{
                  width: '100%',
                  display: 'flex',
                  flexDirection: !isMobile ? { xs: 'column', sm: 'row' } : 'row',
                  borderRadius: 3,
                  overflow: 'hidden',
                  border: '1px solid',
                  borderColor: 'divider',
                  backgroundColor: 'background.paper',
                }}
              >
                {!isMobile && (
                  <FormControl
                    fullWidth
                    sx={{
                      maxWidth: { sm: 200 },
                      '& .MuiOutlinedInput-notchedOutline': { border: 'none' },
                    }}
                  >
                    <Select
                      value={category}
                      onChange={(event) => setCategory(event.target.value)}
                      displayEmpty
                      input={<OutlinedInput notched={false} />}
                    >
                      <MenuItem value="">All Categories</MenuItem>
                      <MenuItem value="fashion">Baju</MenuItem>
                      <MenuItem value="electronics">Elektronik</MenuItem>
                      <MenuItem value="others">Apapun</MenuItem>
                    </Select>
                  </FormControl>
                )}

                <OutlinedInput
                  placeholder="Search product..."
                  fullWidth
                  sx={{
                    borderRadius: 0,
                    borderLeft: !isMobile ? `1px solid ${theme.palette.divider}` : 'none',
                    '& .MuiOutlinedInput-notchedOutline': { border: 'none' },
                  }}
                  startAdornment={
                    <InputAdornment position="start">
                      <Search />
                    </InputAdornment>
                  }
                />
              </Paper>

              {actionArea}
            </Box>
          </Toolbar>
        </Container>
      </Box>
      <Menu
        anchorEl={userMenuAnchor}
        open={Boolean(userMenuAnchor)}
        onClose={handleCloseUserMenu}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        transformOrigin={{ vertical: 'top', horizontal: 'right' }}
        slotProps={{
          list: {
            onMouseLeave: handleCloseUserMenu
          }
        }}
      >
        <Box px={2} py={1.5} display="flex" alignItems="center" gap={1.5} minWidth={220}>
          <Avatar sx={{ bgcolor: 'primary.main', width: 36, height: 36 }}>
            {profile?.username?.slice(0, 1).toUpperCase() ?? 'A'}
          </Avatar>
          <Box>
            <Typography variant="subtitle2" fontWeight={700}>
              {profile?.username ?? 'Akun'}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Selamat datang kembali
            </Typography>
          </Box>
        </Box>
        <MenuItem onClick={() => handleNavigate('/')}>
          <Person fontSize="small" style={{ marginRight: 8 }} />
          Profil
        </MenuItem>
        <MenuItem onClick={() => handleNavigate('/checkout/status')}>
          <ReceiptLong fontSize="small" style={{ marginRight: 8 }} />
          Pesanan
        </MenuItem>
        <MenuItem onClick={() => handleNavigate('/dashboard')}>
          <Storefront fontSize="small" style={{ marginRight: 8 }} />
          Toko / Dashboard
        </MenuItem>
        <MenuItem onClick={handleLogout}>
          <Logout fontSize="small" style={{ marginRight: 8 }} />
          Keluar
        </MenuItem>
      </Menu>
    </Box>
  )
}

export default AppNavbar

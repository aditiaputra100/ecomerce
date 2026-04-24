import {
  AppBar,
  Box,
  Button,
  Container,
  FormControl,
  IconButton,
  InputAdornment,
  Link,
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
import { ShoppingCart, Notifications, Search } from '@mui/icons-material'
import { useLayoutEffect, useRef, useState } from 'react'
import { APP_NAME } from '../../config'

const AppNavbar = () => {
  const theme = useTheme()
  const appBarRef = useRef<HTMLDivElement>(null)
  const isMobile = useMediaQuery(theme.breakpoints.down('md'))
  const [category, setCategory] = useState('')
  const [height, setHeight] = useState(0)

  useLayoutEffect(() => {
    const updateHeight = () => {
      if (appBarRef.current) {
        setHeight(appBarRef.current?.getBoundingClientRect().height)
      }
    }

    updateHeight()
    window.addEventListener('resize', updateHeight)

    return () => {
      window.removeEventListener('resize', updateHeight)
    }
  }, [isMobile])

  const ActionButton = isMobile ? (
    <Button variant='contained'>
      Masuk
    </Button>
  ) : (
    <>
      <IconButton aria-label="cart">
        <ShoppingCart />
      </IconButton>
      <IconButton aria-label="notification">
        <Notifications />
      </IconButton>
    </>
  )

  return (
    <Box sx={{marginTop: `${height}px`}}>
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
        }}>
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
                  <Link href="/login" underline="none" color="text.secondary" variant="body2">
                    Masuk
                  </Link>
                  <Link href="/register" underline="none" color="primary.main" fontWeight={600} variant="body2">
                    Daftar
                  </Link>
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
                sx={{ textDecoration: 'none', color: 'inherit', display: {xs: 'none', md: 'block'}}}>
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
                      <InputAdornment position='start'>
                        <Search />
                      </InputAdornment>
                    }
                  />
                </Paper>
                {ActionButton}
              </Box>
              
            </Toolbar>
          </Container>
        </Box>
    </Box>
  )
}

export default AppNavbar

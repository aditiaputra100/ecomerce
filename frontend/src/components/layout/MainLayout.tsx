import {
  Box,
  useMediaQuery,
  useTheme,
} from '@mui/material'
import { Outlet } from 'react-router-dom'
import AppNavbar from '../navigation/AppNavbar'
import Footer from '../Footer'
import BottomAppBar from '../navigation/BottomAppBar'

function MainLayout() {
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down('md'))

  return (
    <Box className='app-container'>
      <AppNavbar />
      <Box component='main' sx={{ pb: isMobile ? '72px' : 0 }}>
        <Outlet />
      </Box>
      {
        isMobile ? (<BottomAppBar />) : (<Footer />)
      }
    </Box>
  )
}

export default MainLayout

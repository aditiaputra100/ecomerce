import { createTheme, responsiveFontSizes } from '@mui/material/styles'

let theme = createTheme({
  palette: {
    primary: {
      main: '#1687a7',
      contrastText: '#f6f5f5',
    },
    secondary: {
      main: '#276678',
      contrastText: '#f6f5f5',
    },
    info: {
      main: '#d3e0ea',
      contrastText: '#276678',
    },
    success: {
      main: '#22c55e',
    },
    divider: '#d3e0ea',
    background: {
      default: '#f6f5f5',
    },
    text: {
      primary: '#1f1b2e',
      secondary: '#4a5568',
    },
  },
  typography: {
    fontFamily: '"Plus Jakarta Sans", "Inter", system-ui, -apple-system, BlinkMacSystemFont, sans-serif',
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          paddingInline: 24,
          textTransform: 'capitalize'
        },
        containedSecondary: {
          color: '#fff',
        },
      },
    },
    MuiOutlinedInput: {
      styleOverrides: {
        root: {
          minHeight: 46,
          borderRadius: 12,
          '& .MuiOutlinedInput-input': {
            fontSize: '0.95rem',
          },
        },
      },
    },
    MuiInputBase: {
      styleOverrides: {
        input: {
          fontSize: '0.9rem',
        },
      },
    },
  },
})

theme = responsiveFontSizes(theme)

export default theme

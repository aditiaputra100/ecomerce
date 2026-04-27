import { MemoryRouter } from 'react-router-dom'
import { ThemeProvider } from '@mui/material'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { vi } from 'vitest'
import LoginPage from '../../../resources/src/pages/LoginPage'
import theme from '../../../resources/src/theme'

const mocks = vi.hoisted(() => ({
  navigate: vi.fn(),
  useAuthStore: vi.fn(),
  locationState: null as { from?: { pathname?: string } } | null,
}))

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual<typeof import('react-router-dom')>('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mocks.navigate,
    useLocation: () => ({ state: mocks.locationState }),
  }
})

vi.mock('../../../resources/src/store/auth', () => ({
  useAuthStore: mocks.useAuthStore,
}))

type LoginStoreState = {
  login: (payload: { username: string; password: string }) => Promise<void>
  loading: boolean
  error: string | null
}

function renderLoginPage() {
  return render(
    <ThemeProvider theme={theme}>
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>
    </ThemeProvider>,
  )
}

function setAuthStoreState(state: LoginStoreState) {
  mocks.useAuthStore.mockImplementation((selector: (store: LoginStoreState) => unknown) => selector(state))
}

describe('LoginPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mocks.locationState = null
    setAuthStoreState({
      login: vi.fn().mockResolvedValue(undefined),
      loading: false,
      error: null,
    })
  })

  it('calls login and redirects using location.state.from pathname', async () => {
    const loginMock = vi.fn().mockResolvedValue(undefined)
    setAuthStoreState({ login: loginMock, loading: false, error: null })
    mocks.locationState = { from: { pathname: '/checkout' } }

    renderLoginPage()

    const user = userEvent.setup()
    await user.type(screen.getByLabelText(/username/i), 'milda')
    await user.type(screen.getByLabelText(/password/i), 'password123')
    await user.click(screen.getByRole('button', { name: /masuk/i }))

    await waitFor(() => {
      expect(loginMock).toHaveBeenCalledWith({ username: 'milda', password: 'password123' })
    })
    expect(mocks.navigate).toHaveBeenCalledWith('/checkout')
  })

  it('renders error alert and loading state from auth store', () => {
    setAuthStoreState({
      login: vi.fn().mockRejectedValue(new Error('Unauthorized')),
      loading: true,
      error: 'Username atau password salah.',
    })

    renderLoginPage()

    expect(screen.getByRole('alert')).toHaveTextContent('Username atau password salah.')
    expect(screen.getByRole('button', { name: /memproses\.\.\./i })).toBeDisabled()
  })
})
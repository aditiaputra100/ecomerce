import { MemoryRouter } from 'react-router-dom'
import { ThemeProvider } from '@mui/material'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { vi } from 'vitest'
import AppNavbar from '../../../resources/src/components/navigation/AppNavbar'
import theme from '../../../resources/src/theme'

const mocks = vi.hoisted(() => ({
  navigate: vi.fn(),
  useAuthStore: vi.fn(),
}))

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual<typeof import('react-router-dom')>('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mocks.navigate,
  }
})

vi.mock('../../../resources/src/store/auth', () => ({
  useAuthStore: mocks.useAuthStore,
}))

type NavbarStoreState = {
  token: string | null
  profile: { id: number; username: string; email: string } | null
  logout: () => Promise<void>
}

function renderNavbar() {
  return render(
    <ThemeProvider theme={theme}>
      <MemoryRouter>
        <AppNavbar />
      </MemoryRouter>
    </ThemeProvider>,
  )
}

function setAuthStoreState(state: NavbarStoreState) {
  mocks.useAuthStore.mockImplementation((selector: (store: NavbarStoreState) => unknown) => selector(state))
}

describe('AppNavbar', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('shows guest actions when session is absent', () => {
    setAuthStoreState({
      token: null,
      profile: null,
      logout: vi.fn().mockResolvedValue(undefined),
    })

    renderNavbar()

    expect(screen.getByRole('link', { name: /masuk/i })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /daftar/i })).toBeInTheDocument()
    expect(screen.queryByLabelText(/user menu/i)).not.toBeInTheDocument()
  })

  it('shows user menu and logout action when session exists', async () => {
    const logoutMock = vi.fn().mockResolvedValue(undefined)
    setAuthStoreState({
      token: 'token-123',
      profile: { id: 1, username: 'milda', email: 'milda@example.com' },
      logout: logoutMock,
    })

    renderNavbar()

    expect(screen.queryByRole('link', { name: /masuk/i })).not.toBeInTheDocument()
    expect(screen.queryByRole('link', { name: /daftar/i })).not.toBeInTheDocument()

    const user = userEvent.setup()
    await user.click(screen.getByLabelText(/user menu/i))

    expect(await screen.findByText(/profil/i)).toBeInTheDocument()
    expect(screen.getByText(/pesanan/i)).toBeInTheDocument()
    expect(screen.getByText(/keluar/i)).toBeInTheDocument()

    await user.click(screen.getByText(/keluar/i))

    await waitFor(() => {
      expect(logoutMock).toHaveBeenCalled()
    })
    expect(mocks.navigate).toHaveBeenCalledWith('/')
  })
})
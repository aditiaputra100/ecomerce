import { MemoryRouter } from 'react-router-dom'
import { ThemeProvider } from '@mui/material'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { vi } from 'vitest'
import RegisterPage from '../../../resources/src/pages/RegisterPage'
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

type RegisterStoreState = {
  register: (payload: { username: string; email: string; password: string }) => Promise<void>
  loading: boolean
  error: string | null
}

function renderRegisterPage() {
  return render(
    <ThemeProvider theme={theme}>
      <MemoryRouter>
        <RegisterPage />
      </MemoryRouter>
    </ThemeProvider>,
  )
}

function setAuthStoreState(state: RegisterStoreState) {
  mocks.useAuthStore.mockImplementation((selector: (store: RegisterStoreState) => unknown) => selector(state))
}

function getInputById(id: string) {
  const element = document.getElementById(id)
  if (!(element instanceof HTMLInputElement)) {
    throw new Error(`Input with id "${id}" was not found.`)
  }
  return element
}

describe('RegisterPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    setAuthStoreState({
      register: vi.fn().mockResolvedValue(undefined),
      loading: false,
      error: null,
    })
  })

  it('shows validation errors and does not submit when form is invalid', async () => {
    const registerMock = vi.fn().mockResolvedValue(undefined)
    setAuthStoreState({ register: registerMock, loading: false, error: null })

    renderRegisterPage()

    const user = userEvent.setup()
    await user.type(screen.getByLabelText(/username/i), 'ab')
    await user.type(screen.getByLabelText(/email/i), 'invalid-email')
    await user.type(getInputById('password'), '12345')
    await user.type(getInputById('confirm-password'), '123456')
    await user.click(screen.getByRole('button', { name: /daftar/i }))

    expect(registerMock).not.toHaveBeenCalled()
    expect(screen.getByText(/username minimal 3 karakter\./i)).toBeInTheDocument()
    expect(screen.getByText(/format email tidak valid\./i)).toBeInTheDocument()
    expect(screen.getByText(/password minimal 8 karakter\./i)).toBeInTheDocument()
    expect(screen.getByText(/konfirmasi password harus sama dengan password\./i)).toBeInTheDocument()
  })

  it('submits register payload and redirects to login when form is valid', async () => {
    const registerMock = vi.fn().mockResolvedValue(undefined)
    setAuthStoreState({ register: registerMock, loading: false, error: null })

    renderRegisterPage()

    const user = userEvent.setup()
    await user.type(screen.getByLabelText(/username/i), 'milda')
    await user.type(screen.getByLabelText(/email/i), 'milda@example.com')
    await user.type(getInputById('password'), 'password123')
    await user.type(getInputById('confirm-password'), 'password123')
    await user.click(screen.getByRole('button', { name: /daftar/i }))

    await waitFor(() => {
      expect(registerMock).toHaveBeenCalledWith({
        username: 'milda',
        email: 'milda@example.com',
        password: 'password123',
      })
    })
    expect(mocks.navigate).toHaveBeenCalledWith('/login')
  })
})
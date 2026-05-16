import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { render, screen } from '@testing-library/react'
import { vi } from 'vitest'
import { ProtectedRoute } from '../../../resources/src/routes/ProtectedRoute'

const mocks = vi.hoisted(() => ({
  useAuthStore: vi.fn(),
}))

vi.mock('../../../resources/src/store/auth', () => ({
  useAuthStore: mocks.useAuthStore,
}))

type AuthStoreState = {
  token: string | null
  shop: unknown | null
  initialized: boolean
}

function setAuthState(state: AuthStoreState) {
  mocks.useAuthStore.mockImplementation((selector: (store: AuthStoreState) => unknown) => selector(state))
}

describe('ProtectedRoute', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders protected content when auth state is ready', () => {
    setAuthState({
      token: 'token-1',
      shop: null,
      initialized: true,
    })

    render(
      <MemoryRouter initialEntries={['/dashboard']}>
        <Routes>
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <div>protected page</div>
              </ProtectedRoute>
            }
          />
          <Route path="/login" element={<div>login page</div>} />
        </Routes>
      </MemoryRouter>,
    )

    expect(screen.getByText('protected page')).toBeInTheDocument()
  })

  it('redirects to login when initialization finished without token', () => {
    setAuthState({
      token: null,
      shop: null,
      initialized: true,
    })

    render(
      <MemoryRouter initialEntries={['/dashboard']}>
        <Routes>
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <div>protected page</div>
              </ProtectedRoute>
            }
          />
          <Route path="/login" element={<div>login page</div>} />
        </Routes>
      </MemoryRouter>,
    )

    expect(screen.getByText('login page')).toBeInTheDocument()
  })
})
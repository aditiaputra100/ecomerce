import { vi } from 'vitest'
import { loginUser, logoutUser, refreshSession, registerUser } from '../../../resources/src/services/user.service'

describe('user.service', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('registerUser posts JSON with credentials', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        message: 'User created successfully',
        data: {
          access_token: 'token-1',
          token_type: 'bearer',
          user: { id: 1, username: 'milda', email: 'milda@example.com' },
        },
      }),
    } as Response)

    const response = await registerUser({ username: 'milda', email: 'milda@example.com', password: 'password123' })

    expect(response.access_token).toBe('token-1')
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/register'),
      expect.objectContaining({
        method: 'POST',
        credentials: 'include',
      }),
    )
  })

  it('loginUser posts urlencoded form with credentials', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        message: '',
        data: {
          access_token: 'token-2',
          token_type: 'bearer',
          user: { id: 1, username: 'milda', email: 'milda@example.com' },
        },
      }),
    } as Response)

    const response = await loginUser({ username: 'milda', password: 'password123' })

    expect(response.access_token).toBe('token-2')
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/token'),
      expect.objectContaining({
        method: 'POST',
        credentials: 'include',
      }),
    )
  })

  it('refreshSession calls refresh endpoint with credentials', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        message: '',
        data: {
          access_token: 'token-3',
          token_type: 'bearer',
          user: { id: 1, username: 'milda', email: 'milda@example.com' },
        },
      }),
    } as Response)

    const response = await refreshSession()

    expect(response.access_token).toBe('token-3')
  })

  it('logoutUser calls logout endpoint with credentials', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ message: 'Logged out successfully', data: null }),
    } as Response)

    await logoutUser()

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/logout'),
      expect.objectContaining({
        method: 'POST',
        credentials: 'include',
      }),
    )
  })
})
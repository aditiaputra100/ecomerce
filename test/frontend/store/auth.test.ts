import { vi } from 'vitest'

const mocks = vi.hoisted(() => ({
  fetchCurrentUser: vi.fn(),
  fetchMyShop: vi.fn(),
  refreshSession: vi.fn(),
  setSessionRefresher: vi.fn(),
}))

vi.mock('../../../resources/src/services', () => ({
  fetchCurrentUser: mocks.fetchCurrentUser,
  fetchMyShop: mocks.fetchMyShop,
  refreshSession: mocks.refreshSession,
  setSessionRefresher: mocks.setSessionRefresher,
  loginUser: vi.fn(),
  logoutUser: vi.fn(),
  openShop: vi.fn(),
  registerUser: vi.fn(),
}))

vi.mock('../../../resources/src/services/http', () => ({
  setSessionRefresher: mocks.setSessionRefresher,
}))

import { useAuthStore } from '../../../resources/src/store/auth'

describe('auth store bootstrap', () => {
  const user = {
    id: 1,
    username: 'milda',
    email: 'milda@example.com',
    disable: false,
    has_shop: false,
  }

  beforeEach(() => {
    vi.clearAllMocks()
    useAuthStore.setState({
      token: null,
      profile: null,
      shop: null,
      loading: false,
      error: null,
      initialized: false,
    })
  })

  it('restores session data when refresh succeeds', async () => {
    mocks.refreshSession.mockResolvedValue({
      access_token: 'new-token',
      token_type: 'bearer',
      user,
    })
    mocks.fetchCurrentUser.mockResolvedValue(user)
    mocks.fetchMyShop.mockResolvedValue(null)

    await useAuthStore.getState().bootstrap()

    const state = useAuthStore.getState()
    expect(state.initialized).toBe(true)
    expect(state.token).toBe('new-token')
    expect(state.profile).toEqual(user)
    expect(state.shop).toBeNull()
    expect(mocks.refreshSession).toHaveBeenCalledTimes(1)
    expect(mocks.fetchCurrentUser).toHaveBeenCalledWith('new-token')
  })

  it('clears auth state when refresh fails', async () => {
    mocks.refreshSession.mockRejectedValue(new Error('Unauthorized'))

    await useAuthStore.getState().bootstrap()

    const state = useAuthStore.getState()
    expect(state.initialized).toBe(true)
    expect(state.token).toBeNull()
    expect(state.profile).toBeNull()
    expect(state.shop).toBeNull()
    expect(mocks.fetchCurrentUser).not.toHaveBeenCalled()
  })

  it('deduplicates concurrent bootstrap refresh requests', async () => {
    type RefreshResponse = { access_token: string; token_type: string; user: typeof user }
    let resolveRefresh!: (value: RefreshResponse) => void

    mocks.refreshSession.mockImplementation(
      () =>
        new Promise<RefreshResponse>((resolve) => {
          resolveRefresh = resolve
        }),
    )
    mocks.fetchCurrentUser.mockResolvedValue(user)
    mocks.fetchMyShop.mockResolvedValue(null)

    const firstBootstrap = useAuthStore.getState().bootstrap()
    const secondBootstrap = useAuthStore.getState().bootstrap()

    expect(mocks.refreshSession).toHaveBeenCalledTimes(1)

    resolveRefresh({
      access_token: 'shared-token',
      token_type: 'bearer',
      user,
    })

    await Promise.all([firstBootstrap, secondBootstrap])

    const state = useAuthStore.getState()
    expect(state.initialized).toBe(true)
    expect(state.token).toBe('shared-token')
    expect(mocks.fetchCurrentUser).toHaveBeenCalledTimes(1)
  })
})
export interface User {
  id: number
  username: string
  email: string
  has_shop: boolean
}

export interface Token {
  access_token: string
  token_type: string
}

export interface AuthSessionResponse extends Token {
  user: User
}

export type AuthTokenResponse = AuthSessionResponse

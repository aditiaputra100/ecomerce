export interface User {
  id: number
  username: string
  email: string
}

export interface Token {
  access_token: string
  token_type: string
}

export type AuthTokenResponse = Token

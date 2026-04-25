import { request } from './http'
import type { MidtransConfigResponse } from '../types'

export function fetchMidtransClientKey() {
  return request<MidtransConfigResponse>('/payments/config')
}

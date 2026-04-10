import { request } from './http'
import type { CampaignCreate, CampaignUpdate, CampaignResponse } from '../types'

export function createCampaign(token: string, payload: CampaignCreate) {
  return request<CampaignResponse>('/campaign', {
    method: 'POST',
    token,
    body: JSON.stringify(payload),
  })
}

export function listActiveCampaigns() {
  return request<CampaignResponse[]>('/campaign/active')
}

export function updateCampaign(token: string, campaignId: number, payload: CampaignUpdate) {
  return request<CampaignResponse>(`/campaign/${campaignId}`, {
    method: 'PUT',
    token,
    body: JSON.stringify(payload),
  })
}

export function toggleCampaignActive(token: string, campaignId: number) {
  return request<CampaignResponse>(`/campaign/${campaignId}/active`, {
    method: 'PATCH',
    token,
  })
}

export function deleteCampaign(token: string, campaignId: number) {
  return request<void>(`/campaign/${campaignId}`, { method: 'DELETE', token })
}

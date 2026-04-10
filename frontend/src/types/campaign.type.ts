export interface CampaignCreate {
  name: string
  start_time?: string | null
  end_time: string
  is_active?: boolean
}

export interface CampaignUpdate {
  name: string
  start_time?: string | null
  end_time: string
  is_active?: boolean
}

export interface CampaignResponse {
  id: number
  name: string
  start_time: string | null
  end_time: string
  is_active: boolean
  created_at: string
  updated_at: string
}

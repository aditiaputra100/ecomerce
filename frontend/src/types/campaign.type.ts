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

interface CampaignItem {
  product_id: number
  special_price: number
  stock_limit: number
  stock_sold: number
  product: {
    name: string
    price: number
    image_url: string
    slug: string
  }

}

export interface CampaignResponse {
  id: number
  name: string
  start_time: string | null
  end_time: string
  is_active: boolean
  created_at: string
  updated_at: string
  items: CampaignItem[]
}

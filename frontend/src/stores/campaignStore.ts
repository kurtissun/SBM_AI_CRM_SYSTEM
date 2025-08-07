import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface Campaign {
  id: string
  name: string
  objective: string
  status: 'active' | 'paused' | 'draft' | 'completed'
  budget: {
    type: 'daily' | 'lifetime'
    amount: number
    spent: number
    bidStrategy?: string
  }
  audience: {
    size: number
    demographics: string[]
    interests: string[]
    behaviors: string[]
    customSegments?: string[]
  }
  performance: {
    impressions: number
    clicks: number
    conversions: number
    ctr: number
    cpc: number
    roi: number
  }
  schedule: {
    startDate: string
    endDate?: string
    timezone: string
  }
  creatives?: {
    copy?: {
      headline: string
      description: string
      cta: string
    }
    mediaCount?: {
      images: number
      videos: number
    }
  }
  settings?: {
    aiGenerated?: {
      copyGenerated: boolean
      audienceSuggestions: boolean
    }
  }
  createdAt: string
  updatedAt: string
  createdBy: string
}

interface CampaignStore {
  campaigns: Campaign[]
  addCampaign: (campaign: Omit<Campaign, 'id' | 'createdAt' | 'updatedAt'>) => void
  updateCampaign: (id: string, updates: Partial<Campaign>) => void
  deleteCampaign: (id: string) => void
  getCampaign: (id: string) => Campaign | undefined
  getCampaignsByStatus: (status: string) => Campaign[]
  generateMockCampaigns: () => void
}

export const useCampaignStore = create<CampaignStore>()(
  persist(
    (set, get) => ({
      campaigns: [],
      
      addCampaign: (campaignData) => {
        const newCampaign: Campaign = {
          ...campaignData,
          id: `campaign_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        }
        
        set((state) => ({
          campaigns: [...state.campaigns, newCampaign]
        }))
      },
      
      updateCampaign: (id, updates) => {
        set((state) => ({
          campaigns: state.campaigns.map((campaign) =>
            campaign.id === id
              ? { ...campaign, ...updates, updatedAt: new Date().toISOString() }
              : campaign
          )
        }))
      },
      
      deleteCampaign: (id) => {
        set((state) => ({
          campaigns: state.campaigns.filter((campaign) => campaign.id !== id)
        }))
      },
      
      getCampaign: (id) => {
        return get().campaigns.find((campaign) => campaign.id === id)
      },
      
      getCampaignsByStatus: (status) => {
        if (status === 'all') return get().campaigns
        return get().campaigns.filter((campaign) => campaign.status === status)
      },
      
      generateMockCampaigns: () => {
        const mockCampaigns: Campaign[] = [
          {
            id: 'mock_1',
            name: 'Summer Sale Campaign',
            objective: 'sales',
            status: 'active',
            budget: {
              type: 'daily',
              amount: 8000,
              spent: 4350
            },
            audience: {
              size: 127000,
              demographics: ['age_25_34', 'female', 'tier1'],
              interests: ['Fashion & Style', 'Online Shopping'],
              behaviors: ['Premium Brand Lovers', 'Online Shoppers']
            },
            performance: {
              impressions: 284750,
              clicks: 12834,
              conversions: 1567,
              ctr: 4.51,
              cpc: 1.83,
              roi: 189.3
            },
            schedule: {
              startDate: '2024-07-01',
              endDate: '2024-07-31',
              timezone: 'Asia/Shanghai'
            },
            createdAt: '2024-07-01T08:00:00.000Z',
            updatedAt: '2024-07-15T14:30:00.000Z',
            createdBy: 'Marketing Manager'
          },
          {
            id: 'mock_2',
            name: 'Brand Awareness Q3',
            objective: 'awareness',
            status: 'active',
            budget: {
              type: 'lifetime',
              amount: 50000,
              spent: 12750
            },
            audience: {
              size: 89000,
              demographics: ['age_18_24', 'age_25_34', 'tier1', 'tier2'],
              interests: ['Technology', 'Innovation'],
              behaviors: ['Early Adopters', 'Social Media Active']
            },
            performance: {
              impressions: 567890,
              clicks: 8234,
              conversions: 423,
              ctr: 1.45,
              cpc: 1.55,
              roi: 67.8
            },
            schedule: {
              startDate: '2024-07-10',
              endDate: '2024-09-30',
              timezone: 'Asia/Shanghai'
            },
            createdAt: '2024-07-10T10:15:00.000Z',
            updatedAt: '2024-07-20T16:45:00.000Z',
            createdBy: 'Brand Manager'
          },
          {
            id: 'mock_3',
            name: 'VIP Customer Retention',
            objective: 'engagement',
            status: 'paused',
            budget: {
              type: 'daily',
              amount: 3000,
              spent: 1890
            },
            audience: {
              size: 1200,
              demographics: ['vip_segment'],
              interests: ['Luxury', 'Premium Services'],
              behaviors: ['VIP Customers', 'Brand Loyal']
            },
            performance: {
              impressions: 45600,
              clicks: 2340,
              conversions: 567,
              ctr: 5.13,
              cpc: 3.80,
              roi: 245.6
            },
            schedule: {
              startDate: '2024-06-15',
              timezone: 'Asia/Shanghai'
            },
            createdAt: '2024-06-15T12:00:00.000Z',
            updatedAt: '2024-07-01T09:20:00.000Z',
            createdBy: 'CRM Manager'
          },
          {
            id: 'mock_4',
            name: 'Mobile App Download Push',
            objective: 'app',
            status: 'draft',
            budget: {
              type: 'lifetime',
              amount: 15000,
              spent: 0
            },
            audience: {
              size: 156000,
              demographics: ['age_18_34', 'mobile_users'],
              interests: ['Mobile Apps', 'Technology'],
              behaviors: ['Mobile-First Users', 'App Users']
            },
            performance: {
              impressions: 0,
              clicks: 0,
              conversions: 0,
              ctr: 0,
              cpc: 0,
              roi: 0
            },
            schedule: {
              startDate: '2024-08-01',
              endDate: '2024-08-31',
              timezone: 'Asia/Shanghai'
            },
            createdAt: '2024-07-20T14:00:00.000Z',
            updatedAt: '2024-07-20T14:00:00.000Z',
            createdBy: 'Product Manager'
          },
          {
            id: 'mock_5',
            name: 'Website Traffic Campaign',
            objective: 'traffic',
            status: 'active',
            budget: {
              type: 'daily',
              amount: 1000,
              spent: 847
            },
            audience: {
              size: 105806,
              demographics: ['age_25_44', 'tier2'],
              interests: ['Shopping', 'Online Retail'],
              behaviors: ['Website Visitors', 'Online Browsers']
            },
            performance: {
              impressions: 156789,
              clicks: 4567,
              conversions: 234,
              ctr: 2.91,
              cpc: 0.85,
              roi: 145.7
            },
            schedule: {
              startDate: '2024-07-30',
              endDate: '2024-08-30',
              timezone: 'Asia/Shanghai'
            },
            createdAt: '2024-07-30T09:00:00.000Z',
            updatedAt: '2024-07-31T11:15:00.000Z',
            createdBy: 'Digital Marketing'
          },
          {
            id: 'mock_6',
            name: 'Brand Awareness Campaign',
            objective: 'awareness',
            status: 'active',
            budget: {
              type: 'daily',
              amount: 1200,
              spent: 945
            },
            audience: {
              size: 78505,
              demographics: ['age_18_35', 'tier1'],
              interests: ['Brand Discovery', 'Lifestyle'],
              behaviors: ['Brand Explorers', 'Social Influencers']
            },
            performance: {
              impressions: 298456,
              clicks: 8923,
              conversions: 445,
              ctr: 2.99,
              cpc: 1.12,
              roi: 167.3
            },
            schedule: {
              startDate: '2024-07-31',
              endDate: '2024-08-31',
              timezone: 'Asia/Shanghai'
            },
            createdAt: '2024-07-31T08:30:00.000Z',
            updatedAt: '2024-07-31T10:45:00.000Z',
            createdBy: 'Brand Team'
          }
        ]
        
        set({ campaigns: mockCampaigns })
      }
    }),
    {
      name: 'campaign-store',
      version: 1,
    }
  )
)
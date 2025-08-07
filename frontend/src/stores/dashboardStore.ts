import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface DashboardData {
  date: string
  revenue: number
  customers: {
    total: number
    vip: number
    regular: number
    new: number
    inactive: number
  }
  campaigns: {
    active: number
    total_impressions: number
    total_clicks: number
    total_conversions: number
    avg_ctr: number
    avg_roi: number
  }
  engagement: {
    session_duration: number
    pages_per_session: number
    bounce_rate: number
    return_rate: number
  }
  geography: {
    [city: string]: {
      customers: number
      revenue: number
      engagement: number
    }
  }
}

export interface AIInsight {
  id: string
  type: 'opportunity' | 'warning' | 'trend' | 'recommendation'
  priority: 'high' | 'medium' | 'low'
  title: string
  description: string
  data_source: string[]
  confidence: number
  impact_estimate: string
  created_at: string
  actions: string[]
}

interface DashboardStore {
  currentTimeframe: 'daily' | 'monthly' | 'yearly'
  selectedDate: string
  data: DashboardData[]
  insights: AIInsight[]
  
  setTimeframe: (timeframe: 'daily' | 'monthly' | 'yearly') => void
  setSelectedDate: (date: string) => void
  getCurrentData: () => DashboardData | null
  getTimeframeData: (days: number) => DashboardData[]
  generateAIInsights: () => void
  initializeData: () => void
}

// Generate realistic historical data
const generateHistoricalData = (): DashboardData[] => {
  const data: DashboardData[] = []
  const today = new Date()
  
  // Generate data for the last 365 days
  for (let i = 365; i >= 0; i--) {
    const date = new Date(today)
    date.setDate(date.getDate() - i)
    
    // Simulate seasonal trends and growth
    const dayOfYear = date.getTime() - new Date(date.getFullYear(), 0, 0).getTime()
    const seasonalMultiplier = 1 + 0.3 * Math.sin(dayOfYear / 365 * 2 * Math.PI)
    const growthMultiplier = 1 + (365 - i) * 0.001 // 0.1% daily growth
    const randomVariation = 0.8 + Math.random() * 0.4 // ±20% random variation
    
    const baseRevenue = 50000
    const dailyRevenue = Math.round(baseRevenue * seasonalMultiplier * growthMultiplier * randomVariation)
    
    // Customer data with realistic relationships
    const totalCustomers = Math.round(1000 + (365 - i) * 2 + Math.random() * 50)
    const vipPercent = 0.08 + Math.random() * 0.04 // 8-12%
    const newPercent = 0.15 + Math.random() * 0.1 // 15-25%
    const inactivePercent = 0.1 + Math.random() * 0.05 // 10-15%
    
    const vipCustomers = Math.round(totalCustomers * vipPercent)
    const newCustomers = Math.round(totalCustomers * newPercent)
    const inactiveCustomers = Math.round(totalCustomers * inactivePercent)
    const regularCustomers = totalCustomers - vipCustomers - newCustomers - inactiveCustomers
    
    // Campaign performance - consistent active campaigns
    const activeCampaigns = Math.round(2 + Math.random() * 2) // 2-4 campaigns
    const impressions = Math.round(dailyRevenue * 20 + Math.random() * 100000)
    const ctr = 2.5 + Math.random() * 2 // 2.5-4.5%
    const clicks = Math.round(impressions * ctr / 100)
    const conversionRate = 3 + Math.random() * 4 // 3-7%
    const conversions = Math.round(clicks * conversionRate / 100)
    const roi = 150 + Math.random() * 100 // 150-250%
    
    // Engagement metrics
    const sessionDuration = 180 + Math.random() * 120 // 3-5 minutes
    const pagesPerSession = 2.5 + Math.random() * 2 // 2.5-4.5 pages
    const bounceRate = 25 + Math.random() * 30 // 25-55%
    const returnRate = 40 + Math.random() * 25 // 40-65%
    
    // Geographic distribution (top Chinese cities)
    const cities = ['Shanghai', 'Beijing', 'Guangzhou', 'Shenzhen', 'Hangzhou', 'Nanjing', 'Wuhan', 'Chengdu']
    const geography: { [city: string]: { customers: number; revenue: number; engagement: number } } = {}
    
    let remainingCustomers = totalCustomers
    let remainingRevenue = dailyRevenue
    
    cities.forEach((city, index) => {
      const isLast = index === cities.length - 1
      const customerShare = isLast ? remainingCustomers : Math.round(remainingCustomers * (0.1 + Math.random() * 0.2))
      const revenueShare = isLast ? remainingRevenue : Math.round(remainingRevenue * (0.1 + Math.random() * 0.2))
      
      geography[city] = {
        customers: customerShare,
        revenue: revenueShare,
        engagement: 60 + Math.random() * 30 // 60-90% engagement
      }
      
      remainingCustomers -= customerShare
      remainingRevenue -= revenueShare
    })
    
    data.push({
      date: date.toISOString().split('T')[0],
      revenue: dailyRevenue,
      customers: {
        total: totalCustomers,
        vip: vipCustomers,
        regular: regularCustomers,
        new: newCustomers,
        inactive: inactiveCustomers
      },
      campaigns: {
        active: activeCampaigns,
        total_impressions: impressions,
        total_clicks: clicks,
        total_conversions: conversions,
        avg_ctr: Math.round(ctr * 10) / 10,
        avg_roi: Math.round(roi * 10) / 10
      },
      engagement: {
        session_duration: Math.round(sessionDuration),
        pages_per_session: Math.round(pagesPerSession * 10) / 10,
        bounce_rate: Math.round(bounceRate * 10) / 10,
        return_rate: Math.round(returnRate * 10) / 10
      },
      geography
    })
  }
  
  return data
}

// AI Analysis Engine
const analyzeDataForInsights = (data: DashboardData[]): AIInsight[] => {
  const insights: AIInsight[] = []
  
  if (data.length < 7) return insights // Need at least a week of data
  
  const recent = data.slice(-7) // Last 7 days
  const previous = data.slice(-14, -7) // Previous 7 days
  const longTerm = data.slice(-30) // Last 30 days
  
  // Revenue trend analysis
  const recentRevenue = recent.reduce((sum, d) => sum + d.revenue, 0)
  const previousRevenue = previous.reduce((sum, d) => sum + d.revenue, 0)
  const revenueGrowth = ((recentRevenue - previousRevenue) / previousRevenue) * 100
  
  if (revenueGrowth > 10) {
    insights.push({
      id: `revenue_growth_${Date.now()}`,
      type: 'opportunity',
      priority: 'high',
      title: 'Strong Revenue Growth Detected',
      description: `Revenue has increased by ${revenueGrowth.toFixed(1)}% over the past week. This trend indicates successful campaign performance and market expansion.`,
      data_source: ['revenue', 'campaigns'],
      confidence: 92,
      impact_estimate: `+¥${Math.round(revenueGrowth * 1000)}K potential monthly impact`,
      created_at: new Date().toISOString(),
      actions: ['Scale successful campaigns', 'Increase marketing budget', 'Expand to similar audiences']
    })
  } else if (revenueGrowth < -5) {
    insights.push({
      id: `revenue_decline_${Date.now()}`,
      type: 'warning',
      priority: 'high',
      title: 'Revenue Decline Alert',
      description: `Revenue has decreased by ${Math.abs(revenueGrowth).toFixed(1)}% over the past week. Immediate action required to identify and address underlying causes.`,
      data_source: ['revenue', 'campaigns', 'customer_segments'],
      confidence: 89,
      impact_estimate: `${Math.abs(revenueGrowth).toFixed(1)}% revenue at risk`,
      created_at: new Date().toISOString(),
      actions: ['Review campaign performance', 'Analyze customer behavior', 'Implement retention strategies']
    })
  }
  
  // Customer segment analysis
  const avgVipPercent = recent.reduce((sum, d) => sum + (d.customers.vip / d.customers.total * 100), 0) / recent.length
  const avgNewPercent = recent.reduce((sum, d) => sum + (d.customers.new / d.customers.total * 100), 0) / recent.length
  
  if (avgVipPercent > 12) {
    insights.push({
      id: `vip_growth_${Date.now()}`,
      type: 'opportunity',
      priority: 'medium',
      title: 'VIP Customer Base Expanding',
      description: `VIP customers now represent ${avgVipPercent.toFixed(1)}% of your customer base, above the optimal 8-12% range. Focus on VIP retention and upselling.`,
      data_source: ['customer_segments', 'revenue'],
      confidence: 85,
      impact_estimate: '+15-25% customer lifetime value',
      created_at: new Date().toISOString(),
      actions: ['Launch VIP loyalty program', 'Create premium product tiers', 'Implement VIP-only campaigns']
    })
  }
  
  if (avgNewPercent < 15) {
    insights.push({
      id: `new_customer_decline_${Date.now()}`,
      type: 'warning',
      priority: 'medium',
      title: 'New Customer Acquisition Slowing',
      description: `New customers represent only ${avgNewPercent.toFixed(1)}% of your base, below the healthy 15-25% range. Customer acquisition needs attention.`,
      data_source: ['customer_segments', 'campaigns'],
      confidence: 88,
      impact_estimate: 'Growth rate at risk',
      created_at: new Date().toISOString(),
      actions: ['Increase acquisition campaigns', 'Improve referral programs', 'Optimize conversion funnels']
    })
  }
  
  // Campaign performance analysis
  const avgROI = recent.reduce((sum, d) => sum + d.campaigns.avg_roi, 0) / recent.length
  const avgCTR = recent.reduce((sum, d) => sum + d.campaigns.avg_ctr, 0) / recent.length
  
  if (avgROI > 200) {
    insights.push({
      id: `high_roi_${Date.now()}`,
      type: 'opportunity',
      priority: 'high',
      title: 'Exceptional Campaign ROI Achieved',
      description: `Current campaigns are delivering ${avgROI.toFixed(1)}% ROI, significantly above industry average. Scale these high-performing campaigns.`,
      data_source: ['campaigns', 'revenue'],
      confidence: 94,
      impact_estimate: `+${Math.round(avgROI * 10)}% revenue scaling potential`,
      created_at: new Date().toISOString(),
      actions: ['Increase campaign budgets', 'Replicate successful ad creatives', 'Expand to lookalike audiences']
    })
  }
  
  // Geographic performance analysis
  const geoData = recent[recent.length - 1].geography
  const topCity = Object.entries(geoData).reduce((top, [city, data]) => 
    data.revenue > top.revenue ? { city, ...data } : top, 
    { city: '', revenue: 0, customers: 0, engagement: 0 }
  )
  
  if (topCity.engagement > 80) {
    insights.push({
      id: `geo_opportunity_${Date.now()}`,
      type: 'opportunity',
      priority: 'medium',
      title: `${topCity.city} Shows High Engagement`,
      description: `${topCity.city} has ${topCity.engagement.toFixed(1)}% engagement rate with ${topCity.customers} customers. Consider market expansion in similar tier-1 cities.`,
      data_source: ['geography', 'engagement'],
      confidence: 82,
      impact_estimate: '+20-30% market reach potential',
      created_at: new Date().toISOString(),
      actions: ['Expand to similar cities', 'Increase local marketing', 'Partner with local businesses']
    })
  }
  
  // Engagement trend analysis
  const avgBounceRate = recent.reduce((sum, d) => sum + d.engagement.bounce_rate, 0) / recent.length
  const avgSessionDuration = recent.reduce((sum, d) => sum + d.engagement.session_duration, 0) / recent.length
  
  if (avgBounceRate > 50) {
    insights.push({
      id: `bounce_rate_warning_${Date.now()}`,
      type: 'warning',
      priority: 'medium',
      title: 'High Bounce Rate Detected',
      description: `Average bounce rate is ${avgBounceRate.toFixed(1)}%, indicating potential user experience issues. Website optimization recommended.`,
      data_source: ['engagement', 'user_behavior'],
      confidence: 86,
      impact_estimate: 'Up to 25% conversion improvement potential',
      created_at: new Date().toISOString(),
      actions: ['Optimize page load speed', 'Improve content relevance', 'A/B test landing pages']
    })
  }
  
  if (avgSessionDuration > 300) {
    insights.push({
      id: `high_engagement_${Date.now()}`,
      type: 'trend',
      priority: 'low',
      title: 'Excellent User Engagement',
      description: `Users spend an average of ${Math.round(avgSessionDuration / 60)} minutes per session, indicating high content quality and user interest.`,
      data_source: ['engagement', 'content_analytics'],
      confidence: 90,
      impact_estimate: 'Strong foundation for growth',
      created_at: new Date().toISOString(),
      actions: ['Maintain content quality', 'Create more similar content', 'Implement engagement tracking']
    })
  }
  
  return insights
}

export const useDashboardStore = create<DashboardStore>()(
  persist(
    (set, get) => ({
      currentTimeframe: 'daily',
      selectedDate: new Date().toISOString().split('T')[0],
      data: [],
      insights: [],
      
      setTimeframe: (timeframe) => {
        set({ currentTimeframe: timeframe })
        // Regenerate insights when timeframe changes
        get().generateAIInsights()
      },
      
      setSelectedDate: (date) => {
        set({ selectedDate: date })
      },
      
      getCurrentData: () => {
        const { data, selectedDate } = get()
        return data.find(d => d.date === selectedDate) || null
      },
      
      getTimeframeData: (days) => {
        const { data, selectedDate } = get()
        const endDate = new Date(selectedDate)
        const startDate = new Date(endDate)
        startDate.setDate(startDate.getDate() - days + 1)
        
        return data.filter(d => {
          const date = new Date(d.date)
          return date >= startDate && date <= endDate
        })
      },
      
      generateAIInsights: () => {
        const { data } = get()
        const insights = analyzeDataForInsights(data)
        set({ insights })
      },
      
      initializeData: () => {
        const existingData = get().data
        if (existingData.length === 0) {
          const data = generateHistoricalData()
          const insights = analyzeDataForInsights(data)
          set({ data, insights })
        }
      }
    }),
    {
      name: 'dashboard-store',
      version: 1,
    }
  )
)
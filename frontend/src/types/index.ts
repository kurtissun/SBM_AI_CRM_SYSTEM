// Global type definitions for the SBM AI CRM Frontend

export interface User {
  id: string
  email: string
  name: string
  role: string
  permissions: string[]
}

export interface Customer {
  id: string
  customer_id: string
  name: string
  email: string
  total_spent: number
  purchase_frequency: number
  membership_level: string
  location: string
  predicted_clv?: number
  churn_risk?: 'low' | 'medium' | 'high'
}

export interface Campaign {
  id: string
  name: string
  description: string
  status: 'active' | 'paused' | 'completed' | 'draft'
  budget: number
  start_date: string
  end_date: string
  impressions?: number
  conversions?: number
  roi?: number
  conversion_rate?: number
  budget_spent?: number
  target_audience_size?: number
  ai_predictions?: {
    expected_roi: number
    confidence: number
  }
}

export interface DashboardData {
  total_customers: number
  monthly_revenue: number
  active_campaigns: number
  today_traffic: number
  user_name: string
  live_visitors: number
  conversion_rate: number
  peak_hour: string
  top_zone: string
}

export interface MetricCardProps {
  title: string
  value: string
  change: string
  trend: 'up' | 'down'
  icon: React.ComponentType<any>
  color: 'blue' | 'green' | 'purple' | 'orange' | 'red'
  link: string
}

export interface ApiResponse<T = any> {
  data: T
  message?: string
  status: number
}
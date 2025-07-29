import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  Users, ShoppingCart, TrendingUp, DollarSign, Target, Brain,
  Activity, Calendar, ChevronRight, ArrowUp, ArrowDown,
  Sparkles, Building, Eye, Globe
} from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'
import { Line, Bar, Doughnut } from 'react-chartjs-2'
import { api } from '@/lib/api'
import { MetricCard } from '@/components/dashboard/MetricCard'
import { ActivityFeed } from '@/components/dashboard/ActivityFeed'
import { CampaignPerformance } from '@/components/dashboard/CampaignPerformance'
import { AIInsightsFeed } from '@/components/dashboard/AIInsightsFeed'
import { RevenueChart } from '@/components/dashboard/RevenueChart'
import { CustomerSegmentChart } from '@/components/dashboard/CustomerSegmentChart'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

export const Dashboard: React.FC = () => {
  const [selectedPeriod, setSelectedPeriod] = useState('7d')
  const [greeting, setGreeting] = useState('')

  // Fetch dashboard data
  const { data: dashboardData, isLoading } = useQuery({
    queryKey: ['dashboard', selectedPeriod],
    queryFn: () => api.get(`/analytics/dashboard?period=${selectedPeriod}`),
  })

  // Set greeting based on time
  useEffect(() => {
    const hour = new Date().getHours()
    if (hour < 12) setGreeting('Good morning')
    else if (hour < 18) setGreeting('Good afternoon')
    else setGreeting('Good evening')
  }, [])

  const metrics = [
    {
      title: 'Total Customers',
      value: dashboardData?.total_customers || '0',
      change: '+12.5%',
      trend: 'up' as const,
      icon: Users,
      color: 'blue' as const,
      link: '/customers'
    },
    {
      title: 'Revenue (Current Month)',
      value: `¥${dashboardData?.monthly_revenue || '0'}`,
      change: '+23.1%',
      trend: 'up' as const,
      icon: DollarSign,
      color: 'green' as const,
      link: '/analytics'
    },
    {
      title: 'Active Campaigns',
      value: dashboardData?.active_campaigns || '0',
      change: '+5',
      trend: 'up' as const,
      icon: Target,
      color: 'purple' as const,
      link: '/campaigns'
    },
    {
      title: 'Mall Traffic Today',
      value: dashboardData?.today_traffic || '0',
      change: '-2.4%',
      trend: 'down' as const,
      icon: Building,
      color: 'orange' as const,
      link: '/mall-operations'
    },
  ]

  const quickActions = [
    { label: 'Create Campaign', icon: Target, link: '/campaigns/new', color: 'blue' },
    { label: 'View Analytics', icon: Activity, link: '/analytics', color: 'green' },
    { label: 'Segment Customers', icon: Brain, link: '/segmentation', color: 'purple' },
    { label: 'Generate Report', icon: Sparkles, link: '/reports', color: 'orange' },
  ]

  return (
    <div className="p-6 space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            {greeting}, {dashboardData?.user_name || 'there'}!
          </h1>
          <p className="text-gray-600 mt-1">
            Here's what's happening with your mall today
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <select
            value={selectedPeriod}
            onChange={(e) => setSelectedPeriod(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="1d">Today</option>
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
          </select>
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
            <Calendar className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {metrics.map((metric, index) => (
          <motion.div
            key={metric.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <MetricCard {...metric} />
          </motion.div>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {quickActions.map((action, index) => (
            <motion.div
              key={action.label}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.05 }}
            >
              <Link
                to={action.link}
                className="flex flex-col items-center p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors group"
              >
                <div className={`w-12 h-12 bg-${action.color}-100 rounded-lg flex items-center justify-center mb-3 group-hover:scale-110 transition-transform`}>
                  <action.icon className={`w-6 h-6 text-${action.color}-600`} />
                </div>
                <span className="text-sm font-medium text-gray-700">{action.label}</span>
              </Link>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Revenue Chart - 2 columns */}
        <div className="lg:col-span-2">
          <RevenueChart period={selectedPeriod} />
        </div>

        {/* Customer Segments - 1 column */}
        <div>
          <CustomerSegmentChart />
        </div>

        {/* Campaign Performance - 2 columns */}
        <div className="lg:col-span-2">
          <CampaignPerformance />
        </div>

        {/* AI Insights Feed - 1 column */}
        <div>
          <AIInsightsFeed />
        </div>

        {/* Live Mall Analytics - Full width */}
        <div className="lg:col-span-3">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-semibold text-gray-900">Live Mall Analytics</h2>
              <Link
                to="/mall-operations"
                className="text-sm text-blue-600 hover:text-blue-700 flex items-center"
              >
                View Details
                <ChevronRight className="w-4 h-4 ml-1" />
              </Link>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <Eye className="w-5 h-5 text-blue-600" />
                  <span className="text-xs text-blue-600 font-medium">Live</span>
                </div>
                <p className="text-2xl font-bold text-gray-900">{dashboardData?.live_visitors || '0'}</p>
                <p className="text-sm text-gray-600">Current Visitors</p>
              </div>
              <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <ShoppingCart className="w-5 h-5 text-green-600" />
                  <span className="text-xs text-green-600 font-medium">+15%</span>
                </div>
                <p className="text-2xl font-bold text-gray-900">{dashboardData?.conversion_rate || '0'}%</p>
                <p className="text-sm text-gray-600">Conversion Rate</p>
              </div>
              <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <TrendingUp className="w-5 h-5 text-purple-600" />
                  <span className="text-xs text-purple-600 font-medium">Peak</span>
                </div>
                <p className="text-2xl font-bold text-gray-900">{dashboardData?.peak_hour || '2-3 PM'}</p>
                <p className="text-sm text-gray-600">Busiest Time</p>
              </div>
              <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <Globe className="w-5 h-5 text-orange-600" />
                  <span className="text-xs text-orange-600 font-medium">Top</span>
                </div>
                <p className="text-2xl font-bold text-gray-900">{dashboardData?.top_zone || 'Zone A'}</p>
                <p className="text-sm text-gray-600">Hottest Zone</p>
              </div>
            </div>
          </div>
        </div>

        {/* Activity Feed - Full width */}
        <div className="lg:col-span-3">
          <ActivityFeed />
        </div>
      </div>
    </div>
  )
}
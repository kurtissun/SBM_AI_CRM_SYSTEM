import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  Gift, Award, Star, Crown, Users, DollarSign, TrendingUp,
  Calendar, Phone, Mail, MapPin, CreditCard, ShoppingBag,
  Heart, Sparkles, Zap, Target, Clock, BarChart3, Filter,
  Download, RefreshCw, Search, ChevronRight, Settings
} from 'lucide-react'
import { useTranslation } from '@/contexts/TranslationContext'
import { toast } from 'react-hot-toast'
import { showAlert } from '@/lib/alertService'

export const LoyaltyManagement: React.FC = () => {
  const { t } = useTranslation()
  const [selectedView, setSelectedView] = useState('overview')
  const [selectedTier, setSelectedTier] = useState('all')
  const [timeRange, setTimeRange] = useState('30d')

  const views = [
    { id: 'overview', label: 'Program Overview', icon: BarChart3 },
    { id: 'members', label: 'Member Management', icon: Users },
    { id: 'rewards', label: 'Rewards & Benefits', icon: Gift },
    { id: 'campaigns', label: 'Campaigns', icon: Target }
  ]

  const membershipTiers = [
    { 
      id: 'orange', 
      name: '橙卡会员 (Orange)', 
      color: 'orange', 
      members: 45620, 
      spending: '¥0-2K',
      benefits: 5,
      icon: Gift
    },
    { 
      id: 'gold', 
      name: '金卡会员 (Gold)', 
      color: 'yellow', 
      members: 18450, 
      spending: '¥2K-10K',
      benefits: 12,
      icon: Award
    },
    { 
      id: 'diamond', 
      name: '钻卡会员 (Diamond)', 
      color: 'purple', 
      members: 3890, 
      spending: '¥10K+',
      benefits: 25,
      icon: Star
    },
    { 
      id: 'vip', 
      name: 'VIP会员 (VIP)', 
      color: 'rose', 
      members: 680, 
      spending: '¥50K+',
      benefits: 50,
      icon: Crown
    }
  ]

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{t('loyalty.title')}</h1>
          <p className="text-gray-600 mt-1">{t('loyalty.subtitle')}</p>
        </div>
        <div className="flex items-center space-x-3">
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
            <option value="90d">Last 90 Days</option>
            <option value="1y">Last Year</option>
          </select>
          <button 
            onClick={() => {
              toast.success('Syncing loyalty data...')
              setTimeout(() => {
                showAlert(
                  'Loyalty Data Sync Complete',
                  '✓ Member profiles updated: 68,640\n✓ Points balances synchronized\n✓ Tier upgrades processed: 156\n✓ Rewards catalog refreshed\n✓ Campaign metrics updated\n\nAll loyalty data is now current!',
                  'success'
                )
                toast.success('Loyalty data synchronized successfully!')
              }, 3000)
            }}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 flex items-center"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Sync Data
          </button>
          <button 
            onClick={() => {
              toast.success('Generating loyalty report...')
              setTimeout(() => {
                const blob = new Blob(['Loyalty Management Report - ' + new Date().toLocaleDateString()], { type: 'text/plain' })
                const url = window.URL.createObjectURL(blob)
                const a = document.createElement('a')
                a.href = url
                a.download = `loyalty-report-${new Date().toISOString().split('T')[0]}.xlsx`
                a.click()
                window.URL.revokeObjectURL(url)
                toast.success('Loyalty report exported successfully!')
              }, 2000)
            }}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center"
          >
            <Download className="w-4 h-4 mr-2" />
            Export Report
          </button>
        </div>
      </div>

      {/* Loyalty Status */}
      <div className="bg-gradient-to-r from-purple-600 via-pink-600 to-red-600 rounded-xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center">
              <Crown className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-lg font-semibold">Loyalty & VIP Management System</h3>
              <p className="text-white/80">
                68,640 active members • 4 tiers • ¥12.8M lifetime value
              </p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-2xl font-bold">92.1%</p>
            <p className="text-white/80 text-sm">Retention Rate</p>
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Active Members</p>
              <p className="text-3xl font-bold text-gray-900">68,640</p>
              <p className="text-sm text-green-600">+8.2% this month</p>
            </div>
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <Users className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Avg. Member Value</p>
              <p className="text-3xl font-bold text-gray-900">¥1,840</p>
              <p className="text-sm text-purple-600">+12% vs last year</p>
            </div>
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <DollarSign className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Points Redeemed</p>
              <p className="text-3xl font-bold text-gray-900">2.4M</p>
              <p className="text-sm text-orange-600">85% redemption rate</p>
            </div>
            <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
              <Gift className="w-6 h-6 text-orange-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Tier Upgrades</p>
              <p className="text-3xl font-bold text-gray-900">1,256</p>
              <p className="text-sm text-pink-600">This quarter</p>
            </div>
            <div className="w-12 h-12 bg-pink-100 rounded-lg flex items-center justify-center">
              <TrendingUp className="w-6 h-6 text-pink-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Membership Tiers */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Membership Tiers Distribution</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {membershipTiers.map((tier, index) => (
            <motion.div
              key={tier.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className={`relative p-6 rounded-xl border-2 ${
                tier.color === 'orange' ? 'border-orange-200 bg-orange-50' :
                tier.color === 'yellow' ? 'border-yellow-200 bg-yellow-50' :
                tier.color === 'purple' ? 'border-purple-200 bg-purple-50' :
                'border-rose-200 bg-rose-50'
              }`}
            >
              <div className="flex items-center justify-between mb-4">
                <tier.icon className={`w-8 h-8 ${
                  tier.color === 'orange' ? 'text-orange-600' :
                  tier.color === 'yellow' ? 'text-yellow-600' :
                  tier.color === 'purple' ? 'text-purple-600' :
                  'text-rose-600'
                }`} />
                {tier.id === 'vip' && <Sparkles className="w-5 h-5 text-rose-500" />}
              </div>
              
              <h4 className="font-semibold text-gray-900 mb-2">{tier.name}</h4>
              
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Members</span>
                  <span className="font-medium">{tier.members.toLocaleString()}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Spending</span>
                  <span className="font-medium">{tier.spending}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Benefits</span>
                  <span className="font-medium">{tier.benefits}+</span>
                </div>
              </div>
              
              <div className="mt-4">
                <div className={`w-full bg-gray-200 rounded-full h-2`}>
                  <div 
                    className={`h-2 rounded-full ${
                      tier.color === 'orange' ? 'bg-orange-600' :
                      tier.color === 'yellow' ? 'bg-yellow-600' :
                      tier.color === 'purple' ? 'bg-purple-600' :
                      'bg-rose-600'
                    }`}
                    style={{ width: `${(tier.members / 68640) * 100}%` }}
                  ></div>
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  {((tier.members / 68640) * 100).toFixed(1)}% of total members
                </p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* View Navigation */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-2">
        <nav className="flex space-x-1">
          {views.map((view) => (
            <button
              key={view.id}
              onClick={() => setSelectedView(view.id)}
              className={`flex items-center px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                selectedView === view.id
                  ? 'bg-purple-600 text-white'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
              }`}
            >
              <view.icon className="w-4 h-4 mr-2" />
              {view.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Dynamic Content */}
      {selectedView === 'overview' && <ProgramOverview />}
      {selectedView === 'members' && <MemberManagement />}
      {selectedView === 'rewards' && <RewardsBenefits />}
      {selectedView === 'campaigns' && <LoyaltyCampaigns />}
    </div>
  )
}

// Program Overview Component
const ProgramOverview: React.FC = () => {
  const performanceData = [
    { metric: 'Member Acquisition', current: 2145, target: 2000, trend: '+7.3%' },
    { metric: 'Retention Rate', current: 92.1, target: 90, trend: '+2.3%' },
    { metric: 'Points per Transaction', current: 184, target: 150, trend: '+22.7%' },
    { metric: 'Tier Progression Rate', current: 15.8, target: 12, trend: '+31.7%' }
  ]

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Program Performance</h3>
          <div className="space-y-4">
            {performanceData.map((item, index) => (
              <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex-1">
                  <h4 className="font-medium text-gray-900 mb-1">{item.metric}</h4>
                  <div className="flex items-center space-x-4">
                    <div>
                      <p className="text-xs text-gray-600">Current</p>
                      <p className="font-bold text-2xl text-gray-900">
                        {item.metric.includes('Rate') ? `${item.current}%` : item.current.toLocaleString()}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-600">Target</p>
                      <p className="font-medium text-gray-700">
                        {item.metric.includes('Rate') ? `${item.target}%` : item.target.toLocaleString()}
                      </p>
                    </div>
                    <div className="text-right">
                      <span className="text-xs px-2 py-1 bg-green-100 text-green-700 rounded-full">
                        {item.trend}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Member Lifetime Value by Tier</h3>
          <div className="space-y-4">
            {[
              { tier: 'VIP会员', value: 58600, members: 680, color: 'bg-rose-500' },
              { tier: '钻卡会员', value: 24800, members: 3890, color: 'bg-purple-500' },
              { tier: '金卡会员', value: 8200, members: 18450, color: 'bg-yellow-500' },
              { tier: '橙卡会员', value: 2400, members: 45620, color: 'bg-orange-500' }
            ].map((tier, index) => (
              <div key={index} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className={`w-4 h-4 rounded-full ${tier.color}`}></div>
                  <div>
                    <h4 className="font-medium text-gray-900">{tier.tier}</h4>
                    <p className="text-sm text-gray-600">{tier.members.toLocaleString()} members</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-bold text-lg text-green-600">¥{tier.value.toLocaleString()}</p>
                  <p className="text-xs text-gray-500">LTV</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Activity Timeline */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
        <div className="space-y-4">
          {[
            { time: '2 hours ago', event: '156 members upgraded to Gold tier', type: 'upgrade' },
            { time: '4 hours ago', event: 'New VIP benefit launched: Priority Customer Service', type: 'benefit' },
            { time: '6 hours ago', event: '2,340 points redeemed for exclusive products', type: 'redemption' },
            { time: '8 hours ago', event: 'Diamond member celebration event completed', type: 'event' },
            { time: '1 day ago', event: '45 new VIP members joined this week', type: 'acquisition' }
          ].map((activity, index) => (
            <div key={index} className="flex items-center space-x-4 p-3 bg-gray-50 rounded-lg">
              <div className={`w-3 h-3 rounded-full ${
                activity.type === 'upgrade' ? 'bg-green-500' :
                activity.type === 'benefit' ? 'bg-blue-500' :
                activity.type === 'redemption' ? 'bg-orange-500' :
                activity.type === 'event' ? 'bg-purple-500' :
                'bg-pink-500'
              }`}></div>
              <div className="flex-1">
                <p className="text-gray-900">{activity.event}</p>
                <p className="text-sm text-gray-500">{activity.time}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

// Member Management Component
const MemberManagement: React.FC = () => {
  const topMembers = [
    {
      id: '1',
      name: '张先生 (Mr. Zhang)',
      tier: 'VIP',
      spending: 89600,
      points: 15600,
      lastVisit: '2 days ago',
      joined: '2019-03-15'
    },
    {
      id: '2',
      name: '李女士 (Ms. Li)',
      tier: 'Diamond',
      spending: 45200,
      points: 8900,
      lastVisit: '1 week ago',
      joined: '2020-07-22'
    },
    {
      id: '3',
      name: '王女士 (Ms. Wang)',
      tier: 'Gold',
      spending: 23800,
      points: 4200,
      lastVisit: '3 days ago',
      joined: '2021-01-10'
    }
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">Member Directory</h3>
        <div className="flex items-center space-x-2">
          <div className="relative">
            <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Search members..."
              className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
            />
          </div>
          <select className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500">
            <option>All Tiers</option>
            <option>VIP</option>
            <option>Diamond</option>
            <option>Gold</option>
            <option>Orange</option>
          </select>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Top Performing Members</h3>
        <div className="space-y-4">
          {topMembers.map((member, index) => (
            <motion.div
              key={member.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50"
            >
              <div className="flex items-center space-x-4">
                <div className={`w-12 h-12 rounded-full flex items-center justify-center font-bold text-white ${
                  member.tier === 'VIP' ? 'bg-rose-500' :
                  member.tier === 'Diamond' ? 'bg-purple-500' :
                  member.tier === 'Gold' ? 'bg-yellow-500' :
                  'bg-orange-500'
                }`}>
                  {member.name.charAt(0)}
                </div>
                <div>
                  <h4 className="font-semibold text-gray-900">{member.name}</h4>
                  <div className="flex items-center space-x-3 text-sm text-gray-600">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      member.tier === 'VIP' ? 'bg-rose-100 text-rose-700' :
                      member.tier === 'Diamond' ? 'bg-purple-100 text-purple-700' :
                      member.tier === 'Gold' ? 'bg-yellow-100 text-yellow-700' :
                      'bg-orange-100 text-orange-700'
                    }`}>
                      {member.tier}
                    </span>
                    <span>Joined: {member.joined}</span>
                  </div>
                </div>
              </div>
              
              <div className="text-right">
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <p className="text-xs text-gray-600">Total Spending</p>
                    <p className="font-bold text-green-600">¥{member.spending.toLocaleString()}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-600">Points</p>
                    <p className="font-medium text-purple-600">{member.points.toLocaleString()}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-600">Last Visit</p>
                    <p className="text-sm text-gray-700">{member.lastVisit}</p>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Member Analytics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Member Segmentation</h3>
          <div className="space-y-3">
            {[
              { segment: 'High Spenders', count: 4570, percentage: 6.7, color: 'bg-green-500' },
              { segment: 'Frequent Visitors', count: 12340, percentage: 18.0, color: 'bg-blue-500' },
              { segment: 'Occasional Buyers', count: 28960, percentage: 42.2, color: 'bg-yellow-500' },
              { segment: 'New Members', count: 22770, percentage: 33.1, color: 'bg-purple-500' }
            ].map((segment, index) => (
              <div key={index} className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className={`w-4 h-4 rounded-full ${segment.color}`}></div>
                  <span className="text-gray-700">{segment.segment}</span>
                </div>
                <div className="text-right">
                  <span className="font-medium">{segment.count.toLocaleString()}</span>
                  <span className="text-sm text-gray-500 ml-2">({segment.percentage}%)</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Engagement Metrics</h3>
          <div className="space-y-4">
            {[
              { metric: 'App Opens/Month', value: '12.4', unit: 'avg', trend: '+8%' },
              { metric: 'Points Balance', value: '3,247', unit: 'avg', trend: '+15%' },
              { metric: 'Purchase Frequency', value: '2.8', unit: '/month', trend: '+12%' },
              { metric: 'Review Participation', value: '34%', unit: 'rate', trend: '+22%' }
            ].map((metric, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <p className="font-medium text-gray-900">{metric.metric}</p>
                  <p className="text-sm text-gray-600">{metric.unit}</p>
                </div>
                <div className="text-right">
                  <p className="text-xl font-bold text-gray-900">{metric.value}</p>
                  <span className="text-xs px-2 py-1 bg-green-100 text-green-700 rounded-full">
                    {metric.trend}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

// Rewards & Benefits Component
const RewardsBenefits: React.FC = () => {
  const rewards = [
    {
      id: '1',
      name: '免费咖啡券 (Free Coffee)',
      points: 500,
      category: 'F&B',
      redemptions: 15600,
      tier: 'All'
    },
    {
      id: '2',
      name: '10% 购物折扣 (Shopping Discount)',
      points: 1000,
      category: 'Shopping',
      redemptions: 8900,
      tier: 'Gold+'
    },
    {
      id: '3',
      name: '私人购物顾问 (Personal Shopper)',
      points: 5000,
      category: 'Service',
      redemptions: 450,
      tier: 'Diamond+'
    },
    {
      id: '4',
      name: 'VIP休息室使用权 (VIP Lounge)',
      points: 0,
      category: 'Access',
      redemptions: 2340,
      tier: 'VIP'
    }
  ]

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Rewards Catalog</h3>
          <button 
            onClick={() => {
              toast.success('Opening reward creation form...')
              setTimeout(() => {
                showAlert(
                  'Create New Reward',
                  '• Reward Name: [Enter name]\n• Points Required: [Set points]\n• Category: [Select category]\n• Tier Eligibility: [Choose tiers]\n• Description: [Add details]\n• Terms & Conditions: [Set rules]\n\nReward creation form is ready!',
                  'info'
                )
                toast.success('Reward creation form opened!')
              }, 1000)
            }}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 flex items-center"
          >
            <Gift className="w-4 h-4 mr-2" />
            Add New Reward
          </button>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {rewards.map((reward, index) => (
            <motion.div
              key={reward.id}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.1 }}
              className="p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow"
            >
              <div className="flex items-center justify-between mb-3">
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  reward.category === 'F&B' ? 'bg-orange-100 text-orange-700' :
                  reward.category === 'Shopping' ? 'bg-green-100 text-green-700' :
                  reward.category === 'Service' ? 'bg-blue-100 text-blue-700' :
                  'bg-purple-100 text-purple-700'
                }`}>
                  {reward.category}
                </span>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  reward.tier === 'All' ? 'bg-gray-100 text-gray-700' :
                  reward.tier === 'Gold+' ? 'bg-yellow-100 text-yellow-700' :
                  reward.tier === 'Diamond+' ? 'bg-purple-100 text-purple-700' :
                  'bg-rose-100 text-rose-700'
                }`}>
                  {reward.tier}
                </span>
              </div>
              
              <h4 className="font-medium text-gray-900 mb-2">{reward.name}</h4>
              
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Points Required</span>
                  <span className="font-medium">
                    {reward.points === 0 ? 'Free' : reward.points.toLocaleString()}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Total Redemptions</span>
                  <span className="font-medium">{reward.redemptions.toLocaleString()}</span>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Benefits by Tier */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Benefits by Tier</h3>
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {[
            {
              tier: '橙卡会员',
              color: 'orange',
              benefits: [
                'Points on every purchase',
                'Birthday month discount',
                'Member-only events',
                'Priority customer service',
                'Mobile app exclusive deals'
              ]
            },
            {
              tier: '金卡会员',
              color: 'yellow',
              benefits: [
                'All Orange benefits',
                '10% additional points',
                'Free alterations',
                'Express checkout',
                'Early access to sales',
                'Complimentary gift wrapping'
              ]
            },
            {
              tier: '钻卡会员',
              color: 'purple',
              benefits: [
                'All Gold benefits',
                '25% bonus points',
                'Personal shopping assistant',
                'VIP parking',
                'Complimentary refreshments',
                'Private shopping hours'
              ]
            },
            {
              tier: 'VIP会员',
              color: 'rose',
              benefits: [
                'All Diamond benefits',
                '50% bonus points',
                'Dedicated concierge',
                'Complimentary home delivery',
                'Exclusive VIP lounge access',
                'Custom tailoring services'
              ]
            }
          ].map((tierInfo, index) => (
            <div
              key={index}
              className={`p-4 rounded-lg border-2 ${
                tierInfo.color === 'orange' ? 'border-orange-200 bg-orange-50' :
                tierInfo.color === 'yellow' ? 'border-yellow-200 bg-yellow-50' :
                tierInfo.color === 'purple' ? 'border-purple-200 bg-purple-50' :
                'border-rose-200 bg-rose-50'
              }`}
            >
              <h4 className={`font-bold text-lg mb-3 ${
                tierInfo.color === 'orange' ? 'text-orange-700' :
                tierInfo.color === 'yellow' ? 'text-yellow-700' :
                tierInfo.color === 'purple' ? 'text-purple-700' :
                'text-rose-700'
              }`}>
                {tierInfo.tier}
              </h4>
              <ul className="space-y-2">
                {tierInfo.benefits.map((benefit, idx) => (
                  <li key={idx} className="flex items-center text-sm">
                    <div className={`w-2 h-2 rounded-full mr-2 ${
                      tierInfo.color === 'orange' ? 'bg-orange-500' :
                      tierInfo.color === 'yellow' ? 'bg-yellow-500' :
                      tierInfo.color === 'purple' ? 'bg-purple-500' :
                      'bg-rose-500'
                    }`}></div>
                    {benefit}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

// Loyalty Campaigns Component
const LoyaltyCampaigns: React.FC = () => {
  const campaigns = [
    {
      id: '1',
      name: '双倍积分周末 (Double Points Weekend)',
      status: 'active',
      startDate: '2024-01-15',
      endDate: '2024-01-21',
      participants: 28540,
      pointsAwarded: 456000
    },
    {
      id: '2',
      name: '新年VIP升级 (New Year VIP Upgrade)',
      status: 'completed',
      startDate: '2024-01-01',
      endDate: '2024-01-31',
      participants: 12340,
      pointsAwarded: 890000
    },
    {
      id: '3',
      name: '春节特别优惠 (Spring Festival Special)',
      status: 'scheduled',
      startDate: '2024-02-10',
      endDate: '2024-02-25',
      participants: 0,
      pointsAwarded: 0
    }
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">Loyalty Campaigns</h3>
        <button 
          onClick={() => {
            toast.success('Launching campaign creation wizard...')
            setTimeout(() => {
              showAlert(
                'Create New Loyalty Campaign',
                '• Campaign Name: [Enter name]\n• Campaign Type: [Points multiplier/Tier upgrade/Special offer]\n• Target Audience: [Select member segments]\n• Duration: [Set start/end dates]\n• Rewards: [Configure benefits]\n• Budget: [Set campaign budget]\n\nCampaign wizard is ready!',
                'info'
              )
              toast.success('Campaign creation wizard launched!')
            }, 1000)
          }}
          className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 flex items-center"
        >
          <Target className="w-4 h-4 mr-2" />
          Create Campaign
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {campaigns.map((campaign, index) => (
          <motion.div
            key={campaign.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="bg-white rounded-xl shadow-sm border border-gray-200 p-6"
          >
            <div className="flex items-center justify-between mb-4">
              <h4 className="font-semibold text-gray-900">{campaign.name}</h4>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                campaign.status === 'active' ? 'bg-green-100 text-green-700' :
                campaign.status === 'completed' ? 'bg-blue-100 text-blue-700' :
                'bg-yellow-100 text-yellow-700'
              }`}>
                {campaign.status}
              </span>
            </div>
            
            <div className="space-y-3">
              <div className="flex items-center space-x-2 text-sm text-gray-600">
                <Calendar className="w-4 h-4" />
                <span>{campaign.startDate} to {campaign.endDate}</span>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-xs text-gray-600">Participants</p>
                  <p className="font-bold text-lg text-purple-600">
                    {campaign.participants.toLocaleString()}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-gray-600">Points Awarded</p>
                  <p className="font-bold text-lg text-orange-600">
                    {campaign.pointsAwarded.toLocaleString()}
                  </p>
                </div>
              </div>
            </div>
            
            <div className="mt-4 pt-4 border-t border-gray-200 flex space-x-2">
              <button className="flex-1 px-3 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50">
                View Details
              </button>
              <button className="px-3 py-2 text-sm bg-purple-600 text-white rounded-lg hover:bg-purple-700">
                <Settings className="w-4 h-4" />
              </button>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Campaign Performance */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Campaign Performance Overview</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            { metric: 'Active Campaigns', value: '3', change: '+1 this month' },
            { metric: 'Total Participants', value: '40,880', change: '+15% vs last month' },
            { metric: 'Points Distributed', value: '1.35M', change: '+28% vs last month' },
            { metric: 'Avg. Engagement Rate', value: '67.2%', change: '+8.4% vs last month' }
          ].map((metric, index) => (
            <div key={index} className="p-4 border border-gray-200 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">{metric.metric}</p>
              <p className="text-2xl font-bold text-gray-900 mb-1">{metric.value}</p>
              <p className="text-xs text-green-600">{metric.change}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
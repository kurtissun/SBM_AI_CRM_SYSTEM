import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  Globe, TrendingUp, MessageCircle, Users, DollarSign, BarChart3,
  Smartphone, CreditCard, Eye, Star, Calendar, MapPin, Target,
  Heart, Share2, ThumbsUp, Zap, ShoppingBag, Gift, Award,
  Filter, Download, RefreshCw, Search, ChevronRight, Clock
} from 'lucide-react'
import { useTranslation } from '@/contexts/TranslationContext'

export const ChineseMarket: React.FC = () => {
  const { t } = useTranslation()
  const [selectedView, setSelectedView] = useState('overview')
  const [selectedPlatform, setSelectedPlatform] = useState('all')
  const [timeRange, setTimeRange] = useState('7d')

  const views = [
    { id: 'overview', label: 'Market Overview', icon: Globe },
    { id: 'social', label: 'Social Monitoring', icon: MessageCircle },
    { id: 'payments', label: 'Payment Analytics', icon: CreditCard },
    { id: 'competitors', label: 'Competitive Intelligence', icon: Target }
  ]

  const socialPlatforms = [
    { id: 'wechat', name: 'WeChat', users: '1.2B', color: 'bg-green-500' },
    { id: 'weibo', name: 'Weibo', users: '573M', color: 'bg-red-500' },
    { id: 'douyin', name: 'Douyin', users: '600M', color: 'bg-black' },
    { id: 'xiaohongshu', name: 'Xiaohongshu', users: '300M', color: 'bg-pink-500' }
  ]

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{t('chinese.title')}</h1>
          <p className="text-gray-600 mt-1">{t('chinese.subtitle')}</p>
        </div>
        <div className="flex items-center space-x-3">
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="24h">Last 24 Hours</option>
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
            <option value="90d">Last 90 Days</option>
          </select>
          <button className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 flex items-center">
            <RefreshCw className="w-4 h-4 mr-2" />
            Sync Data
          </button>
          <button className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center">
            <Download className="w-4 h-4 mr-2" />
            Export Report
          </button>
        </div>
      </div>

      {/* Market Status */}
      <div className="bg-gradient-to-r from-red-600 via-orange-600 to-yellow-600 rounded-xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center">
              <Globe className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-lg font-semibold">中国市场智能平台 (Chinese Market Intelligence)</h3>
              <p className="text-white/80">
                Real-time monitoring • 1.4B consumers • Multi-platform analytics
              </p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-2xl font-bold">89.2%</p>
            <p className="text-white/80 text-sm">Market Penetration</p>
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Social Engagement</p>
              <p className="text-3xl font-bold text-gray-900">2.8M</p>
              <p className="text-sm text-green-600">+23% from last month</p>
            </div>
            <div className="w-12 h-12 bg-pink-100 rounded-lg flex items-center justify-center">
              <Heart className="w-6 h-6 text-pink-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Payment Volume</p>
              <p className="text-3xl font-bold text-gray-900">¥45.2M</p>
              <p className="text-sm text-blue-600">WeChat Pay: 67%</p>
            </div>
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <CreditCard className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Market Share</p>
              <p className="text-3xl font-bold text-gray-900">15.8%</p>
              <p className="text-sm text-orange-600">Tier 1 cities</p>
            </div>
            <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
              <Target className="w-6 h-6 text-orange-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Brand Sentiment</p>
              <p className="text-3xl font-bold text-gray-900">4.6/5</p>
              <p className="text-sm text-purple-600">Across all platforms</p>
            </div>
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
              <Star className="w-6 h-6 text-purple-600" />
            </div>
          </div>
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
                  ? 'bg-red-600 text-white'
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
      {selectedView === 'overview' && <MarketOverview />}
      {selectedView === 'social' && <SocialMonitoring />}
      {selectedView === 'payments' && <PaymentAnalytics />}
      {selectedView === 'competitors' && <CompetitiveIntelligence />}
    </div>
  )
}

// Market Overview Component
const MarketOverview: React.FC = () => {
  const marketData = [
    { region: 'Beijing', population: '21.5M', penetration: 92, revenue: 12800000 },
    { region: 'Shanghai', population: '26.3M', penetration: 89, revenue: 15600000 },
    { region: 'Guangzhou', population: '18.7M', penetration: 85, revenue: 9400000 },
    { region: 'Shenzhen', population: '17.6M', penetration: 94, revenue: 11200000 },
    { region: 'Hangzhou', population: '12.2M', penetration: 78, revenue: 6800000 },
    { region: 'Chengdu', population: '20.9M', penetration: 71, revenue: 5900000 }
  ]

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Tier 1 Cities Performance</h3>
          <div className="space-y-4">
            {marketData.map((city, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
              >
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium text-gray-900">{city.region}</h4>
                    <span className="text-sm text-gray-500">{city.population}</span>
                  </div>
                  <div className="flex items-center space-x-4">
                    <div>
                      <p className="text-xs text-gray-600">Market Penetration</p>
                      <div className="flex items-center space-x-2">
                        <div className="w-20 bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-red-600 h-2 rounded-full" 
                            style={{ width: `${city.penetration}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-medium">{city.penetration}%</span>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-xs text-gray-600">Revenue (Monthly)</p>
                      <p className="font-medium text-green-600">¥{(city.revenue/1000000).toFixed(1)}M</p>
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Consumer Demographics</h3>
          <div className="space-y-4">
            <div>
              <h4 className="font-medium text-gray-900 mb-3">Age Distribution</h4>
              <div className="space-y-2">
                {[
                  { range: '18-25', percentage: 28, label: 'Gen Z' },
                  { range: '26-35', percentage: 34, label: 'Millennials' },
                  { range: '36-45', percentage: 22, label: 'Gen X' },
                  { range: '46+', percentage: 16, label: 'Boomers' }
                ].map((age, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <span className="text-sm text-gray-600 w-12">{age.range}</span>
                      <span className="text-xs text-gray-500">({age.label})</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="w-24 bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-blue-600 h-2 rounded-full" 
                          style={{ width: `${age.percentage * 2.5}%` }}
                        ></div>
                      </div>
                      <span className="text-sm font-medium w-8">{age.percentage}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            
            <div className="pt-4 border-t border-gray-200">
              <h4 className="font-medium text-gray-900 mb-3">Income Levels (Monthly)</h4>
              <div className="space-y-2">
                {[
                  { range: '¥5K-10K', percentage: 32 },
                  { range: '¥10K-20K', percentage: 28 },
                  { range: '¥20K-35K', percentage: 24 },
                  { range: '¥35K+', percentage: 16 }
                ].map((income, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">{income.range}</span>
                    <div className="flex items-center space-x-2">
                      <div className="w-24 bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-green-600 h-2 rounded-full" 
                          style={{ width: `${income.percentage * 2.5}%` }}
                        ></div>
                      </div>
                      <span className="text-sm font-medium w-8">{income.percentage}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

// Social Monitoring Component
const SocialMonitoring: React.FC = () => {
  const socialData = [
    {
      platform: 'WeChat',
      followers: '2.3M',
      engagement: 8.7,
      sentiment: 4.5,
      posts: 156,
      trending: '+12%'
    },
    {
      platform: 'Weibo',
      followers: '1.8M',
      engagement: 6.2,
      sentiment: 4.2,
      posts: 89,
      trending: '+8%'
    },
    {
      platform: 'Douyin',
      followers: '980K',
      engagement: 12.4,
      sentiment: 4.8,
      posts: 67,
      trending: '+24%'
    },
    {
      platform: 'Xiaohongshu',
      followers: '650K',
      engagement: 9.1,
      sentiment: 4.6,
      posts: 94,
      trending: '+18%'
    }
  ]

  const trendingTopics = [
    { topic: '#新品发布', posts: 15600, sentiment: 'positive' },
    { topic: '#品质生活', posts: 12400, sentiment: 'positive' },
    { topic: '#智能购物', posts: 8900, sentiment: 'neutral' },
    { topic: '#客户服务', posts: 6700, sentiment: 'mixed' },
    { topic: '#价格优势', posts: 5200, sentiment: 'positive' }
  ]

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Platform Performance</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {socialData.map((platform, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="p-4 border border-gray-200 rounded-lg"
            >
              <div className="flex items-center justify-between mb-3">
                <h4 className="font-medium text-gray-900">{platform.platform}</h4>
                <span className={`text-xs px-2 py-1 rounded-full ${
                  platform.trending.startsWith('+') ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                }`}>
                  {platform.trending}
                </span>
              </div>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Followers</span>
                  <span className="text-sm font-medium">{platform.followers}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Engagement</span>
                  <span className="text-sm font-medium">{platform.engagement}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Sentiment</span>
                  <div className="flex items-center">
                    <Star className="w-3 h-3 text-yellow-500 mr-1" />
                    <span className="text-sm font-medium">{platform.sentiment}</span>
                  </div>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Posts</span>
                  <span className="text-sm font-medium">{platform.posts}</span>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Trending Topics (热门话题)</h3>
          <div className="space-y-3">
            {trendingTopics.map((topic, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <h4 className="font-medium text-gray-900">{topic.topic}</h4>
                  <p className="text-sm text-gray-600">{topic.posts.toLocaleString()} posts</p>
                </div>
                <div className="flex items-center space-x-2">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    topic.sentiment === 'positive' ? 'bg-green-100 text-green-700' :
                    topic.sentiment === 'neutral' ? 'bg-yellow-100 text-yellow-700' :
                    topic.sentiment === 'mixed' ? 'bg-orange-100 text-orange-700' :
                    'bg-red-100 text-red-700'
                  }`}>
                    {topic.sentiment}
                  </span>
                  <ChevronRight className="w-4 h-4 text-gray-400" />
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Influencer Partnerships</h3>
          <div className="space-y-3">
            {[
              { name: '李佳琦 (Austin Li)', platform: 'Douyin', followers: '40M', engagement: '15.2%' },
              { name: '薇娅 (Viya)', platform: 'Taobao Live', followers: '35M', engagement: '12.8%' },
              { name: '张大奕', platform: 'Weibo', followers: '12M', engagement: '8.4%' },
              { name: '雪梨', platform: 'Xiaohongshu', followers: '8M', engagement: '11.6%' }
            ].map((influencer, index) => (
              <div key={index} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
                <div>
                  <h4 className="font-medium text-gray-900">{influencer.name}</h4>
                  <p className="text-sm text-gray-600">{influencer.platform} • {influencer.followers}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium text-blue-600">{influencer.engagement}</p>
                  <p className="text-xs text-gray-500">engagement</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

// Payment Analytics Component
const PaymentAnalytics: React.FC = () => {
  const paymentMethods = [
    { name: 'WeChat Pay', share: 67, volume: 30200000, trend: '+8%' },
    { name: 'Alipay', share: 25, volume: 11300000, trend: '+5%' },
    { name: 'UnionPay', share: 6, volume: 2700000, trend: '-2%' },
    { name: 'Others', share: 2, volume: 900000, trend: '+12%' }
  ]

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Payment Method Distribution</h3>
          <div className="space-y-4">
            {paymentMethods.map((method, index) => (
              <div key={index} className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-medium text-gray-900">{method.name}</span>
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-medium">{method.share}%</span>
                    <span className={`text-xs px-2 py-1 rounded-full ${
                      method.trend.startsWith('+') ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                    }`}>
                      {method.trend}
                    </span>
                  </div>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div 
                    className={`h-3 rounded-full ${
                      method.name === 'WeChat Pay' ? 'bg-green-600' :
                      method.name === 'Alipay' ? 'bg-blue-600' :
                      method.name === 'UnionPay' ? 'bg-red-600' :
                      'bg-gray-600'
                    }`}
                    style={{ width: `${method.share}%` }}
                  ></div>
                </div>
                <p className="text-sm text-gray-600">Volume: ¥{(method.volume/1000000).toFixed(1)}M</p>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Transaction Patterns</h3>
          <div className="space-y-4">
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Peak Hours</h4>
              <div className="space-y-2">
                {[
                  { time: '10:00-12:00', volume: 28, label: 'Morning Shopping' },
                  { time: '14:00-16:00', volume: 35, label: 'Afternoon Peak' },
                  { time: '19:00-21:00', volume: 52, label: 'Evening Rush' },
                  { time: '21:00-23:00', volume: 41, label: 'Night Shopping' }
                ].map((peak, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <div>
                      <span className="text-sm font-medium">{peak.time}</span>
                      <p className="text-xs text-gray-600">{peak.label}</p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="w-20 bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-purple-600 h-2 rounded-full" 
                          style={{ width: `${peak.volume}%` }}
                        ></div>
                      </div>
                      <span className="text-sm font-medium w-8">{peak.volume}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="pt-4 border-t border-gray-200">
              <h4 className="font-medium text-gray-900 mb-2">Average Transaction Value</h4>
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center p-3 bg-green-50 rounded-lg">
                  <p className="text-2xl font-bold text-green-600">¥186</p>
                  <p className="text-sm text-gray-600">WeChat Pay</p>
                </div>
                <div className="text-center p-3 bg-blue-50 rounded-lg">
                  <p className="text-2xl font-bold text-blue-600">¥204</p>
                  <p className="text-sm text-gray-600">Alipay</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

// Competitive Intelligence Component
const CompetitiveIntelligence: React.FC = () => {
  const competitors = [
    {
      name: 'Competitor A (天猫)',
      marketShare: 32,
      revenue: '¥180M',
      growth: '+15%',
      strength: 'Brand Recognition',
      weakness: 'Price Sensitivity'
    },
    {
      name: 'Competitor B (京东)',
      marketShare: 28,
      revenue: '¥156M',
      growth: '+12%',
      strength: 'Logistics Network',
      weakness: 'User Experience'
    },
    {
      name: 'Our Company',
      marketShare: 16,
      revenue: '¥89M',
      growth: '+23%',
      strength: 'Innovation',
      weakness: 'Market Penetration'
    },
    {
      name: 'Competitor C (拼多多)',
      marketShare: 24,
      revenue: '¥134M',
      growth: '+18%',
      strength: 'Price Advantage',
      weakness: 'Brand Image'
    }
  ]

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Competitive Landscape</h3>
        <div className="space-y-4">
          {competitors.map((competitor, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className={`p-4 rounded-lg border-2 ${
                competitor.name.includes('Our Company') 
                  ? 'border-blue-300 bg-blue-50' 
                  : 'border-gray-200 bg-gray-50'
              }`}
            >
              <div className="flex items-center justify-between mb-3">
                <h4 className="font-semibold text-gray-900">{competitor.name}</h4>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                  competitor.growth.startsWith('+') ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                }`}>
                  {competitor.growth}
                </span>
              </div>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <p className="text-xs text-gray-600">Market Share</p>
                  <div className="flex items-center space-x-2">
                    <div className="w-16 bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-red-600 h-2 rounded-full" 
                        style={{ width: `${competitor.marketShare * 2.5}%` }}
                      ></div>
                    </div>
                    <span className="text-sm font-medium">{competitor.marketShare}%</span>
                  </div>
                </div>
                
                <div>
                  <p className="text-xs text-gray-600">Revenue</p>
                  <p className="font-medium text-green-600">{competitor.revenue}</p>
                </div>
                
                <div>
                  <p className="text-xs text-gray-600">Key Strength</p>
                  <p className="text-sm font-medium text-blue-600">{competitor.strength}</p>
                </div>
                
                <div>
                  <p className="text-xs text-gray-600">Weakness</p>
                  <p className="text-sm font-medium text-orange-600">{competitor.weakness}</p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Competitive Advantages</h3>
          <div className="space-y-3">
            {[
              { advantage: 'AI-Powered Personalization', impact: 'High', status: 'Leading' },
              { advantage: 'Mobile-First Experience', impact: 'Medium', status: 'Competitive' },
              { advantage: 'Customer Service Quality', impact: 'High', status: 'Leading' },
              { advantage: 'Price Competitiveness', impact: 'Medium', status: 'Behind' },
              { advantage: 'Brand Recognition', impact: 'High', status: 'Behind' }
            ].map((item, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <h4 className="font-medium text-gray-900">{item.advantage}</h4>
                  <p className="text-sm text-gray-600">Impact: {item.impact}</p>
                </div>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                  item.status === 'Leading' ? 'bg-green-100 text-green-700' :
                  item.status === 'Competitive' ? 'bg-yellow-100 text-yellow-700' :
                  'bg-red-100 text-red-700'
                }`}>
                  {item.status}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Market Opportunities</h3>
          <div className="space-y-3">
            {[
              { opportunity: 'Lower-tier Cities Expansion', potential: 'High', timeline: 'Q2 2024' },
              { opportunity: 'Live Commerce Integration', potential: 'High', timeline: 'Q1 2024' },
              { opportunity: 'Cross-border E-commerce', potential: 'Medium', timeline: 'Q3 2024' },
              { opportunity: 'B2B Market Entry', potential: 'Medium', timeline: 'Q4 2024' },
              { opportunity: 'Sustainable Products Line', potential: 'Low', timeline: 'Q1 2025' }
            ].map((item, index) => (
              <div key={index} className="p-3 border border-gray-200 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium text-gray-900">{item.opportunity}</h4>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    item.potential === 'High' ? 'bg-green-100 text-green-700' :
                    item.potential === 'Medium' ? 'bg-yellow-100 text-yellow-700' :
                    'bg-gray-100 text-gray-700'
                  }`}>
                    {item.potential} Potential
                  </span>
                </div>
                <div className="flex items-center space-x-2 text-sm text-gray-600">
                  <Calendar className="w-4 h-4" />
                  <span>Target: {item.timeline}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
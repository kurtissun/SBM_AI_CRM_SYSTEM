import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  Mic, MessageSquare, TrendingUp, Star, ThumbsUp, ThumbsDown,
  AlertTriangle, CheckCircle, Users, BarChart3, PieChart, Activity,
  RefreshCw, Download, Filter, Search, Calendar, Globe, Heart,
  Zap, Target, Award, Lightbulb, Eye, Share2, Clock, MapPin
} from 'lucide-react'
import { useTranslation } from '@/contexts/TranslationContext'
import { toast } from 'react-hot-toast'

export const VoiceOfCustomer: React.FC = () => {
  const { t } = useTranslation()
  const [selectedView, setSelectedView] = useState('overview')
  const [selectedPlatform, setSelectedPlatform] = useState('all')
  const [timeRange, setTimeRange] = useState('30d')
  const [sentimentFilter, setSentimentFilter] = useState('all')

  const views = [
    { id: 'overview', label: 'Sentiment Overview', icon: BarChart3 },
    { id: 'feedback', label: 'Feedback Analysis', icon: MessageSquare },
    { id: 'social', label: 'Social Listening', icon: Mic },
    { id: 'insights', label: 'AI Insights', icon: Lightbulb },
    { id: 'trends', label: 'Trend Analysis', icon: TrendingUp }
  ]

  const platforms = [
    { id: 'all', name: 'All Platforms', count: '12.8K' },
    { id: 'google', name: 'Google Reviews', count: '4.2K' },
    { id: 'yelp', name: 'Yelp', count: '2.1K' },
    { id: 'facebook', name: 'Facebook', count: '1.8K' },
    { id: 'twitter', name: 'Twitter/X', count: '3.2K' },
    { id: 'instagram', name: 'Instagram', count: '1.5K' }
  ]

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{t('voc.title')}</h1>
          <p className="text-gray-600 mt-1">{t('voc.subtitle')}</p>
        </div>
        <div className="flex items-center space-x-3">
          <select
            value={selectedPlatform}
            onChange={(e) => setSelectedPlatform(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {platforms.map((platform) => (
              <option key={platform.id} value={platform.id}>
                {platform.name} ({platform.count})
              </option>
            ))}
          </select>
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
              toast.success('Refreshing voice of customer data...')
              setTimeout(() => {
                window.location.reload()
              }, 1000)
            }}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </button>
          <button 
            onClick={() => {
              toast.success('Exporting voice of customer report...')
              setTimeout(() => {
                const blob = new Blob(['Voice of Customer Report - ' + new Date().toLocaleDateString()], { type: 'text/plain' })
                const url = window.URL.createObjectURL(blob)
                const a = document.createElement('a')
                a.href = url
                a.download = `voice-of-customer-${new Date().toISOString().split('T')[0]}.xlsx`
                a.click()
                window.URL.revokeObjectURL(url)
                toast.success('VOC report exported successfully!')
              }, 2000)
            }}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center"
          >
            <Download className="w-4 h-4 mr-2" />
            Export
          </button>
        </div>
      </div>

      {/* Voice of Customer Status */}
      <div className="bg-gradient-to-r from-green-600 via-blue-600 to-purple-600 rounded-xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center">
              <Heart className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-lg font-semibold">Voice of Customer Intelligence</h3>
              <p className="text-white/80">
                12.8K reviews analyzed • 94% accuracy • Real-time sentiment tracking
              </p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-2xl font-bold">4.6/5</p>
            <p className="text-white/80 text-sm">Overall Satisfaction</p>
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Sentiment Score</p>
              <p className="text-3xl font-bold text-gray-900">87.3</p>
              <p className="text-sm text-green-600">+5.2 vs last month</p>
            </div>
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <ThumbsUp className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Reviews Analyzed</p>
              <p className="text-3xl font-bold text-gray-900">12.8K</p>
              <p className="text-sm text-blue-600">+23% this month</p>
            </div>
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <MessageSquare className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Response Rate</p>
              <p className="text-3xl font-bold text-gray-900">94.7%</p>
              <p className="text-sm text-purple-600">Above industry avg</p>
            </div>
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
              <Target className="w-6 h-6 text-purple-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Issue Resolution</p>
              <p className="text-3xl font-bold text-gray-900">2.4h</p>
              <p className="text-sm text-orange-600">Average response time</p>
            </div>
            <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
              <Clock className="w-6 h-6 text-orange-600" />
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
                  ? 'bg-green-600 text-white'
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
      {selectedView === 'overview' && <SentimentOverview />}
      {selectedView === 'feedback' && <FeedbackAnalysis />}
      {selectedView === 'social' && <SocialListening />}
      {selectedView === 'insights' && <AIInsights />}
      {selectedView === 'trends' && <TrendAnalysis />}
    </div>
  )
}

// Sentiment Overview Component
const SentimentOverview: React.FC = () => {
  const sentimentData = [
    { sentiment: 'Positive', count: 8420, percentage: 65.8, color: 'bg-green-500' },
    { sentiment: 'Neutral', count: 2890, percentage: 22.6, color: 'bg-yellow-500' },
    { sentiment: 'Negative', count: 1490, percentage: 11.6, color: 'bg-red-500' }
  ]

  const topKeywords = [
    { keyword: 'excellent service', mentions: 1240, sentiment: 'positive' },
    { keyword: 'fast delivery', mentions: 980, sentiment: 'positive' },
    { keyword: 'great quality', mentions: 856, sentiment: 'positive' },
    { keyword: 'expensive price', mentions: 340, sentiment: 'negative' },
    { keyword: 'slow response', mentions: 290, sentiment: 'negative' },
    { keyword: 'good value', mentions: 650, sentiment: 'positive' }
  ]

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Sentiment Distribution</h3>
          <div className="space-y-4">
            {sentimentData.map((data, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="flex items-center space-x-4"
              >
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium text-gray-900">{data.sentiment}</span>
                    <div className="flex items-center space-x-2">
                      <span className="text-sm text-gray-600">{data.count.toLocaleString()}</span>
                      <span className="text-sm font-medium">{data.percentage}%</span>
                    </div>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div 
                      className={`h-3 rounded-full ${data.color}`}
                      style={{ width: `${data.percentage}%` }}
                    ></div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
          
          <div className="mt-6 pt-4 border-t border-gray-200">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">Overall Sentiment Score</span>
              <span className="font-bold text-2xl text-green-600">87.3</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Top Keywords</h3>
          <div className="space-y-3">
            {topKeywords.map((keyword, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
              >
                <div className="flex items-center space-x-3">
                  <div className={`w-3 h-3 rounded-full ${
                    keyword.sentiment === 'positive' ? 'bg-green-500' :
                    keyword.sentiment === 'neutral' ? 'bg-yellow-500' : 'bg-red-500'
                  }`}></div>
                  <span className="font-medium text-gray-900">{keyword.keyword}</span>
                </div>
                <div className="text-right">
                  <span className="text-sm font-medium text-gray-900">{keyword.mentions}</span>
                  <p className="text-xs text-gray-500">mentions</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      {/* Rating Breakdown */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Rating Breakdown</h3>
        <div className="space-y-3">
          {[
            { rating: 5, count: 6420, percentage: 50.2 },
            { rating: 4, count: 3140, percentage: 24.5 },
            { rating: 3, count: 1890, percentage: 14.8 },
            { rating: 2, count: 820, percentage: 6.4 },
            { rating: 1, count: 530, percentage: 4.1 }
          ].map((rating, index) => (
            <div key={index} className="flex items-center space-x-4">
              <div className="flex items-center space-x-1 w-16">
                <span className="text-sm font-medium">{rating.rating}</span>
                <Star className="w-4 h-4 text-yellow-500 fill-current" />
              </div>
              <div className="flex-1 flex items-center space-x-3">
                <div className="flex-1 bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-yellow-500 h-2 rounded-full" 
                    style={{ width: `${rating.percentage}%` }}
                  ></div>
                </div>
                <span className="text-sm text-gray-600 w-16">{rating.count.toLocaleString()}</span>
                <span className="text-sm font-medium w-12">{rating.percentage}%</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

// Feedback Analysis Component
const FeedbackAnalysis: React.FC = () => {
  const feedbackCategories = [
    { category: 'Product Quality', positive: 78, negative: 22, total: 3240 },
    { category: 'Customer Service', positive: 85, negative: 15, total: 2890 },
    { category: 'Delivery & Shipping', positive: 72, negative: 28, total: 2650 },
    { category: 'Pricing', positive: 45, negative: 55, total: 1980 },
    { category: 'User Experience', positive: 81, negative: 19, total: 1560 },
    { category: 'Return Policy', positive: 68, negative: 32, total: 1240 }
  ]

  const recentFeedback = [
    {
      id: 1,
      customer: 'Sarah Johnson',
      rating: 5,
      comment: 'Absolutely love the new product line! The quality exceeded my expectations and the customer service was outstanding.',
      platform: 'Google Reviews',
      time: '2 hours ago',
      sentiment: 'positive'
    },
    {
      id: 2,
      customer: 'Mike Chen',
      rating: 2,
      comment: 'Delivery took way too long and the package was damaged. Customer support was slow to respond.',
      platform: 'Yelp',
      time: '4 hours ago',
      sentiment: 'negative'
    },
    {
      id: 3,
      customer: 'Emily Davis',
      rating: 4,
      comment: 'Good product overall, but the price point is a bit high compared to competitors.',
      platform: 'Facebook',
      time: '6 hours ago',
      sentiment: 'neutral'
    }
  ]

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Feedback by Category</h3>
        <div className="space-y-4">
          {feedbackCategories.map((category, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="p-4 border border-gray-200 rounded-lg"
            >
              <div className="flex items-center justify-between mb-3">
                <h4 className="font-medium text-gray-900">{category.category}</h4>
                <span className="text-sm text-gray-500">{category.total} reviews</span>
              </div>
              <div className="flex items-center space-x-4">
                <div className="flex-1">
                  <div className="flex items-center justify-between text-sm mb-1">
                    <span className="text-green-600">Positive: {category.positive}%</span>
                    <span className="text-red-600">Negative: {category.negative}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2 flex">
                    <div 
                      className="bg-green-500 h-2 rounded-l-full" 
                      style={{ width: `${category.positive}%` }}
                    ></div>
                    <div 
                      className="bg-red-500 h-2 rounded-r-full" 
                      style={{ width: `${category.negative}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Feedback</h3>
        <div className="space-y-4">
          {recentFeedback.map((feedback) => (
            <motion.div
              key={feedback.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="p-4 border border-gray-200 rounded-lg"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center space-x-3">
                  <div className={`w-3 h-3 rounded-full ${
                    feedback.sentiment === 'positive' ? 'bg-green-500' :
                    feedback.sentiment === 'negative' ? 'bg-red-500' : 'bg-yellow-500'
                  }`}></div>
                  <div>
                    <h4 className="font-medium text-gray-900">{feedback.customer}</h4>
                    <div className="flex items-center space-x-2">
                      <div className="flex items-center">
                        {[...Array(5)].map((_, i) => (
                          <Star
                            key={i}
                            className={`w-4 h-4 ${
                              i < feedback.rating ? 'text-yellow-500 fill-current' : 'text-gray-300'
                            }`}
                          />
                        ))}
                      </div>
                      <span className="text-sm text-gray-500">• {feedback.platform}</span>
                    </div>
                  </div>
                </div>
                <span className="text-sm text-gray-500">{feedback.time}</span>
              </div>
              <p className="text-gray-700">{feedback.comment}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  )
}

// Social Listening Component
const SocialListening: React.FC = () => (
  <div className="space-y-6">
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Brand Mentions</h3>
        <div className="space-y-4">
          {[
            { platform: 'Twitter/X', mentions: 1240, sentiment: 72, trend: '+15%' },
            { platform: 'Instagram', mentions: 890, sentiment: 85, trend: '+23%' },
            { platform: 'Facebook', mentions: 650, sentiment: 68, trend: '+8%' },
            { platform: 'TikTok', mentions: 450, sentiment: 91, trend: '+45%' },
            { platform: 'LinkedIn', mentions: 230, sentiment: 78, trend: '+12%' }
          ].map((platform, index) => (
            <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div>
                <h4 className="font-medium text-gray-900">{platform.platform}</h4>
                <p className="text-sm text-gray-600">{platform.mentions} mentions</p>
              </div>
              <div className="text-right">
                <p className="font-medium text-green-600">{platform.sentiment}% positive</p>
                <p className="text-sm text-blue-600">{platform.trend}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Trending Hashtags</h3>
        <div className="space-y-3">
          {[
            { hashtag: '#BestService2024', uses: 2340, growth: '+180%' },
            { hashtag: '#CustomerFirst', uses: 1890, growth: '+95%' },
            { hashtag: '#QualityProducts', uses: 1560, growth: '+67%' },
            { hashtag: '#FastDelivery', uses: 1240, growth: '+45%' },
            { hashtag: '#Recommended', uses: 980, growth: '+38%' }
          ].map((tag, index) => (
            <div key={index} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
              <div>
                <h4 className="font-medium text-blue-600">{tag.hashtag}</h4>
                <p className="text-sm text-gray-600">{tag.uses.toLocaleString()} uses</p>
              </div>
              <span className="text-sm font-medium text-green-600">{tag.growth}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  </div>
)

// AI Insights Component
const AIInsights: React.FC = () => (
  <div className="space-y-6">
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">AI-Generated Insights</h3>
      <div className="space-y-4">
        {[
          {
            type: 'opportunity',
            title: 'Customer service excellence driving loyalty',
            description: 'Analysis shows 85% positive sentiment for customer service correlates with 34% higher repeat purchase rates',
            impact: 'High',
            confidence: 94
          },
          {
            type: 'warning',
            title: 'Pricing concerns in competitive segments',
            description: 'Negative sentiment around pricing increased 23% in electronics category, potential market share risk',
            impact: 'Medium',
            confidence: 87
          },
          {
            type: 'trend',
            title: 'Social media engagement accelerating',
            description: 'TikTok mentions up 45% with 91% positive sentiment, opportunity for increased social presence',
            impact: 'Medium',
            confidence: 78
          }
        ].map((insight, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="p-4 border border-gray-200 rounded-lg"
          >
            <div className="flex items-start space-x-3">
              <div className={`w-3 h-3 rounded-full mt-2 ${
                insight.type === 'opportunity' ? 'bg-green-500' :
                insight.type === 'warning' ? 'bg-red-500' : 'bg-blue-500'
              }`}></div>
              <div className="flex-1">
                <h4 className="font-semibold text-gray-900 mb-2">{insight.title}</h4>
                <p className="text-gray-700 mb-3">{insight.description}</p>
                <div className="flex items-center space-x-4 text-sm">
                  <span className={`px-2 py-1 rounded-full font-medium ${
                    insight.impact === 'High' ? 'bg-red-100 text-red-700' :
                    insight.impact === 'Medium' ? 'bg-yellow-100 text-yellow-700' :
                    'bg-green-100 text-green-700'
                  }`}>
                    {insight.impact} Impact
                  </span>
                  <span className="text-blue-600">{insight.confidence}% confidence</span>
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  </div>
)

// Trend Analysis Component
const TrendAnalysis: React.FC = () => (
  <div className="space-y-6">
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Sentiment Trends (30 Days)</h3>
        <div className="space-y-4">
          {[
            { week: 'Week 1', positive: 82, neutral: 12, negative: 6 },
            { week: 'Week 2', positive: 85, neutral: 10, negative: 5 },
            { week: 'Week 3', positive: 88, neutral: 8, negative: 4 },
            { week: 'Week 4', positive: 87, neutral: 9, negative: 4 }
          ].map((week, index) => (
            <div key={index} className="p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium text-gray-900">{week.week}</span>
                <span className="text-sm text-gray-600">
                  {week.positive + week.neutral + week.negative}% total
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2 flex">
                <div 
                  className="bg-green-500 h-2 rounded-l-full" 
                  style={{ width: `${week.positive}%` }}
                ></div>
                <div 
                  className="bg-yellow-500 h-2" 
                  style={{ width: `${week.neutral}%` }}
                ></div>
                <div 
                  className="bg-red-500 h-2 rounded-r-full" 
                  style={{ width: `${week.negative}%` }}
                ></div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Emerging Topics</h3>
        <div className="space-y-3">
          {[
            { topic: 'Sustainability initiatives', mentions: 450, growth: '+120%', sentiment: 'positive' },
            { topic: 'Mobile app updates', mentions: 380, growth: '+85%', sentiment: 'mixed' },
            { topic: 'New product launches', mentions: 320, growth: '+200%', sentiment: 'positive' },
            { topic: 'Shipping improvements', mentions: 290, growth: '+67%', sentiment: 'positive' },
            { topic: 'Payment options', mentions: 210, growth: '+45%', sentiment: 'neutral' }
          ].map((topic, index) => (
            <div key={index} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
              <div className="flex items-center space-x-3">
                <div className={`w-3 h-3 rounded-full ${
                  topic.sentiment === 'positive' ? 'bg-green-500' :
                  topic.sentiment === 'mixed' ? 'bg-yellow-500' : 'bg-gray-500'
                }`}></div>
                <div>
                  <h4 className="font-medium text-gray-900">{topic.topic}</h4>
                  <p className="text-sm text-gray-600">{topic.mentions} mentions</p>
                </div>
              </div>
              <span className="text-sm font-medium text-green-600">{topic.growth}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  </div>
)
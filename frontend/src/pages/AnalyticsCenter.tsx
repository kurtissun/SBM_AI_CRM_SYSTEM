import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  BarChart3, TrendingUp, Users, DollarSign, Brain, Zap, Target, Eye,
  Calendar, Filter, Download, RefreshCw, Settings, Sparkles, 
  ChevronDown, Play, Pause, ArrowUpRight, ArrowDownRight, AlertTriangle,
  Clock, Star, Award, Lightbulb, Activity, PieChart, LineChart,
  Database, Globe, Cpu, Bot
} from 'lucide-react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'react-hot-toast'
import { api } from '@/lib/api'
import { useTranslation } from '@/contexts/TranslationContext'

export const AnalyticsCenter: React.FC = () => {
  const { t } = useTranslation()
  const [selectedView, setSelectedView] = useState('overview')
  const [selectedTimeRange, setSelectedTimeRange] = useState('30d')
  const [selectedMetrics, setSelectedMetrics] = useState(['revenue', 'clv', 'churn'])
  const [isAutoRefresh, setIsAutoRefresh] = useState(true)
  const queryClient = useQueryClient()

  // Fetch analytics data
  const { data: analyticsData, refetch: refetchAnalytics } = useQuery({
    queryKey: ['analytics-data', selectedTimeRange],
    queryFn: () => api.get(`/analytics/comprehensive?range=${selectedTimeRange}`),
    refetchInterval: isAutoRefresh ? 30000 : false
  })

  const { data: customerStats } = useQuery({
    queryKey: ['customer-stats'],
    queryFn: () => api.get('/customers/stats'),
  })

  // AI Analytics Generation
  const generateInsights = useMutation({
    mutationFn: () => api.post('/analytics/generate-insights', { metrics: selectedMetrics, timeRange: selectedTimeRange }),
    onSuccess: () => {
      toast.success('AI insights generated successfully!')
      queryClient.invalidateQueries({ queryKey: ['analytics-data'] })
    },
    onError: () => {
      toast.error('Failed to generate AI insights')
    }
  })

  const views = [
    { id: 'overview', label: t('analytics.overview'), icon: BarChart3 },
    { id: 'predictions', label: t('analytics.predictions'), icon: Brain },
    { id: 'insights', label: t('analytics.insights'), icon: Lightbulb },
    { id: 'performance', label: t('analytics.performance'), icon: TrendingUp }
  ]

  const timeRanges = [
    { value: '7d', label: 'Last 7 days' },
    { value: '30d', label: 'Last 30 days' },
    { value: '90d', label: 'Last 3 months' },
    { value: '1y', label: 'Last year' }
  ]

  const metrics = [
    { id: 'revenue', label: 'Revenue Analytics', color: 'blue' },
    { id: 'clv', label: 'Customer Lifetime Value', color: 'green' },
    { id: 'churn', label: 'Churn Analysis', color: 'red' },
    { id: 'engagement', label: 'Engagement Metrics', color: 'purple' },
    { id: 'conversion', label: 'Conversion Rates', color: 'orange' }
  ]

  const toggleMetric = (metricId: string) => {
    setSelectedMetrics(prev =>
      prev.includes(metricId)
        ? prev.filter(id => id !== metricId)
        : [...prev, metricId]
    )
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{t('analytics.title')}</h1>
          <p className="text-gray-600 mt-1">{t('analytics.subtitle')}</p>
        </div>
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2">
            <select
              value={selectedTimeRange}
              onChange={(e) => setSelectedTimeRange(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {timeRanges.map(range => (
                <option key={range.value} value={range.value}>{range.label}</option>
              ))}
            </select>
            <button
              onClick={() => setIsAutoRefresh(!isAutoRefresh)}
              className={`px-3 py-2 rounded-lg flex items-center ${
                isAutoRefresh 
                  ? 'bg-green-100 text-green-700 border border-green-300' 
                  : 'bg-gray-100 text-gray-600 border border-gray-300'
              }`}
            >
              {isAutoRefresh ? <Play className="w-4 h-4 mr-1" /> : <Pause className="w-4 h-4 mr-1" />}
{t('analytics.autoRefresh')}
            </button>
          </div>
          <button
            onClick={() => generateInsights.mutate()}
            disabled={generateInsights.isPending}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 flex items-center disabled:opacity-50"
          >
            {generateInsights.isPending ? (
              <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
            ) : (
              <Sparkles className="w-4 h-4 mr-2" />
            )}
{generateInsights.isPending ? t('analytics.generating') : t('analytics.generateInsights')}
          </button>
          <button className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center">
            <Download className="w-4 h-4 mr-2" />
{t('analytics.export')}
          </button>
        </div>
      </div>

      {/* AI Status Banner */}
      <div className="bg-gradient-to-r from-purple-600 via-blue-600 to-green-600 rounded-xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center">
              <Brain className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-lg font-semibold">{t('analytics.aiEngine')}</h3>
              <p className="text-white/80">
                {t('analytics.aiModels')} • {t('analytics.realTime')} • {t('analytics.creative')}
              </p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-2xl font-bold">98.7%</p>
            <p className="text-white/80 text-sm">{t('analytics.accuracy')}</p>
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
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
              }`}
            >
              <view.icon className="w-4 h-4 mr-2" />
              {view.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Dynamic Content Based on Selected View */}
      {selectedView === 'overview' && (
        <AnalyticsOverview 
          data={analyticsData} 
          selectedMetrics={selectedMetrics}
          onToggleMetric={toggleMetric}
          metrics={metrics}
        />
      )}

      {selectedView === 'predictions' && (
        <AIPredictions 
          data={analyticsData}
          customerStats={customerStats}
        />
      )}

      {selectedView === 'insights' && (
        <CreativeInsights 
          data={analyticsData}
          onRefresh={() => refetchAnalytics()}
        />
      )}

      {selectedView === 'performance' && (
        <PerformanceAnalytics 
          data={analyticsData}
          selectedMetrics={selectedMetrics}
        />
      )}
    </div>
  )
}

// 📊 Analytics Overview Component
const AnalyticsOverview: React.FC<{ 
  data: any, 
  selectedMetrics: string[],
  onToggleMetric: (id: string) => void,
  metrics: any[]
}> = ({ data, selectedMetrics, onToggleMetric, metrics }) => {
  const overviewStats = [
    { 
      id: 'predictive', 
      label: 'Predictive Accuracy', 
      value: '94.2%', 
      change: '+2.1%', 
      trend: 'up',
      icon: Target,
      color: 'blue'
    },
    { 
      id: 'clv', 
      label: 'Avg CLV Prediction', 
      value: '¥12.8K', 
      change: '+8.3%', 
      trend: 'up',
      icon: DollarSign,
      color: 'green'
    },
    { 
      id: 'churn', 
      label: 'Churn Risk Score', 
      value: '7.8%', 
      change: '-1.2%', 
      trend: 'down',
      icon: AlertTriangle,
      color: 'red'
    },
    { 
      id: 'revenue', 
      label: 'Revenue Forecast', 
      value: '¥2.3M', 
      change: '+12.4%', 
      trend: 'up',
      icon: TrendingUp,
      color: 'purple'
    }
  ]

  return (
    <div className="space-y-6">
      {/* Metric Selector */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Active Analytics Metrics</h3>
        <div className="flex flex-wrap gap-3">
          {metrics.map((metric) => (
            <button
              key={metric.id}
              onClick={() => onToggleMetric(metric.id)}
              className={`px-4 py-2 rounded-lg border-2 transition-colors ${
                selectedMetrics.includes(metric.id)
                  ? `border-${metric.color}-500 bg-${metric.color}-50 text-${metric.color}-700`
                  : 'border-gray-200 hover:border-gray-300 text-gray-600'
              }`}
            >
              {metric.label}
            </button>
          ))}
        </div>
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {overviewStats.map((stat) => (
          <motion.div
            key={stat.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow"
          >
            <div className="flex items-center justify-between mb-4">
              <div className={`w-12 h-12 bg-${stat.color}-100 rounded-lg flex items-center justify-center`}>
                <stat.icon className={`w-6 h-6 text-${stat.color}-600`} />
              </div>
              <div className={`flex items-center text-sm ${
                stat.trend === 'up' ? 'text-green-600' : 'text-red-600'
              }`}>
                {stat.trend === 'up' ? <ArrowUpRight className="w-4 h-4" /> : <ArrowDownRight className="w-4 h-4" />}
                {stat.change}
              </div>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-600">{stat.label}</p>
              <p className="text-3xl font-bold text-gray-900">{stat.value}</p>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Interactive Analytics Dashboard */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-gray-900">Interactive Analytics Dashboard</h3>
          <div className="flex items-center space-x-2">
            <button className="flex items-center px-3 py-2 text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-lg">
              <PieChart className="w-4 h-4 mr-2" />
              Chart View
            </button>
            <button className="flex items-center px-3 py-2 text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-lg">
              <LineChart className="w-4 h-4 mr-2" />
              Trend View
            </button>
          </div>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-xl p-6 border border-blue-200">
            <h4 className="font-semibold text-gray-900 mb-4">Real-time Revenue Analytics</h4>
            <div className="space-y-4">
              <div className="flex justify-between">
                <span className="text-gray-600">Today's Revenue</span>
                <span className="font-bold text-blue-600">¥187,450</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Weekly Target</span>
                <span className="font-bold text-green-600">¥1,200,000</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Progress</span>
                <span className="font-bold text-purple-600">73.2%</span>
              </div>
            </div>
          </div>

          <div className="bg-gradient-to-br from-green-50 to-blue-50 rounded-xl p-6 border border-green-200">
            <h4 className="font-semibold text-gray-900 mb-4">Customer Intelligence</h4>
            <div className="space-y-4">
              <div className="flex justify-between">
                <span className="text-gray-600">Active Customers</span>
                <span className="font-bold text-green-600">2,847</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">New This Week</span>
                <span className="font-bold text-blue-600">+142</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Engagement Score</span>
                <span className="font-bold text-purple-600">8.7/10</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

// 🤖 AI Predictions Component
const AIPredictions: React.FC<{ data: any, customerStats: any }> = ({ data, customerStats }) => {
  const [selectedModel, setSelectedModel] = useState('ensemble')
  
  const aiModels = [
    { id: 'ensemble', label: 'Ensemble Model (22 AI engines)', accuracy: '98.7%' },
    { id: 'neural', label: 'Deep Neural Network', accuracy: '96.2%' },
    { id: 'forest', label: 'Random Forest', accuracy: '94.8%' },
    { id: 'gradient', label: 'Gradient Boosting', accuracy: '95.3%' }
  ]

  const predictions = [
    {
      type: 'Revenue Forecast',
      prediction: '¥2.8M next month',
      confidence: '94%',
      factors: ['Seasonal trends', 'Customer behavior', 'Market conditions'],
      icon: DollarSign,
      color: 'green'
    },
    {
      type: 'Churn Risk Alert',
      prediction: '23 customers at risk',
      confidence: '91%',
      factors: ['Low engagement', 'Payment delays', 'Support tickets'],
      icon: AlertTriangle,
      color: 'red'
    },
    {
      type: 'Growth Opportunity',
      prediction: '+34% VIP segment growth',
      confidence: '89%',
      factors: ['Premium preferences', 'Purchase patterns', 'Loyalty scores'],
      icon: TrendingUp,
      color: 'blue'
    }
  ]

  return (
    <div className="space-y-6">
      {/* AI Model Selector */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">AI Prediction Models</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {aiModels.map((model) => (
            <button
              key={model.id}
              onClick={() => setSelectedModel(model.id)}
              className={`p-4 rounded-lg border-2 transition-colors text-left ${
                selectedModel === model.id
                  ? 'border-purple-500 bg-purple-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center space-x-2 mb-2">
                <Cpu className="w-5 h-5 text-purple-600" />
                <span className="font-medium text-gray-900">{model.label}</span>
              </div>
              <div className="text-sm text-gray-600">Accuracy: {model.accuracy}</div>
            </button>
          ))}
        </div>
      </div>

      {/* AI Predictions Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {predictions.map((prediction, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: index * 0.1 }}
            className="bg-white rounded-xl shadow-sm border border-gray-200 p-6"
          >
            <div className="flex items-center space-x-3 mb-4">
              <div className={`w-10 h-10 bg-${prediction.color}-100 rounded-lg flex items-center justify-center`}>
                <prediction.icon className={`w-5 h-5 text-${prediction.color}-600`} />
              </div>
              <div>
                <h4 className="font-semibold text-gray-900">{prediction.type}</h4>
                <p className="text-sm text-gray-600">Confidence: {prediction.confidence}</p>
              </div>
            </div>
            
            <div className="mb-4">
              <p className="text-xl font-bold text-gray-900">{prediction.prediction}</p>
            </div>
            
            <div>
              <p className="text-sm font-medium text-gray-600 mb-2">Key Factors:</p>
              <div className="space-y-1">
                {prediction.factors.map((factor, i) => (
                  <div key={i} className="text-sm text-gray-600 flex items-center">
                    <div className="w-1.5 h-1.5 bg-gray-400 rounded-full mr-2"></div>
                    {factor}
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  )
}

// 💡 Creative Insights Component
const CreativeInsights: React.FC<{ data: any, onRefresh: () => void }> = ({ data, onRefresh }) => {
  const [selectedInsightType, setSelectedInsightType] = useState('all')
  
  const insightTypes = [
    { id: 'all', label: 'All Insights' },
    { id: 'opportunities', label: 'Opportunities' },
    { id: 'risks', label: 'Risk Alerts' },
    { id: 'patterns', label: 'Behavior Patterns' },
    { id: 'recommendations', label: 'AI Recommendations' }
  ]

  const creativeInsights = [
    {
      type: 'opportunities',
      title: 'Weekend Warriors Discovered!',
      description: 'Your weekend customers spend 43% more than weekday shoppers and prefer premium products. They\'re your hidden goldmine!',
      impact: 'High',
      actionable: 'Launch weekend-exclusive VIP experiences',
      icon: Star,
      gradient: 'from-yellow-400 to-orange-500'
    },
    {
      type: 'patterns',
      title: 'The "3-Purchase Rule"',
      description: 'Customers who make 3+ purchases within 30 days have a 89% chance of becoming long-term VIPs. It\'s like a loyalty magic number!',
      impact: 'Medium',
      actionable: 'Create 3-purchase milestone rewards',
      icon: Award,
      gradient: 'from-purple-400 to-pink-500'
    },
    {
      type: 'risks',
      title: 'Silent Customer Syndrome',
      description: 'Customers who don\'t engage with support in their first 60 days are 5x more likely to churn. Silence isn\'t golden here!',
      impact: 'High',
      actionable: 'Proactive outreach program for quiet customers',
      icon: AlertTriangle,
      gradient: 'from-red-400 to-pink-500'
    },
    {
      type: 'recommendations',
      title: 'AI-Powered Personalization Boost',
      description: 'Your AI suggests implementing dynamic pricing based on customer engagement scores. High-engagement customers show 67% price elasticity tolerance.',
      impact: 'Very High',
      actionable: 'Deploy smart pricing algorithm',
      icon: Brain,
      gradient: 'from-blue-400 to-purple-500'
    }
  ]

  const filteredInsights = selectedInsightType === 'all' 
    ? creativeInsights 
    : creativeInsights.filter(insight => insight.type === selectedInsightType)

  return (
    <div className="space-y-6">
      {/* Insight Type Filter */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Creative AI Insights</h3>
          <button
            onClick={onRefresh}
            className="flex items-center px-3 py-2 text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-lg"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh Insights
          </button>
        </div>
        <div className="flex flex-wrap gap-2">
          {insightTypes.map((type) => (
            <button
              key={type.id}
              onClick={() => setSelectedInsightType(type.id)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                selectedInsightType === type.id
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {type.label}
            </button>
          ))}
        </div>
      </div>

      {/* Creative Insights Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {filteredInsights.map((insight, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-lg transition-shadow"
          >
            <div className={`h-2 bg-gradient-to-r ${insight.gradient}`}></div>
            <div className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className={`w-10 h-10 bg-gradient-to-r ${insight.gradient} rounded-lg flex items-center justify-center`}>
                    <insight.icon className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <h4 className="font-bold text-gray-900">{insight.title}</h4>
                    <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${
                      insight.impact === 'Very High' ? 'bg-red-100 text-red-700' :
                      insight.impact === 'High' ? 'bg-orange-100 text-orange-700' :
                      'bg-blue-100 text-blue-700'
                    }`}>
                      {insight.impact} Impact
                    </span>
                  </div>
                </div>
              </div>
              
              <p className="text-gray-700 mb-4">{insight.description}</p>
              
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center space-x-2 mb-2">
                  <Lightbulb className="w-4 h-4 text-yellow-600" />
                  <span className="font-medium text-gray-900">Recommended Action:</span>
                </div>
                <p className="text-sm text-gray-700">{insight.actionable}</p>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  )
}

// 📈 Performance Analytics Component
const PerformanceAnalytics: React.FC<{ data: any, selectedMetrics: string[] }> = ({ data, selectedMetrics }) => {
  const performanceMetrics = [
    {
      metric: 'AI Model Performance',
      current: '98.7%',
      target: '95.0%',
      status: 'exceeding',
      trend: '+2.3%'
    },
    {
      metric: 'Prediction Accuracy',
      current: '94.2%',
      target: '90.0%',
      status: 'exceeding',
      trend: '+1.8%'
    },
    {
      metric: 'Data Processing Speed',
      current: '2.3s',
      target: '3.0s',
      status: 'exceeding',
      trend: '-0.4s'
    },
    {
      metric: 'Insight Generation Rate',
      current: '156/hr',
      target: '120/hr',
      status: 'exceeding',
      trend: '+23/hr'
    }
  ]

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-6">AI Analytics Performance Dashboard</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {performanceMetrics.map((metric, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.1 }}
              className="bg-gradient-to-br from-gray-50 to-white border border-gray-200 rounded-xl p-6"
            >
              <div className="flex items-center justify-between mb-3">
                <Activity className="w-6 h-6 text-blue-600" />
                <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                  metric.status === 'exceeding' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'
                }`}>
                  {metric.status}
                </span>
              </div>
              
              <div className="space-y-2">
                <h4 className="font-medium text-gray-900 text-sm">{metric.metric}</h4>
                <p className="text-2xl font-bold text-gray-900">{metric.current}</p>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-gray-600">Target: {metric.target}</span>
                  <span className="text-green-600 font-medium">{metric.trend}</span>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* System Health */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">System Health Monitor</h3>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="space-y-4">
            <h4 className="font-medium text-gray-900">AI Engine Status</h4>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Neural Networks</span>
                <div className="flex items-center">
                  <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                  <span className="text-sm font-medium">Optimal</span>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Data Processing</span>
                <div className="flex items-center">
                  <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                  <span className="text-sm font-medium">Optimal</span>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Prediction Models</span>
                <div className="flex items-center">
                  <div className="w-2 h-2 bg-yellow-500 rounded-full mr-2"></div>
                  <span className="text-sm font-medium">Good</span>
                </div>
              </div>
            </div>
          </div>

          <div className="space-y-4">
            <h4 className="font-medium text-gray-900">Resource Usage</h4>
            <div className="space-y-3">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">CPU Usage</span>
                  <span className="font-medium">67%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-blue-600 h-2 rounded-full" style={{ width: '67%' }}></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">Memory</span>
                  <span className="font-medium">73%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-green-600 h-2 rounded-full" style={{ width: '73%' }}></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">Storage</span>
                  <span className="font-medium">45%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-purple-600 h-2 rounded-full" style={{ width: '45%' }}></div>
                </div>
              </div>
            </div>
          </div>

          <div className="space-y-4">
            <h4 className="font-medium text-gray-900">Data Insights</h4>
            <div className="space-y-3">
              <div className="text-center">
                <p className="text-2xl font-bold text-blue-600">2,847</p>
                <p className="text-sm text-gray-600">Customers Analyzed</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-green-600">156</p>
                <p className="text-sm text-gray-600">Insights Generated</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-purple-600">22</p>
                <p className="text-sm text-gray-600">AI Models Active</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
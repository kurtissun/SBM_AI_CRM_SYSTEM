import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  ArrowLeft, Brain, Target, Users, DollarSign, TrendingUp, BarChart3, 
  Eye, Zap, Sparkles, RefreshCw, Download, Settings, ChevronDown,
  Calendar, Clock, MapPin, Smartphone, Monitor, Tablet, Globe,
  Heart, Star, Share2, MessageCircle, ShoppingCart, CreditCard,
  AlertTriangle, CheckCircle, Info, Lightbulb, Filter, Search
} from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from '@/contexts/TranslationContext'
import { toast } from 'react-hot-toast'
import { Line, Bar, Doughnut, Radar } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  RadialLinearScale,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  RadialLinearScale,
  Title,
  Tooltip,
  Legend
)

export const CampaignIntelligence: React.FC = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [selectedTimeframe, setSelectedTimeframe] = useState('30d')
  const [selectedMetric, setSelectedMetric] = useState('roi')
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [selectedModel, setSelectedModel] = useState('advanced')

  const timeframes = [
    { id: '7d', label: t('time.last7days') },
    { id: '30d', label: t('time.last30days') },
    { id: '90d', label: t('time.last90days') },
    { id: '365d', label: t('time.last365days') }
  ]

  const aiModels = [
    { id: 'basic', label: 'Basic AI', accuracy: '85%', speed: 'Fast' },
    { id: 'advanced', label: 'Advanced AI', accuracy: '94%', speed: 'Medium' },
    { id: 'enterprise', label: 'Enterprise AI', accuracy: '97%', speed: 'Slow' }
  ]

  const metricTypes = [
    { id: 'roi', label: 'ROI Analysis', icon: DollarSign, color: 'green' },
    { id: 'audience', label: 'Audience Insights', icon: Users, color: 'blue' },
    { id: 'creative', label: 'Creative Performance', icon: Eye, color: 'purple' },
    { id: 'attribution', label: 'Attribution Analysis', icon: Target, color: 'orange' }
  ]

  // Generate dynamic data based on timeframe
  const generateTimeframedData = (timeframe: string) => {
    const dataPoints = {
      '7d': { labels: ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Day 7'], points: 7 },
      '30d': { labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'], points: 4 },
      '90d': { labels: ['Month 1', 'Month 2', 'Month 3'], points: 3 },
      '365d': { labels: ['Q1', 'Q2', 'Q3', 'Q4'], points: 4 }
    }
    
    const config = dataPoints[timeframe as keyof typeof dataPoints] || dataPoints['30d']
    
    // Generate different data patterns based on timeframe
    const generateROIData = () => {
      const baseROI = 120
      const growth = timeframe === '365d' ? 40 : timeframe === '90d' ? 25 : timeframe === '30d' ? 15 : 8
      return Array.from({ length: config.points }, (_, i) => 
        Math.round(baseROI + (growth * i) + (Math.random() * 10 - 5))
      )
    }
    
    const generateAudienceData = () => {
      const multiplier = timeframe === '365d' ? 1.5 : timeframe === '90d' ? 1.2 : 1.0
      return [
        Math.round(78 * multiplier),
        Math.round(85 * multiplier),
        Math.round(92 * multiplier),
        Math.round(67 * multiplier),
        Math.round(54 * multiplier)
      ]
    }
    
    const generateMetrics = () => {
      const timeMultiplier = {
        '7d': 0.3,
        '30d': 1.0,
        '90d': 2.8,
        '365d': 12.5
      }[timeframe] || 1.0
      
      return {
        roi: Math.round((120 + (timeframe === '365d' ? 40 : timeframe === '90d' ? 25 : 15)) * 10) / 10,
        impressions: Math.round(2.8 * timeMultiplier * 1000000),
        ctr: Math.round((3.2 + (timeframe === '90d' ? 1.0 : timeframe === '365d' ? 1.8 : 0.6)) * 10) / 10,
        reach: Math.round(89.3 * timeMultiplier * 1000),
        growth: {
          roi: timeframe === '7d' ? 5.2 : timeframe === '30d' ? 23.4 : timeframe === '90d' ? 31.7 : 45.8,
          impressions: timeframe === '7d' ? 8.1 : timeframe === '30d' ? 15.2 : timeframe === '90d' ? 28.4 : 52.3,
          ctr: timeframe === '7d' ? 3.1 : timeframe === '30d' ? 8.7 : timeframe === '90d' ? 15.9 : 23.1,
          reach: timeframe === '7d' ? 6.8 : timeframe === '30d' ? 12.1 : timeframe === '90d' ? 19.7 : 31.4
        }
      }
    }
    
    return { config, generateROIData, generateAudienceData, generateMetrics }
  }
  
  const { config, generateROIData, generateAudienceData, generateMetrics } = generateTimeframedData(selectedTimeframe)
  const metrics = generateMetrics()
  
  const roiTrendData = {
    labels: config.labels,
    datasets: [
      {
        label: 'ROI %',
        data: generateROIData(),
        borderColor: 'rgb(34, 197, 94)',
        backgroundColor: 'rgba(34, 197, 94, 0.1)',
        tension: 0.4,
      },
      {
        label: 'Target ROI',
        data: Array(config.points).fill(100),
        borderColor: 'rgb(156, 163, 175)',
        backgroundColor: 'rgba(156, 163, 175, 0.1)',
        borderDash: [5, 5],
      }
    ],
  }

  const audienceData = {
    labels: ['18-24', '25-34', '35-44', '45-54', '55+'],
    datasets: [
      {
        label: 'Engagement Rate',
        data: generateAudienceData(),
        backgroundColor: [
          'rgba(59, 130, 246, 0.8)',
          'rgba(16, 185, 129, 0.8)',
          'rgba(245, 158, 11, 0.8)',
          'rgba(239, 68, 68, 0.8)',
          'rgba(139, 92, 246, 0.8)',
        ],
      },
    ],
  }

  const deviceData = {
    labels: ['Mobile', 'Desktop', 'Tablet'],
    datasets: [
      {
        data: [68, 24, 8],
        backgroundColor: [
          'rgba(59, 130, 246, 0.8)',
          'rgba(16, 185, 129, 0.8)',
          'rgba(245, 158, 11, 0.8)',
        ],
      },
    ],
  }

  const performanceRadarData = {
    labels: ['Reach', 'Engagement', 'Conversions', 'Brand Lift', 'Cost Efficiency', 'Quality Score'],
    datasets: [
      {
        label: 'Current Campaign',
        data: [85, 92, 78, 88, 76, 94],
        backgroundColor: 'rgba(59, 130, 246, 0.2)',
        borderColor: 'rgba(59, 130, 246, 1)',
        pointBackgroundColor: 'rgba(59, 130, 246, 1)',
      },
      {
        label: 'Industry Average',
        data: [70, 65, 60, 55, 65, 70],
        backgroundColor: 'rgba(156, 163, 175, 0.2)',
        borderColor: 'rgba(156, 163, 175, 1)',
        pointBackgroundColor: 'rgba(156, 163, 175, 1)',
      },
    ],
  }

  const intelligenceInsights = [
    {
      id: 1,
      type: 'opportunity',
      priority: 'high',
      title: 'Weekend Performance Surge',
      description: 'Your campaigns show 34% higher conversion rates on weekends. Consider increasing weekend budget allocation.',
      impact: '+¥180K potential revenue',
      confidence: 94,
      action: 'Optimize Budget Schedule'
    },
    {
      id: 2,
      type: 'warning',
      priority: 'medium',
      title: 'Creative Fatigue Detected',
      description: 'Ad creative performance declining by 12% over past 2 weeks. Fresh creatives recommended.',
      impact: 'Prevent 8% CTR drop',
      confidence: 87,
      action: 'Generate New Creatives'
    },
    {
      id: 3,
      type: 'success',
      priority: 'low',
      title: 'Mobile Optimization Success',
      description: 'Mobile campaigns outperforming desktop by 23%. Mobile-first strategy is working well.',
      impact: '+15% overall performance',
      confidence: 91,
      action: 'Continue Current Strategy'
    },
    {
      id: 4,
      type: 'info',
      priority: 'medium',
      title: 'Audience Expansion Opportunity',
      description: 'Lookalike audiences showing 89% similarity to your best customers. Ready for testing.',
      impact: '+47K potential reach',
      confidence: 89,
      action: 'Test Lookalike Audiences'
    }
  ]

  const runAIAnalysis = () => {
    setIsAnalyzing(true)
    toast.success('Running advanced AI analysis...')
    
    setTimeout(() => {
      setIsAnalyzing(false)
      toast.success('AI analysis completed! New insights available.')
    }, 3000)
  }

  const exportReport = () => {
    toast.success('Generating intelligence report...')
    
    setTimeout(() => {
      const blob = new Blob([`Campaign Intelligence Report - ${new Date().toLocaleDateString()}\n\nGenerated by SBM AI Intelligence Engine`], { type: 'text/plain' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `campaign-intelligence-${new Date().toISOString().split('T')[0]}.pdf`
      a.click()
      window.URL.revokeObjectURL(url)
      toast.success('Intelligence report exported successfully!')
    }, 2000)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => navigate('/campaigns')}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <ArrowLeft className="w-5 h-5 text-gray-600" />
            </button>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Campaign Intelligence Center</h1>
              <p className="text-gray-600 mt-1">Advanced AI-powered campaign analysis and optimization</p>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <button
              onClick={runAIAnalysis}
              disabled={isAnalyzing}
              className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isAnalyzing ? (
                <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <Brain className="w-4 h-4 mr-2" />
              )}
              {isAnalyzing ? 'Analyzing...' : 'Run AI Analysis'}
            </button>
            <button
              onClick={exportReport}
              className="flex items-center px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
            >
              <Download className="w-4 h-4 mr-2" />
              Export Report
            </button>
          </div>
        </div>
      </div>

      {/* AI Status Banner */}
      <div className="bg-gradient-to-r from-blue-600 via-purple-600 to-green-600 text-white px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center">
              <Brain className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-xl font-bold">AI Intelligence Engine Active</h2>
              <p className="text-white/90">22 AI models analyzing your campaign performance in real-time</p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-2xl font-bold">97.3%</p>
            <p className="text-white/80 text-sm">Prediction Accuracy</p>
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">AI Model</label>
              <select
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {aiModels.map(model => (
                  <option key={model.id} value={model.id}>
                    {model.label} - {model.accuracy}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Timeframe</label>
              <select
                value={selectedTimeframe}
                onChange={(e) => setSelectedTimeframe(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {timeframes.map(timeframe => (
                  <option key={timeframe.id} value={timeframe.id}>
                    {timeframe.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            {metricTypes.map((metric) => (
              <button
                key={metric.id}
                onClick={() => setSelectedMetric(metric.id)}
                className={`flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  selectedMetric === metric.id
                    ? `bg-${metric.color}-600 text-white`
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                }`}
              >
                <metric.icon className="w-4 h-4 mr-1" />
                {metric.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="p-6 space-y-6">
        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <DollarSign className="w-6 h-6 text-green-600" />
              </div>
              <span className="text-green-600 text-sm font-medium">+{metrics.growth.roi}%</span>
            </div>
            <h3 className="text-2xl font-bold text-gray-900">{metrics.roi}%</h3>
            <p className="text-gray-600 text-sm">Average ROI</p>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <Eye className="w-6 h-6 text-blue-600" />
              </div>
              <span className="text-blue-600 text-sm font-medium">+{metrics.growth.impressions}%</span>
            </div>
            <h3 className="text-2xl font-bold text-gray-900">{(metrics.impressions / 1000000).toFixed(1)}M</h3>
            <p className="text-gray-600 text-sm">Total Impressions</p>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                <Target className="w-6 h-6 text-purple-600" />
              </div>
              <span className="text-purple-600 text-sm font-medium">+{metrics.growth.ctr}%</span>
            </div>
            <h3 className="text-2xl font-bold text-gray-900">{metrics.ctr}%</h3>
            <p className="text-gray-600 text-sm">Click-through Rate</p>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
                <Users className="w-6 h-6 text-orange-600" />
              </div>
              <span className="text-orange-600 text-sm font-medium">+{metrics.growth.reach}%</span>
            </div>
            <h3 className="text-2xl font-bold text-gray-900">{(metrics.reach / 1000).toFixed(1)}K</h3>
            <p className="text-gray-600 text-sm">Unique Reach</p>
          </div>
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* ROI Trend */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-gray-900">ROI Performance Trend</h3>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                <span className="text-sm text-gray-600">Above Target</span>
              </div>
            </div>
            <div className="h-64">
              <Line data={roiTrendData} options={{ responsive: true, maintainAspectRatio: false }} />
            </div>
          </div>

          {/* Audience Engagement */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-gray-900">Audience Engagement by Age</h3>
              <button className="text-blue-600 text-sm hover:text-blue-700">View Details</button>
            </div>
            <div className="h-64">
              <Bar data={audienceData} options={{ responsive: true, maintainAspectRatio: false }} />
            </div>
          </div>

          {/* Device Distribution */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-gray-900">Device Distribution</h3>
              <div className="flex items-center space-x-2">
                <Smartphone className="w-4 h-4 text-blue-600" />
                <span className="text-sm text-gray-600">Mobile Leading</span>
              </div>
            </div>
            <div className="h-64">
              <Doughnut data={deviceData} options={{ responsive: true, maintainAspectRatio: false }} />
            </div>
          </div>

          {/* Performance Radar */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-gray-900">Overall Performance Score</h3>
              <div className="text-right">
                <div className="text-2xl font-bold text-green-600">8.5/10</div>
                <div className="text-sm text-gray-600">Excellent</div>
              </div>
            </div>
            <div className="h-64">
              <Radar data={performanceRadarData} options={{ responsive: true, maintainAspectRatio: false }} />
            </div>
          </div>
        </div>

        {/* AI Insights */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-blue-500 rounded-lg flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">AI Intelligence Insights</h3>
                <p className="text-sm text-gray-600">Powered by 22 AI models analyzing your campaign data</p>
              </div>
            </div>
            <button className="text-blue-600 text-sm hover:text-blue-700">View All Insights</button>
          </div>

          <div className="space-y-4">
            {intelligenceInsights.map((insight) => (
              <div
                key={insight.id}
                className={`p-4 rounded-lg border-l-4 ${
                  insight.type === 'opportunity' ? 'bg-green-50 border-green-400' :
                  insight.type === 'warning' ? 'bg-yellow-50 border-yellow-400' :
                  insight.type === 'success' ? 'bg-blue-50 border-blue-400' :
                  'bg-gray-50 border-gray-400'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-3">
                    <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                      insight.type === 'opportunity' ? 'bg-green-100 text-green-600' :
                      insight.type === 'warning' ? 'bg-yellow-100 text-yellow-600' :
                      insight.type === 'success' ? 'bg-blue-100 text-blue-600' :
                      'bg-gray-100 text-gray-600'
                    }`}>
                      {insight.type === 'opportunity' ? <Lightbulb className="w-4 h-4" /> :
                       insight.type === 'warning' ? <AlertTriangle className="w-4 h-4" /> :
                       insight.type === 'success' ? <CheckCircle className="w-4 h-4" /> :
                       <Info className="w-4 h-4" />}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-1">
                        <h4 className="font-semibold text-gray-900">{insight.title}</h4>
                        <span className={`px-2 py-0.5 text-xs rounded-full ${
                          insight.priority === 'high' ? 'bg-red-100 text-red-700' :
                          insight.priority === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                          'bg-gray-100 text-gray-700'
                        }`}>
                          {insight.priority} priority
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 mb-2">{insight.description}</p>
                      <div className="flex items-center space-x-4 text-xs text-gray-500">
                        <span>Impact: {insight.impact}</span>
                        <span>Confidence: {insight.confidence}%</span>
                      </div>
                    </div>
                  </div>
                  <button className="px-3 py-1 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 ml-4">
                    {insight.action}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Optimization Recommendations */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-6 border border-green-200">
            <div className="flex items-center space-x-3 mb-4">
              <div className="w-10 h-10 bg-green-500 rounded-lg flex items-center justify-center">
                <TrendingUp className="w-5 h-5 text-white" />
              </div>
              <div>
                <h4 className="font-semibold text-gray-900">Budget Optimization</h4>
                <p className="text-sm text-gray-600">Maximize ROI potential</p>
              </div>
            </div>
            <p className="text-sm text-gray-600 mb-4">
              Reallocate 15% of budget from underperforming segments to high-ROI audiences for +23% revenue boost.
            </p>
            <button className="w-full py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm font-medium">
              Apply Optimization
            </button>
          </div>

          <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-6 border border-blue-200">
            <div className="flex items-center space-x-3 mb-4">
              <div className="w-10 h-10 bg-blue-500 rounded-lg flex items-center justify-center">
                <Users className="w-5 h-5 text-white" />
              </div>
              <div>
                <h4 className="font-semibold text-gray-900">Audience Expansion</h4>
                <p className="text-sm text-gray-600">Reach new customers</p>
              </div>
            </div>
            <p className="text-sm text-gray-600 mb-4">
              3 high-potential lookalike audiences identified. Estimated +47K quality reach with 89% similarity score.
            </p>
            <button className="w-full py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm font-medium">
              Test Audiences
            </button>
          </div>

          <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-6 border border-purple-200">
            <div className="flex items-center space-x-3 mb-4">
              <div className="w-10 h-10 bg-purple-500 rounded-lg flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <div>
                <h4 className="font-semibold text-gray-900">Creative Refresh</h4>
                <p className="text-sm text-gray-600">Combat ad fatigue</p>
              </div>
            </div>
            <p className="text-sm text-gray-600 mb-4">
              Current creatives showing 12% performance decline. AI can generate 5 new high-performing variants.
            </p>
            <button className="w-full py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 text-sm font-medium">
              Generate Creatives
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default CampaignIntelligence
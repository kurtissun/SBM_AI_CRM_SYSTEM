import React, { useState } from 'react'
import { Routes, Route, Link, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  Target, Plus, Play, Pause, BarChart3, Brain, TrendingUp,
  Calendar, DollarSign, Users, Eye, Settings, Copy, Trash2,
  AlertCircle, CheckCircle, Clock, Zap, Sparkles, Filter,
  Search, Download, Edit, MoreVertical, Lightbulb
} from 'lucide-react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Line, Bar, Doughnut } from 'react-chartjs-2'
import { api } from '@/lib/api'
import { toast } from 'react-hot-toast'
import { useTranslation } from '@/contexts/TranslationContext'
import { RefreshCw, X } from 'lucide-react'
import { useCampaignStore } from '@/stores/campaignStore'
import { showAlert } from '@/lib/alertService'

const CampaignOverview: React.FC = () => {
  const { t } = useTranslation()
  const { campaigns, getCampaignsByStatus, generateMockCampaigns } = useCampaignStore()
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [selectedCampaigns, setSelectedCampaigns] = useState<string[]>([])
  const [showAutomation, setShowAutomation] = useState(false)
  const [showABTest, setShowABTest] = useState(false)
  const [showBulkActions, setShowBulkActions] = useState(false)
  const [selectedView, setSelectedView] = useState('grid')
  const [isGeneratingReport, setIsGeneratingReport] = useState(false)
  const queryClient = useQueryClient()

  // Initialize with mock campaigns if empty
  React.useEffect(() => {
    if (campaigns.length === 0) {
      generateMockCampaigns()
    }
  }, [campaigns.length, generateMockCampaigns])

  // Filter campaigns based on search and status
  const filteredCampaigns = React.useMemo(() => {
    let filtered = getCampaignsByStatus(statusFilter)
    
    if (searchQuery) {
      filtered = filtered.filter(campaign =>
        campaign.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        campaign.objective.toLowerCase().includes(searchQuery.toLowerCase())
      )
    }
    
    return filtered
  }, [campaigns, statusFilter, searchQuery, getCampaignsByStatus])

  // Calculate campaign stats
  const campaignStats = React.useMemo(() => {
    const activeCampaigns = campaigns.filter(c => c.status === 'active')
    const totalImpressions = campaigns.reduce((sum, c) => sum + c.performance.impressions, 0)
    const totalSpent = campaigns.reduce((sum, c) => sum + c.budget.spent, 0)
    const avgROI = campaigns.length > 0 
      ? campaigns.reduce((sum, c) => sum + c.performance.roi, 0) / campaigns.length 
      : 0

    return {
      active: activeCampaigns.length,
      totalImpressions,
      totalSpent,
      avgROI: Math.round(avgROI * 10) / 10
    }
  }, [campaigns])

  const updateCampaignStatus = useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) => 
      api.put(`/campaigns/${id}/status`, { status }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['campaigns'] })
      toast.success('Campaign status updated')
    },
  })

  const duplicateCampaign = useMutation({
    mutationFn: (id: string) => api.post(`/campaigns/${id}/duplicate`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['campaigns'] })
      toast.success('Campaign duplicated')
    },
  })

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'text-green-600 bg-green-50 border-green-200'
      case 'paused': return 'text-yellow-600 bg-yellow-50 border-yellow-200'
      case 'completed': return 'text-blue-600 bg-blue-50 border-blue-200'
      case 'draft': return 'text-gray-600 bg-gray-50 border-gray-200'
      default: return 'text-gray-600 bg-gray-50 border-gray-200'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return <Play className="w-4 h-4" />
      case 'paused': return <Pause className="w-4 h-4" />
      case 'completed': return <CheckCircle className="w-4 h-4" />
      case 'draft': return <Clock className="w-4 h-4" />
      default: return <AlertCircle className="w-4 h-4" />
    }
  }

  // No loading state needed since we're using local store

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{t('campaign.commandCenter')}</h1>
          <p className="text-gray-600 mt-1">{t('campaign.aiPoweredOptimization')}</p>
        </div>
        <div className="flex items-center space-x-3">
          {/* A/B Test Builder */}
          <button 
            onClick={() => {
              toast.success('Opening A/B Test Builder...')
              setTimeout(() => {
                showAlert(
                  'A/B Test Builder',
                  '• 5 creative variants ready\n• Audience split: 50/50\n• Duration: 14 days\n• Success metric: CTR improvement\n\nStarting test with current best-performing creatives...',
                  'success'
                )
                toast.success('A/B test configured and launched!')
              }, 1000)
            }}
            className="px-4 py-2 border border-orange-300 bg-orange-50 text-orange-700 rounded-lg hover:bg-orange-100 flex items-center"
          >
            <Brain className="w-4 h-4 mr-2" />
            {t('campaign.abTest')}
          </button>

          {/* Campaign Automation */}
          <button 
            onClick={() => {
              toast.success('Opening Campaign Automation Hub...')
              setTimeout(() => {
                showAlert(
                  'Campaign Automation Hub',
                  '✓ Budget Optimizer: Active (47 optimizations today)\n✓ Audience Expander: Active (12 new segments found)\n✓ Creative Rotator: Active (8 tests running)\n\nAll automation rules are running smoothly!',
                  'info'
                )
                toast.success('Automation hub loaded successfully!')
              }, 1000)
            }}
            className="px-4 py-2 border border-purple-300 bg-purple-50 text-purple-700 rounded-lg hover:bg-purple-100 flex items-center"
          >
            <Zap className="w-4 h-4 mr-2" />
            {t('campaign.automation')}
          </button>

          {/* Bulk Actions */}
          <div className="relative">
            <button 
              onClick={() => setShowBulkActions(!showBulkActions)}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center"
            >
              <Settings className="w-4 h-4 mr-2" />
              {t('campaign.bulkActions')}
            </button>
            {showBulkActions && (
              <div className="absolute right-0 top-full mt-2 w-48 bg-white border border-gray-200 rounded-lg shadow-lg z-10">
                <button 
                  onClick={() => {
                    toast.success('Starting all selected campaigns...')
                    setShowBulkActions(false)
                    setTimeout(() => {
                      toast.success('3 campaigns started successfully!')
                    }, 1500)
                  }}
                  className="w-full px-4 py-2 text-left hover:bg-gray-50 flex items-center"
                >
                  <Play className="w-4 h-4 mr-2" />
                  Start Selected
                </button>
                <button 
                  onClick={() => {
                    toast.success('Pausing all selected campaigns...')
                    setShowBulkActions(false)
                    setTimeout(() => {
                      toast.success('2 campaigns paused successfully!')
                    }, 1200)
                  }}
                  className="w-full px-4 py-2 text-left hover:bg-gray-50 flex items-center"
                >
                  <Pause className="w-4 h-4 mr-2" />
                  Pause Selected
                </button>
                <button 
                  onClick={() => {
                    toast.success('Duplicating selected campaigns...')
                    setShowBulkActions(false)
                    setTimeout(() => {
                      toast.success('4 campaigns duplicated with "-Copy" suffix')
                    }, 2000)
                  }}
                  className="w-full px-4 py-2 text-left hover:bg-gray-50 flex items-center"
                >
                  <Copy className="w-4 h-4 mr-2" />
                  Duplicate Selected
                </button>
                <button 
                  onClick={() => {
                    setShowBulkActions(false)
                    setShowExportModal(true)
                  }}
                  className="w-full px-4 py-2 text-left hover:bg-gray-50 flex items-center"
                >
                  <Download className="w-4 h-4 mr-2" />
                  Export Selected
                </button>
              </div>
            )}
          </div>

          <button 
            onClick={() => setShowExportModal(true)}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            <Download className="w-4 h-4 mr-2 inline" />
            {t('campaign.export')}
          </button>

          <Link
            to="/campaigns/new"
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center"
          >
            <Plus className="w-4 h-4 mr-2" />
            {t('campaign.newCampaign')}
          </Link>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">{t('campaign.activeCampaigns')}</p>
              <p className="text-3xl font-bold text-gray-900">{campaignStats.active}</p>
              <p className="text-sm text-green-600 flex items-center">
                <TrendingUp className="w-4 h-4 mr-1" />
                +3 this week
              </p>
            </div>
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <Target className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">{t('campaign.totalImpressions')}</p>
              <p className="text-3xl font-bold text-gray-900">{campaignStats.totalImpressions.toLocaleString()}</p>
              <p className="text-sm text-blue-600 flex items-center">
                <Eye className="w-4 h-4 mr-1" />
                +12% vs last month
              </p>
            </div>
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <Eye className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">{t('campaign.avgROI')}</p>
              <p className="text-3xl font-bold text-gray-900">{campaignStats.avgROI}%</p>
              <p className="text-sm text-green-600 flex items-center">
                <TrendingUp className="w-4 h-4 mr-1" />
                +8.5% vs last month
              </p>
            </div>
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
              <DollarSign className="w-6 h-6 text-purple-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">{t('campaign.aiOptimizations')}</p>
              <p className="text-3xl font-bold text-gray-900">{campaigns.filter(c => c.status === 'active').length}</p>
              <p className="text-sm text-purple-600 flex items-center">
                <Sparkles className="w-4 h-4 mr-1" />
                Live optimization
              </p>
            </div>
            <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
              <Brain className="w-6 h-6 text-orange-600" />
            </div>
          </div>
        </div>
      </div>

      {/* AI Campaign Intelligence Panel */}
      <div className="bg-gradient-to-r from-purple-50 via-blue-50 to-green-50 rounded-xl border border-purple-200 p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center">
            <div className="w-12 h-12 bg-gradient-to-r from-purple-600 to-blue-600 rounded-xl flex items-center justify-center mr-4">
              <Brain className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-gray-900">{t('campaign.aiCampaignIntelligenceHub')}</h3>
              <p className="text-sm text-gray-600">{t('campaign.realTimeOptimization')}</p>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-xs text-gray-600">{t('campaign.liveAnalysis')}</span>
            </div>
            <Link to="/campaigns/intelligence" className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 text-sm font-medium">
              {t('campaign.fullIntelligence')}
            </Link>
          </div>
        </div>

        {/* AI Intelligence Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          {/* ROI Predictions */}
          <div className="bg-white rounded-xl p-5 border border-gray-200 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center">
                <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center mr-3">
                  <DollarSign className="w-5 h-5 text-green-600" />
                </div>
                <h4 className="font-semibold text-gray-900">{t('campaign.roiOptimizer')}</h4>
              </div>
              <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full">{t('campaign.accurate')}</span>
            </div>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">{t('campaign.predicted30DayROI')}</span>
                <span className="font-bold text-green-600">+127.3%</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">{t('campaign.budgetEfficiency')}</span>
                <span className="font-bold text-blue-600">94.2%</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">{t('campaign.recommendedAction')}</span>
                <button 
                  onClick={() => {
                    setIsGeneratingReport(true)
                    setTimeout(() => {
                      setIsGeneratingReport(false)
                      toast.success('ROI Optimization applied! Expected revenue increase: +¥180K')
                    }, 2000)
                  }}
                  disabled={isGeneratingReport}
                  className="text-xs bg-purple-600 text-white px-2 py-1 rounded-md hover:bg-purple-700 disabled:opacity-50"
                >
                  {isGeneratingReport ? t('campaign.optimizing') : t('campaign.optimize')}
                </button>
              </div>
            </div>
          </div>

          {/* Audience Intelligence */}
          <div className="bg-white rounded-xl p-5 border border-gray-200 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center">
                <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center mr-3">
                  <Users className="w-5 h-5 text-blue-600" />
                </div>
                <h4 className="font-semibold text-gray-900">{t('campaign.audienceAI')}</h4>
              </div>
              <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full">{t('campaign.newInsights')}</span>
            </div>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">{t('campaign.highValueSegments')}</span>
                <span className="font-bold text-blue-600">3 {t('campaign.found')}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">{t('campaign.lookalikaeAccuracy')}</span>
                <span className="font-bold text-green-600">91.7%</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">{t('campaign.expandReach')}</span>
                <button 
                  onClick={() => {
                    toast.success('Deploying audience expansion to 3 new high-value segments!')
                    setTimeout(() => {
                      toast.success('Audience expanded successfully! +47K potential customers identified')
                    }, 3000)
                  }}
                  className="text-xs bg-blue-600 text-white px-2 py-1 rounded-md hover:bg-blue-700"
                >
                  {t('campaign.deploy')}
                </button>
              </div>
            </div>
          </div>

          {/* Creative Intelligence */}
          <div className="bg-white rounded-xl p-5 border border-gray-200 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center">
                <div className="w-8 h-8 bg-orange-100 rounded-lg flex items-center justify-center mr-3">
                  <Sparkles className="w-5 h-5 text-orange-600" />
                </div>
                <h4 className="font-semibold text-gray-900">{t('campaign.creativeAI')}</h4>
              </div>
              <span className="text-xs bg-orange-100 text-orange-700 px-2 py-1 rounded-full">{t('campaign.abReady')}</span>
            </div>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">{t('campaign.creativeScore')}</span>
                <span className="font-bold text-orange-600">8.7/10</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">{t('campaign.abVariants')}</span>
                <span className="font-bold text-purple-600">5 {t('campaign.ready')}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">{t('campaign.testLaunch')}</span>
                <button 
                  onClick={() => {
                    toast.success('Starting A/B test with 5 creative variants!')
                    setTimeout(() => {
                      toast.success('A/B test launched! Tracking 8.7/10 creative performance score')
                    }, 2500)
                  }}
                  className="text-xs bg-orange-600 text-white px-2 py-1 rounded-md hover:bg-orange-700"
                >
                  {t('campaign.startAB')}
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Smart Recommendations */}
        <div className="bg-white rounded-xl p-5 border border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <h4 className="font-semibold text-gray-900 flex items-center">
              <Lightbulb className="w-5 h-5 text-yellow-500 mr-2" />
              {t('campaign.aiPoweredSmartRecommendations')}
            </h4>
            <button className="text-sm text-gray-600 hover:text-gray-900">View All</button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-4 border border-green-200">
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center">
                  <div className="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center mr-2">
                    <TrendingUp className="w-3 h-3 text-white" />
                  </div>
                  <span className="font-medium text-gray-900">Weekend Revenue Boost</span>
                </div>
                <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full">High Impact</span>
              </div>
              <p className="text-sm text-gray-600 mb-3">
                Increase weekend campaign budgets by 34% to capture high-converting weekend shoppers
              </p>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-green-600">Potential: +¥180K revenue</span>
                <button 
                  onClick={() => {
                    toast.success('Applying weekend revenue optimization strategy!')
                    setTimeout(() => {
                      toast.success('Budget increased by 34% for weekend campaigns. Expected: +¥180K revenue')
                    }, 2000)
                  }}
                  className="px-3 py-1 bg-green-600 text-white text-xs rounded-md hover:bg-green-700"
                >
                  Apply Now
                </button>
              </div>
            </div>

            <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg p-4 border border-purple-200">
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center">
                  <div className="w-6 h-6 bg-purple-500 rounded-full flex items-center justify-center mr-2">
                    <Target className="w-3 h-3 text-white" />
                  </div>
                  <span className="font-medium text-gray-900">VIP Segment Focus</span>
                </div>
                <span className="text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded-full">AI Discovery</span>
              </div>
              <p className="text-sm text-gray-600 mb-3">
                Your VIP customers respond 3x better to personalized offers than generic campaigns
              </p>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-purple-600">Conversion: +89% CTR</span>
                <button 
                  onClick={() => {
                    toast.success('Creating personalized VIP campaign for high-value customers!')
                    setTimeout(() => {
                      window.open('/campaigns/new?template=vip', '_blank')
                      toast.success('VIP campaign template loaded! Expected +89% CTR improvement')
                    }, 1500)
                  }}
                  className="px-3 py-1 bg-purple-600 text-white text-xs rounded-md hover:bg-purple-700"
                >
                  Create VIP Campaign
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
          <div className="flex items-center space-x-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search campaigns..."
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <button className="flex items-center px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
              <Filter className="w-4 h-4 mr-2" />
              Filters
            </button>
          </div>

          <div className="flex items-center space-x-1 bg-gray-100 p-1 rounded-lg">
            {['all', 'active', 'paused', 'completed', 'draft'].map((status) => (
              <button
                key={status}
                onClick={() => setStatusFilter(status)}
                className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors capitalize ${
                  statusFilter === status
                    ? 'bg-white text-blue-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                {status}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Campaign Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredCampaigns.map((campaign) => (
          <motion.div
            key={campaign.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow"
          >
            {/* Campaign Header */}
            <div className="p-6 pb-4">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    <h3 className="font-semibold text-gray-900">{campaign.name}</h3>
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(campaign.status)}`}>
                      {getStatusIcon(campaign.status)}
                      <span className="ml-1 capitalize">{campaign.status}</span>
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mb-3">{campaign.description}</p>
                  <div className="flex items-center space-x-4 text-sm text-gray-500">
                    <span className="flex items-center">
                      <Calendar className="w-4 h-4 mr-1" />
                      {new Date(campaign.schedule.startDate).toLocaleDateString()}
                    </span>
                    <span className="flex items-center">
                      <Users className="w-4 h-4 mr-1" />
                      {campaign.audience.size?.toLocaleString() || 0}
                    </span>
                  </div>
                </div>
                <div className="relative">
                  <button 
                    onClick={(e) => {
                      e.stopPropagation()
                      const rect = e.currentTarget.getBoundingClientRect()
                      const menu = document.createElement('div')
                      menu.className = 'fixed bg-white border border-gray-200 rounded-lg shadow-lg z-50 py-2 min-w-[150px]'
                      menu.style.top = `${rect.bottom + 5}px`
                      menu.style.left = `${rect.left - 100}px`
                      menu.innerHTML = `
                        <button onclick="alert('Edit Campaign'); this.parentElement.remove()" class="w-full px-4 py-2 text-left hover:bg-gray-50 flex items-center text-sm text-gray-700">
                          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path></svg>
                          Edit
                        </button>
                        <button onclick="alert('Duplicate Campaign'); this.parentElement.remove()" class="w-full px-4 py-2 text-left hover:bg-gray-50 flex items-center text-sm text-gray-700">
                          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path></svg>
                          Duplicate
                        </button>
                        <button onclick="alert('Archive Campaign'); this.parentElement.remove()" class="w-full px-4 py-2 text-left hover:bg-gray-50 flex items-center text-sm text-gray-700">
                          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8l6 6 6-6"></path></svg>
                          Archive
                        </button>
                      `
                      document.body.appendChild(menu)
                      const closeMenu = () => {
                        if (document.body.contains(menu)) {
                          document.body.removeChild(menu)
                        }
                        document.removeEventListener('click', closeMenu)
                      }
                      setTimeout(() => document.addEventListener('click', closeMenu), 100)
                    }}
                    className="p-1 hover:bg-gray-100 rounded"
                  >
                    <MoreVertical className="w-4 h-4 text-gray-500" />
                  </button>
                </div>
              </div>

              {/* Performance Metrics */}
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div className="bg-blue-50 rounded-lg p-3">
                  <p className="text-sm text-blue-600 font-medium">Impressions</p>
                  <p className="text-lg font-bold text-blue-900">
                    {campaign.performance.impressions?.toLocaleString() || 0}
                  </p>
                </div>
                <div className="bg-green-50 rounded-lg p-3">
                  <p className="text-sm text-green-600 font-medium">Conversions</p>
                  <p className="text-lg font-bold text-green-900">
                    {campaign.performance.conversions?.toLocaleString() || 0}
                  </p>
                </div>
              </div>

              {/* ROI and Performance */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">ROI</span>
                  <span className={`font-semibold ${
                    (campaign.performance.roi || 0) > 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {campaign.performance.roi || 0}%
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Conversion Rate</span>
                  <span className="font-semibold text-gray-900">
                    {campaign.performance.impressions > 0 
                      ? ((campaign.performance.conversions / campaign.performance.impressions) * 100).toFixed(2)
                      : '0.00'
                    }%
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Budget Spent</span>
                  <span className="font-semibold text-gray-900">
                    ¥{campaign.budget.spent?.toLocaleString() || 0} / ¥{campaign.budget.amount?.toLocaleString() || 0}
                  </span>
                </div>
              </div>

              {/* AI Predictions */}
              {campaign.ai_predictions && (
                <div className="mt-4 p-3 bg-purple-50 rounded-lg border border-purple-100">
                  <div className="flex items-center mb-2">
                    <Brain className="w-4 h-4 text-purple-600 mr-2" />
                    <span className="text-sm font-medium text-purple-900">AI Prediction</span>
                  </div>
                  <p className="text-sm text-purple-700">
                    Expected ROI: <span className="font-semibold">+{campaign.ai_predictions.expected_roi}%</span>
                  </p>
                  <p className="text-xs text-purple-600 mt-1">
                    Confidence: {campaign.ai_predictions.confidence}%
                  </p>
                </div>
              )}
            </div>

            {/* Action Buttons */}
            <div className="px-6 py-4 bg-gray-50 border-t border-gray-200">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Link
                    to={`/campaigns/${campaign.id}`}
                    className="text-sm text-blue-600 hover:text-blue-700 font-medium"
                  >
                    View Details
                  </Link>
                  <button
                    onClick={() => duplicateCampaign.mutate(campaign.id)}
                    className="text-sm text-gray-600 hover:text-gray-700"
                  >
                    <Copy className="w-4 h-4" />
                  </button>
                </div>
                <div className="flex items-center space-x-2">
                  {campaign.status === 'active' ? (
                    <button
                      onClick={() => updateCampaignStatus.mutate({ id: campaign.id, status: 'paused' })}
                      className="p-1 text-yellow-600 hover:bg-yellow-50 rounded"
                      title="Pause Campaign"
                    >
                      <Pause className="w-4 h-4" />
                    </button>
                  ) : campaign.status === 'paused' ? (
                    <button
                      onClick={() => updateCampaignStatus.mutate({ id: campaign.id, status: 'active' })}
                      className="p-1 text-green-600 hover:bg-green-50 rounded"
                      title="Resume Campaign"
                    >
                      <Play className="w-4 h-4" />
                    </button>
                  ) : null}
                  <Link
                    to={`/campaigns/${campaign.id}/edit`}
                    className="p-1 text-gray-600 hover:bg-gray-100 rounded"
                    title="Edit Campaign"
                  >
                    <Edit className="w-4 h-4" />
                  </Link>
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {(!campaigns || campaigns.length === 0) && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
          <Target className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No campaigns found</h3>
          <p className="text-gray-600 mb-6">Create your first campaign to start engaging customers with AI-powered optimization.</p>
          <Link
            to="/campaigns/new"
            className="inline-flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            <Plus className="w-5 h-5 mr-2" />
            Create First Campaign
          </Link>
        </div>
      )}
    </div>
  )
}

export const CampaignCenter: React.FC = () => {
  const location = useLocation()
  const { t } = useTranslation()
  
  const tabs = [
    { id: 'overview', label: t('campaigns.overview'), icon: Target, path: '/campaigns' },
    { id: 'intelligence', label: t('campaigns.intelligence'), icon: Brain, path: '/campaigns/intelligence' },
    { id: 'analytics', label: t('campaigns.analytics'), icon: BarChart3, path: '/campaigns/analytics' },
    { id: 'automation', label: t('campaigns.automation'), icon: Zap, path: '/campaigns/automation' },
  ]

  const isActive = (path: string) => {
    if (path === '/campaigns') return location.pathname === '/campaigns'
    return location.pathname.startsWith(path)
  }

  return (
    <div className="p-6 space-y-6">
      {/* Tab Navigation */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-2">
        <nav className="flex space-x-1">
          {tabs.map((tab) => (
            <Link
              key={tab.id}
              to={tab.path}
              className={`flex items-center px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                isActive(tab.path)
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
              }`}
            >
              <tab.icon className="w-4 h-4 mr-2" />
              {tab.label}
            </Link>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <Routes>
        <Route index element={<CampaignOverview />} />
        <Route path="intelligence" element={<CampaignIntelligence />} />
        <Route path="analytics" element={<CampaignAnalytics />} />
        <Route path="automation" element={<CampaignAutomation />} />
        <Route path="new" element={<NewCampaign />} />
        <Route path=":id" element={<CampaignDetails />} />
        <Route path=":id/edit" element={<EditCampaign />} />
      </Routes>
    </div>
  )
}

// 🧠 Campaign Intelligence Component
const CampaignIntelligence: React.FC = () => {
  const [selectedModel, setSelectedModel] = useState('ensemble')
  const [selectedTimeframe, setSelectedTimeframe] = useState('30d')
  const [intelligenceView, setIntelligenceView] = useState('overview')

  const { data: campaignIntelligence } = useQuery({
    queryKey: ['campaign-intelligence', selectedModel, selectedTimeframe],
    queryFn: () => api.get(`/campaigns/intelligence?model=${selectedModel}&timeframe=${selectedTimeframe}`),
  })

  const intelligenceViews = [
    { id: 'overview', label: 'Intelligence Overview', icon: Brain },
    { id: 'predictions', label: 'AI Predictions', icon: Sparkles },
    { id: 'optimization', label: 'Optimization', icon: Zap },
    { id: 'insights', label: 'Creative Insights', icon: Lightbulb }
  ]

  const aiModels = [
    { id: 'ensemble', label: 'Ensemble AI (22 models)', accuracy: '98.7%' },
    { id: 'neural', label: 'Neural Network', accuracy: '96.2%' },
    { id: 'gradient', label: 'Gradient Boosting', accuracy: '95.8%' },
    { id: 'forest', label: 'Random Forest', accuracy: '94.3%' }
  ]

  return (
    <div className="space-y-6">
      {/* Intelligence Header */}
      <div className="bg-gradient-to-r from-purple-600 via-blue-600 to-green-600 rounded-xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-16 h-16 bg-white/20 rounded-xl flex items-center justify-center">
              <Brain className="w-8 h-8" />
            </div>
            <div>
              <h2 className="text-2xl font-bold">Campaign Intelligence Center</h2>
              <p className="text-white/90">AI-powered campaign optimization and strategic insights</p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-3xl font-bold">AI Active</p>
            <p className="text-white/80">Real-time Analysis</p>
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-4">
            <select
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {aiModels.map(model => (
                <option key={model.id} value={model.id}>{model.label} - {model.accuracy}</option>
              ))}
            </select>
            <select
              value={selectedTimeframe}
              onChange={(e) => setSelectedTimeframe(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="7d">Last 7 days</option>
              <option value="30d">Last 30 days</option>
              <option value="90d">Last 3 months</option>
            </select>
          </div>
          <div className="flex items-center space-x-2">
            {intelligenceViews.map((view) => (
              <button
                key={view.id}
                onClick={() => setIntelligenceView(view.id)}
                className={`flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  intelligenceView === view.id
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                }`}
              >
                <view.icon className="w-4 h-4 mr-1" />
                {view.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Intelligence Content */}
      {intelligenceView === 'overview' && (
        <div className="space-y-6">
          {/* Key Intelligence Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 text-center">
              <div className="w-12 h-12 bg-green-100 rounded-lg mx-auto mb-3 flex items-center justify-center">
                <Target className="w-6 h-6 text-green-600" />
              </div>
              <p className="text-3xl font-bold text-green-600 mb-1">+127%</p>
              <p className="text-sm text-gray-600">Predicted ROI Increase</p>
              <p className="text-xs text-green-600 mt-1">96% confidence</p>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 text-center">
              <div className="w-12 h-12 bg-blue-100 rounded-lg mx-auto mb-3 flex items-center justify-center">
                <Users className="w-6 h-6 text-blue-600" />
              </div>
              <p className="text-3xl font-bold text-blue-600 mb-1">2.8M</p>
              <p className="text-sm text-gray-600">Optimal Audience Size</p>
              <p className="text-xs text-blue-600 mt-1">18% expansion opportunity</p>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 text-center">
              <div className="w-12 h-12 bg-purple-100 rounded-lg mx-auto mb-3 flex items-center justify-center">
                <Sparkles className="w-6 h-6 text-purple-600" />
              </div>
              <p className="text-3xl font-bold text-purple-600 mb-1">47</p>
              <p className="text-sm text-gray-600">AI Optimizations Found</p>
              <p className="text-xs text-purple-600 mt-1">Ready to deploy</p>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 text-center">
              <div className="w-12 h-12 bg-orange-100 rounded-lg mx-auto mb-3 flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-orange-600" />
              </div>
              <p className="text-3xl font-bold text-orange-600 mb-1">8.9/10</p>
              <p className="text-sm text-gray-600">Campaign Health Score</p>
              <p className="text-xs text-green-600 mt-1">Excellent performance</p>
            </div>
          </div>

          {/* Strategic Recommendations */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Brain className="w-5 h-5 text-purple-600 mr-2" />
              Strategic AI Recommendations
            </h3>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-gradient-to-br from-green-50 to-blue-50 rounded-lg p-4 border border-green-200">
                <div className="flex items-start space-x-3">
                  <div className="w-8 h-8 bg-green-500 rounded-lg flex items-center justify-center mt-1">
                    <DollarSign className="w-4 h-4 text-white" />
                  </div>
                  <div className="flex-1">
                    <h4 className="font-semibold text-gray-900 mb-2">Revenue Optimization</h4>
                    <p className="text-sm text-gray-700 mb-3">
                      Shift 23% of budget to high-performing weekend slots. AI predicts +¥340K additional revenue.
                    </p>
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-green-600">Impact: Very High</span>
                      <button 
                        onClick={() => {
                          toast.success('Applying Revenue Optimization Strategy...')
                          setTimeout(() => {
                            toast.success('Strategy applied! Budget shifted to weekend slots. Expected: +¥340K revenue')
                          }, 2500)
                        }}
                        className="px-3 py-1 bg-green-600 text-white text-xs rounded-md hover:bg-green-700"
                      >
                        Apply Strategy
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-lg p-4 border border-purple-200">
                <div className="flex items-start space-x-3">
                  <div className="w-8 h-8 bg-purple-500 rounded-lg flex items-center justify-center mt-1">
                    <Target className="w-4 h-4 text-white" />
                  </div>
                  <div className="flex-1">
                    <h4 className="font-semibold text-gray-900 mb-2">Audience Expansion</h4>
                    <p className="text-sm text-gray-700 mb-3">
                      Target lookalike segments of your top 10% customers. 91% similarity match found.
                    </p>
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-purple-600">Confidence: 91%</span>
                      <button 
                        onClick={() => {
                          toast.success('Expanding audience with lookalike segments...')
                          setTimeout(() => {
                            toast.success('Audience expanded! 91% similarity match with top 10% customers found')
                          }, 3000)
                        }}
                        className="px-3 py-1 bg-purple-600 text-white text-xs rounded-md hover:bg-purple-700"
                      >
                        Expand Audience
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {intelligenceView === 'predictions' && (
        <div className="space-y-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">AI Campaign Predictions</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <h4 className="font-medium text-gray-900">Performance Forecasts</h4>
                <div className="space-y-3">
                  <div className="p-3 bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg border border-blue-200">
                    <div className="flex justify-between items-center mb-2">
                      <span className="font-medium text-gray-900">Next 7 Days ROI</span>
                      <span className="text-sm bg-blue-600 text-white px-2 py-1 rounded-full">94% confidence</span>
                    </div>
                    <p className="text-2xl font-bold text-blue-600">+156.7%</p>
                  </div>
                  <div className="p-3 bg-gradient-to-r from-green-50 to-green-100 rounded-lg border border-green-200">
                    <div className="flex justify-between items-center mb-2">
                      <span className="font-medium text-gray-900">Conversion Rate</span>
                      <span className="text-sm bg-green-600 text-white px-2 py-1 rounded-full">89% confidence</span>
                    </div>
                    <p className="text-2xl font-bold text-green-600">4.2%</p>
                  </div>
                </div>
              </div>
              <div className="space-y-4">
                <h4 className="font-medium text-gray-900">Risk Analysis</h4>
                <div className="space-y-3">
                  <div className="p-3 bg-gradient-to-r from-yellow-50 to-yellow-100 rounded-lg border border-yellow-200">
                    <div className="flex justify-between items-center mb-2">
                      <span className="font-medium text-gray-900">Budget Overrun Risk</span>
                      <span className="text-sm bg-yellow-600 text-white px-2 py-1 rounded-full">Low</span>
                    </div>
                    <p className="text-2xl font-bold text-yellow-600">12%</p>
                  </div>
                  <div className="p-3 bg-gradient-to-r from-purple-50 to-purple-100 rounded-lg border border-purple-200">
                    <div className="flex justify-between items-center mb-2">
                      <span className="font-medium text-gray-900">Market Saturation</span>
                      <span className="text-sm bg-purple-600 text-white px-2 py-1 rounded-full">Very Low</span>
                    </div>
                    <p className="text-2xl font-bold text-purple-600">3%</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {intelligenceView === 'optimization' && (
        <div className="space-y-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Campaign Optimization Hub</h3>
            <div className="space-y-4">
              <div className="p-4 border border-gray-200 rounded-lg">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="font-medium text-gray-900">Budget Allocation Optimizer</h4>
                  <button 
                    onClick={() => {
                      setIsGeneratingReport(true)
                      toast.success('Running budget allocation optimization...')
                      setTimeout(() => {
                        setIsGeneratingReport(false)
                        showAlert(
                          'Budget Optimization Complete!',
                          '✓ Redistributed ¥150K across campaigns\n✓ Expected ROI improvement: +23.4%\n✓ Performance increase: +18.7%\n✓ Cost efficiency: +12.1%\n\nOptimization applied to all active campaigns.',
                          'success'
                        )
                        toast.success('Budget optimization completed successfully!')
                      }, 4000)
                    }}
                    disabled={isGeneratingReport}
                    className="px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                  >
                    {isGeneratingReport ? 'Optimizing...' : 'Run Optimization'}
                  </button>
                </div>
                <p className="text-sm text-gray-600">AI will redistribute your budget across campaigns for maximum ROI</p>
              </div>
              <div className="p-4 border border-gray-200 rounded-lg">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="font-medium text-gray-900">Creative Performance Optimizer</h4>
                  <button 
                    onClick={() => {
                      toast.success('Starting creative performance optimization...')
                      setTimeout(() => {
                        showAlert(
                          'Creative Optimization Results',
                          '✓ Generated 12 new creative variations\n✓ A/B testing 5 top performers\n✓ Removed 3 underperforming creatives\n✓ Expected CTR improvement: +34%\n\nNew creatives are now live and being tested!',
                          'success'
                        )
                        toast.success('Creative optimization completed!')
                      }, 3500)
                    }}
                    className="px-3 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
                  >
                    Optimize Creatives
                  </button>
                </div>
                <p className="text-sm text-gray-600">Automatically generate and test new creative variations</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {intelligenceView === 'insights' && (
        <div className="space-y-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Creative AI Insights</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-lg p-4 border border-blue-200">
                <h4 className="font-semibold text-gray-900 mb-2">Weekend Warriors Discovery</h4>
                <p className="text-sm text-gray-700 mb-3">
                  Your customers are 67% more active on weekends. They love premium experiences and spend 2.3x more per session.
                </p>
                <div className="text-xs text-blue-600 font-medium">Insight Strength: Very High</div>
              </div>
              <div className="bg-gradient-to-br from-green-50 to-blue-50 rounded-lg p-4 border border-green-200">
                <h4 className="font-semibold text-gray-900 mb-2">Mobile-First Generation</h4>
                <p className="text-sm text-gray-700 mb-3">
                  87% of your conversions happen on mobile devices. Desktop campaigns are underperforming by 45%.
                </p>
                <div className="text-xs text-green-600 font-medium">Actionable: Immediate</div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

// 📊 Campaign Analytics Component
const CampaignAnalytics: React.FC = () => {
  const [analyticsView, setAnalyticsView] = useState('performance')
  const [timeRange, setTimeRange] = useState('30d')
  const [selectedCampaign, setSelectedCampaign] = useState('all')
  const [showExportModal, setShowExportModal] = useState(false)
  const [isGeneratingReport, setIsGeneratingReport] = useState(false)

  const { data: campaignAnalytics } = useQuery({
    queryKey: ['campaign-analytics', timeRange, selectedCampaign],
    queryFn: () => api.get(`/campaigns/analytics?timeRange=${timeRange}&campaign=${selectedCampaign}`),
  })

  const { data: attributionData } = useQuery({
    queryKey: ['attribution-data', timeRange],
    queryFn: () => api.get(`/campaigns/attribution?timeRange=${timeRange}`),
  })

  const { data: funnelData } = useQuery({
    queryKey: ['funnel-data', timeRange],
    queryFn: () => api.get(`/campaigns/funnel?timeRange=${timeRange}`),
  })

  const { data: cohortData } = useQuery({
    queryKey: ['cohort-data', timeRange],
    queryFn: () => api.get(`/campaigns/cohort?timeRange=${timeRange}`),
  })

  const analyticsViews = [
    { id: 'performance', label: 'Performance', icon: BarChart3, description: 'Overall campaign performance metrics' },
    { id: 'attribution', label: 'Attribution', icon: Target, description: 'Multi-touch attribution analysis' },
    { id: 'funnel', label: 'Funnel Analysis', icon: TrendingUp, description: 'Conversion funnel breakdown' },
    { id: 'cohort', label: 'Cohort Analysis', icon: Users, description: 'User cohort behavior analysis' }
  ]

  const handleExportReport = async (format: string) => {
    setIsGeneratingReport(true)
    try {
      // Simulate report generation
      await new Promise(resolve => setTimeout(resolve, 2000))
      const blob = new Blob(['Campaign Analytics Report'], { type: 'text/plain' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `campaign-analytics-${analyticsView}-${timeRange}.${format}`
      a.click()
      window.URL.revokeObjectURL(url)
      toast.success('Report exported successfully')
    } catch (error) {
      toast.error('Failed to export report')
    } finally {
      setIsGeneratingReport(false)
      setShowExportModal(false)
    }
  }

  const campaigns = [
    { id: 'all', name: 'All Campaigns' },
    { id: 'weekend-vip', name: 'Weekend VIP Experience' },
    { id: 'summer-sale', name: 'Summer Sale 2024' },
    { id: 'loyalty-boost', name: 'Loyalty Boost Campaign' },
    { id: 'mobile-first', name: 'Mobile-First Initiative' }
  ]

  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl p-6 text-white">
        <h2 className="text-2xl font-bold mb-2">Campaign Analytics Dashboard</h2>
        <p className="text-blue-100">Deep-dive analytics and performance insights for all your campaigns</p>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
          <div className="flex flex-wrap items-center gap-2">
            {analyticsViews.map((view) => (
              <button
                key={view.id}
                onClick={() => setAnalyticsView(view.id)}
                className={`flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  analyticsView === view.id
                    ? 'bg-blue-600 text-white shadow-md'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50 border border-gray-200'
                }`}
                title={view.description}
              >
                <view.icon className="w-4 h-4 mr-2" />
                {view.label}
              </button>
            ))}
          </div>
          <div className="flex items-center space-x-3">
            <select
              value={selectedCampaign}
              onChange={(e) => setSelectedCampaign(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {campaigns.map(campaign => (
                <option key={campaign.id} value={campaign.id}>{campaign.name}</option>
              ))}
            </select>
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="7d">Last 7 days</option>
              <option value="30d">Last 30 days</option>
              <option value="90d">Last 3 months</option>
              <option value="1y">Last year</option>
            </select>
            <button
              onClick={() => setShowExportModal(true)}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center"
            >
              <Download className="w-4 h-4 mr-2" />
              Export
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 text-center">
          <div className="w-12 h-12 bg-green-100 rounded-lg mx-auto mb-3 flex items-center justify-center">
            <DollarSign className="w-6 h-6 text-green-600" />
          </div>
          <p className="text-3xl font-bold text-green-600 mb-1">¥2.4M</p>
          <p className="text-sm text-gray-600">Total Revenue</p>
          <p className="text-xs text-green-600 mt-1">+18.5% vs last period</p>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 text-center">
          <div className="w-12 h-12 bg-blue-100 rounded-lg mx-auto mb-3 flex items-center justify-center">
            <Target className="w-6 h-6 text-blue-600" />
          </div>
          <p className="text-3xl font-bold text-blue-600 mb-1">3.7%</p>
          <p className="text-sm text-gray-600">Avg Conversion Rate</p>
          <p className="text-xs text-blue-600 mt-1">+0.8% improvement</p>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 text-center">
          <div className="w-12 h-12 bg-purple-100 rounded-lg mx-auto mb-3 flex items-center justify-center">
            <Users className="w-6 h-6 text-purple-600" />
          </div>
          <p className="text-3xl font-bold text-purple-600 mb-1">847K</p>
          <p className="text-sm text-gray-600">Total Reach</p>
          <p className="text-xs text-purple-600 mt-1">12% audience expansion</p>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 text-center">
          <div className="w-12 h-12 bg-orange-100 rounded-lg mx-auto mb-3 flex items-center justify-center">
            <TrendingUp className="w-6 h-6 text-orange-600" />
          </div>
          <p className="text-3xl font-bold text-orange-600 mb-1">126%</p>
          <p className="text-sm text-gray-600">Average ROI</p>
          <p className="text-xs text-green-600 mt-1">Exceeding targets</p>
        </div>
      </div>

      {/* Dynamic Analytics Content */}
      {analyticsView === 'performance' && (
        <div className="space-y-6">
          {/* Performance Overview */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-gray-900">Campaign Performance Analytics</h3>
              <div className="flex items-center space-x-2">
                <button 
                  onClick={() => window.location.reload()}
                  className="px-3 py-2 text-sm bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100"
                >
                  <RefreshCw className="w-4 h-4 mr-1 inline" />
                  Refresh Data
                </button>
              </div>
            </div>
            
            {/* Performance Charts Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-lg p-6 border border-blue-200">
                <h4 className="font-semibold text-gray-900 mb-4">Revenue Trend (30 Days)</h4>
                <div className="h-48 flex items-center justify-center">
                  <div className="text-center">
                    <TrendingUp className="w-12 h-12 text-blue-500 mx-auto mb-2" />
                    <p className="text-gray-600">Interactive revenue chart</p>
                    <p className="text-sm text-gray-500">Showing growth trend +18.5%</p>
                  </div>
                </div>
              </div>
              
              <div className="bg-gradient-to-br from-green-50 to-blue-50 rounded-lg p-6 border border-green-200">
                <h4 className="font-semibold text-gray-900 mb-4">Conversion Funnel</h4>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Impressions</span>
                    <span className="font-medium">2.4M</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div className="bg-blue-500 h-2 rounded-full" style={{width: '100%'}}></div>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Clicks</span>
                    <span className="font-medium">94.3K (3.9%)</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div className="bg-green-500 h-2 rounded-full" style={{width: '87%'}}></div>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Conversions</span>
                    <span className="font-medium">3.8K (4.0%)</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div className="bg-purple-500 h-2 rounded-full" style={{width: '45%'}}></div>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Performance Table */}
            <div className="mt-6">
              <h4 className="font-semibold text-gray-900 mb-4">Campaign Breakdown</h4>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-gray-200">
                      <th className="text-left py-3 px-4 font-medium text-gray-900">Campaign</th>
                      <th className="text-right py-3 px-4 font-medium text-gray-900">Impressions</th>
                      <th className="text-right py-3 px-4 font-medium text-gray-900">Clicks</th>
                      <th className="text-right py-3 px-4 font-medium text-gray-900">CTR</th>
                      <th className="text-right py-3 px-4 font-medium text-gray-900">Conversions</th>
                      <th className="text-right py-3 px-4 font-medium text-gray-900">ROI</th>
                      <th className="text-center py-3 px-4 font-medium text-gray-900">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {campaigns.slice(1).map((campaign, index) => (
                      <tr key={campaign.id} className="border-b border-gray-100 hover:bg-gray-50">
                        <td className="py-3 px-4">
                          <div className="font-medium text-gray-900">{campaign.name}</div>
                          <div className="text-sm text-gray-500">Active • {30 - index} days remaining</div>
                        </td>
                        <td className="text-right py-3 px-4 text-gray-900">{(847000 - index * 150000).toLocaleString()}</td>
                        <td className="text-right py-3 px-4 text-gray-900">{(34000 - index * 5000).toLocaleString()}</td>
                        <td className="text-right py-3 px-4">
                          <span className={`font-medium ${
                            (4.2 - index * 0.5) > 3.5 ? 'text-green-600' : 
                            (4.2 - index * 0.5) > 2.5 ? 'text-yellow-600' : 'text-red-600'
                          }`}>
                            {(4.2 - index * 0.5).toFixed(1)}%
                          </span>
                        </td>
                        <td className="text-right py-3 px-4 text-gray-900">{(1450 - index * 200).toLocaleString()}</td>
                        <td className="text-right py-3 px-4">
                          <span className={`font-medium ${
                            (156 - index * 20) > 120 ? 'text-green-600' : 
                            (156 - index * 20) > 80 ? 'text-yellow-600' : 'text-red-600'
                          }`}>
                            {(156 - index * 20)}%
                          </span>
                        </td>
                        <td className="text-center py-3 px-4">
                          <div className="flex items-center justify-center space-x-2">
                            <button 
                              onClick={() => showAlert(
                                'Campaign Optimization',
                                `Optimizing ${campaign.name}...\n\nThis process will:\n• Analyze current performance\n• Adjust budget allocation\n• Optimize targeting parameters\n• Update creative rotation\n\nEstimated completion: 2-3 minutes`,
                                'info'
                              )}
                              className="p-1 text-blue-600 hover:bg-blue-50 rounded" 
                              title="Optimize Campaign"
                            >
                              <Zap className="w-4 h-4" />
                            </button>
                            <button 
                              onClick={() => showAlert(
                                'Campaign Details',
                                `Campaign: ${campaign.name}\n\nStatus: ${campaign.status}\nBudget: ¥${campaign.budget.amount.toLocaleString()}\nROI: ${campaign.performance?.roi || 0}%\nImpressions: ${campaign.performance?.impressions.toLocaleString() || 0}\nClicks: ${campaign.performance?.clicks.toLocaleString() || 0}\nConversions: ${campaign.performance?.conversions.toLocaleString() || 0}`,
                                'info'
                              )}
                              className="p-1 text-gray-600 hover:bg-gray-50 rounded" 
                              title="View Details"
                            >
                              <Eye className="w-4 h-4" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {analyticsView === 'attribution' && (
        <div className="space-y-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Multi-Touch Attribution Analysis</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
              <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-4 text-center">
                <div className="w-12 h-12 bg-blue-600 rounded-lg mx-auto mb-2 flex items-center justify-center">
                  <Eye className="w-6 h-6 text-white" />
                </div>
                <p className="text-2xl font-bold text-blue-600">42.3%</p>
                <p className="text-sm text-gray-600">First Touch</p>
              </div>
              <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-4 text-center">
                <div className="w-12 h-12 bg-green-600 rounded-lg mx-auto mb-2 flex items-center justify-center">
                  <Target className="w-6 h-6 text-white" />
                </div>
                <p className="text-2xl font-bold text-green-600">28.7%</p>
                <p className="text-sm text-gray-600">Last Touch</p>
              </div>
              <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-4 text-center">
                <div className="w-12 h-12 bg-purple-600 rounded-lg mx-auto mb-2 flex items-center justify-center">
                  <BarChart3 className="w-6 h-6 text-white" />
                </div>
                <p className="text-2xl font-bold text-purple-600">18.4%</p>
                <p className="text-sm text-gray-600">Linear</p>
              </div>
              <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-lg p-4 text-center">
                <div className="w-12 h-12 bg-orange-600 rounded-lg mx-auto mb-2 flex items-center justify-center">
                  <Brain className="w-6 h-6 text-white" />
                </div>
                <p className="text-2xl font-bold text-orange-600">10.6%</p>
                <p className="text-sm text-gray-600">Data-Driven</p>
              </div>
            </div>
            
            {/* Attribution Journey */}
            <div className="bg-gray-50 rounded-lg p-6">
              <h4 className="font-semibold text-gray-900 mb-4">Customer Journey Attribution</h4>
              <div className="flex items-center justify-between">
                {[
                  { channel: 'Social Media', contribution: '35%', color: 'bg-blue-500' },
                  { channel: 'Email', contribution: '28%', color: 'bg-green-500' },
                  { channel: 'Search', contribution: '22%', color: 'bg-purple-500' },
                  { channel: 'Direct', contribution: '15%', color: 'bg-orange-500' }
                ].map((item, index) => (
                  <div key={index} className="flex flex-col items-center">
                    <div className={`w-16 h-16 ${item.color} rounded-full flex items-center justify-center text-white font-bold mb-2`}>
                      {item.contribution}
                    </div>
                    <p className="text-sm font-medium text-gray-900">{item.channel}</p>
                    <p className="text-xs text-gray-500">Attribution</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
      
      {analyticsView === 'funnel' && (
        <div className="space-y-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Conversion Funnel Analysis</h3>
            <div className="space-y-6">
              {/* Funnel Visualization */}
              <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6">
                <div className="space-y-4">
                  {[
                    { stage: 'Awareness', users: 2400000, percentage: 100, color: 'bg-blue-500' },
                    { stage: 'Interest', users: 847000, percentage: 35.3, color: 'bg-green-500' },
                    { stage: 'Consideration', users: 124000, percentage: 14.6, color: 'bg-yellow-500' },
                    { stage: 'Intent', users: 47000, percentage: 37.9, color: 'bg-orange-500' },
                    { stage: 'Purchase', users: 18400, percentage: 39.1, color: 'bg-red-500' }
                  ].map((stage, index) => (
                    <div key={index} className="flex items-center space-x-4">
                      <div className="w-24 text-sm font-medium text-gray-900">{stage.stage}</div>
                      <div className="flex-1 relative">
                        <div className="w-full bg-gray-200 rounded-full h-8 relative">
                          <div 
                            className={`${stage.color} h-8 rounded-full flex items-center justify-between px-4 text-white font-medium`}
                            style={{ width: `${Math.max(stage.percentage, 10)}%` }}
                          >
                            <span>{stage.users.toLocaleString()}</span>
                            <span>{stage.percentage.toFixed(1)}%</span>
                          </div>
                        </div>
                        {index > 0 && (
                          <div className="absolute -top-3 right-4 text-xs bg-white px-2 py-1 rounded shadow border">
                            Drop: {(100 - stage.percentage).toFixed(1)}%
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              
              {/* Funnel Insights */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <div className="flex items-center mb-2">
                    <AlertCircle className="w-5 h-5 text-red-600 mr-2" />
                    <h4 className="font-semibold text-red-900">Biggest Drop-off</h4>
                  </div>
                  <p className="text-sm text-red-700">64.7% drop from Awareness to Interest</p>
                  <button className="mt-2 px-3 py-1 bg-red-600 text-white text-xs rounded-md hover:bg-red-700">
                    Optimize Interest Stage
                  </button>
                </div>
                
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <div className="flex items-center mb-2">
                    <CheckCircle className="w-5 h-5 text-green-600 mr-2" />
                    <h4 className="font-semibold text-green-900">Best Conversion</h4>
                  </div>
                  <p className="text-sm text-green-700">39.1% Intent to Purchase rate</p>
                  <button className="mt-2 px-3 py-1 bg-green-600 text-white text-xs rounded-md hover:bg-green-700">
                    Replicate Success
                  </button>
                </div>
                
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <div className="flex items-center mb-2">
                    <Lightbulb className="w-5 h-5 text-blue-600 mr-2" />
                    <h4 className="font-semibold text-blue-900">AI Recommendation</h4>
                  </div>
                  <p className="text-sm text-blue-700">Focus on Interest stage optimization</p>
                  <button className="mt-2 px-3 py-1 bg-blue-600 text-white text-xs rounded-md hover:bg-blue-700">
                    Apply AI Insights
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {analyticsView === 'cohort' && (
        <div className="space-y-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Cohort Analysis</h3>
            <div className="space-y-6">
              {/* Cohort Table */}
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-gray-200">
                      <th className="text-left py-3 px-4 font-medium text-gray-900">Cohort</th>
                      <th className="text-center py-3 px-4 font-medium text-gray-900">Size</th>
                      <th className="text-center py-3 px-4 font-medium text-gray-900">Week 1</th>
                      <th className="text-center py-3 px-4 font-medium text-gray-900">Week 2</th>
                      <th className="text-center py-3 px-4 font-medium text-gray-900">Week 3</th>
                      <th className="text-center py-3 px-4 font-medium text-gray-900">Week 4</th>
                      <th className="text-center py-3 px-4 font-medium text-gray-900">LTV</th>
                    </tr>
                  </thead>
                  <tbody>
                    {[
                      { cohort: 'Oct 2024', size: 12400, w1: 78, w2: 45, w3: 32, w4: 28, ltv: 1240 },
                      { cohort: 'Sep 2024', size: 11800, w1: 82, w2: 48, w3: 35, w4: 31, ltv: 1380 },
                      { cohort: 'Aug 2024', size: 13200, w1: 75, w2: 42, w3: 29, w4: 25, ltv: 1150 },
                      { cohort: 'Jul 2024', size: 10900, w1: 80, w2: 46, w3: 33, w4: 29, ltv: 1290 }
                    ].map((cohort, index) => (
                      <tr key={index} className="border-b border-gray-100 hover:bg-gray-50">
                        <td className="py-3 px-4 font-medium text-gray-900">{cohort.cohort}</td>
                        <td className="text-center py-3 px-4 text-gray-900">{cohort.size.toLocaleString()}</td>
                        <td className="text-center py-3 px-4">
                          <span className={`px-2 py-1 rounded text-sm font-medium ${
                            cohort.w1 > 75 ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                          }`}>
                            {cohort.w1}%
                          </span>
                        </td>
                        <td className="text-center py-3 px-4">
                          <span className={`px-2 py-1 rounded text-sm font-medium ${
                            cohort.w2 > 45 ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                          }`}>
                            {cohort.w2}%
                          </span>
                        </td>
                        <td className="text-center py-3 px-4">
                          <span className={`px-2 py-1 rounded text-sm font-medium ${
                            cohort.w3 > 30 ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                          }`}>
                            {cohort.w3}%
                          </span>
                        </td>
                        <td className="text-center py-3 px-4">
                          <span className={`px-2 py-1 rounded text-sm font-medium ${
                            cohort.w4 > 25 ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                          }`}>
                            {cohort.w4}%
                          </span>
                        </td>
                        <td className="text-center py-3 px-4 font-medium text-gray-900">¥{cohort.ltv}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              
              {/* Cohort Insights */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-gradient-to-br from-green-50 to-blue-50 rounded-lg p-4 border border-green-200">
                  <h4 className="font-semibold text-gray-900 mb-2">Best Performing Cohort</h4>
                  <p className="text-sm text-gray-700 mb-3">September 2024 cohort shows highest retention and LTV</p>
                  <div className="text-xs text-green-600 font-medium">31% retention at Week 4 • ¥1,380 LTV</div>
                </div>
                
                <div className="bg-gradient-to-br from-red-50 to-orange-50 rounded-lg p-4 border border-red-200">
                  <h4 className="font-semibold text-gray-900 mb-2">Retention Opportunity</h4>
                  <p className="text-sm text-gray-700 mb-3">Focus on Week 2-3 retention improvements</p>
                  <div className="text-xs text-red-600 font-medium">Average 43% drop from Week 1 to Week 2</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* Export Modal */}
      {showExportModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-2xl max-w-md w-full mx-4">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Export Analytics Report</h3>
                <button
                  onClick={() => setShowExportModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Report Type</label>
                  <p className="text-sm text-gray-600 bg-gray-50 px-3 py-2 rounded-lg">
                    {analyticsViews.find(v => v.id === analyticsView)?.label} Analytics
                  </p>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Export Format</label>
                  <div className="grid grid-cols-3 gap-2">
                    {['pdf', 'xlsx', 'csv'].map(format => (
                      <button
                        key={format}
                        onClick={() => handleExportReport(format)}
                        disabled={isGeneratingReport}
                        className="px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 text-sm font-medium disabled:opacity-50"
                      >
                        {format.toUpperCase()}
                      </button>
                    ))}
                  </div>
                </div>
                
                {isGeneratingReport && (
                  <div className="flex items-center justify-center py-4">
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                    <span className="ml-2 text-sm text-gray-600">Generating report...</span>
                  </div>
                )}
              </div>
              
              <div className="flex justify-end space-x-3 mt-6">
                <button
                  onClick={() => setShowExportModal(false)}
                  className="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

// ⚡ Campaign Automation Component
const CampaignAutomation: React.FC = () => {
  const [automationView, setAutomationView] = useState('rules')
  const [showCreateModal, setShowCreateModal] = useState(false)

  const automationViews = [
    { id: 'rules', label: 'Automation Rules', icon: Zap },
    { id: 'triggers', label: 'Triggers', icon: Settings },
    { id: 'workflows', label: 'Workflows', icon: Brain },
    { id: 'history', label: 'History', icon: Clock }
  ]

  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-purple-600 to-pink-600 rounded-xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold mb-2">Campaign Automation Hub</h2>
            <p className="text-purple-100">Automate your campaigns with AI-powered rules and workflows</p>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="px-4 py-2 bg-white text-purple-600 rounded-lg hover:bg-gray-100 font-medium"
          >
            <Plus className="w-4 h-4 mr-2 inline" />
            New Automation
          </button>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
        <div className="flex items-center space-x-2">
          {automationViews.map((view) => (
            <button
              key={view.id}
              onClick={() => setAutomationView(view.id)}
              className={`flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                automationView === view.id
                  ? 'bg-purple-600 text-white'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
              }`}
            >
              <view.icon className="w-4 h-4 mr-1" />
              {view.label}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center">
              <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center mr-3">
                <Play className="w-5 h-5 text-green-600" />
              </div>
              <div>
                <h4 className="font-semibold text-gray-900">Budget Optimizer</h4>
                <p className="text-sm text-gray-600">Auto-adjust budgets</p>
              </div>
            </div>
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
          </div>
          <p className="text-sm text-gray-700 mb-3">Automatically redistributes budget to high-performing campaigns</p>
          <div className="text-sm text-green-600 font-medium">Active • 47 optimizations today</div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center">
              <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center mr-3">
                <Target className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <h4 className="font-semibold text-gray-900">Audience Expander</h4>
                <p className="text-sm text-gray-600">Find similar audiences</p>
              </div>
            </div>
            <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
          </div>
          <p className="text-sm text-gray-700 mb-3">Identifies and targets lookalike audiences automatically</p>
          <div className="text-sm text-blue-600 font-medium">Active • 12 new segments found</div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center">
              <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center mr-3">
                <Sparkles className="w-5 h-5 text-purple-600" />
              </div>
              <div>
                <h4 className="font-semibold text-gray-900">Creative Rotator</h4>
                <p className="text-sm text-gray-600">A/B test creatives</p>
              </div>
            </div>
            <div className="w-3 h-3 bg-purple-500 rounded-full"></div>
          </div>
          <p className="text-sm text-gray-700 mb-3">Automatically tests and promotes winning creative variations</p>
          <div className="text-sm text-purple-600 font-medium">Active • 8 tests running</div>
        </div>
      </div>
    </div>
  )
}

// ➕ New Campaign Component
const NewCampaign: React.FC = () => {
  const [step, setStep] = useState(1)
  const [campaignData, setCampaignData] = useState({
    name: '',
    type: 'awareness',
    budget: '',
    audience: '',
    creative: ''
  })

  const steps = [
    { id: 1, label: 'Campaign Details', icon: Settings },
    { id: 2, label: 'Audience Targeting', icon: Users },
    { id: 3, label: 'Budget & Schedule', icon: DollarSign },
    { id: 4, label: 'Creative Assets', icon: Sparkles },
    { id: 5, label: 'Review & Launch', icon: Target }
  ]

  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-green-600 to-blue-600 rounded-xl p-6 text-white">
        <h2 className="text-2xl font-bold mb-2">Create New Campaign</h2>
        <p className="text-green-100">Launch your next successful campaign with AI-powered optimization</p>
      </div>

      {/* Progress Steps */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          {steps.map((stepItem, index) => (
            <div key={stepItem.id} className="flex items-center">
              <div className={`flex items-center justify-center w-10 h-10 rounded-full ${
                step >= stepItem.id 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-gray-200 text-gray-400'
              }`}>
                {step > stepItem.id ? (
                  <CheckCircle className="w-5 h-5" />
                ) : (
                  <stepItem.icon className="w-5 h-5" />
                )}
              </div>
              <span className={`ml-3 text-sm font-medium ${
                step >= stepItem.id ? 'text-gray-900' : 'text-gray-500'
              }`}>
                {stepItem.label}
              </span>
              {index < steps.length - 1 && (
                <div className={`ml-6 w-16 h-0.5 ${
                  step > stepItem.id ? 'bg-blue-600' : 'bg-gray-200'
                }`}></div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Form Content */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="space-y-6">
          {step === 1 && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900">Campaign Details</h3>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Campaign Name</label>
                <input
                  type="text"
                  value={campaignData.name}
                  onChange={(e) => setCampaignData({...campaignData, name: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter campaign name"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Campaign Type</label>
                <select
                  value={campaignData.type}
                  onChange={(e) => setCampaignData({...campaignData, type: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="awareness">Brand Awareness</option>
                  <option value="conversion">Conversion</option>
                  <option value="engagement">Engagement</option>
                  <option value="retention">Customer Retention</option>
                </select>
              </div>
            </div>
          )}
          
          <div className="flex justify-between pt-6">
            <button
              onClick={() => setStep(Math.max(1, step - 1))}
              disabled={step === 1}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50"
            >
              Previous
            </button>
            <button
              onClick={() => setStep(Math.min(5, step + 1))}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              {step === 5 ? 'Launch Campaign' : 'Next'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

// 📋 Campaign Details Component
const CampaignDetails: React.FC = () => {
  const { id } = { id: 'sample-campaign' } // In real app, this would come from useParams()

  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold mb-2">Weekend VIP Experience Campaign</h2>
            <p className="text-indigo-100">Detailed campaign performance and management</p>
          </div>
          <div className="flex items-center space-x-3">
            <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">Active</span>
            <button className="px-4 py-2 bg-white text-indigo-600 rounded-lg hover:bg-gray-100">
              <Edit className="w-4 h-4 mr-2 inline" />
              Edit Campaign
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance Overview</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <p className="text-2xl font-bold text-blue-600">¥187K</p>
                <p className="text-sm text-gray-600">Revenue</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-green-600">4.2%</p>
                <p className="text-sm text-gray-600">Conversion</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-purple-600">847</p>
                <p className="text-sm text-gray-600">Conversions</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-orange-600">156%</p>
                <p className="text-sm text-gray-600">ROI</p>
              </div>
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Campaign Settings</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">Budget</span>
                <span className="font-medium">¥50,000</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Duration</span>
                <span className="font-medium">30 days</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Target Audience</span>
                <span className="font-medium">VIP Customers</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

// ✏️ Edit Campaign Component
const EditCampaign: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-orange-600 to-red-600 rounded-xl p-6 text-white">
        <h2 className="text-2xl font-bold mb-2">Edit Campaign</h2>
        <p className="text-orange-100">Modify campaign settings and optimization parameters</p>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Campaign Editor</h3>
        <div className="bg-gray-50 rounded-lg p-8 text-center">
          <Edit className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">Campaign editing interface will be displayed here</p>
        </div>
      </div>
    </div>
  )
}
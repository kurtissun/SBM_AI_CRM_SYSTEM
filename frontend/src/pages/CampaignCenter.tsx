import React, { useState } from 'react'
import { Routes, Route, Link, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  Target, Plus, Play, Pause, BarChart3, Brain, TrendingUp,
  Calendar, DollarSign, Users, Eye, Settings, Copy, Trash2,
  AlertCircle, CheckCircle, Clock, Zap, Sparkles, Filter,
  Search, Download, Edit, MoreVertical
} from 'lucide-react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Line, Bar, Doughnut } from 'react-chartjs-2'
import { api } from '@/lib/api'
import { toast } from 'react-hot-toast'

const CampaignOverview: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [selectedCampaigns, setSelectedCampaigns] = useState<string[]>([])
  const queryClient = useQueryClient()

  const { data: campaigns, isLoading } = useQuery({
    queryKey: ['campaigns', searchQuery, statusFilter],
    queryFn: () => api.get(`/campaigns?search=${searchQuery}&status=${statusFilter}`),
  })

  const { data: campaignStats } = useQuery({
    queryKey: ['campaign-stats'],
    queryFn: () => api.get('/campaigns/stats'),
  })

  const { data: roiPredictions } = useQuery({
    queryKey: ['roi-predictions'],
    queryFn: () => api.get('/campaign-intelligence/predictions'),
  })

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

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="h-64 bg-gray-200 rounded-xl"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Campaign Command Center</h1>
          <p className="text-gray-600 mt-1">AI-powered campaign optimization and management</p>
        </div>
        <div className="flex items-center space-x-3">
          <button className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
            <Download className="w-4 h-4 mr-2 inline" />
            Export
          </button>
          <Link
            to="/campaigns/new"
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            <Plus className="w-4 h-4 mr-2 inline" />
            New Campaign
          </Link>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Active Campaigns</p>
              <p className="text-3xl font-bold text-gray-900">{campaignStats?.active || 0}</p>
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
              <p className="text-sm font-medium text-gray-600">Total Impressions</p>
              <p className="text-3xl font-bold text-gray-900">{campaignStats?.total_impressions?.toLocaleString() || 0}</p>
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
              <p className="text-sm font-medium text-gray-600">Avg. ROI</p>
              <p className="text-3xl font-bold text-gray-900">{campaignStats?.avg_roi || 0}%</p>
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
              <p className="text-sm font-medium text-gray-600">AI Optimizations</p>
              <p className="text-3xl font-bold text-gray-900">{campaignStats?.ai_optimizations || 0}</p>
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

      {/* AI Recommendations Panel */}
      {roiPredictions && roiPredictions.length > 0 && (
        <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-xl border border-purple-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center">
              <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center mr-3">
                <Sparkles className="w-5 h-5 text-purple-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">AI Campaign Intelligence</h3>
                <p className="text-sm text-gray-600">Optimization recommendations based on your data</p>
              </div>
            </div>
            <Link to="/campaigns/intelligence" className="text-sm text-purple-600 hover:text-purple-700">
              View All →
            </Link>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {roiPredictions.slice(0, 3).map((prediction: any, index: number) => (
              <div key={index} className="bg-white rounded-lg p-4 border border-purple-100">
                <h4 className="font-medium text-gray-900 mb-2">{prediction.title}</h4>
                <p className="text-sm text-gray-600 mb-3">{prediction.description}</p>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-purple-600">
                    +{prediction.potential_improvement}% ROI
                  </span>
                  <button className="px-3 py-1 bg-purple-600 text-white text-xs rounded-md hover:bg-purple-700">
                    Apply
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

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
        {campaigns?.map((campaign: any) => (
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
                      {new Date(campaign.start_date).toLocaleDateString()}
                    </span>
                    <span className="flex items-center">
                      <Users className="w-4 h-4 mr-1" />
                      {campaign.target_audience_size?.toLocaleString() || 0}
                    </span>
                  </div>
                </div>
                <div className="relative">
                  <button className="p-1 hover:bg-gray-100 rounded">
                    <MoreVertical className="w-4 h-4 text-gray-500" />
                  </button>
                </div>
              </div>

              {/* Performance Metrics */}
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div className="bg-blue-50 rounded-lg p-3">
                  <p className="text-sm text-blue-600 font-medium">Impressions</p>
                  <p className="text-lg font-bold text-blue-900">
                    {campaign.impressions?.toLocaleString() || 0}
                  </p>
                </div>
                <div className="bg-green-50 rounded-lg p-3">
                  <p className="text-sm text-green-600 font-medium">Conversions</p>
                  <p className="text-lg font-bold text-green-900">
                    {campaign.conversions?.toLocaleString() || 0}
                  </p>
                </div>
              </div>

              {/* ROI and Performance */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">ROI</span>
                  <span className={`font-semibold ${
                    (campaign.roi || 0) > 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {campaign.roi || 0}%
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Conversion Rate</span>
                  <span className="font-semibold text-gray-900">
                    {campaign.conversion_rate || 0}%
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Budget Spent</span>
                  <span className="font-semibold text-gray-900">
                    ¥{campaign.budget_spent?.toLocaleString() || 0} / ¥{campaign.budget?.toLocaleString() || 0}
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
  
  const tabs = [
    { id: 'overview', label: 'Overview', icon: Target, path: '/campaigns' },
    { id: 'intelligence', label: 'AI Intelligence', icon: Brain, path: '/campaigns/intelligence' },
    { id: 'analytics', label: 'Analytics', icon: BarChart3, path: '/campaigns/analytics' },
    { id: 'automation', label: 'Automation', icon: Zap, path: '/campaigns/automation' },
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
        <Route path="intelligence" element={<div>Campaign Intelligence</div>} />
        <Route path="analytics" element={<div>Campaign Analytics</div>} />
        <Route path="automation" element={<div>Campaign Automation</div>} />
        <Route path="new" element={<div>New Campaign</div>} />
        <Route path=":id" element={<div>Campaign Details</div>} />
        <Route path=":id/edit" element={<div>Edit Campaign</div>} />
      </Routes>
    </div>
  )
}
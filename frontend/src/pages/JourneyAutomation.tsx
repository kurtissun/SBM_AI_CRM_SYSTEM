import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  Play, Pause, Plus, Edit, Trash2, Copy, Settings, Users, Mail, 
  MessageCircle, Phone, Calendar, Clock, Target, Zap, Brain, 
  ArrowRight, Check, AlertTriangle, TrendingUp, Activity, 
  GitBranch, Filter, Search, Download, RefreshCw, Eye,
  Workflow, Route, Timer, Bell, Star, Award, ChevronDown,
  Bot, Database, Globe, Cpu, BarChart3, PieChart
} from 'lucide-react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'react-hot-toast'
import { api } from '@/lib/api'
import { useTranslation } from '@/contexts/TranslationContext'
import { showAlert } from '@/lib/alertService'

export const JourneyAutomation: React.FC = () => {
  const { t } = useTranslation()
  const [selectedView, setSelectedView] = useState('journeys')
  const [selectedJourney, setSelectedJourney] = useState<string | null>(null)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const queryClient = useQueryClient()

  // Fetch journey data
  const { data: journeys } = useQuery({
    queryKey: ['customer-journeys'],
    queryFn: () => api.get('/journeys/all'),
  })

  const { data: automations } = useQuery({
    queryKey: ['automations'],
    queryFn: () => api.get('/automations/all'),
  })

  const { data: journeyStats } = useQuery({
    queryKey: ['journey-stats'],
    queryFn: () => api.get('/journeys/stats'),
  })

  const views = [
    { id: 'journeys', label: 'Customer Journeys', icon: Route },
    { id: 'automation', label: 'Automation Hub', icon: Bot },
    { id: 'workflows', label: 'Workflow Builder', icon: Workflow },
    { id: 'analytics', label: 'Journey Analytics', icon: BarChart3 }
  ]

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{t('journeys.title')}</h1>
          <p className="text-gray-600 mt-1">{t('journeys.subtitle')}</p>
        </div>
        <div className="flex items-center space-x-3">
          <button 
            onClick={() => {
              toast.success('Opening journey creation wizard...')
              setTimeout(() => {
                showAlert(
                  'Journey Creation Wizard',
                  '• Choose journey type (Onboarding/Retention/Re-engagement)\n• Define target audience and triggers\n• Design workflow steps and conditions\n• Set up email templates and messaging\n• Configure timing and delays\n• Define success metrics and goals\n\nJourney wizard is ready to guide you!',
                  'info'
                )
                toast.success('Journey creation wizard opened!')
              }, 1000)
            }}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center"
          >
            <Plus className="w-4 h-4 mr-2" />
            {t('journeys.createJourney')}
          </button>
          <button 
            onClick={() => {
              toast.success('Loading journey preview...')
              setTimeout(() => {
                showAlert(
                  'Journey Preview Mode',
                  '• Live journey visualization\n• Customer flow tracking\n• Real-time touchpoint analysis\n• Conversion funnel view\n• Drop-off point identification\n\nPreview mode is now active!',
                  'info'
                )
                toast.success('Journey preview loaded!')
              }, 1500)
            }}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center"
          >
            <Eye className="w-4 h-4 mr-2" />
            {t('journeys.preview')}
          </button>
          <button 
            onClick={() => {
              toast.success('Exporting journey data...')
              setTimeout(() => {
                const blob = new Blob(['Journey Automation Report - ' + new Date().toLocaleDateString()], { type: 'text/plain' })
                const url = window.URL.createObjectURL(blob)
                const a = document.createElement('a')
                a.href = url
                a.download = `journey-automation-${new Date().toISOString().split('T')[0]}.xlsx`
                a.click()
                window.URL.revokeObjectURL(url)
                toast.success('Journey data exported successfully!')
              }, 2000)
            }}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center"
          >
            <Download className="w-4 h-4 mr-2" />
            {t('common.export')}
          </button>
        </div>
      </div>

      {/* Journey Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">{t('journeys.activeJourneys')}</p>
              <p className="text-3xl font-bold text-gray-900">24</p>
              <p className="text-sm text-green-600">+3 this week</p>
            </div>
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <Route className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">{t('journeys.customersInJourneys')}</p>
              <p className="text-3xl font-bold text-gray-900">2,847</p>
              <p className="text-sm text-green-600">+12% this month</p>
            </div>
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <Users className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">{t('journeys.conversionRate')}</p>
              <p className="text-3xl font-bold text-gray-900">67.8%</p>
              <p className="text-sm text-green-600">+5.2% improvement</p>
            </div>
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
              <Target className="w-6 h-6 text-purple-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">{t('journeys.automationSavings')}</p>
              <p className="text-3xl font-bold text-gray-900">¥184K</p>
              <p className="text-sm text-green-600">Monthly savings</p>
            </div>
            <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
              <Zap className="w-6 h-6 text-orange-600" />
            </div>
          </div>
        </div>
      </div>

      {/* AI Automation Status */}
      <div className="bg-gradient-to-r from-blue-600 via-purple-600 to-green-600 rounded-xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center">
              <Brain className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-lg font-semibold">{t('journeys.aiAutomationEngine')}</h3>
              <p className="text-white/80">
                {t('journeys.aiCapabilities')}
              </p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-2xl font-bold">94.3%</p>
            <p className="text-white/80 text-sm">{t('journeys.automationEfficiency')}</p>
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

      {/* Dynamic Content */}
      {selectedView === 'journeys' && <CustomerJourneys />}
      {selectedView === 'automation' && <AutomationHub />}
      {selectedView === 'workflows' && <WorkflowBuilder />}
      {selectedView === 'analytics' && <JourneyAnalytics />}
    </div>
  )
}

// Customer Journeys Component
const CustomerJourneys: React.FC = () => {
  const { t } = useTranslation()
  const [filterStatus, setFilterStatus] = useState('all')

  const journeys = [
    {
      id: '1',
      name: 'Welcome Series',
      type: 'Onboarding',
      status: 'active',
      customers: 342,
      conversionRate: 78.5,
      revenue: 156000,
      stages: 5,
      lastUpdated: '2 hours ago',
      color: 'blue'
    },
    {
      id: '2', 
      name: 'VIP Nurture Campaign',
      type: 'Retention',
      status: 'active',
      customers: 89,
      conversionRate: 92.1,
      revenue: 289000,
      stages: 7,
      lastUpdated: '1 day ago',
      color: 'purple'
    },
    {
      id: '3',
      name: 'Win-Back Campaign',
      type: 'Re-engagement',
      status: 'paused',
      customers: 156,
      conversionRate: 45.2,
      revenue: 67000,
      stages: 4,
      lastUpdated: '3 days ago',
      color: 'orange'
    },
    {
      id: '4',
      name: 'Product Discovery Journey',
      type: 'Acquisition',
      status: 'active',
      customers: 567,
      conversionRate: 65.8,
      revenue: 198000,
      stages: 6,
      lastUpdated: '1 hour ago',
      color: 'green'
    }
  ]

  const filteredJourneys = filterStatus === 'all' 
    ? journeys 
    : journeys.filter(journey => journey.status === filterStatus)

  return (
    <div className="space-y-6">
      {/* Filters */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">{t('journeys.customerJourneys')}</h3>
          <div className="flex items-center space-x-3">
            <div className="relative">
              <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder={t('journeys.searchJourneys')}
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">{t('journeys.allStatuses')}</option>
              <option value="active">{t('common.active')}</option>
              <option value="paused">{t('common.paused')}</option>
              <option value="draft">{t('common.draft')}</option>
            </select>
          </div>
        </div>
      </div>

      {/* Journey Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {filteredJourneys.map((journey, index) => (
          <motion.div
            key={journey.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow"
          >
            <div className={`h-2 bg-${journey.color}-500`}></div>
            <div className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h4 className="text-lg font-semibold text-gray-900">{journey.name}</h4>
                  <div className="flex items-center space-x-2 mt-1">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      journey.status === 'active' ? 'bg-green-100 text-green-700' :
                      journey.status === 'paused' ? 'bg-yellow-100 text-yellow-700' :
                      'bg-gray-100 text-gray-700'
                    }`}>
                      {journey.status}
                    </span>
                    <span className="text-xs text-gray-500">{journey.type}</span>
                  </div>
                </div>
                <div className="flex items-center space-x-1">
                  <button className="p-2 hover:bg-gray-100 rounded-lg">
                    <Edit className="w-4 h-4 text-gray-400" />
                  </button>
                  <button className="p-2 hover:bg-gray-100 rounded-lg">
                    <Copy className="w-4 h-4 text-gray-400" />
                  </button>
                  <button className="p-2 hover:bg-gray-100 rounded-lg">
                    <Settings className="w-4 h-4 text-gray-400" />
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 mb-4">
                <div>
                  <p className="text-sm text-gray-600">{t('journeys.customers')}</p>
                  <p className="text-xl font-bold text-gray-900">{journey.customers.toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">{t('journeys.conversionRate')}</p>
                  <p className="text-xl font-bold text-green-600">{journey.conversionRate}%</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">{t('journeys.revenue')}</p>
                  <p className="text-xl font-bold text-blue-600">¥{(journey.revenue / 1000).toFixed(0)}K</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">{t('journeys.stages')}</p>
                  <p className="text-xl font-bold text-purple-600">{journey.stages}</p>
                </div>
              </div>

              <div className="flex items-center justify-between pt-4 border-t border-gray-200">
                <span className="text-xs text-gray-500">
                  {t('journeys.lastUpdated')}: {journey.lastUpdated}
                </span>
                <div className="flex items-center space-x-2">
                  <button className="px-3 py-1 text-xs bg-blue-100 text-blue-700 rounded-full hover:bg-blue-200">
                    {t('journeys.viewFlow')}
                  </button>
                  <button className="px-3 py-1 text-xs bg-gray-100 text-gray-700 rounded-full hover:bg-gray-200">
                    {t('journeys.analytics')}
                  </button>
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  )
}

// Automation Hub Component
const AutomationHub: React.FC = () => {
  const { t } = useTranslation()

  const automations = [
    {
      id: '1',
      name: 'Smart Email Sequences',
      type: 'Email Marketing',
      status: 'active',
      triggers: 12,
      actions: 34,
      success_rate: 89.5,
      icon: Mail,
      color: 'blue'
    },
    {
      id: '2',
      name: 'Behavioral Triggers',
      type: 'Customer Behavior',
      status: 'active',
      triggers: 8,
      actions: 23,
      success_rate: 94.2,
      icon: Activity,
      color: 'green'
    },
    {
      id: '3',
      name: 'VIP Escalation',
      type: 'Customer Service',
      status: 'active',
      triggers: 5,
      actions: 15,
      success_rate: 96.8,
      icon: Star,
      color: 'purple'
    },
    {
      id: '4',
      name: 'Loyalty Rewards',
      type: 'Retention',
      status: 'active',
      triggers: 6,
      actions: 18,
      success_rate: 87.3,
      icon: Award,
      color: 'orange'
    }
  ]

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-6">{t('journeys.automationHub')}</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {automations.map((automation, index) => (
            <motion.div
              key={automation.id}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.1 }}
              className="border border-gray-200 rounded-xl p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex items-center justify-between mb-4">
                <div className={`w-12 h-12 bg-${automation.color}-100 rounded-lg flex items-center justify-center`}>
                  <automation.icon className={`w-6 h-6 text-${automation.color}-600`} />
                </div>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  automation.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'
                }`}>
                  {automation.status}
                </span>
              </div>

              <div className="mb-4">
                <h4 className="font-semibold text-gray-900 mb-1">{automation.name}</h4>
                <p className="text-sm text-gray-600">{automation.type}</p>
              </div>

              <div className="grid grid-cols-3 gap-4 mb-4 text-center">
                <div>
                  <p className="text-lg font-bold text-gray-900">{automation.triggers}</p>
                  <p className="text-xs text-gray-600">{t('journeys.triggers')}</p>
                </div>
                <div>
                  <p className="text-lg font-bold text-gray-900">{automation.actions}</p>
                  <p className="text-xs text-gray-600">{t('journeys.actions')}</p>
                </div>
                <div>
                  <p className="text-lg font-bold text-green-600">{automation.success_rate}%</p>
                  <p className="text-xs text-gray-600">{t('journeys.successRate')}</p>
                </div>
              </div>

              <div className="flex items-center space-x-2">
                <button className="flex-1 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm">
                  {t('journeys.configure')}
                </button>
                <button className="px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 text-sm">
                  {t('journeys.analytics')}
                </button>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  )
}

// Workflow Builder Component  
const WorkflowBuilder: React.FC = () => {
  const { t } = useTranslation()

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-gray-900">{t('journeys.workflowBuilder')}</h3>
          <button 
            onClick={() => {
              toast.success('Creating new workflow...')
              setTimeout(() => {
                showAlert(
                  'New Workflow Creation',
                  '• Workflow Name: [Enter name]\n• Trigger Type: [Customer action/Time-based/Event-based]\n• Target Audience: [Define segments]\n• Workflow Steps: [Design automation flow]\n• Conditions & Logic: [Set decision points]\n• Actions & Responses: [Configure responses]\n\nWorkflow template created!',
                  'success'
                )
                toast.success('New workflow template created!')
              }, 1000)
            }}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center"
          >
            <Plus className="w-4 h-4 mr-2" />
            {t('journeys.newWorkflow')}
          </button>
        </div>

        {/* Workflow Canvas Placeholder */}
        <div className="bg-gray-50 border-2 border-dashed border-gray-300 rounded-xl p-12 text-center">
          <div className="max-w-md mx-auto">
            <Workflow className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h4 className="text-lg font-semibold text-gray-900 mb-2">{t('journeys.dragDropBuilder')}</h4>
            <p className="text-gray-600 mb-6">{t('journeys.builderDescription')}</p>
            <button 
              onClick={() => {
                toast.success('Launching workflow builder...')
                setTimeout(() => {
                  showAlert(
                    'Workflow Builder Features',
                    '✓ Drag-and-drop interface\n✓ Pre-built templates and components\n✓ Visual workflow designer\n✓ Real-time validation and testing\n✓ Advanced logic and conditions\n✓ Integration with all SBM systems\n\nWorkflow builder is now active!',
                    'success'
                  )
                  toast.success('Workflow builder launched successfully!')
                }, 1500)
              }}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              {t('journeys.startBuilding')}
            </button>
          </div>
        </div>

        {/* Workflow Components */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mt-8">
          <div className="space-y-4">
            <h4 className="font-medium text-gray-900">{t('journeys.triggers')}</h4>
            <div className="space-y-2">
              {[
                { icon: Users, label: t('journeys.newCustomer') },
                { icon: Mail, label: t('journeys.emailOpened') },
                { icon: Calendar, label: t('journeys.dateReached') },
                { icon: Target, label: t('journeys.goalAchieved') }
              ].map((trigger, index) => (
                <div key={index} className="flex items-center p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
                  <trigger.icon className="w-5 h-5 text-blue-600 mr-3" />
                  <span className="text-sm text-gray-700">{trigger.label}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="space-y-4">
            <h4 className="font-medium text-gray-900">{t('journeys.conditions')}</h4>
            <div className="space-y-2">
              {[
                { icon: GitBranch, label: t('journeys.ifThenLogic') },
                { icon: Clock, label: t('journeys.timeDelay') },
                { icon: Filter, label: t('journeys.dataFilter') },
                { icon: Target, label: t('journeys.segmentCheck') }
              ].map((condition, index) => (
                <div key={index} className="flex items-center p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
                  <condition.icon className="w-5 h-5 text-purple-600 mr-3" />
                  <span className="text-sm text-gray-700">{condition.label}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="space-y-4">
            <h4 className="font-medium text-gray-900">{t('journeys.actions')}</h4>
            <div className="space-y-2">
              {[
                { icon: Mail, label: t('journeys.sendEmail') },
                { icon: MessageCircle, label: t('journeys.sendSMS') },
                { icon: Bell, label: t('journeys.createTask') },
                { icon: Star, label: t('journeys.updateScore') }
              ].map((action, index) => (
                <div key={index} className="flex items-center p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
                  <action.icon className="w-5 h-5 text-green-600 mr-3" />
                  <span className="text-sm text-gray-700">{action.label}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="space-y-4">
            <h4 className="font-medium text-gray-900">{t('journeys.analytics')}</h4>
            <div className="space-y-2">
              {[
                { icon: BarChart3, label: t('journeys.trackConversion') },
                { icon: TrendingUp, label: t('journeys.measureROI') },
                { icon: Activity, label: t('journeys.monitorEngagement') },
                { icon: PieChart, label: t('journeys.analyzeFlow') }
              ].map((analytic, index) => (
                <div key={index} className="flex items-center p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
                  <analytic.icon className="w-5 h-5 text-orange-600 mr-3" />
                  <span className="text-sm text-gray-700">{analytic.label}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

// Journey Analytics Component
const JourneyAnalytics: React.FC = () => {
  const { t } = useTranslation()

  const analyticsData = [
    {
      journey: 'Welcome Series',
      totalCustomers: 2847,
      completed: 2156,
      dropOffRate: 24.3,
      avgTimeToComplete: '7.2 days',
      revenue: 456000,
      roi: 189
    },
    {
      journey: 'VIP Nurture',
      totalCustomers: 892,
      completed: 823,
      dropOffRate: 7.7,
      avgTimeToComplete: '12.5 days', 
      revenue: 892000,
      roi: 245
    },
    {
      journey: 'Win-Back Campaign',
      totalCustomers: 1456,
      completed: 658,
      dropOffRate: 54.8,
      avgTimeToComplete: '5.1 days',
      revenue: 234000,
      roi: 67
    }
  ]

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-6">{t('journeys.journeyAnalytics')}</h3>
        
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-4 font-medium text-gray-900">{t('journeys.journeyName')}</th>
                <th className="text-left py-3 px-4 font-medium text-gray-900">{t('journeys.totalCustomers')}</th>
                <th className="text-left py-3 px-4 font-medium text-gray-900">{t('journeys.completed')}</th>
                <th className="text-left py-3 px-4 font-medium text-gray-900">{t('journeys.dropOffRate')}</th>
                <th className="text-left py-3 px-4 font-medium text-gray-900">{t('journeys.avgTime')}</th>
                <th className="text-left py-3 px-4 font-medium text-gray-900">{t('journeys.revenue')}</th>
                <th className="text-left py-3 px-4 font-medium text-gray-900">{t('journeys.roi')}</th>
              </tr>
            </thead>
            <tbody>
              {analyticsData.map((data, index) => (
                <tr key={index} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="py-4 px-4 font-medium text-gray-900">{data.journey}</td>
                  <td className="py-4 px-4 text-gray-700">{data.totalCustomers.toLocaleString()}</td>
                  <td className="py-4 px-4 text-gray-700">{data.completed.toLocaleString()}</td>
                  <td className="py-4 px-4">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      data.dropOffRate < 20 ? 'bg-green-100 text-green-700' :
                      data.dropOffRate < 40 ? 'bg-yellow-100 text-yellow-700' :
                      'bg-red-100 text-red-700'
                    }`}>
                      {data.dropOffRate}%
                    </span>
                  </td>
                  <td className="py-4 px-4 text-gray-700">{data.avgTimeToComplete}</td>
                  <td className="py-4 px-4 font-medium text-green-600">¥{(data.revenue / 1000).toFixed(0)}K</td>
                  <td className="py-4 px-4 font-medium text-blue-600">{data.roi}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Performance Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h4 className="font-semibold text-gray-900 mb-4">{t('journeys.overallPerformance')}</h4>
          <div className="space-y-4">
            <div className="flex justify-between">
              <span className="text-gray-600">{t('journeys.avgCompletionRate')}</span>
              <span className="font-bold text-green-600">76.8%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">{t('journeys.avgRevenuePer')}</span>
              <span className="font-bold text-blue-600">¥198</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">{t('journeys.totalROI')}</span>
              <span className="font-bold text-purple-600">167%</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h4 className="font-semibold text-gray-900 mb-4">{t('journeys.topPerformers')}</h4>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-gray-700">VIP Nurture</span>
              <span className="text-green-600 font-medium">245% ROI</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-700">Welcome Series</span>
              <span className="text-green-600 font-medium">189% ROI</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-700">Product Discovery</span>
              <span className="text-green-600 font-medium">156% ROI</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h4 className="font-semibold text-gray-900 mb-4">{t('journeys.improvementOpportunities')}</h4>
          <div className="space-y-3">
            <div className="p-3 bg-yellow-50 rounded-lg">
              <p className="text-sm font-medium text-yellow-800">{t('journeys.highDropOff')}</p>
              <p className="text-xs text-yellow-600">{t('journeys.optimizeSteps')}</p>
            </div>
            <div className="p-3 bg-blue-50 rounded-lg">
              <p className="text-sm font-medium text-blue-800">{t('journeys.timeOptimization')}</p>
              <p className="text-xs text-blue-600">{t('journeys.reduceCompletionTime')}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default JourneyAutomation
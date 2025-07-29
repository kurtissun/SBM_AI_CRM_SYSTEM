import React, { useState } from 'react'
import { Routes, Route, Link, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  Users, Search, Filter, Download, Plus, BarChart3, Brain,
  Network, Eye, TrendingUp, MapPin, Calendar, Mail, Phone,
  ShoppingBag, Star, Award, Activity, Zap
} from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'

const CustomerOverview: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedSegment, setSelectedSegment] = useState('all')
  const [selectedView, setSelectedView] = useState('grid')

  const { data: customers, isLoading } = useQuery({
    queryKey: ['customers', searchQuery, selectedSegment],
    queryFn: () => api.get(`/customers?search=${searchQuery}&segment=${selectedSegment}`),
  })

  const { data: customerStats } = useQuery({
    queryKey: ['customer-stats'],
    queryFn: () => api.get('/customers/stats'),
  })

  const segments = [
    { id: 'all', label: 'All Customers', count: customerStats?.total || 0 },
    { id: 'vip', label: 'VIP Members', count: customerStats?.vip || 0 },
    { id: 'regular', label: 'Regular', count: customerStats?.regular || 0 },
    { id: 'new', label: 'New Visitors', count: customerStats?.new || 0 },
    { id: 'inactive', label: 'Inactive', count: customerStats?.inactive || 0 },
  ]

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="h-48 bg-gray-200 rounded-xl"></div>
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
          <h1 className="text-2xl font-bold text-gray-900">Customer Intelligence</h1>
          <p className="text-gray-600 mt-1">360° customer insights powered by AI</p>
        </div>
        <div className="flex items-center space-x-3">
          <button className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
            <Download className="w-4 h-4 mr-2 inline" />
            Export
          </button>
          <Link
            to="/customers/new"
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            <Plus className="w-4 h-4 mr-2 inline" />
            Add Customer
          </Link>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Customers</p>
              <p className="text-3xl font-bold text-gray-900">{customerStats?.total?.toLocaleString() || 0}</p>
              <p className="text-sm text-green-600 flex items-center">
                <TrendingUp className="w-4 h-4 mr-1" />
                +12% vs last month
              </p>
            </div>
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <Users className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Avg. Lifetime Value</p>
              <p className="text-3xl font-bold text-gray-900">¥{customerStats?.avg_clv?.toLocaleString() || 0}</p>
              <p className="text-sm text-green-600 flex items-center">
                <TrendingUp className="w-4 h-4 mr-1" />
                +8.5% vs last month
              </p>
            </div>
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <Star className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Retention Rate</p>
              <p className="text-3xl font-bold text-gray-900">{customerStats?.retention_rate || 0}%</p>
              <p className="text-sm text-red-600 flex items-center">
                <TrendingUp className="w-4 h-4 mr-1 rotate-180" />
                -2.1% vs last month
              </p>
            </div>
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
              <Activity className="w-6 h-6 text-purple-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Active Today</p>
              <p className="text-3xl font-bold text-gray-900">{customerStats?.active_today || 0}</p>
              <p className="text-sm text-blue-600 flex items-center">
                <Zap className="w-4 h-4 mr-1" />
                Live tracking
              </p>
            </div>
            <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
              <Eye className="w-6 h-6 text-orange-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
          {/* Search */}
          <div className="flex items-center space-x-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search customers..."
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <button className="flex items-center px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
              <Filter className="w-4 h-4 mr-2" />
              Filters
            </button>
          </div>

          {/* Segment Tabs */}
          <div className="flex items-center space-x-1 bg-gray-100 p-1 rounded-lg">
            {segments.map((segment) => (
              <button
                key={segment.id}
                onClick={() => setSelectedSegment(segment.id)}
                className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                  selectedSegment === segment.id
                    ? 'bg-white text-blue-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                {segment.label}
                <span className="ml-2 text-xs text-gray-500">({segment.count})</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Customer Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {customers?.map((customer: any) => (
          <motion.div
            key={customer.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow cursor-pointer"
          >
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center space-x-3">
                <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                  <span className="text-white font-semibold text-lg">
                    {customer.name?.charAt(0) || 'U'}
                  </span>
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">{customer.name}</h3>
                  <p className="text-sm text-gray-600">{customer.email}</p>
                </div>
              </div>
              <div className="flex items-center space-x-1">
                {customer.membership_level === '钻卡会员' && (
                  <Award className="w-5 h-5 text-yellow-500" />
                )}
                {customer.membership_level === '金卡会员' && (
                  <Award className="w-5 h-5 text-gray-400" />
                )}
                {customer.membership_level === '橙卡会员' && (
                  <Award className="w-5 h-5 text-orange-500" />
                )}
              </div>
            </div>

            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Total Spent</span>
                <span className="font-semibold text-gray-900">¥{customer.total_spent?.toLocaleString() || 0}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Purchase Frequency</span>
                <span className="font-semibold text-gray-900">{customer.purchase_frequency || 0}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">CLV Prediction</span>
                <span className="font-semibold text-green-600">¥{customer.predicted_clv?.toLocaleString() || 0}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Churn Risk</span>
                <span className={`text-sm font-medium ${
                  customer.churn_risk === 'high' ? 'text-red-600' :
                  customer.churn_risk === 'medium' ? 'text-yellow-600' : 'text-green-600'
                }`}>
                  {customer.churn_risk || 'Low'}
                </span>
              </div>
            </div>

            <div className="mt-4 pt-4 border-t border-gray-200">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2 text-sm text-gray-600">
                  <MapPin className="w-4 h-4" />
                  <span>{customer.location || 'Unknown'}</span>
                </div>
                <div className="flex items-center space-x-1">
                  <Link
                    to={`/customers/${customer.id}`}
                    className="p-1 hover:bg-gray-100 rounded"
                  >
                    <Eye className="w-4 h-4 text-gray-500" />
                  </Link>
                  <button className="p-1 hover:bg-gray-100 rounded">
                    <Mail className="w-4 h-4 text-gray-500" />
                  </button>
                  <button className="p-1 hover:bg-gray-100 rounded">
                    <Phone className="w-4 h-4 text-gray-500" />
                  </button>
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {(!customers || customers.length === 0) && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
          <Users className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No customers found</h3>
          <p className="text-gray-600 mb-6">Get started by adding your first customer or importing customer data.</p>
          <div className="flex items-center justify-center space-x-4">
            <Link
              to="/customers/new"
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Add Customer
            </Link>
            <button className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
              Import Data
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

const CustomerDetails: React.FC = () => {
  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold">Customer Details</h2>
      {/* Customer detail view implementation */}
    </div>
  )
}

const CustomerAnalytics: React.FC = () => {
  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold">Customer Analytics</h2>
      {/* Customer analytics implementation */}
    </div>
  )
}

const CustomerNetworkView: React.FC = () => {
  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold">Customer Network</h2>
      {/* Network visualization implementation */}
    </div>
  )
}

export const CustomerIntelligence: React.FC = () => {
  const location = useLocation()
  
  const tabs = [
    { id: 'overview', label: 'Overview', icon: Users, path: '/customers' },
    { id: 'analytics', label: 'Analytics', icon: BarChart3, path: '/customers/analytics' },
    { id: 'network', label: 'Network', icon: Network, path: '/customers/network' },
    { id: 'ai-insights', label: 'AI Insights', icon: Brain, path: '/customers/insights' },
  ]

  const isActive = (path: string) => {
    if (path === '/customers') return location.pathname === '/customers'
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
        <Route index element={<CustomerOverview />} />
        <Route path="analytics" element={<CustomerAnalytics />} />
        <Route path="network" element={<CustomerNetworkView />} />
        <Route path="insights" element={<div>AI Insights Coming Soon</div>} />
        <Route path=":id" element={<CustomerDetails />} />
      </Routes>
    </div>
  )
}
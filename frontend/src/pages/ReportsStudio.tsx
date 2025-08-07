import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  FileText, Download, Share, Calendar, Filter, Search, Plus,
  BarChart3, PieChart, LineChart, TrendingUp, Users, DollarSign,
  Clock, Settings, Eye, Edit, Trash2, Copy, Star
} from 'lucide-react'
import { useTranslation } from '@/contexts/TranslationContext'

export const ReportsStudio: React.FC = () => {
  const { t } = useTranslation()
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [selectedView, setSelectedView] = useState('gallery')

  const categories = [
    { id: 'all', label: 'All Reports', count: 24 },
    { id: 'financial', label: 'Financial', count: 8 },
    { id: 'customer', label: 'Customer Analytics', count: 6 },
    { id: 'operations', label: 'Operations', count: 5 },
    { id: 'marketing', label: 'Marketing', count: 5 }
  ]

  const reports = [
    {
      id: '1',
      title: 'Monthly Revenue Analysis',
      description: 'Comprehensive revenue breakdown with forecasting',
      category: 'financial',
      type: 'Dashboard',
      lastUpdated: '2 hours ago',
      author: 'Finance Team',
      views: 1247,
      favorite: true,
      status: 'published'
    },
    {
      id: '2',
      title: 'Customer Segmentation Report',
      description: 'Detailed customer behavior and segmentation analysis',
      category: 'customer',
      type: 'Report',
      lastUpdated: '1 day ago',
      author: 'Marketing Team',
      views: 892,
      favorite: false,
      status: 'published'
    },
    {
      id: '3',
      title: 'Campaign Performance Dashboard',
      description: 'Real-time campaign metrics and ROI analysis',
      category: 'marketing',
      type: 'Dashboard',
      lastUpdated: '3 hours ago',
      author: 'Campaign Manager',
      views: 564,
      favorite: true,
      status: 'published'
    },
    {
      id: '4',
      title: 'Operations Efficiency Report',
      description: 'System performance and operational metrics',
      category: 'operations',
      type: 'Report',
      lastUpdated: '6 hours ago',
      author: 'Operations Team',
      views: 423,
      favorite: false,
      status: 'draft'
    }
  ]

  const filteredReports = selectedCategory === 'all' 
    ? reports 
    : reports.filter(report => report.category === selectedCategory)

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Reports Studio</h1>
          <p className="text-gray-600 mt-1">Advanced reporting and business intelligence platform</p>
        </div>
        <div className="flex items-center space-x-3">
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center">
            <Plus className="w-4 h-4 mr-2" />
            Create Report
          </button>
          <button className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center">
            <Download className="w-4 h-4 mr-2" />
            Export All
          </button>
        </div>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Reports</p>
              <p className="text-3xl font-bold text-gray-900">24</p>
            </div>
            <FileText className="w-8 h-8 text-blue-600" />
          </div>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Active Users</p>
              <p className="text-3xl font-bold text-gray-900">156</p>
            </div>
            <Users className="w-8 h-8 text-green-600" />
          </div>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Monthly Views</p>
              <p className="text-3xl font-bold text-gray-900">12.4K</p>
            </div>
            <Eye className="w-8 h-8 text-purple-600" />
          </div>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Automation Rate</p>
              <p className="text-3xl font-bold text-gray-900">84%</p>
            </div>
            <TrendingUp className="w-8 h-8 text-orange-600" />
          </div>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
          <div className="flex items-center space-x-4">
            <div className="relative">
              <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Search reports..."
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <select className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option>All Types</option>
              <option>Dashboards</option>
              <option>Reports</option>
              <option>Analytics</option>
            </select>
          </div>
          <div className="flex items-center space-x-2">
            {categories.map((category) => (
              <button
                key={category.id}
                onClick={() => setSelectedCategory(category.id)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  selectedCategory === category.id
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {category.label} ({category.count})
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Reports Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredReports.map((report, index) => (
          <motion.div
            key={report.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow"
          >
            <div className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    <h3 className="font-semibold text-gray-900">{report.title}</h3>
                    {report.favorite && <Star className="w-4 h-4 text-yellow-500 fill-current" />}
                  </div>
                  <p className="text-sm text-gray-600 mb-3">{report.description}</p>
                  
                  <div className="flex items-center space-x-4 text-xs text-gray-500">
                    <span>{report.type}</span>
                    <span>{report.views} views</span>
                    <span>{report.lastUpdated}</span>
                  </div>
                </div>
              </div>
              
              <div className="flex items-center justify-between pt-4 border-t border-gray-200">
                <div className="flex items-center space-x-2">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    report.status === 'published' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'
                  }`}>
                    {report.status}
                  </span>
                  <span className="text-xs text-gray-500">by {report.author}</span>
                </div>
                
                <div className="flex items-center space-x-1">
                  <button className="p-2 hover:bg-gray-100 rounded-lg">
                    <Eye className="w-4 h-4 text-gray-400" />
                  </button>
                  <button className="p-2 hover:bg-gray-100 rounded-lg">
                    <Edit className="w-4 h-4 text-gray-400" />
                  </button>
                  <button className="p-2 hover:bg-gray-100 rounded-lg">
                    <Share className="w-4 h-4 text-gray-400" />
                  </button>
                  <button className="p-2 hover:bg-gray-100 rounded-lg">
                    <Download className="w-4 h-4 text-gray-400" />
                  </button>
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Quick Report Builder */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Report Builder</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            { icon: BarChart3, title: 'Revenue Report', desc: 'Financial performance analysis' },
            { icon: PieChart, title: 'Customer Segments', desc: 'Customer behavior breakdown' },
            { icon: LineChart, title: 'Trend Analysis', desc: 'Historical trend tracking' },
            { icon: TrendingUp, title: 'Growth Metrics', desc: 'Business growth indicators' }
          ].map((template, index) => (
            <div key={index} className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors">
              <template.icon className="w-8 h-8 text-blue-600 mb-3" />
              <h4 className="font-medium text-gray-900 mb-1">{template.title}</h4>
              <p className="text-sm text-gray-600">{template.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default ReportsStudio
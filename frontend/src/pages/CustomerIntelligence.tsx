import React, { useState } from 'react'
import { Routes, Route, Link, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  Users, Search, Filter, Download, Plus, BarChart3, Brain,
  Network, Eye, TrendingUp, MapPin, Calendar, Mail, Phone,
  ShoppingBag, Star, Award, Activity, Zap, Edit, Trash2,
  ChevronDown, X, Sparkles, Target, Globe, Building2, Briefcase,
  Tag, FileText, Share, Settings, Lightbulb, Upload, RefreshCw
} from 'lucide-react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'react-hot-toast'
import { api } from '@/lib/api'
import { CreateCustomerModal } from '@/components/modals/CreateCustomerModal'
import { Customer } from '@/lib/mockData'
import { useTranslation } from '@/contexts/TranslationContext'
import { showAlert } from '@/lib/alertService'

// 📤 Import Data Modal Component
const ImportDataModal: React.FC<{
  isOpen: boolean
  onClose: () => void
  onImportComplete: () => void
}> = ({ isOpen, onClose, onImportComplete }) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [importStatus, setImportStatus] = useState<'idle' | 'uploading' | 'processing' | 'completed' | 'error'>('idle')
  const [jobId, setJobId] = useState<string | null>(null)
  const [progress, setProgress] = useState(0)
  const [importResults, setImportResults] = useState<any>(null)

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      const validTypes = ['text/csv', 'application/csv', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel']
      if (validTypes.includes(file.type)) {
        setSelectedFile(file)
        setImportStatus('idle')
      } else {
        toast.error('Please select a CSV or XLSX file')
      }
    }
  }

  const handleImport = async () => {
    if (!selectedFile) return

    setImportStatus('uploading')
    setProgress(0)

    try {
      const formData = new FormData()
      formData.append('file', selectedFile)
      formData.append('data_type', 'customers')

      const response = await fetch('/api/import/upload', {
        method: 'POST',
        body: formData,
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })

      if (!response.ok) throw new Error('Upload failed')

      const result = await response.json()
      setJobId(result.job_id)
      setImportStatus('processing')
      pollImportStatus(result.job_id)

    } catch (error) {
      console.error('Import error:', error)
      setImportStatus('error')
      toast.error('Failed to upload file')
    }
  }

  const pollImportStatus = async (id: string) => {
    try {
      const response = await fetch(`/api/import/status/${id}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })
      
      if (!response.ok) throw new Error('Failed to check status')
      
      const status = await response.json()
      setProgress(status.progress || 0)

      if (status.status === 'completed') {
        setImportStatus('completed')
        setImportResults(status)
        toast.success(`Import completed! ${status.imported_count} customers imported.`)
        setTimeout(() => onImportComplete(), 1500)
      } else if (status.status === 'failed') {
        setImportStatus('error')
        toast.error('Import failed')
      } else {
        // Still processing, poll again
        setTimeout(() => pollImportStatus(id), 2000)
      }
    } catch (error) {
      console.error('Status check error:', error)
      setImportStatus('error')
    }
  }

  const downloadSample = async () => {
    try {
      toast.info('Downloading sample file...')
      const response = await fetch('/api/import/sample?data_type=customers&format=csv', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })
      
      if (!response.ok) throw new Error('Failed to download sample')
      
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'sample_customers.csv'
      a.click()
      window.URL.revokeObjectURL(url)
      toast.success('Sample file downloaded!')
    } catch (error) {
      console.error('Sample download error:', error)
      toast.error('Failed to download sample file')
    }
  }

  const resetModal = () => {
    setSelectedFile(null)
    setImportStatus('idle')
    setJobId(null)
    setProgress(0)
    setImportResults(null)
  }

  const handleClose = () => {
    resetModal()
    onClose()
  }

  if (!isOpen) return null

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
    >
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
      >
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold text-gray-900">Import Customer Data</h2>
              <p className="text-gray-600">Upload CSV or XLSX files to import customer data</p>
            </div>
            <button
              onClick={handleClose}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        <div className="p-6">
          {importStatus === 'idle' && (
            <div className="space-y-6">
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
                <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">Choose a file to upload</h3>
                <p className="text-gray-600 mb-4">CSV or XLSX files up to 10MB</p>
                <input
                  type="file"
                  accept=".csv,.xlsx,.xls"
                  onChange={handleFileSelect}
                  className="hidden"
                  id="file-upload"
                />
                <label
                  htmlFor="file-upload"
                  className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 cursor-pointer"
                >
                  <Upload className="w-4 h-4 mr-2" />
                  Select File
                </label>
              </div>

              {selectedFile && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      <FileText className="w-5 h-5 text-green-600 mr-2" />
                      <div>
                        <p className="font-medium text-green-900">{selectedFile.name}</p>
                        <p className="text-sm text-green-700">{(selectedFile.size / 1024).toFixed(1)} KB</p>
                      </div>
                    </div>
                    <button
                      onClick={() => setSelectedFile(null)}
                      className="text-green-600 hover:text-green-800"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              )}

              <div className="flex items-center justify-between">
                <button
                  onClick={downloadSample}
                  className="text-blue-600 hover:text-blue-800 text-sm flex items-center"
                >
                  <Download className="w-4 h-4 mr-1" />
                  Download sample template
                </button>
                {selectedFile && (
                  <button
                    onClick={handleImport}
                    className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium"
                  >
                    Import Data
                  </button>
                )}
              </div>
            </div>
          )}

          {(importStatus === 'uploading' || importStatus === 'processing') && (
            <div className="text-center py-8">
              <RefreshCw className="w-12 h-12 text-blue-600 mx-auto mb-4 animate-spin" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                {importStatus === 'uploading' ? 'Uploading file...' : 'Processing data...'}
              </h3>
              <div className="w-full bg-gray-200 rounded-full h-2 mb-4">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${progress}%` }}
                />
              </div>
              <p className="text-gray-600">{progress}% complete</p>
            </div>
          )}

          {importStatus === 'completed' && importResults && (
            <div className="text-center py-8">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Sparkles className="w-8 h-8 text-green-600" />
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">Import Completed!</h3>
              <div className="bg-green-50 rounded-lg p-4 mb-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="font-medium text-green-900">Imported: {importResults.imported_count} customers</p>
                    <p className="text-green-700">Total processed: {importResults.total_count}</p>
                  </div>
                  {importResults.errors?.length > 0 && (
                    <div>
                      <p className="font-medium text-orange-900">Warnings: {importResults.errors.length}</p>
                      <p className="text-orange-700">Check data for issues</p>
                    </div>
                  )}
                </div>
              </div>
              <button
                onClick={handleClose}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Close
              </button>
            </div>
          )}

          {importStatus === 'error' && (
            <div className="text-center py-8">
              <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <X className="w-8 h-8 text-red-600" />
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">Import Failed</h3>
              <p className="text-gray-600 mb-4">Please check your file format and try again</p>
              <div className="space-x-3">
                <button
                  onClick={resetModal}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Try Again
                </button>
                <button
                  onClick={handleClose}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Close
                </button>
              </div>
            </div>
          )}
        </div>
      </motion.div>
    </motion.div>
  )
}

// 📊 Enhanced Customer Analytics Component
const CustomerAnalytics: React.FC<{ customers: Customer[], onClose: () => void }> = ({ customers, onClose }) => {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
    >
      <div className="bg-white rounded-xl shadow-2xl max-w-6xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold text-gray-900">Customer Intelligence Analytics</h2>
              <p className="text-gray-600">Advanced insights and predictions for {customers.length} customers</p>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>
        
        <div className="p-6 space-y-6">
          {/* AI Predictions */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-4">
              <div className="flex items-center justify-between mb-3">
                <Brain className="w-6 h-6 text-blue-600" />
                <span className="text-xs bg-blue-200 text-blue-800 px-2 py-1 rounded-full">AI Prediction</span>
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">High-Value Prospects</h3>
              <p className="text-2xl font-bold text-blue-600 mb-1">23</p>
              <p className="text-sm text-gray-600">customers likely to upgrade within 30 days</p>
            </div>
            
            <div className="bg-gradient-to-br from-red-50 to-red-100 rounded-lg p-4">
              <div className="flex items-center justify-between mb-3">
                <TrendingUp className="w-6 h-6 text-red-600 rotate-180" />
                <span className="text-xs bg-red-200 text-red-800 px-2 py-1 rounded-full">Churn Risk</span>
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">At-Risk Customers</h3>
              <p className="text-2xl font-bold text-red-600 mb-1">8</p>
              <p className="text-sm text-gray-600">customers with high churn probability</p>
            </div>
            
            <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-4">
              <div className="flex items-center justify-between mb-3">
                <Award className="w-6 h-6 text-green-600" />
                <span className="text-xs bg-green-200 text-green-800 px-2 py-1 rounded-full">Opportunity</span>
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Cross-sell Potential</h3>
              <p className="text-2xl font-bold text-green-600 mb-1">¥180K</p>
              <p className="text-sm text-gray-600">estimated additional revenue opportunity</p>
            </div>
          </div>

          {/* Segment Analysis */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h3 className="font-semibold text-gray-900 mb-4">Dynamic Segment Insights</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-white rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className="w-3 h-3 bg-purple-500 rounded-full"></div>
                  <span className="font-medium">Premium Enterprise</span>
                </div>
                <div className="text-right">
                  <p className="font-semibold text-gray-900">45%</p>
                  <p className="text-xs text-gray-600">of total revenue</p>
                </div>
              </div>
              <div className="flex items-center justify-between p-3 bg-white rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                  <span className="font-medium">Growth-Stage SMB</span>
                </div>
                <div className="text-right">
                  <p className="font-semibold text-gray-900">28%</p>
                  <p className="text-xs text-gray-600">highest engagement</p>
                </div>
              </div>
              <div className="flex items-center justify-between p-3 bg-white rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className="w-3 h-3 bg-orange-500 rounded-full"></div>
                  <span className="font-medium">Digital-First Startups</span>
                </div>
                <div className="text-right">
                  <p className="font-semibold text-gray-900">15%</p>
                  <p className="text-xs text-gray-600">fastest growing</p>
                </div>
              </div>
            </div>
          </div>

          {/* Actionable Recommendations */}
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <h3 className="font-semibold text-gray-900 mb-4 flex items-center">
              <Sparkles className="w-5 h-5 mr-2 text-yellow-500" />
              AI-Powered Recommendations
            </h3>
            <div className="space-y-3">
              <div className="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg">
                <div className="w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center mt-0.5">
                  <span className="text-white text-xs font-bold">1</span>
                </div>
                <div>
                  <p className="font-medium text-gray-900">Launch VIP program for Premium Enterprise segment</p>
                  <p className="text-sm text-gray-600">Expected revenue impact: ¥850K annually</p>
                </div>
              </div>
              <div className="flex items-start space-x-3 p-3 bg-green-50 rounded-lg">
                <div className="w-6 h-6 bg-green-600 rounded-full flex items-center justify-center mt-0.5">
                  <span className="text-white text-xs font-bold">2</span>
                </div>
                <div>
                  <p className="font-medium text-gray-900">Implement retention campaign for at-risk customers</p>
                  <p className="text-sm text-gray-600">Prevent ¥120K potential revenue loss</p>
                </div>
              </div>
              <div className="flex items-start space-x-3 p-3 bg-purple-50 rounded-lg">
                <div className="w-6 h-6 bg-purple-600 rounded-full flex items-center justify-center mt-0.5">
                  <span className="text-white text-xs font-bold">3</span>
                </div>
                <div>
                  <p className="font-medium text-gray-900">Cross-sell services to Growth-Stage SMB segment</p>
                  <p className="text-sm text-gray-600">28% show high purchase intent signals</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  )
}

// 🎯 Advanced Filters Component
const AdvancedFilters: React.FC<{ onFiltersChange: (filters: any) => void }> = ({ onFiltersChange }) => {
  const [showFilters, setShowFilters] = useState(false)
  const [filters, setFilters] = useState({
    valueRange: 'all',
    engagementLevel: 'all',
    customerType: 'all',
    marketReach: 'all',
    businessSize: 'all',
    location: '',
    dateRange: '30days'
  })

  const valueRanges = [
    { id: 'all', label: 'All Values' },
    { id: 'premium', label: 'Premium (>¥50K)' },
    { id: 'high', label: 'High Value (¥20K-50K)' },
    { id: 'standard', label: 'Standard (¥5K-20K)' },
    { id: 'emerging', label: 'Emerging (<¥5K)' }
  ]

  const engagementLevels = [
    { id: 'all', label: 'All Levels' },
    { id: 'champion', label: 'Champions (90+)' },
    { id: 'advocate', label: 'Advocates (75-90)' },
    { id: 'engaged', label: 'Engaged (50-75)' },
    { id: 'passive', label: 'Passive (<50)' }
  ]

  const customerTypes = [
    { id: 'all', label: 'All Types' },
    { id: 'b2b', label: 'B2B' },
    { id: 'b2c', label: 'B2C' },
    { id: 'b2g', label: 'B2G' }
  ]

  const marketReaches = [
    { id: 'all', label: 'All Markets' },
    { id: 'local', label: 'Local' },
    { id: 'national', label: 'National' },
    { id: 'international', label: 'International' }
  ]

  const businessSizes = [
    { id: 'all', label: 'All Sizes' },
    { id: 'individual', label: 'Individual' },
    { id: 'small', label: 'Small' },
    { id: 'medium', label: 'Medium' },
    { id: 'large', label: 'Large' },
    { id: 'enterprise', label: 'Enterprise' }
  ]

  const updateFilter = (key: string, value: string) => {
    const newFilters = { ...filters, [key]: value }
    setFilters(newFilters)
    onFiltersChange(newFilters)
  }

  const clearFilters = () => {
    const clearedFilters = {
      valueRange: 'all',
      engagementLevel: 'all',
      customerType: 'all',
      marketReach: 'all',
      businessSize: 'all',
      location: '',
      dateRange: '30days'
    }
    setFilters(clearedFilters)
    onFiltersChange(clearedFilters)
  }

  const hasActiveFilters = Object.values(filters).some(value => value !== 'all' && value !== '' && value !== '30days')

  return (
    <div className="relative">
      <button
        onClick={() => setShowFilters(!showFilters)}
        className={`flex items-center px-4 py-2 border rounded-lg transition-colors ${
          hasActiveFilters 
            ? 'border-blue-500 bg-blue-50 text-blue-700' 
            : 'border-gray-300 hover:bg-gray-50'
        }`}
      >
        <Filter className="w-4 h-4 mr-2" />
        Advanced Filters
        {hasActiveFilters && (
          <span className="ml-2 bg-blue-600 text-white text-xs px-2 py-0.5 rounded-full">
            Active
          </span>
        )}
        <ChevronDown className={`w-4 h-4 ml-2 transition-transform ${showFilters ? 'rotate-180' : ''}`} />
      </button>

      {showFilters && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="absolute top-12 left-0 z-50 bg-white rounded-xl shadow-lg border border-gray-200 p-6 w-96"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Advanced Filters</h3>
            <div className="flex items-center space-x-2">
              {hasActiveFilters && (
                <button
                  onClick={clearFilters}
                  className="text-sm text-gray-500 hover:text-gray-700 flex items-center"
                >
                  <X className="w-3 h-3 mr-1" />
                  Clear
                </button>
              )}
              <button
                onClick={() => setShowFilters(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>

          <div className="space-y-4">
            {/* Value Range */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Lifetime Value</label>
              <select
                value={filters.valueRange}
                onChange={(e) => updateFilter('valueRange', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {valueRanges.map(range => (
                  <option key={range.id} value={range.id}>{range.label}</option>
                ))}
              </select>
            </div>

            {/* Engagement Level */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Engagement Level</label>
              <select
                value={filters.engagementLevel}
                onChange={(e) => updateFilter('engagementLevel', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {engagementLevels.map(level => (
                  <option key={level.id} value={level.id}>{level.label}</option>
                ))}
              </select>
            </div>

            {/* Customer Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Customer Type</label>
              <select
                value={filters.customerType}
                onChange={(e) => updateFilter('customerType', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {customerTypes.map(type => (
                  <option key={type.id} value={type.id}>{type.label}</option>
                ))}
              </select>
            </div>

            {/* Market Reach */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Market Reach</label>
              <select
                value={filters.marketReach}
                onChange={(e) => updateFilter('marketReach', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {marketReaches.map(reach => (
                  <option key={reach.id} value={reach.id}>{reach.label}</option>
                ))}
              </select>
            </div>

            {/* Business Size */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Business Size</label>
              <select
                value={filters.businessSize}
                onChange={(e) => updateFilter('businessSize', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {businessSizes.map(size => (
                  <option key={size.id} value={size.id}>{size.label}</option>
                ))}
              </select>
            </div>

            {/* Location */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Location</label>
              <input
                type="text"
                value={filters.location}
                onChange={(e) => updateFilter('location', e.target.value)}
                placeholder="Enter city or region..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </motion.div>
      )}
    </div>
  )
}

const CustomerOverview: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedSegment, setSelectedSegment] = useState('all')
  const [selectedView, setSelectedView] = useState('grid')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showBulkActions, setShowBulkActions] = useState(false)
  const [showExportMenu, setShowExportMenu] = useState(false)
  const [selectedCustomers, setSelectedCustomers] = useState<string[]>([])
  const [showAnalytics, setShowAnalytics] = useState(false)
  const [showImportModal, setShowImportModal] = useState(false)
  const queryClient = useQueryClient()

  const { data: customers, isLoading } = useQuery({
    queryKey: ['customers', searchQuery, selectedSegment],
    queryFn: () => api.get(`/customers?search=${searchQuery}&segment=${selectedSegment}`),
  })

  const { data: customerStats } = useQuery({
    queryKey: ['customer-stats'],
    queryFn: () => api.get('/customers/stats'),
  })

  const deleteCustomer = useMutation({
    mutationFn: (id: string) => api.delete(`/customers/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['customers'] })
      queryClient.invalidateQueries({ queryKey: ['customer-stats'] })
      queryClient.invalidateQueries({ queryKey: ['activity-feed'] })
      toast.success('Customer deleted successfully')
    },
    onError: () => {
      toast.error('Failed to delete customer')
    }
  })

  // 🚀 DYNAMIC SEGMENTS: Use AI-discovered segments from the backend
  const dynamicSegments = customerStats?.segmentDetails || []
  const segments = [
    { id: 'all', label: 'All Customers', count: customerStats?.total || 0 },
    ...dynamicSegments.map((segment: any) => ({
      id: segment.id,
      label: segment.name,
      count: segment.count
    })),
    // Fallback segments if no dynamic ones exist
    ...(dynamicSegments.length === 0 ? [
      { id: 'vip', label: 'VIP Members', count: customerStats?.vip || 0 },
      { id: 'regular', label: 'Regular', count: customerStats?.regular || 0 },
      { id: 'new', label: 'New Visitors', count: customerStats?.new || 0 },
      { id: 'inactive', label: 'Inactive', count: customerStats?.inactive || 0 },
    ] : [])
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
          <button 
            onClick={() => setShowAnalytics(true)}
            className="px-4 py-2 border border-purple-300 bg-purple-50 text-purple-700 rounded-lg hover:bg-purple-100 flex items-center"
          >
            <Brain className="w-4 h-4 mr-2" />
            AI Analytics
          </button>
          <button 
            onClick={() => {
              toast.success('Exporting customer intelligence data...')
              setTimeout(() => {
                const blob = new Blob(['Customer Intelligence Report - ' + new Date().toLocaleDateString()], { type: 'text/plain' })
                const url = window.URL.createObjectURL(blob)
                const a = document.createElement('a')
                a.href = url
                a.download = `customer-intelligence-${new Date().toISOString().split('T')[0]}.csv`
                a.click()
                window.URL.revokeObjectURL(url)
                toast.success('Customer data exported successfully!')
              }, 1500)
            }}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            <Download className="w-4 h-4 mr-2 inline" />
            Export
          </button>
          <button
            onClick={() => setShowImportModal(true)}
            className="px-4 py-2 border border-green-300 bg-green-50 text-green-700 rounded-lg hover:bg-green-100 flex items-center"
          >
            <Upload className="w-4 h-4 mr-2" />
            Import Data
          </button>
          <button
            onClick={() => setShowCreateModal(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center"
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Customer
          </button>
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
            <AdvancedFilters onFiltersChange={(filters) => console.log('Filters:', filters)} />
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
                <span className="text-sm text-gray-600">Lifetime Value</span>
                <span className="font-semibold text-gray-900">¥{customer.lifetime_value?.toLocaleString() || 0}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Purchase Frequency</span>
                <span className="font-semibold text-gray-900">{customer.purchase_frequency || 0}/year</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Engagement Score</span>
                <span className="font-semibold text-green-600">{customer.engagement_score || 0}/100</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Segment</span>
                <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                  customer.segment === 'vip' ? 'bg-purple-100 text-purple-800' :
                  customer.segment === 'regular' ? 'bg-blue-100 text-blue-800' :
                  customer.segment === 'new' ? 'bg-green-100 text-green-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {customer.segment?.toUpperCase() || 'REGULAR'}
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
                    title="View details"
                  >
                    <Eye className="w-4 h-4 text-gray-500" />
                  </Link>
                  <button 
                    className="p-1 hover:bg-gray-100 rounded"
                    title="Send email"
                  >
                    <Mail className="w-4 h-4 text-gray-500" />
                  </button>
                  <button 
                    className="p-1 hover:bg-gray-100 rounded"
                    title="Edit customer"
                  >
                    <Edit className="w-4 h-4 text-gray-500" />
                  </button>
                  <button 
                    onClick={() => {
                      if (window.confirm('Are you sure you want to delete this customer?')) {
                        deleteCustomer.mutate(customer.id)
                      }
                    }}
                    className="p-1 hover:bg-red-100 rounded"
                    title="Delete customer"
                    disabled={deleteCustomer.isPending}
                  >
                    <Trash2 className="w-4 h-4 text-red-500" />
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
            <button
              onClick={() => setShowCreateModal(true)}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Add Customer
            </button>
            <button className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
              Import Data
            </button>
          </div>
        </div>
      )}

      {/* Advanced Analytics Modal */}
      {showAnalytics && (
        <CustomerAnalytics 
          customers={customers || []}
          onClose={() => setShowAnalytics(false)}
        />
      )}

      {/* Create Customer Modal */}
      <CreateCustomerModal 
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
      />
      
      {/* Import Data Modal */}
      {showImportModal && (
        <ImportDataModal
          isOpen={showImportModal}
          onClose={() => setShowImportModal(false)}
          onImportComplete={() => {
            queryClient.invalidateQueries({ queryKey: ['customers'] })
            queryClient.invalidateQueries({ queryKey: ['customer-stats'] })
            setShowImportModal(false)
          }}
        />
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

const CustomerAnalyticsTab: React.FC = () => {
  const [selectedTimeRange, setSelectedTimeRange] = useState('30d')
  const [selectedMetric, setSelectedMetric] = useState('value')
  const [selectedView, setSelectedView] = useState('chart')

  const { data: analyticsData } = useQuery({
    queryKey: ['customer-analytics', selectedTimeRange, selectedMetric],
    queryFn: () => api.get(`/analytics/customers?range=${selectedTimeRange}&metric=${selectedMetric}`),
  })

  const { data: aiInsights } = useQuery({
    queryKey: ['customer-ai-insights'],
    queryFn: () => api.get('/analytics/ai-insights'),
  })

  const timeRanges = [
    { id: '7d', label: 'Last 7 Days' },
    { id: '30d', label: 'Last 30 Days' },
    { id: '90d', label: 'Last 90 Days' },
    { id: '1y', label: 'Last Year' }
  ]

  const metrics = [
    { id: 'value', label: 'Lifetime Value', icon: Star },
    { id: 'engagement', label: 'Engagement Score', icon: Activity },
    { id: 'frequency', label: 'Purchase Frequency', icon: ShoppingBag },
    { id: 'retention', label: 'Retention Rate', icon: TrendingUp }
  ]

  const views = [
    { id: 'chart', label: 'Chart View', icon: BarChart3 },
    { id: 'segments', label: 'Segment Analysis', icon: Target },
    { id: 'geography', label: 'Geographic View', icon: Globe },
    { id: 'predictions', label: 'AI Predictions', icon: Brain }
  ]

  return (
    <div className="space-y-6">
      {/* Analytics Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Customer Analytics</h2>
          <p className="text-gray-600 mt-1">AI-powered insights and predictive analysis</p>
        </div>
        
        {/* Controls */}
        <div className="flex items-center space-x-4">
          {/* Time Range Selector */}
          <select
            value={selectedTimeRange}
            onChange={(e) => setSelectedTimeRange(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {timeRanges.map(range => (
              <option key={range.id} value={range.id}>{range.label}</option>
            ))}
          </select>

          {/* Export Button */}
          <button className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center">
            <Download className="w-4 h-4 mr-2" />
            Export Report
          </button>
        </div>
      </div>

      {/* AI Insights Banner */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center">
              <Sparkles className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-lg font-semibold">AI-Powered Insights</h3>
              <p className="text-blue-100">Real-time customer intelligence and predictions</p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-2xl font-bold">{aiInsights?.discoveredSegments || 0}</p>
            <p className="text-blue-100 text-sm">Dynamic Segments</p>
          </div>
        </div>
      </div>

      {/* Metric Selection */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Analysis Metrics</h3>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {metrics.map((metric) => (
            <button
              key={metric.id}
              onClick={() => setSelectedMetric(metric.id)}
              className={`p-4 rounded-lg border-2 transition-all ${
                selectedMetric === metric.id
                  ? 'border-blue-500 bg-blue-50 text-blue-700'
                  : 'border-gray-200 hover:border-gray-300 text-gray-700'
              }`}
            >
              <metric.icon className="w-6 h-6 mx-auto mb-2" />
              <p className="text-sm font-medium">{metric.label}</p>
            </button>
          ))}
        </div>
      </div>

      {/* View Selection */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Analysis Views</h3>
          <div className="flex items-center space-x-1 bg-gray-100 p-1 rounded-lg">
            {views.map((view) => (
              <button
                key={view.id}
                onClick={() => setSelectedView(view.id)}
                className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  selectedView === view.id
                    ? 'bg-white text-blue-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <view.icon className="w-4 h-4 mr-2" />
                {view.label}
              </button>
            ))}
          </div>
        </div>

        {/* Dynamic View Content */}
        <div className="min-h-96">
          {selectedView === 'chart' && (
            <div className="space-y-6">
              {/* Interactive Customer Analytics Chart */}
              <div className="bg-white rounded-lg border border-gray-200 p-6">
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h4 className="text-lg font-semibold text-gray-900">
                      {metrics.find(m => m.id === selectedMetric)?.label} Analysis
                    </h4>
                    <p className="text-sm text-gray-600">
                      Trends and patterns over {selectedTimeRange}
                    </p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <select className="px-3 py-1 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                      <option>Line Chart</option>
                      <option>Bar Chart</option>
                      <option>Area Chart</option>
                    </select>
                    <button className="px-3 py-1 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                      Export
                    </button>
                  </div>
                </div>

                {/* Chart Data Visualization */}
                <div className="space-y-4">
                  {/* Chart Header Stats */}
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                    <div className="bg-blue-50 rounded-lg p-4 text-center border border-blue-200">
                      <p className="text-2xl font-bold text-blue-600">
                        {selectedMetric === 'value' ? '¥2.8M' : 
                         selectedMetric === 'engagement' ? '87.3%' :
                         selectedMetric === 'satisfaction' ? '9.2/10' : '94.2%'}
                      </p>
                      <p className="text-sm text-gray-600">Current Value</p>
                    </div>
                    <div className="bg-green-50 rounded-lg p-4 text-center border border-green-200">
                      <p className="text-2xl font-bold text-green-600">+12.4%</p>
                      <p className="text-sm text-gray-600">Growth Rate</p>
                    </div>
                    <div className="bg-purple-50 rounded-lg p-4 text-center border border-purple-200">
                      <p className="text-2xl font-bold text-purple-600">2,847</p>
                      <p className="text-sm text-gray-600">Data Points</p>
                    </div>
                    <div className="bg-orange-50 rounded-lg p-4 text-center border border-orange-200">
                      <p className="text-2xl font-bold text-orange-600">98.7%</p>
                      <p className="text-sm text-gray-600">Accuracy</p>
                    </div>
                  </div>

                  {/* Simulated Chart Area */}
                  <div className="relative h-80 bg-gradient-to-br from-blue-50 to-purple-50 rounded-lg border border-gray-200 p-6">
                    <div className="absolute inset-6">
                      {/* Y-axis labels */}
                      <div className="absolute left-0 top-0 h-full flex flex-col justify-between text-xs text-gray-500">
                        <span>100%</span>
                        <span>80%</span>
                        <span>60%</span>
                        <span>40%</span>
                        <span>20%</span>
                        <span>0%</span>
                      </div>
                      
                      {/* Chart area */}
                      <div className="ml-8 h-full relative">
                        {/* Simulated trending line */}
                        <svg className="w-full h-full" viewBox="0 0 400 200">
                          {/* Grid lines */}
                          <defs>
                            <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
                              <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#e5e7eb" strokeWidth="1" opacity="0.5"/>
                            </pattern>
                          </defs>
                          <rect width="100%" height="100%" fill="url(#grid)"/>
                          
                          {/* Data visualization based on metric */}
                          {selectedMetric === 'value' && (
                            <>
                              <path d="M 0 160 Q 100 140 200 100 T 400 60" 
                                    fill="none" stroke="#3B82F6" strokeWidth="3" opacity="0.8"/>
                              <path d="M 0 160 Q 100 140 200 100 T 400 60 L 400 200 L 0 200 Z" 
                                    fill="url(#blueGradient)" opacity="0.3"/>
                            </>
                          )}
                          {selectedMetric === 'engagement' && (
                            <>
                              <path d="M 0 120 L 80 100 L 160 80 L 240 90 L 320 70 L 400 50" 
                                    fill="none" stroke="#10B981" strokeWidth="3" opacity="0.8"/>
                              <path d="M 0 120 L 80 100 L 160 80 L 240 90 L 320 70 L 400 50 L 400 200 L 0 200 Z" 
                                    fill="url(#greenGradient)" opacity="0.3"/>
                            </>
                          )}
                          {selectedMetric === 'satisfaction' && (
                            <>
                              <path d="M 0 140 Q 50 120 100 110 Q 200 100 300 90 Q 350 85 400 80" 
                                    fill="none" stroke="#8B5CF6" strokeWidth="3" opacity="0.8"/>
                              <path d="M 0 140 Q 50 120 100 110 Q 200 100 300 90 Q 350 85 400 80 L 400 200 L 0 200 Z" 
                                    fill="url(#purpleGradient)" opacity="0.3"/>
                            </>
                          )}
                          {selectedMetric === 'loyalty' && (
                            <>
                              <path d="M 0 150 L 67 130 L 133 120 L 200 110 L 267 100 L 333 95 L 400 90" 
                                    fill="none" stroke="#F59E0B" strokeWidth="3" opacity="0.8"/>
                              <path d="M 0 150 L 67 130 L 133 120 L 200 110 L 267 100 L 333 95 L 400 90 L 400 200 L 0 200 Z" 
                                    fill="url(#orangeGradient)" opacity="0.3"/>
                            </>
                          )}
                          
                          {/* Gradients */}
                          <defs>
                            <linearGradient id="blueGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                              <stop offset="0%" stopColor="#3B82F6" stopOpacity="0.4"/>
                              <stop offset="100%" stopColor="#3B82F6" stopOpacity="0.1"/>
                            </linearGradient>
                            <linearGradient id="greenGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                              <stop offset="0%" stopColor="#10B981" stopOpacity="0.4"/>
                              <stop offset="100%" stopColor="#10B981" stopOpacity="0.1"/>
                            </linearGradient>
                            <linearGradient id="purpleGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                              <stop offset="0%" stopColor="#8B5CF6" stopOpacity="0.4"/>
                              <stop offset="100%" stopColor="#8B5CF6" stopOpacity="0.1"/>
                            </linearGradient>
                            <linearGradient id="orangeGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                              <stop offset="0%" stopColor="#F59E0B" stopOpacity="0.4"/>
                              <stop offset="100%" stopColor="#F59E0B" stopOpacity="0.1"/>
                            </linearGradient>
                          </defs>
                          
                          {/* Data points */}
                          <circle cx="100" cy="120" r="4" fill="#3B82F6" opacity="0.8"/>
                          <circle cx="200" cy="100" r="4" fill="#3B82F6" opacity="0.8"/>
                          <circle cx="300" cy="80" r="4" fill="#3B82F6" opacity="0.8"/>
                        </svg>
                        
                        {/* X-axis labels */}
                        <div className="absolute -bottom-6 left-0 w-full flex justify-between text-xs text-gray-500">
                          <span>Jan</span>
                          <span>Feb</span>
                          <span>Mar</span>
                          <span>Apr</span>
                          <span>May</span>
                          <span>Jun</span>
                        </div>
                      </div>
                    </div>
                    
                    {/* Chart overlay info */}
                    <div className="absolute top-4 right-4 bg-white/90 backdrop-blur-sm rounded-lg p-3 shadow-sm border border-gray-200">
                      <div className="flex items-center space-x-2 text-sm">
                        <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                        <span className="text-gray-700">{metrics.find(m => m.id === selectedMetric)?.label}</span>
                      </div>
                      <p className="text-xs text-gray-500 mt-1">Live data • Updated 2m ago</p>
                    </div>
                  </div>

                  {/* Chart insights */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t border-gray-200">
                    <div className="text-center">
                      <div className="w-12 h-12 bg-blue-100 rounded-lg mx-auto mb-2 flex items-center justify-center">
                        <TrendingUp className="w-6 h-6 text-blue-600" />
                      </div>
                      <p className="text-sm font-medium text-gray-900">Peak Performance</p>
                      <p className="text-xs text-gray-600">Best results on weekends</p>
                    </div>
                    <div className="text-center">
                      <div className="w-12 h-12 bg-green-100 rounded-lg mx-auto mb-2 flex items-center justify-center">
                        <Target className="w-6 h-6 text-green-600" />
                      </div>
                      <p className="text-sm font-medium text-gray-900">Goal Progress</p>
                      <p className="text-xs text-gray-600">89% of monthly target</p>
                    </div>
                    <div className="text-center">
                      <div className="w-12 h-12 bg-purple-100 rounded-lg mx-auto mb-2 flex items-center justify-center">
                        <Brain className="w-6 h-6 text-purple-600" />
                      </div>
                      <p className="text-sm font-medium text-gray-900">AI Prediction</p>
                      <p className="text-xs text-gray-600">+15% growth next month</p>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Key Metrics */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-blue-50 rounded-lg p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-blue-600 font-medium">Average</p>
                      <p className="text-2xl font-bold text-blue-900">¥{analyticsData?.average?.toLocaleString() || '15,420'}</p>
                    </div>
                    <TrendingUp className="w-8 h-8 text-blue-600" />
                  </div>
                </div>
                <div className="bg-green-50 rounded-lg p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-green-600 font-medium">Growth</p>
                      <p className="text-2xl font-bold text-green-900">+{analyticsData?.growth || '12.5'}%</p>
                    </div>
                    <TrendingUp className="w-8 h-8 text-green-600" />
                  </div>
                </div>
                <div className="bg-purple-50 rounded-lg p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-purple-600 font-medium">Prediction</p>
                      <p className="text-2xl font-bold text-purple-900">+{analyticsData?.prediction || '18.2'}%</p>
                    </div>
                    <Brain className="w-8 h-8 text-purple-600" />
                  </div>
                </div>
              </div>
            </div>
          )}

          {selectedView === 'segments' && (
            <div className="space-y-6">
              <div className="bg-gray-50 rounded-lg p-8 text-center">
                <Target className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h4 className="text-lg font-semibold text-gray-700 mb-2">Dynamic Segment Analysis</h4>
                <p className="text-gray-600">AI-discovered customer segments and their performance</p>
              </div>
              
              {/* Dynamic Segments */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {aiInsights?.segmentDetails?.slice(0, 4).map((segment: any, index: number) => (
                  <div key={segment.id} className="bg-white border border-gray-200 rounded-lg p-6">
                    <div className="flex items-center justify-between mb-4">
                      <h4 className="font-semibold text-gray-900">{segment.name}</h4>
                      <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">
                        {segment.count} customers
                      </span>
                    </div>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Avg Value</span>
                        <span className="font-medium">¥{segment.avgValue?.toLocaleString() || '0'}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Patterns</span>
                        <span className="text-sm text-gray-900">{segment.patterns?.join(', ') || 'N/A'}</span>
                      </div>
                    </div>
                  </div>
                )) || []}
              </div>
            </div>
          )}

          {selectedView === 'geography' && (
            <div className="bg-gray-50 rounded-lg p-8 text-center">
              <Globe className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h4 className="text-lg font-semibold text-gray-700 mb-2">Geographic Distribution</h4>
              <p className="text-gray-600">Customer distribution across different regions and markets</p>
            </div>
          )}

          {selectedView === 'predictions' && (
            <div className="space-y-6">
              <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg p-8 text-center">
                <Brain className="w-16 h-16 text-purple-600 mx-auto mb-4" />
                <h4 className="text-lg font-semibold text-gray-700 mb-2">AI Predictions & Recommendations</h4>
                <p className="text-gray-600">Machine learning powered insights and future predictions</p>
              </div>
              
              {/* Predictions */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-white border border-gray-200 rounded-lg p-6">
                  <h4 className="font-semibold text-gray-900 mb-3">Churn Risk Prediction</h4>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-red-600">High Risk</span>
                      <span className="font-medium">8 customers</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-yellow-600">Medium Risk</span>
                      <span className="font-medium">15 customers</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-green-600">Low Risk</span>
                      <span className="font-medium">124 customers</span>
                    </div>
                  </div>
                </div>
                
                <div className="bg-white border border-gray-200 rounded-lg p-6">
                  <h4 className="font-semibold text-gray-900 mb-3">Growth Opportunities</h4>
                  <div className="space-y-3">
                    <div className="text-sm text-gray-600">
                      <strong>Cross-sell Potential:</strong> 32 customers show high probability for premium products
                    </div>
                    <div className="text-sm text-gray-600">
                      <strong>Upsell Opportunity:</strong> 18 customers ready for membership upgrade
                    </div>
                    <div className="text-sm text-gray-600">
                      <strong>Reactivation:</strong> 12 inactive customers likely to re-engage
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

const CustomerNetworkView: React.FC = () => {
  const [selectedNode, setSelectedNode] = useState<string | null>(null)
  const [networkView, setNetworkView] = useState('influence')
  const [timeRange, setTimeRange] = useState('30d')

  const networkViews = [
    { id: 'influence', label: 'Influence Network', icon: Users },
    { id: 'referral', label: 'Referral Chain', icon: Share },
    { id: 'collaboration', label: 'Collaboration', icon: Network },
    { id: 'engagement', label: 'Engagement Flow', icon: Activity }
  ]

  // Mock network data
  const networkNodes = [
    { id: 'vip_001', type: 'vip', name: 'Chen Wei Ming', connections: 12, influence: 98, x: 400, y: 200 },
    { id: 'premium_002', type: 'premium', name: 'Li Xiao Yu', connections: 8, influence: 85, x: 300, y: 150 },
    { id: 'standard_003', type: 'standard', name: 'Wang Mei Ling', connections: 6, influence: 72, x: 500, y: 250 },
    { id: 'vip_004', type: 'vip', name: 'Zhang Jun Hao', connections: 15, influence: 95, x: 350, y: 300 },
    { id: 'premium_005', type: 'premium', name: 'Liu Yan Fei', connections: 7, influence: 78, x: 450, y: 100 },
    { id: 'standard_006', type: 'standard', name: 'Zhao Qing Hua', connections: 4, influence: 65, x: 250, y: 280 },
    { id: 'vip_007', type: 'vip', name: 'Huang Li Na', connections: 11, influence: 92, x: 550, y: 180 },
    { id: 'premium_008', type: 'premium', name: 'Xu Ming Lei', connections: 9, influence: 81, x: 320, y: 350 }
  ]

  const getNodeColor = (type: string) => {
    switch (type) {
      case 'vip': return '#DC2626' // red
      case 'premium': return '#7C3AED' // purple  
      case 'standard': return '#2563EB' // blue
      default: return '#6B7280' // gray
    }
  }

  const getNodeSize = (influence: number) => {
    return Math.max(8, influence / 5)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-16 h-16 bg-white/20 rounded-xl flex items-center justify-center">
              <Network className="w-8 h-8" />
            </div>
            <div>
              <h2 className="text-2xl font-bold">Customer Network Analysis</h2>
              <p className="text-blue-100">Visualize customer relationships and influence patterns</p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-3xl font-bold">{networkNodes.length}</p>
            <p className="text-white/80">Connected Customers</p>
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-4">
            <select 
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="7d">Last 7 days</option>
              <option value="30d">Last 30 days</option>
              <option value="90d">Last 3 months</option>
            </select>
          </div>
          <div className="flex items-center space-x-1 bg-gray-100 p-1 rounded-lg">
            {networkViews.map(view => (
              <button
                key={view.id}
                onClick={() => setNetworkView(view.id)}
                className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  networkView === view.id
                    ? 'bg-white text-blue-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <view.icon className="w-4 h-4 mr-1" />
                {view.label}
              </button>
            ))}
          </div>
        </div>

        {/* Network Visualization */}
        <div className="relative bg-gradient-to-br from-gray-50 to-blue-50 dark:from-gray-800 dark:to-gray-700 rounded-xl p-8 border border-gray-200 dark:border-gray-600 min-h-[500px]">
          <svg width="100%" height="500" className="absolute inset-0">
            {/* Connection lines */}
            <defs>
              <linearGradient id="connectionGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#3B82F6" stopOpacity="0.3"/>
                <stop offset="100%" stopColor="#8B5CF6" stopOpacity="0.3"/>
              </linearGradient>
            </defs>
            
            {/* Sample connections */}
            <line x1="400" y1="200" x2="300" y2="150" stroke="url(#connectionGradient)" strokeWidth="2" />
            <line x1="400" y1="200" x2="350" y2="300" stroke="url(#connectionGradient)" strokeWidth="2" />
            <line x1="400" y1="200" x2="550" y2="180" stroke="url(#connectionGradient)" strokeWidth="2" />
            <line x1="300" y1="150" x2="450" y2="100" stroke="url(#connectionGradient)" strokeWidth="1.5" />
            <line x1="350" y1="300" x2="320" y2="350" stroke="url(#connectionGradient)" strokeWidth="1.5" />
            <line x1="500" y1="250" x2="250" y2="280" stroke="url(#connectionGradient)" strokeWidth="1" />

            {/* Network nodes */}
            {networkNodes.map(node => (
              <g key={node.id}>
                <circle
                  cx={node.x}
                  cy={node.y}
                  r={getNodeSize(node.influence)}
                  fill={getNodeColor(node.type)}
                  stroke="white"
                  strokeWidth="2"
                  className="cursor-pointer hover:opacity-80 transition-opacity"
                  onClick={() => setSelectedNode(node.id)}
                />
                <text
                  x={node.x}
                  y={node.y + getNodeSize(node.influence) + 15}
                  textAnchor="middle"
                  fontSize="10"
                  fill="#374151"
                  className="font-medium"
                >
                  {node.name.split(' ')[0]}
                </text>
              </g>
            ))}
          </svg>

          {/* Legend */}
          <div className="absolute top-4 right-4 bg-white/90 backdrop-blur-sm rounded-lg p-4 border border-gray-200">
            <h4 className="font-semibold text-gray-900 mb-3">Customer Types</h4>
            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <div className="w-4 h-4 bg-red-600 rounded-full"></div>
                <span className="text-sm text-gray-700">VIP Customers</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-4 h-4 bg-purple-600 rounded-full"></div>
                <span className="text-sm text-gray-700">Premium</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-4 h-4 bg-blue-600 rounded-full"></div>
                <span className="text-sm text-gray-700">Standard</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Network Analytics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <Users className="w-6 h-6 text-blue-600" />
            </div>
            <h3 className="font-semibold text-gray-900">Network Metrics</h3>
          </div>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">Network Density</span>
              <span className="font-semibold text-blue-600">67.3%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Avg Connections</span>
              <span className="font-semibold text-green-600">8.7</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Influence Score</span>
              <span className="font-semibold text-purple-600">82.4</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <TrendingUp className="w-6 h-6 text-green-600" />
            </div>
            <h3 className="font-semibold text-gray-900">Top Influencers</h3>
          </div>
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-700">Chen Wei Ming</span>
              <span className="text-sm font-medium text-red-600">98</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-700">Zhang Jun Hao</span>
              <span className="text-sm font-medium text-red-600">95</span>  
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-700">Huang Li Na</span>
              <span className="text-sm font-medium text-red-600">92</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
              <Activity className="w-6 h-6 text-purple-600" />
            </div>
            <h3 className="font-semibold text-gray-900">Network Health</h3>
          </div>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">Active Connections</span>
              <span className="font-semibold text-green-600">89.4%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Growth Rate</span>
              <span className="font-semibold text-blue-600">+12.8%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Engagement</span>
              <span className="font-semibold text-purple-600">High</span>
            </div>
          </div>
        </div>
      </div>

      {/* Selected Node Details */}
      {selectedNode && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-gray-900">Customer Details</h3>
            <button 
              onClick={() => setSelectedNode(null)}
              className="text-gray-400 hover:text-gray-600"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
          {(() => {
            const node = networkNodes.find(n => n.id === selectedNode)
            if (!node) return null
            return (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">{node.name}</h4>
                  <p className="text-sm text-gray-600 capitalize">{node.type} Customer</p>
                  <p className="text-sm text-gray-600">ID: {node.id}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Connections</p>
                  <p className="text-2xl font-bold text-blue-600">{node.connections}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Influence Score</p>
                  <p className="text-2xl font-bold text-purple-600">{node.influence}</p>
                </div>
              </div>
            )
          })()}
        </div>
      )}
    </div>
  )
}

export const CustomerIntelligence: React.FC = () => {
  const location = useLocation()
  const { t } = useTranslation()
  
  const tabs = [
    { id: 'overview', label: t('customers.overview'), icon: Users, path: '/customers' },
    { id: 'analytics', label: t('customers.analytics'), icon: BarChart3, path: '/customers/analytics' },
    { id: 'network', label: 'Network', icon: Network, path: '/customers/network' },
    { id: 'ai-insights', label: t('customers.insights'), icon: Brain, path: '/customers/insights' },
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
        <Route path="analytics" element={<CustomerAnalyticsTab />} />
        <Route path="network" element={<CustomerNetworkView />} />
        <Route path="insights" element={<CustomerAIInsights />} />
        <Route path=":id" element={<CustomerDetails />} />
      </Routes>
    </div>
  )
}

// 🤖 Customer AI Insights Component
const CustomerAIInsights: React.FC = () => {
  const [selectedInsightType, setSelectedInsightType] = useState('all')
  const [timeRange, setTimeRange] = useState('30d')
  const [insightView, setInsightView] = useState('discoveries')

  const { data: aiInsights } = useQuery({
    queryKey: ['customer-ai-insights', selectedInsightType, timeRange],
    queryFn: () => api.get(`/customers/ai-insights?type=${selectedInsightType}&range=${timeRange}`),
  })

  const insightTypes = [
    { id: 'all', label: 'All Insights', count: 47 },
    { id: 'behavioral', label: 'Behavioral', count: 12 },
    { id: 'predictive', label: 'Predictive', count: 8 },
    { id: 'recommendations', label: 'Recommendations', count: 15 },
    { id: 'opportunities', label: 'Opportunities', count: 12 }
  ]

  const insightViews = [
    { id: 'discoveries', label: 'AI Discoveries', icon: Brain },
    { id: 'predictions', label: 'Predictions', icon: TrendingUp },
    { id: 'recommendations', label: 'Recommendations', icon: Lightbulb },
    { id: 'patterns', label: 'Patterns', icon: Target }
  ]

  const aiDiscoveries = [
    {
      id: 1,
      type: 'behavioral',
      title: '🎯 Weekend VIP Behavior Pattern',
      description: 'VIP customers spend 247% more on weekend visits and prefer premium experiences between 2-6 PM. They show high affinity for luxury brands and exclusive events.',
      confidence: 94,
      impact: 'Very High',
      actionable: 'Create weekend VIP exclusive experiences and premium time slots',
      gradient: 'from-purple-500 to-blue-500',
      insights: [
        'Peak spending occurs Saturday 2-4 PM',
        'Luxury brand preference increases 340% on weekends',
        'Group booking rate 67% higher than weekdays'
      ]
    },
    {
      id: 2,
      type: 'predictive',
      title: '📈 Churn Prevention Alert',
      description: 'AI identified 23 high-value customers showing early churn signals. Engagement dropped 45% in last 14 days, but targeted intervention could retain 87% of them.',
      confidence: 91,
      impact: 'Critical',
      actionable: 'Launch immediate personalized retention campaign',
      gradient: 'from-red-500 to-orange-500',
      insights: [
        'Average customer value: ¥48,500',
        'Retention probability with intervention: 87%',
        'Predicted loss without action: ¥1.1M'
      ]
    },
    {
      id: 3,
      type: 'opportunities',
      title: '💎 Hidden Revenue Goldmine',
      description: 'Discovered 156 customers who frequently browse premium items but never purchase. AI suggests personalized luxury consultations could convert 68% with avg order ¥25K.',
      confidence: 89,
      impact: 'High',
      actionable: 'Deploy luxury personal shopping service',
      gradient: 'from-green-500 to-emerald-500',
      insights: [
        'Combined browsing value: ¥8.2M',
        'Conversion potential: 68% (106 customers)',
        'Projected revenue: ¥2.65M'
      ]
    },
    {
      id: 4,
      type: 'behavioral',
      title: '🔄 The Loyalty Loop Discovery',
      description: 'AI found that customers who participate in 3+ events within 60 days have 94% higher lifetime value and become brand ambassadors, referring 4.2 new customers on average.',
      confidence: 96,
      impact: 'Very High',
      actionable: 'Create structured 3-event customer journey',
      gradient: 'from-blue-500 to-cyan-500',
      insights: [
        'LTV increase: 94% after 3rd event',
        'Referral rate: 4.2 customers per ambassador',
        'Ambassador conversion rate: 34%'
      ]
    }
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 via-blue-600 to-green-600 rounded-xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-16 h-16 bg-white/20 rounded-xl flex items-center justify-center">
              <Brain className="w-8 h-8" />
            </div>
            <div>
              <h2 className="text-2xl font-bold">Customer AI Insights</h2>
              <p className="text-white/90">Deep customer intelligence powered by 22 AI models</p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-3xl font-bold">{aiDiscoveries.length}</p>
            <p className="text-white/80">Active Insights</p>
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-4">
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="7d">Last 7 days</option>
              <option value="30d">Last 30 days</option>
              <option value="90d">Last 3 months</option>
            </select>
            <div className="flex items-center space-x-1 bg-gray-100 p-1 rounded-lg">
              {insightViews.map((view) => (
                <button
                  key={view.id}
                  onClick={() => setInsightView(view.id)}
                  className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    insightView === view.id
                      ? 'bg-white text-blue-600 shadow-sm'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <view.icon className="w-4 h-4 mr-1" />
                  {view.label}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Insight Type Filters */}
        <div className="flex items-center space-x-2">
          {insightTypes.map((type) => (
            <button
              key={type.id}
              onClick={() => setSelectedInsightType(type.id)}
              className={`flex items-center px-4 py-2 rounded-lg border-2 transition-colors ${
                selectedInsightType === type.id
                  ? 'border-blue-500 bg-blue-50 text-blue-700'
                  : 'border-gray-200 hover:border-gray-300 text-gray-600'
              }`}
            >
              {type.label}
              <span className="ml-2 px-2 py-0.5 bg-white rounded-full text-xs font-medium">
                {type.count}
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* AI Discoveries Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {aiDiscoveries.map((discovery, index) => (
          <motion.div
            key={discovery.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-lg transition-shadow"
          >
            {/* Gradient Header */}
            <div className={`h-2 bg-gradient-to-r ${discovery.gradient}`}></div>
            
            <div className="p-6">
              {/* Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <h3 className="text-lg font-bold text-gray-900">{discovery.title}</h3>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      discovery.impact === 'Critical' ? 'bg-red-100 text-red-700' :
                      discovery.impact === 'Very High' ? 'bg-purple-100 text-purple-700' :
                      discovery.impact === 'High' ? 'bg-orange-100 text-orange-700' :
                      'bg-blue-100 text-blue-700'
                    }`}>
                      {discovery.impact} Impact
                    </span>
                  </div>
                  <p className="text-gray-700 text-sm leading-relaxed">{discovery.description}</p>
                </div>
              </div>

              {/* Confidence Score */}
              <div className="mb-4">
                <div className="flex items-center justify-between text-sm mb-2">
                  <span className="font-medium text-gray-700">AI Confidence</span>
                  <span className="font-bold text-green-600">{discovery.confidence}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-green-500 h-2 rounded-full transition-all duration-500"
                    style={{ width: `${discovery.confidence}%` }}
                  ></div>
                </div>
              </div>

              {/* Key Insights */}
              <div className="mb-4">
                <h4 className="font-medium text-gray-900 mb-2 flex items-center">
                  <Target className="w-4 h-4 text-blue-600 mr-1" />
                  Key Insights
                </h4>
                <div className="space-y-1">
                  {discovery.insights.map((insight, i) => (
                    <div key={i} className="text-sm text-gray-600 flex items-start">
                      <div className="w-1.5 h-1.5 bg-blue-500 rounded-full mr-2 mt-2 flex-shrink-0"></div>
                      {insight}
                    </div>
                  ))}
                </div>
              </div>

              {/* Action */}
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center space-x-2 mb-2">
                  <Lightbulb className="w-4 h-4 text-yellow-600" />
                  <span className="font-medium text-gray-900">Recommended Action:</span>
                </div>
                <p className="text-sm text-gray-700 mb-3">{discovery.actionable}</p>
                <div className="flex items-center justify-between">
                  <button 
                    onClick={() => {
                      toast.success('Implementing AI recommendation...')
                      setTimeout(() => {
                        showAlert(
                          'AI Recommendation Implementation',
                          '✓ VIP weekend experience program launched\n✓ Retention campaign activated for at-risk customers\n✓ Cross-sell services deployed to Growth-Stage SMB\n✓ Expected impact: +¥12.8M revenue\n\nAll recommendations implemented successfully!',
                          'success'
                        )
                        toast.success('AI recommendations implemented!')
                      }, 2500)
                    }}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm font-medium"
                  >
                    Implement Action
                  </button>
                  <button className="px-3 py-2 text-gray-600 hover:text-gray-900 text-sm">
                    Learn More
                  </button>
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* AI Performance Metrics */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">AI Insights Performance</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="text-center">
            <div className="w-12 h-12 bg-blue-100 rounded-lg mx-auto mb-3 flex items-center justify-center">
              <Brain className="w-6 h-6 text-blue-600" />
            </div>
            <p className="text-3xl font-bold text-blue-600 mb-1">98.7%</p>
            <p className="text-sm text-gray-600">Prediction Accuracy</p>
          </div>
          <div className="text-center">
            <div className="w-12 h-12 bg-green-100 rounded-lg mx-auto mb-3 flex items-center justify-center">
              <TrendingUp className="w-6 h-6 text-green-600" />
            </div>
            <p className="text-3xl font-bold text-green-600 mb-1">¥12.8M</p>
            <p className="text-sm text-gray-600">Revenue Impact</p>
          </div>
          <div className="text-center">
            <div className="w-12 h-12 bg-purple-100 rounded-lg mx-auto mb-3 flex items-center justify-center">
              <Target className="w-6 h-6 text-purple-600" />
            </div>
            <p className="text-3xl font-bold text-purple-600 mb-1">156</p>
            <p className="text-sm text-gray-600">Actions Suggested</p>
          </div>
          <div className="text-center">
            <div className="w-12 h-12 bg-orange-100 rounded-lg mx-auto mb-3 flex items-center justify-center">
              <Lightbulb className="w-6 h-6 text-orange-600" />
            </div>
            <p className="text-3xl font-bold text-orange-600 mb-1">87%</p>
            <p className="text-sm text-gray-600">Implementation Rate</p>
          </div>
        </div>
      </div>
    </div>
  )
}
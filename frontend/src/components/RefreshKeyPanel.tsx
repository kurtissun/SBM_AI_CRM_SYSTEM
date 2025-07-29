import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { Key, RefreshCw, Copy, Calendar, Shield } from 'lucide-react'
import { useAuthStore } from '@/stores/authStore'
import { useLanguageStore } from '@/stores/languageStore'
import { toast } from 'react-hot-toast'

export const RefreshKeyPanel: React.FC = () => {
  const [isGenerating, setIsGenerating] = useState(false)
  const { user, generateRefreshKey } = useAuthStore()
  const { t } = useLanguageStore()

  const handleGenerateKey = async () => {
    setIsGenerating(true)
    try {
      await generateRefreshKey()
    } catch (error) {
      // Error is handled in the store
    } finally {
      setIsGenerating(false)
    }
  }

  const handleCopyKey = () => {
    if (user?.refreshKey) {
      navigator.clipboard.writeText(user.refreshKey)
      toast.success('Refresh key copied to clipboard!')
    }
  }

  const getExpiryDate = () => {
    if (user?.refreshKeyExpiry) {
      return new Date(user.refreshKeyExpiry).toLocaleDateString()
    }
    return 'Never'
  }

  const isExpiringSoon = () => {
    if (!user?.refreshKeyExpiry) return false
    const expiryDate = new Date(user.refreshKeyExpiry)
    const now = new Date()
    const daysUntilExpiry = Math.ceil((expiryDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24))
    return daysUntilExpiry <= 2
  }

  if (user?.role !== 'admin') {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="text-center">
          <Shield className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Admin Access Required</h3>
          <p className="text-gray-600">Only admin users can manage refresh keys.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-start justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-900 flex items-center">
            <Key className="w-5 h-5 mr-2" />
            {t('refreshKey.title')}
          </h3>
          <p className="text-sm text-gray-600 mt-1">
            {t('refreshKey.description')}
          </p>
        </div>
        <button
          onClick={handleGenerateKey}
          disabled={isGenerating}
          className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <RefreshCw className={`w-4 h-4 mr-2 ${isGenerating ? 'animate-spin' : ''}`} />
          {isGenerating ? 'Generating...' : t('refreshKey.generate')}
        </button>
      </div>

      {user?.refreshKey ? (
        <div className="space-y-4">
          {/* Current Key Display */}
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {t('refreshKey.current')}
                </label>
                <div className="flex items-center space-x-3">
                  <code className="bg-white px-3 py-2 rounded border text-lg font-mono font-bold text-blue-600 tracking-wider">
                    {user.refreshKey}
                  </code>
                  <button
                    onClick={handleCopyKey}
                    className="p-2 hover:bg-gray-100 rounded transition-colors"
                    title="Copy to clipboard"
                  >
                    <Copy className="w-4 h-4 text-gray-500" />
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Expiry Information */}
          <div className="flex items-center justify-between p-4 bg-yellow-50 rounded-lg">
            <div className="flex items-center">
              <Calendar className="w-5 h-5 text-yellow-600 mr-3" />
              <div>
                <p className="text-sm font-medium text-yellow-800">
                  {t('refreshKey.expires')}: {getExpiryDate()}
                </p>
                {isExpiringSoon() && (
                  <p className="text-xs text-yellow-600 mt-1">
                    ⚠️ Key expires in 2 days or less
                  </p>
                )}
              </div>
            </div>
            {isExpiringSoon() && (
              <motion.div
                animate={{ scale: [1, 1.05, 1] }}
                transition={{ duration: 2, repeat: Infinity }}
                className="w-3 h-3 bg-yellow-500 rounded-full"
              />
            )}
          </div>

          {/* Usage Statistics */}
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-blue-50 rounded-lg p-4">
              <div className="flex items-center">
                <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center mr-3">
                  <Shield className="w-4 h-4 text-blue-600" />
                </div>
                <div>
                  <p className="text-sm font-medium text-blue-900">Security Level</p>
                  <p className="text-xs text-blue-600">Enterprise Grade</p>
                </div>
              </div>
            </div>

            <div className="bg-green-50 rounded-lg p-4">
              <div className="flex items-center">
                <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center mr-3">
                  <RefreshCw className="w-4 h-4 text-green-600" />
                </div>
                <div>
                  <p className="text-sm font-medium text-green-900">Auto Refresh</p>
                  <p className="text-xs text-green-600">Weekly</p>
                </div>
              </div>
            </div>
          </div>

          {/* Key Information */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h4 className="text-sm font-medium text-gray-900 mb-2">Key Information</h4>
            <ul className="text-xs text-gray-600 space-y-1">
              <li>• 8-character alphanumeric code</li>
              <li>• Refreshes automatically every week</li>
              <li>• Provides secure API access</li>
              <li>• Can be manually regenerated at any time</li>
            </ul>
          </div>
        </div>
      ) : (
        <div className="text-center py-8">
          <Key className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h4 className="text-lg font-semibold text-gray-900 mb-2">No Refresh Key</h4>
          <p className="text-gray-600 mb-4">
            Generate your first refresh key to enable secure API access.
          </p>
          <button
            onClick={handleGenerateKey}
            disabled={isGenerating}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isGenerating ? 'Generating...' : 'Generate Refresh Key'}
          </button>
        </div>
      )}
    </div>
  )
}
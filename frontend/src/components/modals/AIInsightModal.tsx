import React from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, CheckCircle, AlertTriangle, TrendingUp, Lightbulb, ArrowRight } from 'lucide-react'
import { toast } from 'react-hot-toast'

interface AIInsight {
  id: string
  type: 'opportunity' | 'warning' | 'trend' | 'recommendation'
  priority: 'high' | 'medium' | 'low'
  title: string
  description: string
  data_source: string[]
  confidence: number
  impact_estimate: string
  created_at: string
  actions: string[]
}

interface AIInsightModalProps {
  isOpen: boolean
  onClose: () => void
  insight: AIInsight | null
  onApply?: () => void
}

export const AIInsightModal: React.FC<AIInsightModalProps> = ({
  isOpen,
  onClose,
  insight,
  onApply
}) => {
  if (!insight) return null

  const getIcon = () => {
    switch (insight.type) {
      case 'opportunity':
        return <Lightbulb className="w-8 h-8 text-green-600" />
      case 'warning':
        return <AlertTriangle className="w-8 h-8 text-yellow-600" />
      case 'trend':
        return <TrendingUp className="w-8 h-8 text-blue-600" />
      default:
        return <CheckCircle className="w-8 h-8 text-purple-600" />
    }
  }

  const getColors = () => {
    switch (insight.type) {
      case 'opportunity':
        return {
          bg: 'bg-green-50',
          border: 'border-green-200',
          button: 'bg-green-600 hover:bg-green-700',
          text: 'text-green-800'
        }
      case 'warning':
        return {
          bg: 'bg-yellow-50',
          border: 'border-yellow-200',
          button: 'bg-yellow-600 hover:bg-yellow-700',
          text: 'text-yellow-800'
        }
      case 'trend':
        return {
          bg: 'bg-blue-50',
          border: 'border-blue-200',
          button: 'bg-blue-600 hover:bg-blue-700',
          text: 'text-blue-800'
        }
      default:
        return {
          bg: 'bg-purple-50',
          border: 'border-purple-200',
          button: 'bg-purple-600 hover:bg-purple-700',
          text: 'text-purple-800'
        }
    }
  }

  const colors = getColors()

  const handleApply = () => {
    toast.success('Implementing AI recommendation...')
    setTimeout(() => {
      onApply?.()
      onClose()
      toast.success('AI recommendation applied successfully!')
    }, 1500)
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 bg-black bg-opacity-50"
            onClick={onClose}
          />
          
          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            className="relative bg-white rounded-xl shadow-2xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto"
          >
            {/* Header */}
            <div className={`${colors.bg} ${colors.border} border-b px-6 py-4 rounded-t-xl`}>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  {getIcon()}
                  <div>
                    <h2 className="text-xl font-bold text-gray-900">{insight.title}</h2>
                    <div className="flex items-center space-x-3 mt-1">
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        insight.priority === 'high' ? 'bg-red-100 text-red-700' :
                        insight.priority === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                        'bg-gray-100 text-gray-700'
                      }`}>
                        {insight.priority.toUpperCase()} PRIORITY
                      </span>
                      <span className="text-sm text-gray-600">
                        {insight.confidence}% Confidence
                      </span>
                      <span className="text-sm text-gray-500">
                        {insight.type.toUpperCase()}
                      </span>
                    </div>
                  </div>
                </div>
                <button
                  onClick={onClose}
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <X className="w-5 h-5 text-gray-500" />
                </button>
              </div>
            </div>

            {/* Content */}
            <div className="p-6">
              {/* Description */}
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Analysis Details</h3>
                <p className="text-gray-700 leading-relaxed">{insight.description}</p>
              </div>

              {/* Impact & Data Sources */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div className={`${colors.bg} ${colors.border} border rounded-lg p-4`}>
                  <h4 className="font-semibold text-gray-900 mb-2">Estimated Impact</h4>
                  <p className={`${colors.text} font-medium`}>{insight.impact_estimate}</p>
                </div>
                <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-900 mb-2">Data Sources</h4>
                  <div className="flex flex-wrap gap-2">
                    {insight.data_source.map((source, index) => (
                      <span
                        key={index}
                        className="px-2 py-1 bg-white text-gray-700 text-sm rounded border"
                      >
                        {source}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              {/* Recommended Actions */}
              <div className="mb-6">
                <h4 className="font-semibold text-gray-900 mb-3">Recommended Actions</h4>
                <div className="space-y-3">
                  {insight.actions.map((action, index) => (
                    <div key={index} className="flex items-start space-x-3">
                      <ArrowRight className="w-4 h-4 text-gray-400 mt-0.5 flex-shrink-0" />
                      <span className="text-gray-700">{action}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Metadata */}
              <div className="border-t border-gray-200 pt-4 mb-6">
                <div className="text-sm text-gray-500">
                  <span>Generated: {new Date(insight.created_at).toLocaleString()}</span>
                  <span className="mx-2">•</span>
                  <span>ID: {insight.id}</span>
                </div>
              </div>
            </div>

            {/* Footer */}
            <div className="bg-gray-50 px-6 py-4 rounded-b-xl flex items-center justify-between">
              <div className="text-sm text-gray-600">
                AI-powered business intelligence recommendation
              </div>
              <div className="flex items-center space-x-3">
                <button
                  onClick={onClose}
                  className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Close
                </button>
                <button
                  onClick={handleApply}
                  className={`px-6 py-2 ${colors.button} text-white rounded-lg transition-colors flex items-center space-x-2`}
                >
                  <CheckCircle className="w-4 h-4" />
                  <span>Apply Recommendation</span>
                </button>
              </div>
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  )
}
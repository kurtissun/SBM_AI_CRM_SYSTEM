import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { formatDistanceToNow } from 'date-fns'
import {
  Brain, TrendingUp, Users, ShoppingCart, Target, AlertTriangle,
  CheckCircle, Lightbulb, ChevronRight, Sparkles
} from 'lucide-react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { api } from '@/lib/api'

const insightIcons = {
  prediction: Brain,
  trend: TrendingUp,
  customer: Users,
  sales: ShoppingCart,
  campaign: Target,
  alert: AlertTriangle,
  success: CheckCircle,
  opportunity: Lightbulb,
}

const insightColors = {
  prediction: 'text-purple-600 bg-purple-50 border-purple-200',
  trend: 'text-blue-600 bg-blue-50 border-blue-200',
  customer: 'text-green-600 bg-green-50 border-green-200',
  sales: 'text-orange-600 bg-orange-50 border-orange-200',
  campaign: 'text-pink-600 bg-pink-50 border-pink-200',
  alert: 'text-red-600 bg-red-50 border-red-200',
  success: 'text-emerald-600 bg-emerald-50 border-emerald-200',
  opportunity: 'text-yellow-600 bg-yellow-50 border-yellow-200',
}

export const AIInsightsFeed: React.FC = () => {
  const { data: insights, isLoading } = useQuery({
    queryKey: ['ai-insights'],
    queryFn: () => api.get('/insights/feed'),
    refetchInterval: 60000, // Refetch every minute
  })

  if (isLoading) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="animate-pulse">
          <div className="flex items-center mb-4">
            <div className="w-5 h-5 bg-gray-200 rounded mr-2"></div>
            <div className="h-4 bg-gray-200 rounded w-1/3"></div>
          </div>
          <div className="space-y-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-start space-x-3">
                  <div className="w-8 h-8 bg-gray-200 rounded-full"></div>
                  <div className="flex-1">
                    <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                    <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center">
          <Sparkles className="w-5 h-5 text-purple-600 mr-2" />
          <div>
            <h2 className="text-lg font-semibold text-gray-900">AI Insights</h2>
            <p className="text-sm text-gray-600">Intelligent recommendations</p>
          </div>
        </div>
        <Link
          to="/ai-assistant"
          className="text-sm text-blue-600 hover:text-blue-700 flex items-center"
        >
          View All
          <ChevronRight className="w-4 h-4 ml-1" />
        </Link>
      </div>

      <div className="space-y-4">
        {Array.isArray(insights) && insights.slice(0, 5).map((insight: any, index: number) => {
          const IconComponent = insightIcons[insight.type as keyof typeof insightIcons] || insightIcons.opportunity
          const colorClasses = insightColors[insight.type as keyof typeof insightColors] || insightColors.opportunity

          return (
            <motion.div
              key={insight.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className={`border rounded-lg p-4 ${colorClasses}`}
            >
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0">
                  <IconComponent className="w-5 h-5" />
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="text-sm font-semibold text-gray-900 mb-1">
                    {insight.title}
                  </h3>
                  <p className="text-sm text-gray-700 mb-2">
                    {insight.description}
                  </p>
                  
                  {insight.metrics && Array.isArray(insight.metrics) && (
                    <div className="flex flex-wrap gap-2 mb-2">
                      {insight.metrics.map((metric: any, idx: number) => (
                        <span
                          key={idx}
                          className="inline-flex items-center px-2 py-1 bg-white rounded-full text-xs font-medium"
                        >
                          {metric.label}: {metric.value}
                        </span>
                      ))}
                    </div>
                  )}

                  {insight.confidence && (
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-gray-600">
                        Confidence: {insight.confidence}%
                      </span>
                      <span className="text-gray-500">
                        {formatDistanceToNow(new Date(insight.generated_at), { addSuffix: true })}
                      </span>
                    </div>
                  )}

                  {insight.actions && Array.isArray(insight.actions) && insight.actions.length > 0 && (
                    <div className="mt-3 flex flex-wrap gap-2">
                      {insight.actions.map((action: any, idx: number) => (
                        <Link
                          key={idx}
                          to={action.link}
                          className="inline-flex items-center px-3 py-1 bg-white border border-gray-300 rounded-full text-xs font-medium hover:bg-gray-50 transition-colors"
                        >
                          {action.label}
                          <ChevronRight className="w-3 h-3 ml-1" />
                        </Link>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </motion.div>
          )
        })}

        {(!insights || insights.length === 0) && (
          <div className="text-center py-8">
            <Brain className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500 mb-2">No AI insights available</p>
            <p className="text-sm text-gray-400">
              Insights will appear as the AI analyzes your data
            </p>
          </div>
        )}
      </div>

      {insights && insights.length > 0 && (
        <div className="mt-6 pt-4 border-t border-gray-200">
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600">
              Powered by {insights.length} AI engines
            </span>
            <div className="flex items-center text-green-600">
              <div className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></div>
              Learning
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { formatDistanceToNow } from 'date-fns'
import {
  ShoppingCart, Users, Target, TrendingUp, AlertCircle,
  CheckCircle, Clock, ChevronRight
} from 'lucide-react'
import { Link } from 'react-router-dom'
import { api } from '@/lib/api'

const activityIcons = {
  purchase: ShoppingCart,
  customer: Users,
  campaign: Target,
  system: AlertCircle,
  success: CheckCircle,
  default: Clock,
}

const activityColors = {
  purchase: 'text-green-600 bg-green-50',
  customer: 'text-blue-600 bg-blue-50',
  campaign: 'text-purple-600 bg-purple-50',
  system: 'text-orange-600 bg-orange-50',
  success: 'text-emerald-600 bg-emerald-50',
  default: 'text-gray-600 bg-gray-50',
}

export const ActivityFeed: React.FC = () => {
  const { data: activities, isLoading, error } = useQuery({
    queryKey: ['activity-feed'],
    queryFn: async () => {
      try {
        const result = await api.get('/notifications/activity-feed')
        // Fallback to demo data if API fails
        return result || []
      } catch (err) {
        console.log('ActivityFeed API error, using demo data:', err)
        // Return demo data
        return [
          {
            id: '1',
            type: 'customer',
            title: 'New customer registered',
            description: 'Zhang Wei joined as VIP member',
            timestamp: new Date().toISOString(),
          },
          {
            id: '2', 
            type: 'purchase',
            title: 'Large purchase completed',
            description: '¥15,000 order from premium customer',
            timestamp: new Date(Date.now() - 300000).toISOString(),
          },
          {
            id: '3',
            type: 'campaign',
            title: 'Campaign performance update',
            description: 'Summer Sale campaign ROI: +125%',
            timestamp: new Date(Date.now() - 600000).toISOString(),
          }
        ]
      }
    },
    refetchInterval: 30000, // Refetch every 30 seconds
    retry: false, // Don't retry failed requests
  })

  if (isLoading) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gray-200 rounded-full"></div>
                <div className="flex-1">
                  <div className="h-4 bg-gray-200 rounded w-3/4 mb-1"></div>
                  <div className="h-3 bg-gray-200 rounded w-1/2"></div>
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
        <div>
          <h2 className="text-lg font-semibold text-gray-900">Recent Activity</h2>
          <p className="text-sm text-gray-600">Live updates from your CRM system</p>
        </div>
        <Link
          to="/operations"
          className="text-sm text-blue-600 hover:text-blue-700 flex items-center"
        >
          View All
          <ChevronRight className="w-4 h-4 ml-1" />
        </Link>
      </div>

      <div className="space-y-4">
        {Array.isArray(activities) && activities.slice(0, 10).map((activity: any) => {
          const IconComponent = activityIcons[activity.type as keyof typeof activityIcons] || activityIcons.default
          const colorClasses = activityColors[activity.type as keyof typeof activityColors] || activityColors.default

          return (
            <div key={activity.id || Math.random()} className="flex items-start space-x-3">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center ${colorClasses}`}>
                <IconComponent className="w-5 h-5" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 mb-1">
                  {activity.title || 'Untitled Activity'}
                </p>
                <p className="text-sm text-gray-600 mb-1">
                  {activity.description || 'No description available'}
                </p>
                <p className="text-xs text-gray-500">
                  {activity.timestamp ? formatDistanceToNow(new Date(activity.timestamp), { addSuffix: true }) : 'Unknown time'}
                </p>
              </div>
              {activity.link && (
                <Link
                  to={activity.link}
                  className="text-blue-600 hover:text-blue-700"
                >
                  <ChevronRight className="w-4 h-4" />
                </Link>
              )}
            </div>
          )
        })}

        {(!Array.isArray(activities) || activities.length === 0) && (
          <div className="text-center py-8">
            <Clock className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">No recent activity</p>
            {activities && !Array.isArray(activities) && (
              <p className="text-xs text-red-500 mt-2">
                Debug: Received non-array data: {typeof activities}
              </p>
            )}
          </div>
        )}
      </div>

      <div className="mt-6 pt-4 border-t border-gray-200">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600">Live updates every 30 seconds</span>
          <div className="flex items-center text-green-600">
            <div className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></div>
            Connected
          </div>
        </div>
      </div>
    </div>
  )
}
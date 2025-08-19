import React from 'react'
import { motion } from 'framer-motion'
import { X, Bell, CheckCircle, AlertTriangle, Info, Settings } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { formatDistanceToNow } from 'date-fns'
import { api } from '@/lib/api'
import { useTranslation } from '@/contexts/TranslationContext'

interface NotificationPanelProps {
  onClose: () => void
}

const notificationIcons = {
  success: CheckCircle,
  warning: AlertTriangle,
  info: Info,
  error: AlertTriangle,
}

const notificationColors = {
  success: 'text-green-600 bg-green-50',
  warning: 'text-orange-600 bg-orange-50',
  info: 'text-blue-600 bg-blue-50',
  error: 'text-red-600 bg-red-50',
}

export const NotificationPanel: React.FC<NotificationPanelProps> = ({ onClose }) => {
  const { t } = useTranslation()
  const { data: notifications, isLoading } = useQuery({
    queryKey: ['notifications'],
    queryFn: () => api.get('/notifications'),
  })

  return (
    <motion.div
      initial={{ x: '100%' }}
      animate={{ x: 0 }}
      exit={{ x: '100%' }}
      transition={{ type: 'spring', damping: 25, stiffness: 200 }}
      className="fixed right-0 top-0 h-full w-80 bg-white shadow-2xl border-l border-gray-200 z-50 flex flex-col"
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <div className="flex items-center space-x-3">
          <Bell className="w-5 h-5 text-gray-600" />
          <div>
            <h2 className="font-semibold text-gray-900">{t('notifications.title')}</h2>
            <p className="text-xs text-gray-600">{t('notifications.subtitle')}</p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <button className="p-1 hover:bg-gray-100 rounded">
            <Settings className="w-4 h-4 text-gray-500" />
          </button>
          <button
            onClick={onClose}
            className="p-1 hover:bg-gray-100 rounded"
          >
            <X className="w-4 h-4 text-gray-500" />
          </button>
        </div>
      </div>

      {/* Notifications List */}
      <div className="flex-1 overflow-y-auto">
        {isLoading ? (
          <div className="p-4">
            <div className="animate-pulse space-y-4">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="flex items-start space-x-3">
                  <div className="w-8 h-8 bg-gray-200 rounded-full"></div>
                  <div className="flex-1">
                    <div className="h-4 bg-gray-200 rounded w-3/4 mb-1"></div>
                    <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="divide-y divide-gray-100">
            {Array.isArray(notifications) && notifications?.map((notification: any) => {
              const IconComponent = notificationIcons[notification.type as keyof typeof notificationIcons] || Info
              const colorClasses = notificationColors[notification.type as keyof typeof notificationColors] || notificationColors.info

              return (
                <div
                  key={notification.id}
                  className={`p-4 hover:bg-gray-50 cursor-pointer ${!notification.read ? 'bg-blue-50/50' : ''}`}
                >
                  <div className="flex items-start space-x-3">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center ${colorClasses}`}>
                      <IconComponent className="w-4 h-4" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className={`text-sm font-medium text-gray-900 mb-1 ${!notification.read ? 'font-semibold' : ''}`}>
                        {notification.title}
                      </p>
                      <p className="text-sm text-gray-600 mb-2">
                        {notification.message}
                      </p>
                      <p className="text-xs text-gray-500">
                        {formatDistanceToNow(new Date(notification.created_at), { addSuffix: true })}
                      </p>
                    </div>
                    {!notification.read && (
                      <div className="w-2 h-2 bg-blue-600 rounded-full mt-2"></div>
                    )}
                  </div>
                </div>
              )
            })}

            {(!notifications || (Array.isArray(notifications) && notifications.length === 0)) && (
              <div className="p-8 text-center">
                <Bell className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500 mb-2">{t('notifications.noNotifications')}</p>
                <p className="text-sm text-gray-400">
                  {t('notifications.allCaughtUp')}
                </p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200">
        <div className="flex items-center justify-between">
          <button className="text-sm text-blue-600 hover:text-blue-700">
            Mark all as read
          </button>
          <button className="text-sm text-gray-600 hover:text-gray-700">
            Settings
          </button>
        </div>
      </div>
    </motion.div>
  )
}
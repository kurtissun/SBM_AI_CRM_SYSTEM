import React from 'react'
import { Activity, Bell, Settings } from 'lucide-react'

export const OperationsCenter: React.FC = () => {
  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Real-time Operations Center</h1>
        <p className="text-gray-600 mt-1">Live monitoring, notifications, and system management</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <Activity className="w-8 h-8 text-green-600 mb-4" />
          <h3 className="font-semibold text-gray-900 mb-2">Live Monitoring</h3>
          <p className="text-sm text-gray-600">Real-time system performance and activity tracking</p>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <Bell className="w-8 h-8 text-orange-600 mb-4" />
          <h3 className="font-semibold text-gray-900 mb-2">Notifications</h3>
          <p className="text-sm text-gray-600">Multi-channel alerts and notification management</p>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <Settings className="w-8 h-8 text-blue-600 mb-4" />
          <h3 className="font-semibold text-gray-900 mb-2">Webhooks</h3>
          <p className="text-sm text-gray-600">Integration system for external services</p>
        </div>
      </div>
    </div>
  )
}
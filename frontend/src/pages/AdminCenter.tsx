import React from 'react'
import { Settings, Users, Shield, Key, Database, Activity } from 'lucide-react'
import { RefreshKeyPanel } from '@/components/RefreshKeyPanel'
import { useAuthStore } from '@/stores/authStore'
import { useLanguageStore } from '@/stores/languageStore'

export const AdminCenter: React.FC = () => {
  const { user } = useAuthStore()
  const { t } = useLanguageStore()

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Configuration & Admin Center</h1>
        <p className="text-gray-600 mt-1">System configuration, user management, and security settings</p>
      </div>

      {/* User Info Card */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl border border-blue-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Welcome, {user?.username}</h2>
            <p className="text-sm text-gray-600">
              Role: <span className="font-medium text-blue-600">{user?.role}</span> | 
              Email: <span className="font-medium">{user?.email}</span>
            </p>
          </div>
          <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
            <Shield className="w-6 h-6 text-white" />
          </div>
        </div>
      </div>

      {/* Refresh Key Panel */}
      <RefreshKeyPanel />
      
      {/* Admin Features Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow cursor-pointer">
          <Users className="w-8 h-8 text-blue-600 mb-4" />
          <h3 className="font-semibold text-gray-900 mb-2">User Management</h3>
          <p className="text-sm text-gray-600">Role-based access control and permissions</p>
          <div className="mt-4 flex items-center text-blue-600 text-sm font-medium">
            View Users →
          </div>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow cursor-pointer">
          <Settings className="w-8 h-8 text-green-600 mb-4" />
          <h3 className="font-semibold text-gray-900 mb-2">System Configuration</h3>
          <p className="text-sm text-gray-600">API settings and integration management</p>
          <div className="mt-4 flex items-center text-green-600 text-sm font-medium">
            Configure →
          </div>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow cursor-pointer">
          <Shield className="w-8 h-8 text-purple-600 mb-4" />
          <h3 className="font-semibold text-gray-900 mb-2">Security & Audit</h3>
          <p className="text-sm text-gray-600">Security policies and audit logs</p>
          <div className="mt-4 flex items-center text-purple-600 text-sm font-medium">
            View Logs →
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow cursor-pointer">
          <Database className="w-8 h-8 text-orange-600 mb-4" />
          <h3 className="font-semibold text-gray-900 mb-2">Database Management</h3>
          <p className="text-sm text-gray-600">Backup, restore, and data management</p>
          <div className="mt-4 flex items-center text-orange-600 text-sm font-medium">
            Manage →
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow cursor-pointer">
          <Activity className="w-8 h-8 text-red-600 mb-4" />
          <h3 className="font-semibold text-gray-900 mb-2">System Monitoring</h3>
          <p className="text-sm text-gray-600">Performance metrics and health checks</p>
          <div className="mt-4 flex items-center text-red-600 text-sm font-medium">
            Monitor →
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow cursor-pointer">
          <Key className="w-8 h-8 text-indigo-600 mb-4" />
          <h3 className="font-semibold text-gray-900 mb-2">API Management</h3>
          <p className="text-sm text-gray-600">API keys, rate limiting, and documentation</p>
          <div className="mt-4 flex items-center text-indigo-600 text-sm font-medium">
            Manage APIs →
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">156</div>
            <div className="text-sm text-gray-600">Active Users</div>
          </div>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">99.9%</div>
            <div className="text-sm text-gray-600">System Uptime</div>
          </div>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-orange-600">2.1GB</div>
            <div className="text-sm text-gray-600">Database Size</div>
          </div>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">847</div>
            <div className="text-sm text-gray-600">API Calls Today</div>
          </div>
        </div>
      </div>
    </div>
  )
}
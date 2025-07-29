import React from 'react'
import { Settings, Users, Shield } from 'lucide-react'

export const AdminCenter: React.FC = () => {
  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Configuration & Admin Center</h1>
        <p className="text-gray-600 mt-1">System configuration, user management, and security settings</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <Users className="w-8 h-8 text-blue-600 mb-4" />
          <h3 className="font-semibold text-gray-900 mb-2">User Management</h3>
          <p className="text-sm text-gray-600">Role-based access control and permissions</p>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <Settings className="w-8 h-8 text-green-600 mb-4" />
          <h3 className="font-semibold text-gray-900 mb-2">System Configuration</h3>
          <p className="text-sm text-gray-600">API settings and integration management</p>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <Shield className="w-8 h-8 text-purple-600 mb-4" />
          <h3 className="font-semibold text-gray-900 mb-2">Security & Audit</h3>
          <p className="text-sm text-gray-600">Security policies and audit logs</p>
        </div>
      </div>
    </div>
  )
}
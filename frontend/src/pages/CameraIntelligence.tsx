import React from 'react'
import { Camera, Eye, Users } from 'lucide-react'

export const CameraIntelligence: React.FC = () => {
  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Camera Intelligence Dashboard</h1>
        <p className="text-gray-600 mt-1">AI-powered video analytics and crowd intelligence</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <Camera className="w-8 h-8 text-blue-600 mb-4" />
          <h3 className="font-semibold text-gray-900 mb-2">Live Footfall</h3>
          <p className="text-sm text-gray-600">Real-time visitor counting by zone</p>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <Eye className="w-8 h-8 text-green-600 mb-4" />
          <h3 className="font-semibold text-gray-900 mb-2">Demographics Analysis</h3>
          <p className="text-sm text-gray-600">Age and gender distribution visualization</p>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <Users className="w-8 h-8 text-purple-600 mb-4" />
          <h3 className="font-semibold text-gray-900 mb-2">Emotion Analytics</h3>
          <p className="text-sm text-gray-600">Customer satisfaction heatmaps</p>
        </div>
      </div>
    </div>
  )
}
import React from 'react'
import { Route, MapPin, Zap, Users } from 'lucide-react'

export const JourneyAutomation: React.FC = () => {
  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Journey & Automation Control</h1>
        <p className="text-gray-600 mt-1">Visual customer journey mapping and automated workflows</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <Route className="w-8 h-8 text-blue-600 mb-4" />
          <h3 className="font-semibold text-gray-900 mb-2">Journey Mapping</h3>
          <p className="text-sm text-gray-600">Visual customer journey canvas with touchpoint optimization</p>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <Zap className="w-8 h-8 text-purple-600 mb-4" />
          <h3 className="font-semibold text-gray-900 mb-2">Marketing Automation</h3>
          <p className="text-sm text-gray-600">Trigger-based campaigns and automated workflows</p>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <Users className="w-8 h-8 text-green-600 mb-4" />
          <h3 className="font-semibold text-gray-900 mb-2">Lead Scoring</h3>
          <p className="text-sm text-gray-600">AI-powered lead qualification and scoring</p>
        </div>
      </div>
      
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Journey Canvas</h2>
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-12 text-center">
          <MapPin className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">Drag and drop journey elements to build customer flows</p>
        </div>
      </div>
    </div>
  )
}
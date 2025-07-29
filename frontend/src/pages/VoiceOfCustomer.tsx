import React from 'react'
import { Mic, MessageSquare, TrendingUp } from 'lucide-react'

export const VoiceOfCustomer: React.FC = () => {
  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Voice of Customer Analytics</h1>
        <p className="text-gray-600 mt-1">Multi-platform feedback analysis and sentiment tracking</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <MessageSquare className="w-8 h-8 text-blue-600 mb-4" />
          <h3 className="font-semibold text-gray-900 mb-2">Review Aggregation</h3>
          <p className="text-sm text-gray-600">Collect and analyze reviews from multiple platforms</p>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <TrendingUp className="w-8 h-8 text-green-600 mb-4" />
          <h3 className="font-semibold text-gray-900 mb-2">Sentiment Analysis</h3>
          <p className="text-sm text-gray-600">Track satisfaction trends over time</p>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <Mic className="w-8 h-8 text-purple-600 mb-4" />
          <h3 className="font-semibold text-gray-900 mb-2">Social Listening</h3>
          <p className="text-sm text-gray-600">Monitor brand mentions and conversations</p>
        </div>
      </div>
    </div>
  )
}
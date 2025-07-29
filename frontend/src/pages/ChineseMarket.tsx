import React from 'react'
import { Globe, TrendingUp, MessageCircle } from 'lucide-react'

export const ChineseMarket: React.FC = () => {
  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Chinese Market & Competition Suite</h1>
        <p className="text-gray-600 mt-1">Local market insights and competitive intelligence</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <Globe className="w-8 h-8 text-red-600 mb-4" />
          <h3 className="font-semibold text-gray-900 mb-2">WeChat/Alipay Analytics</h3>
          <p className="text-sm text-gray-600">Payment method preferences and integration</p>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <MessageCircle className="w-8 h-8 text-green-600 mb-4" />
          <h3 className="font-semibold text-gray-900 mb-2">Social Media Monitoring</h3>
          <p className="text-sm text-gray-600">Weibo, Xiaohongshu, and Douyin sentiment analysis</p>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <TrendingUp className="w-8 h-8 text-blue-600 mb-4" />
          <h3 className="font-semibold text-gray-900 mb-2">Competitor Analysis</h3>
          <p className="text-sm text-gray-600">Market share and competitive benchmarking</p>
        </div>
      </div>
    </div>
  )
}
import React from 'react'
import { BarChart3, TrendingUp, Users, DollarSign } from 'lucide-react'

export const AnalyticsCenter: React.FC = () => {
  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Analytics & Insights Center</h1>
        <p className="text-gray-600 mt-1">Comprehensive business intelligence with AI-powered insights</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Predictive Analytics</p>
              <p className="text-3xl font-bold text-gray-900">94%</p>
            </div>
            <BarChart3 className="w-8 h-8 text-blue-600" />
          </div>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">CLV Predictions</p>
              <p className="text-3xl font-bold text-gray-900">¥12.5K</p>
            </div>
            <TrendingUp className="w-8 h-8 text-green-600" />
          </div>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Churn Risk Analysis</p>
              <p className="text-3xl font-bold text-gray-900">8.2%</p>
            </div>
            <Users className="w-8 h-8 text-purple-600" />
          </div>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Revenue Forecasting</p>
              <p className="text-3xl font-bold text-gray-900">¥2.1M</p>
            </div>
            <DollarSign className="w-8 h-8 text-orange-600" />
          </div>
        </div>
      </div>
      
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">AI-Generated Insights</h2>
        <div className="space-y-4">
          <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
            <h3 className="font-medium text-blue-900">Revenue Opportunity Identified</h3>
            <p className="text-sm text-blue-700 mt-1">VIP customers show 34% higher engagement with personalized offers. Recommend increasing VIP-targeted campaigns.</p>
          </div>
          <div className="p-4 bg-green-50 rounded-lg border border-green-200">
            <h3 className="font-medium text-green-900">Customer Behavior Pattern</h3>
            <p className="text-sm text-green-700 mt-1">Weekend shoppers have 28% higher average order value. Consider weekend-specific promotions.</p>
          </div>
        </div>
      </div>
    </div>
  )
}
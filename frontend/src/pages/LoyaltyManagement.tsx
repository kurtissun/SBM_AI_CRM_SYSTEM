import React from 'react'
import { Gift, Award, Star } from 'lucide-react'

export const LoyaltyManagement: React.FC = () => {
  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Loyalty & VIP Management</h1>
        <p className="text-gray-600 mt-1">Comprehensive loyalty program management and VIP services</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <Gift className="w-8 h-8 text-orange-600 mb-4" />
          <h3 className="font-semibold text-gray-900 mb-2">橙卡会员</h3>
          <p className="text-sm text-gray-600">Basic tier membership benefits and progression</p>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <Award className="w-8 h-8 text-yellow-600 mb-4" />
          <h3 className="font-semibold text-gray-900 mb-2">金卡会员</h3>
          <p className="text-sm text-gray-600">Premium tier with enhanced rewards</p>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <Star className="w-8 h-8 text-purple-600 mb-4" />
          <h3 className="font-semibold text-gray-900 mb-2">钻卡会员</h3>
          <p className="text-sm text-gray-600">VIP tier with exclusive concierge services</p>
        </div>
      </div>
    </div>
  )
}
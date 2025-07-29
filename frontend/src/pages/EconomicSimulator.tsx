import React from 'react'
import { TrendingUp, Calculator, Target } from 'lucide-react'

export const EconomicSimulator: React.FC = () => {
  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Economic & What-If Simulator</h1>
        <p className="text-gray-600 mt-1">Strategic planning with scenario modeling and impact analysis</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <Calculator className="w-8 h-8 text-blue-600 mb-4" />
          <h3 className="font-semibold text-gray-900 mb-2">Campaign Impact</h3>
          <p className="text-sm text-gray-600">Simulate campaign effects on revenue and customer behavior</p>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <TrendingUp className="w-8 h-8 text-green-600 mb-4" />
          <h3 className="font-semibold text-gray-900 mb-2">Market Scenarios</h3>
          <p className="text-sm text-gray-600">Model different market conditions and responses</p>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <Target className="w-8 h-8 text-purple-600 mb-4" />
          <h3 className="font-semibold text-gray-900 mb-2">Strategic Planning</h3>
          <p className="text-sm text-gray-600">Long-term planning with risk assessment</p>
        </div>
      </div>
    </div>
  )
}
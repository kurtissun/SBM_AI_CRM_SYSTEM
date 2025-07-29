import React from 'react'
import { FileText, BarChart3, Download } from 'lucide-react'

export const ReportsStudio: React.FC = () => {
  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Reports & Visualization Studio</h1>
        <p className="text-gray-600 mt-1">AI-powered report generation with 18+ chart types</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <FileText className="w-8 h-8 text-blue-600 mb-4" />
          <h3 className="font-semibold text-gray-900 mb-2">Report Builder</h3>
          <p className="text-sm text-gray-600">Drag-and-drop report designer with templates</p>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <BarChart3 className="w-8 h-8 text-green-600 mb-4" />
          <h3 className="font-semibold text-gray-900 mb-2">18+ Chart Types</h3>
          <p className="text-sm text-gray-600">Comprehensive visualization library</p>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <Download className="w-8 h-8 text-purple-600 mb-4" />
          <h3 className="font-semibold text-gray-900 mb-2">Export & Schedule</h3>
          <p className="text-sm text-gray-600">Automated report generation and distribution</p>
        </div>
      </div>
    </div>
  )
}
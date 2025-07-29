import React from 'react'
import { MessageSquare, Sparkles, Bot } from 'lucide-react'

export const AIAssistant: React.FC = () => {
  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">AI Assistant & Chat Suite</h1>
        <p className="text-gray-600 mt-1">Natural language interface for data queries and insights</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <MessageSquare className="w-8 h-8 text-blue-600 mb-4" />
          <h3 className="font-semibold text-gray-900 mb-2">Admin Chat</h3>
          <p className="text-sm text-gray-600">Database-integrated AI chat with natural language queries</p>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <Sparkles className="w-8 h-8 text-purple-600 mb-4" />
          <h3 className="font-semibold text-gray-900 mb-2">Generative Analytics</h3>
          <p className="text-sm text-gray-600">AI-powered report generation and insights</p>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <Bot className="w-8 h-8 text-green-600 mb-4" />
          <h3 className="font-semibold text-gray-900 mb-2">Customer Support</h3>
          <p className="text-sm text-gray-600">Conversational AI for customer interactions</p>
        </div>
      </div>
    </div>
  )
}
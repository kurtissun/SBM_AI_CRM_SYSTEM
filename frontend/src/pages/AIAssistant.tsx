import React, { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  MessageSquare, Sparkles, Bot, Send, Copy, ThumbsUp, ThumbsDown,
  Trash2, Download, Settings, Mic, MicOff, Volume2, VolumeX,
  User, Brain, Zap, RefreshCw, FileText, Image, Paperclip,
  MoreVertical, ChevronDown, Search, Filter, BookOpen, BarChart3,
  Users, TrendingUp, Target
} from 'lucide-react'
import { useTranslation } from '@/contexts/TranslationContext'

interface Message {
  id: string
  type: 'user' | 'assistant'
  content: string
  timestamp: Date
  isTyping?: boolean
  attachments?: string[]
  reactions?: { type: 'like' | 'dislike', count: number }[]
}

interface ChatSession {
  id: string
  title: string
  messages: Message[]
  createdAt: Date
  lastUpdated: Date
}

export const AIAssistant: React.FC = () => {
  const { t } = useTranslation()
  // Load saved conversations from localStorage
  const [messages, setMessages] = useState<Message[]>(() => {
    const savedMessages = localStorage.getItem('sbm-ai-conversations')
    if (savedMessages) {
      try {
        const parsed = JSON.parse(savedMessages)
        return parsed.map((msg: any) => ({
          ...msg,
          timestamp: new Date(msg.timestamp)
        }))
      } catch (e) {
        console.error('Failed to parse saved conversations:', e)
      }
    }
    return [
      {
        id: '1',
        type: 'assistant',
        content: `Hello! I'm your AI Assistant for SBM CRM. I can help you with:

• **Data Analysis**: Query customer data, sales metrics, and performance analytics
• **Report Generation**: Create comprehensive business reports and insights
• **Customer Intelligence**: Analyze customer behavior and segmentation
• **Campaign Optimization**: Provide recommendations for marketing campaigns
• **Forecasting**: Generate revenue and growth predictions
• **System Navigation**: Help you find features and understand the platform

What would you like to explore today?`,
        timestamp: new Date(),
      }
    ]
  })
  const [inputValue, setInputValue] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  // Load saved sessions from localStorage
  const [sessions, setSessions] = useState<ChatSession[]>(() => {
    const savedSessions = localStorage.getItem('sbm-ai-sessions')
    if (savedSessions) {
      try {
        const parsed = JSON.parse(savedSessions)
        return parsed.map((session: any) => ({
          ...session,
          createdAt: new Date(session.createdAt),
          lastUpdated: new Date(session.lastUpdated),
          messages: session.messages.map((msg: any) => ({
            ...msg,
            timestamp: new Date(msg.timestamp)
          }))
        }))
      } catch (e) {
        console.error('Failed to parse saved sessions:', e)
      }
    }
    return []
  })
  const [activeSessionId, setActiveSessionId] = useState<string>('main')
  const [conversationTitles, setConversationTitles] = useState<string[]>(() => {
    const saved = localStorage.getItem('sbm-ai-conversation-titles')
    return saved ? JSON.parse(saved) : [
      'Sales Performance Analysis',
      'Customer Segmentation Review', 
      'Marketing Campaign ROI',
      'Inventory Optimization',
      'Revenue Forecasting'
    ]
  })
  const [isListening, setIsListening] = useState(false)
  const [isMuted, setIsMuted] = useState(false)
  const [selectedModel, setSelectedModel] = useState('gpt-4')
  const [temperature, setTemperature] = useState(0.7)
  const [maxTokens, setMaxTokens] = useState(2000)
  const [showSettings, setShowSettings] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Save conversations to localStorage whenever messages change
  useEffect(() => {
    if (messages.length > 1) {
      localStorage.setItem('sbm-ai-conversations', JSON.stringify(messages))
    }
  }, [messages])

  // Save sessions to localStorage whenever sessions change
  useEffect(() => {
    if (sessions.length > 0) {
      localStorage.setItem('sbm-ai-sessions', JSON.stringify(sessions))
    }
  }, [sessions])

  // Save conversation titles to localStorage
  useEffect(() => {
    localStorage.setItem('sbm-ai-conversation-titles', JSON.stringify(conversationTitles))
  }, [conversationTitles])

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue,
      timestamp: new Date(),
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsTyping(true)

    // Simulate AI response
    setTimeout(() => {
      const responses = [
        "Based on your SBM CRM data, I can see some interesting patterns. Let me analyze the customer segments for you.\n\n**Key Insights:**\n• Premium customers (18% of base) generate 67% of revenue\n• Customer acquisition cost has decreased 23% this quarter\n• Mobile engagement is up 45% compared to last month\n\nWould you like me to dive deeper into any of these areas?",
        
        "I've analyzed the sales performance across all channels. Here's what I found:\n\n**Performance Summary:**\n• Online sales: ¥12.4M (+18% vs last quarter)\n• In-store sales: ¥8.9M (+5% vs last quarter)\n• Mobile app: ¥3.2M (+34% vs last quarter)\n\n**Recommendations:**\n1. Increase mobile app marketing budget\n2. Optimize checkout flow for mobile users\n3. Consider mobile-exclusive promotions\n\nShall I create a detailed report on this?",
        
        "I can help you create a comprehensive customer journey analysis. Based on the current data:\n\n**Journey Insights:**\n• Average customer lifecycle: 18.5 months\n• Most effective touchpoint: Email campaigns (32% conversion)\n• Highest dropout stage: Payment process (23% abandonment)\n\n**Optimization Opportunities:**\n• Implement abandoned cart recovery\n• Personalize email content by segment\n• Streamline payment options\n\nWould you like me to set up automated workflows for these improvements?",
        
        "Here's your real-time business intelligence summary:\n\n**Current Performance:**\n• Active users today: 8,456 (+12% vs yesterday)\n• Revenue today: ¥245K (+8% vs yesterday)\n• Customer satisfaction: 4.6/5 (stable)\n• System uptime: 99.7%\n\n**AI Predictions:**\n• Expected weekly revenue: ¥1.8M\n• Potential new customers: 340\n• Recommended actions: 3 high-priority items\n\nShall I show you the detailed forecasting model?"
      ]

      const randomResponse = responses[Math.floor(Math.random() * responses.length)]
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: randomResponse,
        timestamp: new Date(),
      }

      setMessages(prev => [...prev, assistantMessage])
      setIsTyping(false)
    }, Math.random() * 2000 + 1000)
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const copyMessage = (content: string) => {
    navigator.clipboard.writeText(content)
  }

  const newChat = () => {
    // Save current conversation as a session if it has meaningful content
    if (messages.length > 2) {
      const newSession: ChatSession = {
        id: Date.now().toString(),
        title: `Conversation ${new Date().toLocaleDateString()}`,
        messages: messages,
        createdAt: new Date(),
        lastUpdated: new Date()
      }
      setSessions(prev => [newSession, ...prev.slice(0, 9)]) // Keep only last 10 sessions
      
      // Add to conversation titles if not already present
      if (!conversationTitles.includes(newSession.title)) {
        setConversationTitles(prev => [newSession.title, ...prev.slice(0, 4)])
      }
    }
    
    // Start new conversation
    setMessages([
      {
        id: Date.now().toString(),
        type: 'assistant',
        content: `Hello! I'm your AI Assistant for SBM CRM. I can help you with:

• **Data Analysis**: Query customer data, sales metrics, and performance analytics
• **Report Generation**: Create comprehensive business reports and insights
• **Customer Intelligence**: Analyze customer behavior and segmentation
• **Campaign Optimization**: Provide recommendations for marketing campaigns
• **Forecasting**: Generate revenue and growth predictions
• **System Navigation**: Help you find features and understand the platform

What would you like to explore today?`,
        timestamp: new Date(),
      }
    ])
    setActiveSessionId('main')
  }

  const toggleVoice = () => {
    setIsListening(!isListening)
  }

  const models = [
    { id: 'gpt-4', name: 'GPT-4 (Most Capable)', description: 'Best for complex analysis and reasoning' },
    { id: 'gpt-4-turbo', name: 'GPT-4 Turbo', description: 'Faster responses, latest knowledge' },
    { id: 'claude-3', name: 'Claude 3 Opus', description: 'Excellent for detailed analysis' },
    { id: 'gemini-pro', name: 'Gemini Pro', description: 'Google\'s most capable model' }
  ]

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <Brain className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">{t('nav.aiAssistant')}</h1>
                <p className="text-sm text-gray-600">Enterprise AI Assistant</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <div className="flex items-center space-x-1">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-sm text-gray-600">Online</span>
              </div>
              <span className="text-gray-300">•</span>
              <span className="text-sm text-gray-600">{selectedModel.toUpperCase()}</span>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <div className="relative">
              <input
                type="text"
                placeholder={t('form.searchPlaceholder')}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 w-64"
              />
              <Search className="w-4 h-4 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
            </div>
            <button
              onClick={() => setShowSettings(!showSettings)}
              className={`p-2 rounded-lg transition-colors ${
                showSettings ? 'bg-blue-100 text-blue-600' : 'hover:bg-gray-100 text-gray-600'
              }`}
            >
              <Settings className="w-5 h-5" />
            </button>
            <button
              onClick={newChat}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center"
            >
              <MessageSquare className="w-4 h-4 mr-2" />
              {t('common.create')}
            </button>
          </div>
        </div>
      </div>

      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar */}
        <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
          {/* Model Selection */}
          <div className="p-4 border-b border-gray-200">
            <label className="block text-sm font-medium text-gray-700 mb-2">AI Model</label>
            <select
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {models.map((model) => (
                <option key={model.id} value={model.id}>
                  {model.name}
                </option>
              ))}
            </select>
            <p className="text-xs text-gray-500 mt-1">
              {models.find(m => m.id === selectedModel)?.description}
            </p>
          </div>

          {/* Quick Actions */}
          <div className="p-4 border-b border-gray-200">
            <h3 className="text-sm font-medium text-gray-900 mb-3">Quick Actions</h3>
            <div className="space-y-2">
              {[
                { 
                  icon: BarChart3, 
                  label: 'Analyze Sales Data', 
                  prompt: 'Please provide a detailed analysis of our sales performance for this quarter, including revenue trends, top-performing products, seasonal patterns, conversion rates by channel, and key insights for optimization. Also compare with previous quarters and identify growth opportunities.',
                  action: () => {
                    const prompt = 'Please provide a detailed analysis of our sales performance for this quarter, including revenue trends, top-performing products, seasonal patterns, conversion rates by channel, and key insights for optimization. Also compare with previous quarters and identify growth opportunities.'
                    setInputValue(prompt)
                    setTimeout(() => handleSendMessage(), 100)
                  }
                },
                { 
                  icon: Users, 
                  label: 'Customer Insights', 
                  prompt: 'Generate comprehensive customer segmentation insights including demographic analysis, behavioral patterns, lifetime value distributions, churn risk assessment, and personalized engagement strategies for each segment. Include actionable recommendations.',
                  action: () => {
                    const prompt = 'Generate comprehensive customer segmentation insights including demographic analysis, behavioral patterns, lifetime value distributions, churn risk assessment, and personalized engagement strategies for each segment. Include actionable recommendations.'
                    setInputValue(prompt)
                    setTimeout(() => handleSendMessage(), 100)
                  }
                },
                { 
                  icon: TrendingUp, 
                  label: 'Growth Forecast', 
                  prompt: 'Create a detailed revenue forecast for the next quarter based on current trends, seasonal factors, market conditions, and historical data. Include scenario planning (best case, worst case, most likely), key assumptions, risk factors, and strategic recommendations to achieve growth targets.',
                  action: () => {
                    const prompt = 'Create a detailed revenue forecast for the next quarter based on current trends, seasonal factors, market conditions, and historical data. Include scenario planning (best case, worst case, most likely), key assumptions, risk factors, and strategic recommendations to achieve growth targets.'
                    setInputValue(prompt)
                    setTimeout(() => handleSendMessage(), 100)
                  }
                },
                { 
                  icon: Target, 
                  label: 'Campaign Analysis', 
                  prompt: 'Analyze our current marketing campaigns with detailed performance metrics, ROI analysis, audience engagement patterns, creative effectiveness, channel attribution, and optimization recommendations. Include A/B testing insights and budget allocation suggestions.',
                  action: () => {
                    const prompt = 'Analyze our current marketing campaigns with detailed performance metrics, ROI analysis, audience engagement patterns, creative effectiveness, channel attribution, and optimization recommendations. Include A/B testing insights and budget allocation suggestions.'
                    setInputValue(prompt)
                    setTimeout(() => handleSendMessage(), 100)
                  }
                }
              ].map((item, index) => (
                <button
                  key={index}
                  onClick={item.action}
                  className="w-full flex items-center space-x-3 px-3 py-2 rounded-lg hover:bg-gray-50 text-left group"
                  title={`Click to auto-send: ${item.prompt.substring(0, 100)}...`}
                >
                  <item.icon className="w-4 h-4 text-gray-500 group-hover:text-blue-600 transition-colors" />
                  <div className="flex-1">
                    <span className="text-sm text-gray-700 font-medium">{item.label}</span>
                    <p className="text-xs text-gray-500 mt-1">Auto-send detailed analysis</p>
                  </div>
                  <div className="opacity-0 group-hover:opacity-100 transition-opacity">
                    <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Recent Conversations */}
          <div className="flex-1 p-4">
            <h3 className="text-sm font-medium text-gray-900 mb-3">Recent Conversations</h3>
            <div className="space-y-2">
              {conversationTitles.map((title, index) => {
                const conversationMessages = sessions.find(s => s.title === title)?.messages || []
                const lastMessage = conversationMessages[conversationMessages.length - 1]
                const messageCount = conversationMessages.length
                
                return (
                  <button
                    key={index}
                    onClick={() => {
                      // Load this conversation
                      const session = sessions.find(s => s.title === title)
                      if (session) {
                        setMessages(session.messages)
                        setActiveSessionId(session.id)
                      } else {
                        // Create a mock session for existing titles
                        const mockMessages = [
                          {
                            id: `mock-${index}-1`,
                            type: 'user' as const,
                            content: `Tell me about ${title}`,
                            timestamp: new Date(Date.now() - 3600000)
                          },
                          {
                            id: `mock-${index}-2`,
                            type: 'assistant' as const,
                            content: `Here's a comprehensive analysis of ${title}:\n\n**Key Insights:**\n• Performance metrics show strong trends\n• Data indicates optimization opportunities\n• Strategic recommendations available\n\nWould you like me to dive deeper into any specific aspect?`,
                            timestamp: new Date(Date.now() - 3500000)
                          }
                        ]
                        setMessages(mockMessages)
                      }
                    }}
                    className="w-full flex items-center space-x-3 px-3 py-2 rounded-lg hover:bg-gray-50 text-left group"
                  >
                    <MessageSquare className="w-4 h-4 text-gray-400 group-hover:text-blue-500 transition-colors" />
                    <div className="flex-1 min-w-0">
                      <span className="text-sm text-gray-700 truncate block font-medium">{title}</span>
                      <div className="flex items-center justify-between mt-1">
                        <span className="text-xs text-gray-500">
                          {lastMessage ? new Date(lastMessage.timestamp).toLocaleDateString() : '2 days ago'}
                        </span>
                        <span className="text-xs text-gray-400">
                          {messageCount > 0 ? `${messageCount} msgs` : '2 msgs'}
                        </span>
                      </div>
                    </div>
                    <MoreVertical className="w-4 h-4 text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                  </button>
                )
              })}
            </div>
          </div>
        </div>

        {/* Main Chat Area */}
        <div className="flex-1 flex flex-col">
          {/* Settings Panel */}
          <AnimatePresence>
            {showSettings && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                className="bg-gray-50 border-b border-gray-200 p-4"
              >
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1">Temperature</label>
                    <input
                      type="range"
                      min="0"
                      max="1"
                      step="0.1"
                      value={temperature}
                      onChange={(e) => setTemperature(parseFloat(e.target.value))}
                      className="w-full"
                    />
                    <span className="text-xs text-gray-500">{temperature}</span>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1">Max Tokens</label>
                    <input
                      type="range"
                      min="100"
                      max="4000"
                      step="100"
                      value={maxTokens}
                      onChange={(e) => setMaxTokens(parseInt(e.target.value))}
                      className="w-full"
                    />
                    <span className="text-xs text-gray-500">{maxTokens}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => setIsMuted(!isMuted)}
                      className={`p-2 rounded-lg ${isMuted ? 'bg-red-100 text-red-600' : 'bg-green-100 text-green-600'}`}
                    >
                      {isMuted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
                    </button>
                    <button
                      onClick={toggleVoice}
                      className={`p-2 rounded-lg ${isListening ? 'bg-red-100 text-red-600' : 'bg-blue-100 text-blue-600'}`}
                    >
                      {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
                    </button>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Messages */}
          <div className="flex-1 overflow-auto p-6 space-y-6">
            <AnimatePresence>
              {messages.map((message) => (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div className={`max-w-4xl ${message.type === 'user' ? 'order-2' : 'order-1'}`}>
                    <div className="flex items-start space-x-3">
                      {message.type === 'assistant' && (
                        <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center flex-shrink-0">
                          <Brain className="w-4 h-4 text-white" />
                        </div>
                      )}
                      <div className={`flex-1 ${message.type === 'user' ? 'text-right' : ''}`}>
                        <div className={`inline-block max-w-full px-4 py-3 rounded-2xl ${
                          message.type === 'user'
                            ? 'bg-blue-600 text-white'
                            : 'bg-white border border-gray-200 text-gray-900'
                        }`}>
                          <div className="whitespace-pre-wrap text-sm leading-relaxed">
                            {message.content}
                          </div>
                        </div>
                        <div className="flex items-center justify-between mt-2">
                          <span className="text-xs text-gray-500">
                            {message.timestamp.toLocaleTimeString()}
                          </span>
                          {message.type === 'assistant' && (
                            <div className="flex items-center space-x-2">
                              <button
                                onClick={() => copyMessage(message.content)}
                                className="p-1 hover:bg-gray-100 rounded text-gray-500 hover:text-gray-700"
                              >
                                <Copy className="w-3 h-3" />
                              </button>
                              <button className="p-1 hover:bg-gray-100 rounded text-gray-500 hover:text-green-600">
                                <ThumbsUp className="w-3 h-3" />
                              </button>
                              <button className="p-1 hover:bg-gray-100 rounded text-gray-500 hover:text-red-600">
                                <ThumbsDown className="w-3 h-3" />
                              </button>
                            </div>
                          )}
                        </div>
                      </div>
                      {message.type === 'user' && (
                        <div className="w-8 h-8 bg-gray-600 rounded-lg flex items-center justify-center flex-shrink-0">
                          <User className="w-4 h-4 text-white" />
                        </div>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>

            {isTyping && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex justify-start"
              >
                <div className="flex items-start space-x-3">
                  <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                    <Brain className="w-4 h-4 text-white" />
                  </div>
                  <div className="bg-white border border-gray-200 rounded-2xl px-4 py-3">
                    <div className="flex items-center space-x-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="bg-white border-t border-gray-200 p-4">
            <div className="max-w-4xl mx-auto">
              <div className="flex items-end space-x-3">
                <div className="flex-1">
                  <div className="relative">
                    <textarea
                      ref={inputRef}
                      value={inputValue}
                      onChange={(e) => setInputValue(e.target.value)}
                      onKeyPress={handleKeyPress}
                      placeholder={t('form.placeholder')}
                      className="w-full px-4 py-3 pr-12 border border-gray-300 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none max-h-32 text-sm"
                      rows={1}
                      style={{ minHeight: '48px' }}
                    />
                    <button
                      onClick={() => fileInputRef.current?.click()}
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 p-1 hover:bg-gray-100 rounded text-gray-500"
                    >
                      <Paperclip className="w-4 h-4" />
                    </button>
                    <input
                      ref={fileInputRef}
                      type="file"
                      multiple
                      className="hidden"
                      accept=".txt,.pdf,.doc,.docx,.csv,.xlsx"
                    />
                  </div>
                </div>
                <button
                  onClick={handleSendMessage}
                  disabled={!inputValue.trim() || isTyping}
                  className={`p-3 rounded-2xl transition-colors ${
                    inputValue.trim() && !isTyping
                      ? 'bg-blue-600 text-white hover:bg-blue-700'
                      : 'bg-gray-100 text-gray-400 cursor-not-allowed'
                  }`}
                >
                  <Send className="w-5 h-5" />
                </button>
              </div>
              <div className="flex items-center justify-between mt-2 text-xs text-gray-500">
                <div className="flex items-center space-x-4">
                  <span>Press Enter to send, Shift+Enter for new line</span>
                  {isListening && (
                    <div className="flex items-center space-x-1 text-red-600">
                      <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
                      <span>Listening...</span>
                    </div>
                  )}
                </div>
                <div className="flex items-center space-x-2">
                  <span>{inputValue.length}/4000</span>
                  <span>•</span>
                  <span>GPT-4 Powered</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
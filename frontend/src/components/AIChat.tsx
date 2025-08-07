import React, { useState, useRef, useEffect } from 'react'
import { motion } from 'framer-motion'
import { X, Send, Mic, MicOff, Sparkles, User, Bot, Smile, Briefcase } from 'lucide-react'
import { useMutation } from '@tanstack/react-query'
import { api } from '@/lib/api'
import { toast } from 'react-hot-toast'
import { useTranslation } from '@/contexts/TranslationContext'

interface ChatMessage {
  id: string
  type: 'user' | 'ai'
  content: string
  timestamp: Date
  data_insights?: any
  suggestions?: string[]
}

interface AIChatProps {
  onClose: () => void
}

export const AIChat: React.FC<AIChatProps> = ({ onClose }) => {
  const { t } = useTranslation()
  const [chatMode, setChatMode] = useState<'serious' | 'joking'>('joking')
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      type: 'ai',
      content: '👋 Hello! I\'m your advanced AI business intelligence assistant powered by 22 AI models. I can analyze your CRM data in real-time, generate strategic insights, and provide actionable recommendations.\n\n🧠 I excel at:\n• Revenue forecasting & trend analysis\n• Customer segmentation & behavior insights\n• Campaign performance optimization\n• Business intelligence dashboards\n• Predictive analytics & risk assessment\n\nJust ask me anything about your business data!',
      timestamp: new Date(),
      data_insights: {
        'AI Models Active': '22',
        'Data Processing': 'Real-time',
        'Accuracy Rate': '94.3%',
        'Response Time': '<2s'
      },
      suggestions: [
        'Show me revenue trends',
        'Analyze customer segments',
        'Campaign performance review',
        'Generate business forecast'
      ]
    }
  ])
  const [inputValue, setInputValue] = useState('')
  const [isListening, setIsListening] = useState(false)
  const [isTyping, setIsTyping] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  // Mock AI response generator
  const generateAIResponse = (message: string, mode: 'serious' | 'joking') => {
    const lowerMessage = message.toLowerCase()
    
    // Business intelligence responses
    if (lowerMessage.includes('revenue') || lowerMessage.includes('sales')) {
      return {
        response: mode === 'serious' 
          ? `Based on current data analysis:\n\n• Total revenue: ¥2.4M (↑15% vs last month)\n• Daily average: ¥80K\n• Top performing segment: VIP customers (¥890K)\n• Revenue forecast: ¥2.8M next month\n\nRecommendation: Focus on VIP customer retention and expand mid-tier segment.`
          : `💰 Your revenue is looking quite healthy! We're sitting at ¥2.4M this month - that's like buying 12,000 cups of premium coffee! ☕\n\nThe VIP customers are your golden geese (¥890K), while your other segments are steadily climbing. Keep feeding those geese! 🦢✨`,
        data_insights: {
          'Total Revenue': '¥2.4M',
          'Growth Rate': '+15%',
          'VIP Revenue': '¥890K',
          'Forecast': '¥2.8M'
        },
        suggestions: ['Show me customer segments', 'What about campaign performance?', 'Revenue breakdown by region', 'Predict next quarter']
      }
    }
    
    if (lowerMessage.includes('customer') || lowerMessage.includes('segment')) {
      return {
        response: mode === 'serious'
          ? `Customer Intelligence Analysis:\n\n• Total active customers: 18,456\n• New acquisitions: +12% this month\n• Top segments: VIP (1,200), Premium (4,800), Standard (12,456)\n• Churn rate: 3.2% (below industry average)\n• Average customer value: ¥1,847\n\nKey insight: VIP segment shows 94% retention rate and 3x higher spending.`
          : `🎯 Let's talk customers! You've got 18,456 lovely humans in your ecosystem - that's like a small city!\n\nYour VIP customers (1,200 of them) are basically customer royalty 👑 with 94% sticking around. They're your ride-or-die customers who probably dream about your products! 😄\n\nThe rest are pretty happy too - only 3.2% decided to break up with you this month. Not bad!`,
        data_insights: {
          'Active Customers': '18,456',
          'VIP Customers': '1,200',
          'Retention Rate': '94%',
          'Churn Rate': '3.2%'
        },
        suggestions: ['Analyze VIP behavior', 'Customer acquisition cost', 'Segment performance trends', 'Churn prediction']
      }
    }
    
    if (lowerMessage.includes('create') && lowerMessage.includes('campaign')) {
      return {
        response: mode === 'serious'
          ? `To create a new campaign, I'll guide you through the process:\n\n1. Navigate to Campaign Center from the dashboard\n2. Click "Create Campaign" button\n3. Set up your campaign:\n   • Name & Objective\n   • Target audience selection\n   • Budget allocation\n   • Schedule & duration\n   • Channels (WeChat, SMS, Email)\n\nQuick access: Click on the "Campaign Center" in the left navigation menu or use the quick action button on the dashboard.`
          : `🎯 Ready to launch a new campaign? Let's make it awesome!\n\nJust head over to the Campaign Center (it's in the sidebar) and hit that shiny "Create Campaign" button! 🚀\n\nYou'll need to pick:\n• A catchy name (make it memorable!)\n• Your target audience (who's getting lucky today?)\n• Budget (how much treasure to spend 💰)\n• When to run it (timing is everything!)\n\nThe system will guide you through each step - it's easier than making instant noodles! 🍜`,
        data_insights: {
          'Campaign Center': 'Available',
          'Templates': '12 pre-built',
          'AI Optimization': 'Enabled',
          'Quick Start': '< 5 minutes'
        },
        suggestions: ['Show me Campaign Center', 'What are the best campaign types?', 'Campaign budget recommendations', 'Target audience insights']
      }
    }
    
    if (lowerMessage.includes('campaign') || lowerMessage.includes('marketing')) {
      return {
        response: mode === 'serious'
          ? `Campaign Performance Overview:\n\n• Active campaigns: 24\n• Average ROI: 127.3%\n• Best performer: Summer Sale (180% ROI)\n• Total reach: 145K customers\n• Conversion rate: 8.7%\n• Cost per acquisition: ¥156\n\nRecommendation: Scale successful campaigns and optimize underperforming ones.`
          : `🚀 Your campaigns are working harder than a bee in a flower garden! \n\n24 campaigns are out there doing their thing, with an average ROI of 127% - that's like planting ¥1 and harvesting ¥2.27! 🌱💰\n\nYour Summer Sale campaign is the superstar here with 180% ROI. Maybe it should get its own fan club! 🌟`,
        data_insights: {
          'Active Campaigns': '24',
          'Average ROI': '127.3%',
          'Best Campaign': 'Summer Sale (180%)',
          'Conversion Rate': '8.7%'
        },
        suggestions: ['Campaign optimization tips', 'A/B testing results', 'Budget allocation', 'Seasonal trends']
      }
    }
    
    if (lowerMessage.includes('forecast') || lowerMessage.includes('predict')) {
      return {
        response: mode === 'serious'
          ? `AI Forecasting Analysis:\n\n• Next month revenue: ¥2.8M (16.7% growth)\n• Customer acquisition: +340 new customers\n• High-probability scenarios: 89% confidence\n• Seasonal adjustments: Summer boost expected\n• Risk factors: Market competition, economic conditions\n\nModel accuracy: 94.3% based on historical data.`
          : `🔮 Time to gaze into my crystal ball! \n\nNext month looks bright with ¥2.8M revenue coming your way - that's like finding a treasure chest worth 16.7% more gold! 🏴‍☠️💰\n\n340 new customers are likely to join your adventure, and summer vibes should give you an extra boost. My predictions are right 94.3% of the time (I'm basically a fortune teller with better math skills! 🧙‍♂️)`,
        data_insights: {
          'Revenue Forecast': '¥2.8M',
          'Growth Rate': '+16.7%',
          'New Customers': '+340',
          'Confidence': '89%'
        },
        suggestions: ['Scenario planning', 'Risk analysis', 'Growth strategies', 'Market trends']
      }
    }
    
    if (lowerMessage.includes('analytics') || lowerMessage.includes('report')) {
      return {
        response: mode === 'serious'
          ? `Analytics Dashboard Summary:\n\n• Data points processed: 2.4M daily\n• Active dashboards: 15\n• Real-time metrics: 47 KPIs tracked\n• Report generation: 23 automated reports\n• Data accuracy: 99.2%\n• Processing speed: 1.3ms average\n\nAll systems operational with optimal performance.`
          : `📊 Your analytics are humming like a well-tuned engine! \n\nWe're crunching 2.4M data points daily - that's like counting all the stars in a galaxy! ✨ Your 15 dashboards are showing off 47 different KPIs, and 23 reports are writing themselves (they're pretty smart!).\n\n99.2% accuracy means we're almost perfect - the 0.8% is just us being humble! 😉`,
        data_insights: {
          'Daily Data Points': '2.4M',
          'Active Dashboards': '15',
          'KPIs Tracked': '47',
          'Data Accuracy': '99.2%'
        },
        suggestions: ['Dashboard customization', 'KPI optimization', 'Data visualization', 'Automated insights']
      }
    }
    
    // Default responses for other queries
    const defaultResponses = mode === 'serious' ? [
      `I'm analyzing your request. Could you be more specific about what data or insights you need?`,
      `Based on current system status, all metrics are within normal parameters. What specific analysis would you like me to perform?`,
      `I have access to comprehensive business intelligence data. Please specify which area you'd like me to focus on.`,
      `Your CRM system is operating optimally. What business questions can I help you answer?`
    ] : [
      `🤔 That's an interesting question! I'm like a business detective - give me some clues about what you want to discover!`,
      `💡 I'm ready to dive into your data ocean! What treasure are we hunting for today?`,
      `🎯 I love a good challenge! Tell me more about what you're curious about and I'll work my AI magic!`,
      `✨ Your wish is my command! Well, as long as it involves data analysis and business insights. What can I explore for you?`
    ]
    
    return {
      response: defaultResponses[Math.floor(Math.random() * defaultResponses.length)],
      suggestions: ['Show revenue dashboard', 'Analyze customer behavior', 'Campaign performance', 'Generate forecast']
    }
  }

  const chatMutation = useMutation({
    mutationFn: async (message: string) => {
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000))
      return generateAIResponse(message, chatMode)
    },
    onSuccess: (data: any) => {
      const aiMessage: ChatMessage = {
        id: Date.now().toString(),
        type: 'ai',
        content: data.response,
        timestamp: new Date(),
        data_insights: data.data_insights,
        suggestions: data.suggestions
      }
      setMessages(prev => [...prev, aiMessage])
      setIsTyping(false)
    },
    onError: () => {
      setIsTyping(false)
      toast.error('Failed to send message')
    }
  })

  const handleSendMessage = () => {
    if (!inputValue.trim()) return

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue,
      timestamp: new Date(),
    }

    setMessages(prev => [...prev, userMessage])
    setIsTyping(true)
    chatMutation.mutate(inputValue)
    setInputValue('')
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const handleSuggestionClick = (suggestion: string) => {
    setInputValue(suggestion)
    inputRef.current?.focus()
    // Auto-send the suggestion
    setTimeout(() => {
      if (suggestion.trim()) {
        const userMessage: ChatMessage = {
          id: Date.now().toString(),
          type: 'user',
          content: suggestion,
          timestamp: new Date(),
        }
        setMessages(prev => [...prev, userMessage])
        setIsTyping(true)
        chatMutation.mutate(suggestion)
        setInputValue('')
      }
    }, 100)
  }

  // Process message content to remove ** formatting and add interactive elements
  const processMessageContent = (content: string, messageId: string) => {
    // Remove ** markdown formatting
    const cleanContent = content.replace(/\*\*(.*?)\*\*/g, '$1')
    
    // Split content into paragraphs and identify actionable items
    const paragraphs = cleanContent.split('\n').filter(p => p.trim())
    
    return (
      <div className="space-y-2">
        {paragraphs.map((paragraph, index) => (
          <div key={index}>
            <p className="text-sm">{paragraph}</p>
            {/* Add interactive buttons for specific content */}
            {paragraph.includes('Campaign Center') && (
              <button
                onClick={() => handleSuggestionClick('Take me to Campaign Center')}
                className="mt-1 px-2 py-1 bg-blue-500 text-white text-xs rounded hover:bg-blue-600 transition-colors"
              >
                Go to Campaign Center
              </button>
            )}
            {paragraph.includes('revenue') && paragraph.includes('¥') && (
              <button
                onClick={() => handleSuggestionClick('Show me detailed revenue analysis')}
                className="mt-1 ml-2 px-2 py-1 bg-green-500 text-white text-xs rounded hover:bg-green-600 transition-colors"
              >
                Detailed Analysis
              </button>
            )}
            {paragraph.includes('customer') && paragraph.includes('segment') && (
              <button
                onClick={() => handleSuggestionClick('Analyze customer segments in detail')}
                className="mt-1 ml-2 px-2 py-1 bg-purple-500 text-white text-xs rounded hover:bg-purple-600 transition-colors"
              >
                Deep Dive
              </button>
            )}
            {paragraph.includes('VIP') && (
              <button
                onClick={() => handleSuggestionClick('Tell me more about VIP customers')}
                className="mt-1 ml-2 px-2 py-1 bg-yellow-500 text-white text-xs rounded hover:bg-yellow-600 transition-colors"
              >
                VIP Insights
              </button>
            )}
          </div>
        ))}
      </div>
    )
  }

  const toggleVoiceInput = () => {
    if (!isListening) {
      // Start voice recognition
      if ('webkitSpeechRecognition' in window) {
        const recognition = new (window as any).webkitSpeechRecognition()
        recognition.continuous = false
        recognition.interimResults = false
        recognition.lang = 'en-US'

        recognition.onstart = () => {
          setIsListening(true)
        }

        recognition.onresult = (event: any) => {
          const transcript = event.results[0][0].transcript
          setInputValue(transcript)
          setIsListening(false)
        }

        recognition.onerror = () => {
          setIsListening(false)
          toast.error('Voice recognition failed')
        }

        recognition.onend = () => {
          setIsListening(false)
        }

        recognition.start()
      } else {
        toast.error('Voice recognition not supported')
      }
    } else {
      setIsListening(false)
    }
  }

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  return (
    <motion.div
      initial={{ x: '100%' }}
      animate={{ x: 0 }}
      exit={{ x: '100%' }}
      transition={{ type: 'spring', damping: 25, stiffness: 200 }}
      className="fixed right-0 top-0 h-full w-96 bg-white shadow-2xl border-l border-gray-200 z-50 flex flex-col"
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-gradient-to-r from-blue-600 to-purple-600 text-white">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <h2 className="font-semibold">{t('chat.title')}</h2>
            <p className="text-xs text-white/80">
              {chatMode === 'serious' ? t('chat.seriousMode') : t('chat.jokingMode')}
            </p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          {/* Mode Toggle Buttons */}
          <div className="flex items-center bg-white/10 rounded-lg p-1">
            <button
              onClick={() => setChatMode('serious')}
              className={`p-1.5 rounded-md transition-all duration-200 ${
                chatMode === 'serious'
                  ? 'bg-white/20 text-white shadow-sm'
                  : 'text-white/70 hover:text-white hover:bg-white/10'
              }`}
              title="Serious Mode - Professional analysis"
            >
              <Briefcase className="w-4 h-4" />
            </button>
            <button
              onClick={() => setChatMode('joking')}
              className={`p-1.5 rounded-md transition-all duration-200 ${
                chatMode === 'joking'
                  ? 'bg-white/20 text-white shadow-sm'
                  : 'text-white/70 hover:text-white hover:bg-white/10'
              }`}
              title="Joking Mode - Creative and witty"
            >
              <Smile className="w-4 h-4" />
            </button>
          </div>
          <button
            onClick={onClose}
            className="p-1 hover:bg-white/20 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div className={`flex items-start space-x-2 max-w-[80%] ${message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                message.type === 'user' 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-purple-100 text-purple-600'
              }`}>
                {message.type === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
              </div>
              <div className={`rounded-lg p-3 ${
                message.type === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-900'
              }`}>
                {message.type === 'ai' ? 
                  processMessageContent(message.content, message.id) : 
                  <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                }
                
                {/* Data insights */}
                {message.data_insights && (
                  <div className="mt-3 p-3 bg-white/10 rounded-lg">
                    <p className="text-xs font-medium mb-2">{t('chat.dataInsights')}</p>
                    <div className="space-y-1">
                      {Object.entries(message.data_insights).map(([key, value]) => (
                        <div key={key} className="flex justify-between text-xs">
                          <span>{key}:</span>
                          <span className="font-mono">{String(value)}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Suggestions */}
                {message.suggestions && message.suggestions.length > 0 && (
                  <div className="mt-3">
                    <p className="text-xs font-medium mb-2">{t('chat.tryAsking')}</p>
                    <div className="space-y-1">
                      {message.suggestions.map((suggestion, index) => (
                        <button
                          key={index}
                          onClick={() => handleSuggestionClick(suggestion)}
                          className="block w-full text-left text-xs p-2 bg-white/10 hover:bg-white/20 rounded transition-colors"
                        >
                          {suggestion}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}

        {isTyping && (
          <div className="flex justify-start">
            <div className="flex items-start space-x-2">
              <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                <Bot className="w-4 h-4 text-purple-600" />
              </div>
              <div className="bg-gray-100 rounded-lg p-3">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
                </div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-gray-200">
        <div className="flex items-center space-x-2">
          <div className="flex-1 relative">
            <input
              ref={inputRef}
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={t('chat.placeholder')}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 pr-10"
              disabled={chatMutation.isPending}
            />
            <button
              onClick={toggleVoiceInput}
              className={`absolute right-2 top-1/2 transform -translate-y-1/2 p-1 rounded ${
                isListening 
                  ? 'text-red-600 bg-red-100' 
                  : 'text-gray-400 hover:text-gray-600'
              }`}
            >
              {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
            </button>
          </div>
          <button
            onClick={handleSendMessage}
            disabled={!inputValue.trim() || chatMutation.isPending}
            className="p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
        
        <div className="flex items-center justify-between mt-2 text-xs text-gray-500">
          <span>{t('chat.poweredBy')}</span>
          <div className="flex items-center">
            <div className="w-2 h-2 bg-green-500 rounded-full mr-1 animate-pulse"></div>
            {t('chat.online')}
          </div>
        </div>
      </div>
    </motion.div>
  )
}
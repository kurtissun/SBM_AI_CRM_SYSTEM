import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  ShoppingBag, TrendingUp, Package, BarChart3, Users, DollarSign,
  Calendar, Filter, Download, RefreshCw, Search, ChevronRight,
  AlertTriangle, CheckCircle, Clock, Star, Target, Zap, Brain,
  Lightbulb, Layers, Shuffle, ArrowUpDown, Settings, Eye
} from 'lucide-react'
import { useTranslation } from '@/contexts/TranslationContext'

export const RetailIntelligence: React.FC = () => {
  const { t } = useTranslation()
  const [selectedView, setSelectedView] = useState('overview')
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [timeRange, setTimeRange] = useState('30d')

  const views = [
    { id: 'overview', label: 'Intelligence Overview', icon: Brain },
    { id: 'demand', label: 'Demand Forecasting', icon: TrendingUp },
    { id: 'inventory', label: 'Inventory Analytics', icon: Package },
    { id: 'pricing', label: 'Price Optimization', icon: DollarSign },
    { id: 'products', label: 'Product Intelligence', icon: ShoppingBag }
  ]

  const categories = [
    { id: 'all', name: 'All Categories' },
    { id: 'fashion', name: 'Fashion & Apparel' },
    { id: 'electronics', name: 'Electronics' },
    { id: 'home', name: 'Home & Living' },
    { id: 'beauty', name: 'Beauty & Personal Care' },
    { id: 'sports', name: 'Sports & Outdoors' }
  ]

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{t('retail.title')}</h1>
          <p className="text-gray-600 mt-1">{t('retail.subtitle')}</p>
        </div>
        <div className="flex items-center space-x-3">
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {categories.map((category) => (
              <option key={category.id} value={category.id}>{category.name}</option>
            ))}
          </select>
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
            <option value="90d">Last 90 Days</option>
            <option value="1y">Last Year</option>
          </select>
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center">
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh AI
          </button>
          <button className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center">
            <Download className="w-4 h-4 mr-2" />
            Export Report
          </button>
        </div>
      </div>

      {/* AI Status */}
      <div className="bg-gradient-to-r from-blue-600 via-purple-600 to-teal-600 rounded-xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center">
              <Brain className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-lg font-semibold">Retail Intelligence Engine</h3>
              <p className="text-white/80">
                AI-powered analytics • 99.2% accuracy • Real-time insights
              </p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-2xl font-bold">₿1.8M</p>
            <p className="text-white/80 text-sm">Revenue Impact</p>
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Forecast Accuracy</p>
              <p className="text-3xl font-bold text-gray-900">94.7%</p>
              <p className="text-sm text-green-600">+2.1% vs last month</p>
            </div>
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <Target className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Inventory Turnover</p>
              <p className="text-3xl font-bold text-gray-900">8.2x</p>
              <p className="text-sm text-blue-600">+15% vs target</p>
            </div>
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <Shuffle className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Price Optimization</p>
              <p className="text-3xl font-bold text-gray-900">¥2.4M</p>
              <p className="text-sm text-purple-600">Revenue uplift</p>
            </div>
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
              <DollarSign className="w-6 h-6 text-purple-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Cross-sell Rate</p>
              <p className="text-3xl font-bold text-gray-900">28.6%</p>
              <p className="text-sm text-orange-600">+8.3% vs baseline</p>
            </div>
            <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
              <Zap className="w-6 h-6 text-orange-600" />
            </div>
          </div>
        </div>
      </div>

      {/* View Navigation */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-2">
        <nav className="flex space-x-1">
          {views.map((view) => (
            <button
              key={view.id}
              onClick={() => setSelectedView(view.id)}
              className={`flex items-center px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                selectedView === view.id
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
              }`}
            >
              <view.icon className="w-4 h-4 mr-2" />
              {view.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Dynamic Content */}
      {selectedView === 'overview' && <IntelligenceOverview />}
      {selectedView === 'demand' && <DemandForecasting />}
      {selectedView === 'inventory' && <InventoryAnalytics />}
      {selectedView === 'pricing' && <PriceOptimization />}
      {selectedView === 'products' && <ProductIntelligence />}
    </div>
  )
}

// Intelligence Overview Component
const IntelligenceOverview: React.FC = () => {
  const insights = [
    {
      type: 'opportunity',
      priority: 'high',
      title: 'High-demand products running low',
      description: 'iPhone 15 Pro Max stock will run out in 3 days at current sales velocity',
      impact: '¥890K potential lost revenue',
      action: 'Urgent restock needed'
    },
    {
      type: 'optimization',
      priority: 'medium', 
      title: 'Price optimization opportunity',
      description: 'Premium handbag category showing price elasticity for 8-12% increase',
      impact: '¥340K additional margin',
      action: 'Implement dynamic pricing'
    },
    {
      type: 'trend',
      priority: 'high',
      title: 'Seasonal demand shift detected',
      description: 'Winter clothing demand starting 2 weeks earlier than historical average',
      impact: '¥1.2M forecast adjustment',
      action: 'Accelerate winter inventory'
    },
    {
      type: 'performance',
      priority: 'low',
      title: 'Cross-sell performance improving',
      description: 'AI recommendation engine achieving 31% cross-sell rate this week',
      impact: '¥156K additional revenue',
      action: 'Monitor and maintain'
    }
  ]

  return (
    <div className="space-y-6">
      {/* AI Insights */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">AI-Generated Insights</h3>
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-500">Last updated: 5 minutes ago</span>
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          </div>
        </div>
        
        <div className="space-y-4">
          {insights.map((insight, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3">
                  <div className={`w-3 h-3 rounded-full mt-2 ${
                    insight.priority === 'high' ? 'bg-red-500' :
                    insight.priority === 'medium' ? 'bg-yellow-500' :
                    'bg-green-500'
                  }`}></div>
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <h4 className="font-semibold text-gray-900">{insight.title}</h4>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        insight.type === 'opportunity' ? 'bg-blue-100 text-blue-700' :
                        insight.type === 'optimization' ? 'bg-purple-100 text-purple-700' :
                        insight.type === 'trend' ? 'bg-orange-100 text-orange-700' :
                        'bg-green-100 text-green-700'
                      }`}>
                        {insight.type}
                      </span>
                    </div>
                    <p className="text-gray-700 mb-2">{insight.description}</p>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4 text-sm">
                        <span className="text-green-600 font-medium">{insight.impact}</span>
                        <span className="text-gray-500">•</span>
                        <span className="text-blue-600">{insight.action}</span>
                      </div>
                      <ChevronRight className="w-4 h-4 text-gray-400" />
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Performance Dashboard */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Category Performance</h3>
          <div className="space-y-4">
            {[
              { category: 'Electronics', revenue: 4200000, growth: '+18%', trend: 'up' },
              { category: 'Fashion', revenue: 3800000, growth: '+12%', trend: 'up' },
              { category: 'Home & Living', revenue: 2900000, growth: '+8%', trend: 'up' },
              { category: 'Beauty', revenue: 2100000, growth: '-3%', trend: 'down' },
              { category: 'Sports', revenue: 1600000, growth: '+24%', trend: 'up' }
            ].map((cat, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <h4 className="font-medium text-gray-900">{cat.category}</h4>
                  <p className="text-sm text-gray-600">¥{(cat.revenue/1000000).toFixed(1)}M revenue</p>
                </div>
                <div className="text-right">
                  <span className={`text-sm font-medium ${
                    cat.trend === 'up' ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {cat.growth}
                  </span>
                  <p className="text-xs text-gray-500">vs last month</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">AI Model Performance</h3>
          <div className="space-y-4">
            {[
              { model: 'Demand Forecasting', accuracy: 94.7, status: 'excellent' },
              { model: 'Price Optimization', accuracy: 89.2, status: 'good' },
              { model: 'Inventory Management', accuracy: 91.8, status: 'excellent' },
              { model: 'Customer Segmentation', accuracy: 87.4, status: 'good' },
              { model: 'Cross-sell Prediction', accuracy: 82.1, status: 'fair' }
            ].map((model, index) => (
              <div key={index} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
                <div>
                  <h4 className="font-medium text-gray-900">{model.model}</h4>
                  <p className="text-sm text-gray-600">{model.accuracy}% accuracy</p>
                </div>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                  model.status === 'excellent' ? 'bg-green-100 text-green-700' :
                  model.status === 'good' ? 'bg-blue-100 text-blue-700' :
                  'bg-yellow-100 text-yellow-700'
                }`}>
                  {model.status}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

// Demand Forecasting Component
const DemandForecasting: React.FC = () => {
  const forecasts = [
    {
      product: 'iPhone 15 Pro Max',
      category: 'Electronics',
      currentStock: 450,
      forecastDemand: 680,
      confidence: 96,
      daysUntilStockout: 3,
      recommendedAction: 'urgent_restock'
    },
    {
      product: 'Nike Air Jordan Retro',
      category: 'Sports',
      currentStock: 280,
      forecastDemand: 320,
      confidence: 89,
      daysUntilStockout: 12,
      recommendedAction: 'monitor'
    },
    {
      product: 'Dyson V15 Vacuum',
      category: 'Home',
      currentStock: 120,
      forecastDemand: 95,
      confidence: 82,
      daysUntilStockout: 45,
      recommendedAction: 'reduce_orders'
    }
  ]

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Demand Forecast Analysis</h3>
          <div className="flex items-center space-x-2">
            <select className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option>Next 7 Days</option>
              <option>Next 30 Days</option>
              <option>Next 90 Days</option>
            </select>
            <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
              Run Forecast
            </button>
          </div>
        </div>

        <div className="space-y-4">
          {forecasts.map((forecast, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="border border-gray-200 rounded-lg p-4"
            >
              <div className="flex items-center justify-between mb-3">
                <div>
                  <h4 className="font-semibold text-gray-900">{forecast.product}</h4>
                  <p className="text-sm text-gray-600">{forecast.category}</p>
                </div>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                  forecast.recommendedAction === 'urgent_restock' ? 'bg-red-100 text-red-700' :
                  forecast.recommendedAction === 'monitor' ? 'bg-yellow-100 text-yellow-700' :
                  'bg-blue-100 text-blue-700'
                }`}>
                  {forecast.recommendedAction.replace('_', ' ').toUpperCase()}
                </span>
              </div>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <p className="text-xs text-gray-600">Current Stock</p>
                  <p className="font-bold text-lg text-gray-900">{forecast.currentStock}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-600">Forecast Demand</p>
                  <p className="font-bold text-lg text-blue-600">{forecast.forecastDemand}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-600">Confidence</p>
                  <p className="font-bold text-lg text-green-600">{forecast.confidence}%</p>
                </div>
                <div>
                  <p className="text-xs text-gray-600">Days Until Stockout</p>
                  <p className={`font-bold text-lg ${
                    forecast.daysUntilStockout <= 7 ? 'text-red-600' :
                    forecast.daysUntilStockout <= 30 ? 'text-yellow-600' :
                    'text-green-600'
                  }`}>
                    {forecast.daysUntilStockout}
                  </p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Seasonal Trends */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Seasonal Demand Patterns</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            { season: 'Q1 2024', trend: 'Electronics surge', change: '+23%' },
            { season: 'Q2 2024', trend: 'Summer fashion peak', change: '+18%' },
            { season: 'Q3 2024', trend: 'Back-to-school items', change: '+31%' },
            { season: 'Q4 2024', trend: 'Holiday shopping', change: '+45%' }
          ].map((season, index) => (
            <div key={index} className="p-4 border border-gray-200 rounded-lg">
              <h4 className="font-medium text-gray-900 mb-2">{season.season}</h4>
              <p className="text-sm text-gray-600 mb-2">{season.trend}</p>
              <span className="text-sm font-medium text-green-600">{season.change}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

// Inventory Analytics Component  
const InventoryAnalytics: React.FC = () => (
  <div className="space-y-6">
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h4 className="font-semibold text-gray-900 mb-4">Inventory Health</h4>
        <div className="space-y-3">
          <div className="flex justify-between">
            <span className="text-gray-600">Optimal Stock</span>
            <span className="font-medium text-green-600">67%</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Overstock</span>
            <span className="font-medium text-orange-600">18%</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Understock</span>
            <span className="font-medium text-red-600">15%</span>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h4 className="font-semibold text-gray-900 mb-4">Turnover Rates</h4>
        <div className="space-y-3">
          <div className="flex justify-between">
            <span className="text-gray-600">Fast Movers</span>
            <span className="font-medium text-green-600">15.2x</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Medium Movers</span>
            <span className="font-medium text-blue-600">8.7x</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Slow Movers</span>
            <span className="font-medium text-red-600">2.1x</span>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h4 className="font-semibold text-gray-900 mb-4">Carrying Costs</h4>
        <div className="space-y-3">
          <div className="flex justify-between">
            <span className="text-gray-600">Storage</span>
            <span className="font-medium">¥2.8M</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Insurance</span>
            <span className="font-medium">¥850K</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Obsolescence</span>
            <span className="font-medium text-red-600">¥1.2M</span>
          </div>
        </div>
      </div>
    </div>
  </div>
)

// Price Optimization Component
const PriceOptimization: React.FC = () => (
  <div className="space-y-6">
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Dynamic Pricing Recommendations</h3>
      <div className="space-y-4">
        {[
          { product: 'Premium Handbag Collection', currentPrice: 2800, suggestedPrice: 3100, impact: '+¥340K', confidence: 89 },
          { product: 'Smart Watch Series', currentPrice: 1200, suggestedPrice: 1150, impact: '+¥180K', confidence: 82 },
          { product: 'Designer Shoes', currentPrice: 1500, suggestedPrice: 1650, impact: '+¥220K', confidence: 94 }
        ].map((item, index) => (
          <div key={index} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
            <div>
              <h4 className="font-medium text-gray-900">{item.product}</h4>
              <p className="text-sm text-gray-600">
                ¥{item.currentPrice} → ¥{item.suggestedPrice} ({item.confidence}% confidence)
              </p>
            </div>
            <div className="text-right">
              <p className="font-bold text-green-600">{item.impact}</p>
              <p className="text-xs text-gray-500">revenue impact</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  </div>
)

// Product Intelligence Component
const ProductIntelligence: React.FC = () => (
  <div className="space-y-6">
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Market Basket Analysis</h3>
      <div className="space-y-4">
        {[
          { combo: 'iPhone + AirPods + Case', frequency: '78%', lift: '2.3x', confidence: '89%' },
          { combo: 'Dress + Shoes + Handbag', frequency: '65%', lift: '1.8x', confidence: '76%' },
          { combo: 'Laptop + Mouse + Bag', frequency: '71%', lift: '2.1x', confidence: '82%' }
        ].map((combo, index) => (
          <div key={index} className="p-4 border border-gray-200 rounded-lg">
            <h4 className="font-medium text-gray-900 mb-2">{combo.combo}</h4>
            <div className="grid grid-cols-3 gap-4 text-sm">
              <div>
                <p className="text-gray-600">Frequency</p>
                <p className="font-medium">{combo.frequency}</p>
              </div>
              <div>
                <p className="text-gray-600">Lift</p>
                <p className="font-medium">{combo.lift}</p>
              </div>
              <div>
                <p className="text-gray-600">Confidence</p>
                <p className="font-medium">{combo.confidence}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  </div>
)
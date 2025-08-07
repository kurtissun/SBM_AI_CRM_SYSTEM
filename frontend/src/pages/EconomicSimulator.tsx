import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  TrendingUp, DollarSign, BarChart3, Calculator, Target, Zap,
  Calendar, Clock, Users, ShoppingBag, Globe, Settings,
  RefreshCw, Download, Play, Pause, RotateCcw, AlertTriangle,
  CheckCircle, ArrowUp, ArrowDown, Minus, Brain, LineChart,
  PieChart, Activity, Layers, Filter, Search, ChevronRight
} from 'lucide-react'
import { useTranslation } from '@/contexts/TranslationContext'

export const EconomicSimulator: React.FC = () => {
  const { t } = useTranslation()
  const [selectedView, setSelectedView] = useState('overview')
  const [simulationState, setSimulationState] = useState('running')
  const [timeHorizon, setTimeHorizon] = useState('1y')
  const [selectedScenario, setSelectedScenario] = useState('base')

  const views = [
    { id: 'overview', label: 'Simulation Overview', icon: BarChart3 },
    { id: 'scenarios', label: 'Scenario Planning', icon: Target },
    { id: 'forecasting', label: 'Revenue Forecasting', icon: TrendingUp },
    { id: 'market', label: 'Market Dynamics', icon: Globe },
    { id: 'sensitivity', label: 'Sensitivity Analysis', icon: Calculator }
  ]

  const scenarios = [
    { id: 'base', name: 'Base Case', probability: 60, growth: '+12%' },
    { id: 'optimistic', name: 'Bull Market', probability: 25, growth: '+28%' },
    { id: 'pessimistic', name: 'Bear Market', probability: 15, growth: '-8%' },
    { id: 'disruption', name: 'Market Disruption', probability: 10, growth: '-15%' }
  ]

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{t('economic.title')}</h1>
          <p className="text-gray-600 mt-1">{t('economic.subtitle')}</p>
        </div>
        <div className="flex items-center space-x-3">
          <select
            value={selectedScenario}
            onChange={(e) => setSelectedScenario(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {scenarios.map((scenario) => (
              <option key={scenario.id} value={scenario.id}>{scenario.name}</option>
            ))}
          </select>
          <select
            value={timeHorizon}
            onChange={(e) => setTimeHorizon(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="6m">6 Months</option>
            <option value="1y">1 Year</option>
            <option value="2y">2 Years</option>
            <option value="5y">5 Years</option>
          </select>
          <button 
            onClick={() => setSimulationState(simulationState === 'running' ? 'paused' : 'running')}
            className={`px-4 py-2 rounded-lg flex items-center text-white ${
              simulationState === 'running' ? 'bg-orange-600 hover:bg-orange-700' : 'bg-green-600 hover:bg-green-700'
            }`}
          >
            {simulationState === 'running' ? (
              <>
                <Pause className="w-4 h-4 mr-2" />
                Pause Sim
              </>
            ) : (
              <>
                <Play className="w-4 h-4 mr-2" />
                Run Sim
              </>
            )}
          </button>
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center">
            <RefreshCw className="w-4 h-4 mr-2" />
            Reset
          </button>
          <button className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center">
            <Download className="w-4 h-4 mr-2" />
            Export Results
          </button>
        </div>
      </div>

      {/* Simulation Status */}
      <div className="bg-gradient-to-r from-purple-600 via-blue-600 to-teal-600 rounded-xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center">
              <Brain className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-lg font-semibold">Economic Simulation Engine</h3>
              <p className="text-white/80">
                AI-powered forecasting • 10,000+ iterations • Real-time analysis
              </p>
            </div>
          </div>
          <div className="text-right">
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${
                simulationState === 'running' ? 'bg-green-400 animate-pulse' : 'bg-orange-400'
              }`}></div>
              <span className="text-lg font-semibold">
                {simulationState === 'running' ? 'RUNNING' : 'PAUSED'}
              </span>
            </div>
            <p className="text-white/80 text-sm">Simulation Status</p>
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Revenue Forecast</p>
              <p className="text-3xl font-bold text-gray-900">¥24.8M</p>
              <p className="text-sm text-green-600">+15.3% projected</p>
            </div>
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <TrendingUp className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Market Share</p>
              <p className="text-3xl font-bold text-gray-900">18.2%</p>
              <p className="text-sm text-blue-600">+2.1% gain expected</p>
            </div>
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <Target className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Customer Growth</p>
              <p className="text-3xl font-bold text-gray-900">156K</p>
              <p className="text-sm text-purple-600">+23% new customers</p>
            </div>
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
              <Users className="w-6 h-6 text-purple-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">ROI Projection</p>
              <p className="text-3xl font-bold text-gray-900">284%</p>
              <p className="text-sm text-orange-600">Above industry avg</p>
            </div>
            <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
              <DollarSign className="w-6 h-6 text-orange-600" />
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
                  ? 'bg-purple-600 text-white'
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
      {selectedView === 'overview' && <SimulationOverview />}
      {selectedView === 'scenarios' && <ScenarioPlanning />}
      {selectedView === 'forecasting' && <RevenueForecasting />}
      {selectedView === 'market' && <MarketDynamics />}
      {selectedView === 'sensitivity' && <SensitivityAnalysis />}
    </div>
  )
}

// Simulation Overview Component
const SimulationOverview: React.FC = () => {
  const keyInsights = [
    {
      type: 'growth',
      priority: 'high',
      title: 'Strong revenue growth trajectory',
      description: '15.3% YoY growth projected based on current market trends and customer acquisition rates',
      confidence: 87,
      impact: '¥3.2M additional revenue'
    },
    {
      type: 'market',
      priority: 'medium',
      title: 'Market expansion opportunity',
      description: 'Tier 2 cities showing 28% higher demand than model predictions',
      confidence: 73,
      impact: '¥1.8M potential upside'
    },
    {
      type: 'risk',
      priority: 'high',
      title: 'Economic headwinds detected',
      description: 'GDP slowdown may impact luxury goods segment by 12-15%',
      confidence: 82,
      impact: '¥2.1M potential downside'
    },
    {
      type: 'innovation',
      priority: 'medium',
      title: 'AI implementation benefits',
      description: 'Personalization engine driving 18% higher conversion rates',
      confidence: 91,
      impact: '¥890K efficiency gains'
    }
  ]

  return (
    <div className="space-y-6">
      {/* AI Insights */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Economic Simulation Results</h3>
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-500">Last updated: 2 minutes ago</span>
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          </div>
        </div>
        
        <div className="space-y-4">
          {keyInsights.map((insight, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3">
                  <div className={`w-3 h-3 rounded-full mt-2 ${
                    insight.priority === 'high' ? 'bg-red-500' : 'bg-yellow-500'
                  }`}></div>
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <h4 className="font-semibold text-gray-900">{insight.title}</h4>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        insight.type === 'growth' ? 'bg-green-100 text-green-700' :
                        insight.type === 'market' ? 'bg-blue-100 text-blue-700' :
                        insight.type === 'risk' ? 'bg-red-100 text-red-700' :
                        'bg-purple-100 text-purple-700'
                      }`}>
                        {insight.type}
                      </span>
                    </div>
                    <p className="text-gray-700 mb-2">{insight.description}</p>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4 text-sm">
                        <span className="text-blue-600 font-medium">
                          {insight.confidence}% confidence
                        </span>
                        <span className="text-gray-500">•</span>
                        <span className={`font-medium ${
                          insight.impact.includes('downside') ? 'text-red-600' : 'text-green-600'
                        }`}>
                          {insight.impact}
                        </span>
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

      {/* Performance Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Model Performance</h3>
          <div className="space-y-4">
            {[
              { metric: 'Revenue Prediction Accuracy', value: 94.2, trend: '+2.1%' },
              { metric: 'Customer Behavior Modeling', value: 89.7, trend: '+1.8%' },
              { metric: 'Market Trend Analysis', value: 91.5, trend: '+3.2%' },
              { metric: 'Economic Indicator Tracking', value: 87.3, trend: '+0.9%' }
            ].map((item, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <h4 className="font-medium text-gray-900">{item.metric}</h4>
                  <p className="text-sm text-gray-600">{item.value}% accuracy</p>
                </div>
                <div className="text-right">
                  <span className="text-sm font-medium text-green-600">{item.trend}</span>
                  <p className="text-xs text-gray-500">vs last month</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Simulation Parameters</h3>
          <div className="space-y-4">
            {[
              { parameter: 'Monte Carlo Iterations', value: '10,000', status: 'optimal' },
              { parameter: 'Historical Data Range', value: '5 years', status: 'sufficient' },
              { parameter: 'Market Variables', value: '47 factors', status: 'comprehensive' },
              { parameter: 'Update Frequency', value: 'Real-time', status: 'active' }
            ].map((param, index) => (
              <div key={index} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
                <div>
                  <h4 className="font-medium text-gray-900">{param.parameter}</h4>
                  <p className="text-sm text-gray-600">{param.value}</p>
                </div>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                  param.status === 'optimal' ? 'bg-green-100 text-green-700' :
                  param.status === 'sufficient' ? 'bg-blue-100 text-blue-700' :
                  param.status === 'comprehensive' ? 'bg-purple-100 text-purple-700' :
                  'bg-orange-100 text-orange-700'
                }`}>
                  {param.status}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

// Scenario Planning Component
const ScenarioPlanning: React.FC = () => {
  const scenarioDetails = [
    {
      name: 'Base Case Scenario',
      probability: 60,
      revenue: 24800000,
      growth: 15.3,
      risks: ['Competition', 'Supply Chain'],
      opportunities: ['Market Expansion', 'Digital Transformation'],
      keyDrivers: ['Consumer Spending', 'GDP Growth', 'Market Share']
    },
    {
      name: 'Bull Market Scenario', 
      probability: 25,
      revenue: 31200000,
      growth: 28.7,
      risks: ['Overheating', 'Resource Constraints'],
      opportunities: ['Premium Expansion', 'New Markets'],
      keyDrivers: ['Economic Boom', 'Consumer Confidence', 'Innovation']
    },
    {
      name: 'Bear Market Scenario',
      probability: 15,
      revenue: 22100000,
      growth: -8.2,
      risks: ['Recession', 'Demand Drop'],
      opportunities: ['Cost Optimization', 'Market Consolidation'],
      keyDrivers: ['Economic Downturn', 'Consumer Caution', 'Price Sensitivity']
    }
  ]

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Scenario Analysis</h3>
          <button className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700">
            Run All Scenarios
          </button>
        </div>

        <div className="space-y-6">
          {scenarioDetails.map((scenario, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="border border-gray-200 rounded-lg p-6"
            >
              <div className="flex items-center justify-between mb-4">
                <h4 className="text-lg font-semibold text-gray-900">{scenario.name}</h4>
                <div className="flex items-center space-x-3">
                  <span className="text-sm text-gray-600">{scenario.probability}% probability</span>
                  <div className="w-16 bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-purple-600 h-2 rounded-full" 
                      style={{ width: `${scenario.probability}%` }}
                    ></div>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
                <div className="text-center p-3 bg-green-50 rounded-lg">
                  <p className="text-2xl font-bold text-green-600">¥{(scenario.revenue/1000000).toFixed(1)}M</p>
                  <p className="text-sm text-gray-600">Projected Revenue</p>
                </div>
                <div className="text-center p-3 bg-blue-50 rounded-lg">
                  <p className={`text-2xl font-bold ${scenario.growth > 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {scenario.growth > 0 ? '+' : ''}{scenario.growth}%
                  </p>
                  <p className="text-sm text-gray-600">Growth Rate</p>
                </div>
                <div className="text-center p-3 bg-orange-50 rounded-lg">
                  <p className="text-2xl font-bold text-orange-600">{scenario.risks.length}</p>
                  <p className="text-sm text-gray-600">Key Risks</p>
                </div>
                <div className="text-center p-3 bg-purple-50 rounded-lg">
                  <p className="text-2xl font-bold text-purple-600">{scenario.opportunities.length}</p>
                  <p className="text-sm text-gray-600">Opportunities</p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <h5 className="font-medium text-gray-900 mb-2">Key Drivers</h5>
                  <div className="space-y-1">
                    {scenario.keyDrivers.map((driver, idx) => (
                      <span key={idx} className="inline-block px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full mr-1 mb-1">
                        {driver}
                      </span>
                    ))}
                  </div>
                </div>
                <div>
                  <h5 className="font-medium text-gray-900 mb-2">Risks</h5>
                  <div className="space-y-1">
                    {scenario.risks.map((risk, idx) => (
                      <span key={idx} className="inline-block px-2 py-1 bg-red-100 text-red-700 text-xs rounded-full mr-1 mb-1">
                        {risk}
                      </span>
                    ))}
                  </div>
                </div>
                <div>
                  <h5 className="font-medium text-gray-900 mb-2">Opportunities</h5>
                  <div className="space-y-1">
                    {scenario.opportunities.map((opp, idx) => (
                      <span key={idx} className="inline-block px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full mr-1 mb-1">
                        {opp}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  )
}

// Revenue Forecasting Component
const RevenueForecasting: React.FC = () => (
  <div className="space-y-6">
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Monthly Revenue Projection</h3>
        <div className="space-y-4">
          {[
            { month: 'Jan 2024', forecast: 2100000, actual: 2050000, variance: 2.4 },
            { month: 'Feb 2024', forecast: 2200000, actual: 2180000, variance: 0.9 },
            { month: 'Mar 2024', forecast: 2400000, actual: 2380000, variance: 0.8 },
            { month: 'Apr 2024', forecast: 2350000, actual: null, variance: null },
            { month: 'May 2024', forecast: 2500000, actual: null, variance: null },
            { month: 'Jun 2024', forecast: 2650000, actual: null, variance: null }
          ].map((data, index) => (
            <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div>
                <h4 className="font-medium text-gray-900">{data.month}</h4>
                <p className="text-sm text-gray-600">Forecast: ¥{(data.forecast/1000000).toFixed(1)}M</p>
              </div>
              <div className="text-right">
                {data.actual ? (
                  <>
                    <p className="font-medium text-gray-900">¥{(data.actual/1000000).toFixed(1)}M</p>
                    <p className={`text-xs ${data.variance! < 5 ? 'text-green-600' : 'text-orange-600'}`}>
                      {data.variance}% variance
                    </p>
                  </>
                ) : (
                  <p className="text-sm text-blue-600 font-medium">Projected</p>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Revenue Breakdown</h3>
        <div className="space-y-4">
          {[
            { category: 'Product Sales', amount: 18600000, growth: 12.3, share: 75 },
            { category: 'Service Revenue', amount: 3720000, growth: 8.7, share: 15 },
            { category: 'Digital Products', amount: 1860000, growth: 24.1, share: 7.5 },
            { category: 'Partnerships', amount: 620000, growth: 15.9, share: 2.5 }
          ].map((cat, index) => (
            <div key={index} className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-medium text-gray-900">{cat.category}</span>
                <div className="flex items-center space-x-2">
                  <span className="text-sm font-medium">¥{(cat.amount/1000000).toFixed(1)}M</span>
                  <span className="text-xs text-green-600">+{cat.growth}%</span>
                </div>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-purple-600 h-2 rounded-full" 
                  style={{ width: `${cat.share}%` }}
                ></div>
              </div>
              <p className="text-xs text-gray-500">{cat.share}% of total revenue</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  </div>
)

// Market Dynamics Component
const MarketDynamics: React.FC = () => (
  <div className="space-y-6">
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Market Forces Analysis</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h4 className="font-medium text-gray-900 mb-3">Economic Indicators</h4>
          <div className="space-y-3">
            {[
              { indicator: 'GDP Growth', value: '6.2%', impact: 'positive', strength: 'high' },
              { indicator: 'Consumer Confidence', value: '84.2', impact: 'positive', strength: 'medium' },
              { indicator: 'Inflation Rate', value: '2.8%', impact: 'negative', strength: 'low' },
              { indicator: 'Unemployment', value: '5.1%', impact: 'negative', strength: 'medium' }
            ].map((econ, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <h5 className="font-medium text-gray-900">{econ.indicator}</h5>
                  <p className="text-lg font-bold text-blue-600">{econ.value}</p>
                </div>
                <div className="text-right">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    econ.impact === 'positive' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                  }`}>
                    {econ.impact}
                  </span>
                  <p className="text-xs text-gray-500 mt-1">{econ.strength} impact</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div>
          <h4 className="font-medium text-gray-900 mb-3">Market Trends</h4>
          <div className="space-y-3">
            {[
              { trend: 'Digital Adoption', momentum: 'accelerating', score: 92 },
              { trend: 'Sustainability Focus', momentum: 'growing', score: 78 },
              { trend: 'Premium Products', momentum: 'stable', score: 65 },
              { trend: 'Price Sensitivity', momentum: 'declining', score: 43 }
            ].map((trend, index) => (
              <div key={index} className="p-3 border border-gray-200 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <h5 className="font-medium text-gray-900">{trend.trend}</h5>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    trend.momentum === 'accelerating' ? 'bg-green-100 text-green-700' :
                    trend.momentum === 'growing' ? 'bg-blue-100 text-blue-700' :
                    trend.momentum === 'stable' ? 'bg-yellow-100 text-yellow-700' :
                    'bg-red-100 text-red-700'
                  }`}>
                    {trend.momentum}
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-blue-600 h-2 rounded-full" 
                      style={{ width: `${trend.score}%` }}
                    ></div>
                  </div>
                  <span className="text-sm font-medium">{trend.score}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  </div>
)

// Sensitivity Analysis Component
const SensitivityAnalysis: React.FC = () => (
  <div className="space-y-6">
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Variable Impact Analysis</h3>
      <div className="space-y-4">
        {[
          { variable: 'Customer Acquisition Cost', sensitivity: 'high', impact: '-12.3%', change: '+10%' },
          { variable: 'Market Share Growth', sensitivity: 'high', impact: '+18.7%', change: '+5%' },
          { variable: 'Economic Growth Rate', sensitivity: 'medium', impact: '+8.4%', change: '+1%' },
          { variable: 'Competition Intensity', sensitivity: 'medium', impact: '-6.2%', change: '+15%' },
          { variable: 'Supply Chain Costs', sensitivity: 'low', impact: '-3.1%', change: '+8%' },
          { variable: 'Digital Adoption Rate', sensitivity: 'high', impact: '+14.9%', change: '+20%' }
        ].map((variable, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            className="flex items-center justify-between p-4 border border-gray-200 rounded-lg"
          >
            <div className="flex-1">
              <h4 className="font-medium text-gray-900">{variable.variable}</h4>
              <p className="text-sm text-gray-600">If variable changes by {variable.change}</p>
            </div>
            <div className="flex items-center space-x-4">
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                variable.sensitivity === 'high' ? 'bg-red-100 text-red-700' :
                variable.sensitivity === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                'bg-green-100 text-green-700'
              }`}>
                {variable.sensitivity} sensitivity
              </span>
              <div className="text-right">
                <p className={`font-bold ${
                  variable.impact.startsWith('+') ? 'text-green-600' : 'text-red-600'
                }`}>
                  {variable.impact}
                </p>
                <p className="text-xs text-gray-500">revenue impact</p>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>

    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Risk Factors</h3>
        <div className="space-y-3">
          {[
            { risk: 'Economic Recession', probability: 15, impact: 'high' },
            { risk: 'Supply Chain Disruption', probability: 25, impact: 'medium' },
            { risk: 'New Competitor Entry', probability: 35, impact: 'medium' },
            { risk: 'Regulatory Changes', probability: 20, impact: 'low' }
          ].map((risk, index) => (
            <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div>
                <h4 className="font-medium text-gray-900">{risk.risk}</h4>
                <p className="text-sm text-gray-600">{risk.probability}% probability</p>
              </div>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                risk.impact === 'high' ? 'bg-red-100 text-red-700' :
                risk.impact === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                'bg-green-100 text-green-700'
              }`}>
                {risk.impact} impact
              </span>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Monte Carlo Results</h3>
        <div className="space-y-4">
          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <p className="text-3xl font-bold text-blue-600">¥24.8M</p>
            <p className="text-sm text-gray-600">Expected Value (Mean)</p>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center p-3 bg-green-50 rounded-lg">
              <p className="text-xl font-bold text-green-600">¥29.2M</p>
              <p className="text-xs text-gray-600">90th Percentile</p>
            </div>
            <div className="text-center p-3 bg-red-50 rounded-lg">
              <p className="text-xl font-bold text-red-600">¥20.1M</p>
              <p className="text-xs text-gray-600">10th Percentile</p>
            </div>
          </div>
          <div className="pt-3 border-t border-gray-200">
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Confidence Interval</span>
              <span className="font-medium">95%</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Standard Deviation</span>
              <span className="font-medium">¥2.8M</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
)
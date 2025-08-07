import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  Building2, Users, TrendingUp, MapPin, Clock, Activity, Eye,
  ShoppingBag, Car, Wifi, Thermometer, DollarSign, BarChart3,
  Camera, AlertTriangle, Settings, RefreshCw, Download, Filter,
  Store, CreditCard, Phone, Star, Target, Zap, Calendar, Bell
} from 'lucide-react'
import { useTranslation } from '@/contexts/TranslationContext'
import { toast } from 'react-hot-toast'

export const MallOperations: React.FC = () => {
  const { t } = useTranslation()
  const [selectedView, setSelectedView] = useState('overview')
  const [selectedTimeRange, setSelectedTimeRange] = useState('today')
  const [selectedFloor, setSelectedFloor] = useState('all')

  const views = [
    { id: 'overview', label: 'Operations Overview', icon: Building2 },
    { id: 'foottraffic', label: 'Foot Traffic', icon: Users },
    { id: 'stores', label: 'Store Analytics', icon: Store },
    { id: 'facilities', label: 'Facilities', icon: Settings },
    { id: 'security', label: 'Security', icon: Eye }
  ]

  const timeRanges = [
    { value: 'today', label: 'Today' },
    { value: 'week', label: 'This Week' },
    { value: 'month', label: 'This Month' },
    { value: 'quarter', label: 'This Quarter' }
  ]

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{t('mall.title')}</h1>
          <p className="text-gray-600 mt-1">{t('mall.subtitle')}</p>
        </div>
        <div className="flex items-center space-x-3">
          <select
            value={selectedTimeRange}
            onChange={(e) => setSelectedTimeRange(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {timeRanges.map(range => (
              <option key={range.value} value={range.value}>{range.label}</option>
            ))}
          </select>
          <button 
            onClick={() => {
              toast.success('Refreshing mall operations data...')
              setTimeout(() => {
                window.location.reload()
              }, 1000)
            }}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Live Update
          </button>
          <button 
            onClick={() => {
              toast.success('Exporting mall operations data...')
              setTimeout(() => {
                const blob = new Blob(['Mall Operations Report - ' + new Date().toLocaleDateString()], { type: 'text/plain' })
                const url = window.URL.createObjectURL(blob)
                const a = document.createElement('a')
                a.href = url
                a.download = `mall-operations-${new Date().toISOString().split('T')[0]}.xlsx`
                a.click()
                window.URL.revokeObjectURL(url)
                toast.success('Mall operations data exported successfully!')
              }, 2000)
            }}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center"
          >
            <Download className="w-4 h-4 mr-2" />
            Export Data
          </button>
        </div>
      </div>

      {/* Real-time Status Banner */}
      <div className="bg-gradient-to-r from-green-600 via-blue-600 to-purple-600 rounded-xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center">
              <Building2 className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-lg font-semibold">Mall Operations Live</h3>
              <p className="text-white/80">
                Real-time monitoring • 94 stores active • Peak traffic zone: Level 2
              </p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-2xl font-bold">8,456</p>
            <p className="text-white/80 text-sm">{t('mall.currentVisitors')}</p>
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">{t('mall.currentVisitors')}</p>
              <p className="text-3xl font-bold text-gray-900">8,456</p>
              <p className="text-sm text-green-600">+15% vs yesterday</p>
            </div>
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <Users className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">{t('mall.occupancyRate')}</p>
              <p className="text-3xl font-bold text-gray-900">67%</p>
              <p className="text-sm text-orange-600">Peak: 89% at 2 PM</p>
            </div>
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <TrendingUp className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">{t('mall.avgDwellTime')}</p>
              <p className="text-3xl font-bold text-gray-900">2.4h</p>
              <p className="text-sm text-purple-600">+12 min vs avg</p>
            </div>
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
              <Clock className="w-6 h-6 text-purple-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Revenue Today</p>
              <p className="text-3xl font-bold text-gray-900">¥2.8M</p>
              <p className="text-sm text-green-600">+8.3% vs target</p>
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
      {selectedView === 'overview' && <OperationsOverview />}
      {selectedView === 'foottraffic' && <FootTrafficAnalytics />}
      {selectedView === 'stores' && <StoreAnalytics />}
      {selectedView === 'facilities' && <FacilitiesManagement />}
      {selectedView === 'security' && <SecurityMonitoring />}
    </div>
  )
}

// Operations Overview Component
const OperationsOverview: React.FC = () => {
  const heatmapData = [
    { zone: 'Main Entrance', traffic: 95, revenue: 280000, conversion: 23.4 },
    { zone: 'Food Court L2', traffic: 87, revenue: 456000, conversion: 31.2 },
    { zone: 'Fashion District L1', traffic: 78, revenue: 890000, conversion: 19.8 },
    { zone: 'Electronics L3', traffic: 65, revenue: 670000, conversion: 15.6 },
    { zone: 'Kids Zone L2', traffic: 82, revenue: 320000, conversion: 28.9 },
    { zone: 'Luxury Wing L1', traffic: 45, revenue: 1200000, conversion: 8.7 }
  ]

  return (
    <div className="space-y-6">
      {/* Mall Layout Heatmap */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Live Traffic Heatmap</h3>
        <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
          {heatmapData.map((zone, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.1 }}
              className={`p-4 rounded-lg border-2 ${
                zone.traffic > 80 ? 'border-red-300 bg-red-50' :
                zone.traffic > 60 ? 'border-orange-300 bg-orange-50' :
                'border-green-300 bg-green-50'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium text-gray-900">{zone.zone}</h4>
                <div className={`w-3 h-3 rounded-full ${
                  zone.traffic > 80 ? 'bg-red-500' :
                  zone.traffic > 60 ? 'bg-orange-500' :
                  'bg-green-500'
                }`}></div>
              </div>
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Traffic</span>
                  <span className="font-medium">{zone.traffic}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Revenue</span>
                  <span className="font-medium">¥{(zone.revenue/1000).toFixed(0)}K</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Conversion</span>
                  <span className="font-medium">{zone.conversion}%</span>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Real-time Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Operational Status</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <Store className="w-5 h-5 text-blue-600" />
                <span className="text-gray-700">Active Stores</span>
              </div>
              <span className="font-bold text-blue-600">94/98</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <Car className="w-5 h-5 text-green-600" />
                <span className="text-gray-700">Parking Availability</span>
              </div>
              <span className="font-bold text-green-600">1,247 spaces</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <Wifi className="w-5 h-5 text-purple-600" />
                <span className="text-gray-700">WiFi Connected Devices</span>
              </div>
              <span className="font-bold text-purple-600">3,456</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <Thermometer className="w-5 h-5 text-orange-600" />
                <span className="text-gray-700">Average Temperature</span>
              </div>
              <span className="font-bold text-orange-600">22.5°C</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Peak Hours Analysis</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Morning Peak (10-12 PM)</span>
              <div className="flex items-center space-x-2">
                <div className="w-20 bg-gray-200 rounded-full h-2">
                  <div className="bg-blue-600 h-2 rounded-full" style={{ width: '65%' }}></div>
                </div>
                <span className="text-sm font-medium">65%</span>
              </div>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Lunch Rush (12-2 PM)</span>
              <div className="flex items-center space-x-2">
                <div className="w-20 bg-gray-200 rounded-full h-2">
                  <div className="bg-orange-600 h-2 rounded-full" style={{ width: '89%' }}></div>
                </div>
                <span className="text-sm font-medium">89%</span>
              </div>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Evening Shopping (6-8 PM)</span>
              <div className="flex items-center space-x-2">
                <div className="w-20 bg-gray-200 rounded-full h-2">
                  <div className="bg-red-600 h-2 rounded-full" style={{ width: '95%' }}></div>
                </div>
                <span className="text-sm font-medium">95%</span>
              </div>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Late Night (8-10 PM)</span>
              <div className="flex items-center space-x-2">
                <div className="w-20 bg-gray-200 rounded-full h-2">
                  <div className="bg-green-600 h-2 rounded-full" style={{ width: '45%' }}></div>
                </div>
                <span className="text-sm font-medium">45%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

// Foot Traffic Analytics Component
const FootTrafficAnalytics: React.FC = () => {
  const trafficData = [
    { hour: '9 AM', visitors: 1200, entries: 450, exits: 120 },
    { hour: '10 AM', visitors: 2800, entries: 890, exits: 340 },
    { hour: '11 AM', visitors: 4200, entries: 1200, exits: 580 },
    { hour: '12 PM', visitors: 6800, entries: 1800, exits: 920 },
    { hour: '1 PM', visitors: 8100, entries: 1600, exits: 1100 },
    { hour: '2 PM', visitors: 8456, entries: 980, exits: 1200 },
    { hour: '3 PM', visitors: 7200, entries: 780, exits: 1400 }
  ]

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Hourly Traffic Flow</h3>
        <div className="space-y-4">
          {trafficData.map((data, index) => (
            <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center space-x-4">
                <span className="font-medium text-gray-900 w-16">{data.hour}</span>
                <div className="flex items-center space-x-6">
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                    <span className="text-sm text-gray-600">Entries: {data.entries}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                    <span className="text-sm text-gray-600">Exits: {data.exits}</span>
                  </div>
                </div>
              </div>
              <div className="text-right">
                <span className="font-bold text-lg text-gray-900">{data.visitors.toLocaleString()}</span>
                <p className="text-xs text-gray-500">Current Visitors</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Traffic Patterns */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h4 className="font-semibold text-gray-900 mb-4">Entry Points</h4>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">Main Entrance</span>
              <span className="font-medium">45%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">East Wing</span>
              <span className="font-medium">28%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Parking Level</span>
              <span className="font-medium">27%</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h4 className="font-semibold text-gray-900 mb-4">Age Demographics</h4>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">18-25</span>
              <span className="font-medium">32%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">26-35</span>
              <span className="font-medium">28%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">36-50</span>
              <span className="font-medium">25%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">50+</span>
              <span className="font-medium">15%</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h4 className="font-semibold text-gray-900 mb-4">Visit Duration</h4>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">&lt; 1 hour</span>
              <span className="font-medium">18%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">1-2 hours</span>
              <span className="font-medium">35%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">2-4 hours</span>
              <span className="font-medium">32%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">4+ hours</span>
              <span className="font-medium">15%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

// Store Analytics Component
const StoreAnalytics: React.FC = () => {
  const storeData = [
    { name: 'Fashion Central', category: 'Fashion', revenue: 89000, footfall: 1200, conversion: 15.2, rating: 4.8 },
    { name: 'Tech Hub', category: 'Electronics', revenue: 156000, footfall: 890, conversion: 22.1, rating: 4.6 },
    { name: 'Gourmet Corner', category: 'Food', revenue: 67000, footfall: 2100, conversion: 28.9, rating: 4.9 },
    { name: 'Sports Zone', category: 'Sports', revenue: 78000, footfall: 650, conversion: 18.5, rating: 4.5 },
    { name: 'Beauty Lounge', category: 'Beauty', revenue: 45000, footfall: 780, conversion: 12.3, rating: 4.7 }
  ]

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Top Performing Stores</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-4 font-medium text-gray-900">Store</th>
                <th className="text-left py-3 px-4 font-medium text-gray-900">Category</th>
                <th className="text-left py-3 px-4 font-medium text-gray-900">Revenue</th>
                <th className="text-left py-3 px-4 font-medium text-gray-900">Footfall</th>
                <th className="text-left py-3 px-4 font-medium text-gray-900">Conversion</th>
                <th className="text-left py-3 px-4 font-medium text-gray-900">Rating</th>
              </tr>
            </thead>
            <tbody>
              {storeData.map((store, index) => (
                <tr key={index} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="py-4 px-4 font-medium text-gray-900">{store.name}</td>
                  <td className="py-4 px-4 text-gray-700">{store.category}</td>
                  <td className="py-4 px-4 font-medium text-green-600">¥{store.revenue.toLocaleString()}</td>
                  <td className="py-4 px-4 text-gray-700">{store.footfall.toLocaleString()}</td>
                  <td className="py-4 px-4 font-medium text-blue-600">{store.conversion}%</td>
                  <td className="py-4 px-4">
                    <div className="flex items-center space-x-1">
                      <Star className="w-4 h-4 text-yellow-500 fill-current" />
                      <span className="font-medium">{store.rating}</span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

// Facilities Management Component
const FacilitiesManagement: React.FC = () => (
  <div className="space-y-6">
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h4 className="font-semibold text-gray-900 mb-4">HVAC Systems</h4>
        <div className="space-y-3">
          <div className="flex justify-between">
            <span className="text-gray-600">Temperature</span>
            <span className="font-medium">22.5°C</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Humidity</span>
            <span className="font-medium">45%</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Air Quality</span>
            <span className="font-medium text-green-600">Excellent</span>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h4 className="font-semibold text-gray-900 mb-4">Energy Usage</h4>
        <div className="space-y-3">
          <div className="flex justify-between">
            <span className="text-gray-600">Current Load</span>
            <span className="font-medium">847 kW</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Daily Consumption</span>
            <span className="font-medium">18.4 MWh</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Efficiency</span>
            <span className="font-medium text-green-600">94.2%</span>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h4 className="font-semibold text-gray-900 mb-4">Maintenance</h4>
        <div className="space-y-3">
          <div className="flex justify-between">
            <span className="text-gray-600">Scheduled Tasks</span>
            <span className="font-medium">12</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Pending Issues</span>
            <span className="font-medium text-orange-600">3</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">System Health</span>
            <span className="font-medium text-green-600">98.5%</span>
          </div>
        </div>
      </div>
    </div>
  </div>
)

// Security Monitoring Component
const SecurityMonitoring: React.FC = () => (
  <div className="space-y-6">
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 text-center">
        <Camera className="w-8 h-8 text-blue-600 mx-auto mb-2" />
        <p className="text-2xl font-bold text-gray-900">156</p>
        <p className="text-sm text-gray-600">Active Cameras</p>
      </div>
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 text-center">
        <Eye className="w-8 h-8 text-green-600 mx-auto mb-2" />
        <p className="text-2xl font-bold text-gray-900">24/7</p>
        <p className="text-sm text-gray-600">Monitoring</p>
      </div>
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 text-center">
        <AlertTriangle className="w-8 h-8 text-orange-600 mx-auto mb-2" />
        <p className="text-2xl font-bold text-gray-900">2</p>
        <p className="text-sm text-gray-600">Active Alerts</p>
      </div>
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 text-center">
        <Bell className="w-8 h-8 text-purple-600 mx-auto mb-2" />
        <p className="text-2xl font-bold text-gray-900">0</p>
        <p className="text-sm text-gray-600">Emergency Incidents</p>
      </div>
    </div>

    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Security Events</h3>
      <div className="space-y-3">
        {[
          { time: '14:23', event: 'Suspicious activity detected - Food Court Level 2', severity: 'medium' },
          { time: '12:45', event: 'Emergency exit alarm - False alarm resolved', severity: 'low' },
          { time: '10:30', event: 'Lost child report - Resolved successfully', severity: 'high' },
          { time: '09:15', event: 'Unattended bag - Parking Level B1 - Resolved', severity: 'medium' }
        ].map((event, index) => (
          <div key={index} className="flex items-center p-3 bg-gray-50 rounded-lg">
            <div className={`w-3 h-3 rounded-full mr-3 ${
              event.severity === 'high' ? 'bg-red-500' :
              event.severity === 'medium' ? 'bg-orange-500' :
              'bg-green-500'
            }`}></div>
            <div className="flex-1">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-900">{event.event}</span>
                <span className="text-xs text-gray-500">{event.time}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  </div>
)

export default MallOperations
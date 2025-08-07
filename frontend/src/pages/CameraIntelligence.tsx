import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  Camera, Eye, AlertTriangle, Users, Clock, Activity, MapPin,
  Play, Pause, RotateCcw, ZoomIn, ZoomOut, Settings, Download,
  Bell, Monitor, Cpu, HardDrive, Wifi, Signal, Shield,
  Target, TrendingUp, BarChart3, RefreshCw, Grid3X3, Maximize
} from 'lucide-react'
import { useTranslation } from '@/contexts/TranslationContext'
import { toast } from 'react-hot-toast'
import { showAlert } from '@/lib/alertService'

export const CameraIntelligence: React.FC = () => {
  const { t } = useTranslation()
  const [selectedView, setSelectedView] = useState('live')
  const [selectedCamera, setSelectedCamera] = useState('all')
  const [alertLevel, setAlertLevel] = useState('all')

  const views = [
    { id: 'live', label: 'Live Feeds', icon: Camera },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
    { id: 'alerts', label: 'Alert Center', icon: AlertTriangle },
    { id: 'system', label: 'System Health', icon: Monitor }
  ]

  const cameras = [
    { id: 'cam_001', name: 'Main Entrance', location: 'Ground Floor', status: 'active', alerts: 0 },
    { id: 'cam_002', name: 'Food Court', location: 'Level 2', status: 'active', alerts: 2 },
    { id: 'cam_003', name: 'Parking Level B1', location: 'Basement', status: 'maintenance', alerts: 0 },
    { id: 'cam_004', name: 'Fashion District', location: 'Level 1', status: 'active', alerts: 1 },
    { id: 'cam_005', name: 'Emergency Exit', location: 'All Levels', status: 'active', alerts: 0 },
    { id: 'cam_006', name: 'Electronics Zone', location: 'Level 3', status: 'active', alerts: 0 }
  ]

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{t('camera.title')}</h1>
          <p className="text-gray-600 mt-1">{t('camera.subtitle')}</p>
        </div>
        <div className="flex items-center space-x-3">
          <select
            value={selectedCamera}
            onChange={(e) => setSelectedCamera(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Cameras</option>
            {cameras.map((camera) => (
              <option key={camera.id} value={camera.id}>{camera.name}</option>
            ))}
          </select>
          <button 
            onClick={() => {
              toast.success('Refreshing all camera feeds...')
              setTimeout(() => {
                showAlert(
                  'Camera System Refresh Complete',
                  '✓ 156 camera feeds refreshed\n✓ AI detection models updated\n✓ Alert systems synchronized\n✓ System health verified\n✓ Network connectivity optimized\n\nAll cameras are now up to date!',
                  'success'
                )
                toast.success('All camera feeds refreshed successfully!')
              }, 3000)
            }}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh All
          </button>
          <button 
            onClick={() => {
              toast.success('Exporting camera logs...')
              setTimeout(() => {
                const blob = new Blob(['Camera Intelligence Logs - ' + new Date().toLocaleDateString()], { type: 'text/plain' })
                const url = window.URL.createObjectURL(blob)
                const a = document.createElement('a')
                a.href = url
                a.download = `camera-logs-${new Date().toISOString().split('T')[0]}.log`
                a.click()
                window.URL.revokeObjectURL(url)
                toast.success('Camera logs exported successfully!')
              }, 2000)
            }}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center"
          >
            <Download className="w-4 h-4 mr-2" />
            Export Logs
          </button>
        </div>
      </div>

      {/* Real-time Status */}
      <div className="bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 rounded-xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center">
              <Eye className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-lg font-semibold">Camera Intelligence System</h3>
              <p className="text-white/80">
                156 cameras active • AI detection enabled • 24/7 monitoring
              </p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-2xl font-bold">99.2%</p>
            <p className="text-white/80 text-sm">System Uptime</p>
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Active Cameras</p>
              <p className="text-3xl font-bold text-gray-900">148</p>
              <p className="text-sm text-green-600">95% operational</p>
            </div>
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <Camera className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Active Alerts</p>
              <p className="text-3xl font-bold text-gray-900">3</p>
              <p className="text-sm text-orange-600">2 high priority</p>
            </div>
            <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
              <AlertTriangle className="w-6 h-6 text-orange-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">People Tracked</p>
              <p className="text-3xl font-bold text-gray-900">8,456</p>
              <p className="text-sm text-blue-600">Real-time count</p>
            </div>
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <Users className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Incidents Today</p>
              <p className="text-3xl font-bold text-gray-900">12</p>
              <p className="text-sm text-purple-600">-15% vs yesterday</p>
            </div>
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
              <Shield className="w-6 h-6 text-purple-600" />
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
      {selectedView === 'live' && <LiveFeeds />}
      {selectedView === 'analytics' && <CameraAnalytics />}
      {selectedView === 'alerts' && <AlertCenter />}
      {selectedView === 'system' && <SystemHealth />}
    </div>
  )
}

// Live Feeds Component
const LiveFeeds: React.FC = () => {
  const feeds = [
    { id: 1, name: 'Main Entrance', location: 'Ground Floor', status: 'live', people: 23 },
    { id: 2, name: 'Food Court', location: 'Level 2', status: 'live', people: 89 },
    { id: 3, name: 'Fashion District', location: 'Level 1', status: 'live', people: 45 },
    { id: 4, name: 'Electronics Zone', location: 'Level 3', status: 'live', people: 34 },
    { id: 5, name: 'Parking B1', location: 'Basement', status: 'maintenance', people: 0 },
    { id: 6, name: 'Emergency Exit', location: 'All Levels', status: 'live', people: 2 }
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">Live Camera Feeds</h3>
        <div className="flex items-center space-x-2">
          <button className="px-3 py-2 bg-gray-100 rounded-lg hover:bg-gray-200 flex items-center">
            <Grid3X3 className="w-4 h-4 mr-2" />
            Grid View
          </button>
          <button className="px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center">
            <Maximize className="w-4 h-4 mr-2" />
            Full Screen
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {feeds.map((feed, index) => (
          <motion.div
            key={feed.id}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: index * 0.1 }}
            className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden"
          >
            <div className="relative">
              <div className="aspect-video bg-gray-900 flex items-center justify-center">
                <div className="text-center text-white">
                  <Camera className="w-12 h-12 mx-auto mb-2 opacity-50" />
                  <p className="text-sm">{feed.status === 'live' ? 'Live Feed' : 'Maintenance'}</p>
                </div>
              </div>
              <div className="absolute top-3 left-3">
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  feed.status === 'live' ? 'bg-green-500 text-white' : 'bg-orange-500 text-white'
                }`}>
                  {feed.status === 'live' ? '● LIVE' : '● MAINTENANCE'}
                </span>
              </div>
              <div className="absolute top-3 right-3">
                <div className="flex space-x-1">
                  <button className="p-1 bg-black/50 rounded hover:bg-black/70">
                    <ZoomIn className="w-4 h-4 text-white" />
                  </button>
                  <button className="p-1 bg-black/50 rounded hover:bg-black/70">
                    <Settings className="w-4 h-4 text-white" />
                  </button>
                </div>
              </div>
            </div>
            <div className="p-4">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-semibold text-gray-900">{feed.name}</h4>
                <span className="text-sm text-gray-500">{feed.location}</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Users className="w-4 h-4 text-blue-600" />
                  <span className="text-sm font-medium">{feed.people} people</span>
                </div>
                <div className="flex space-x-1">
                  <button className="p-1 hover:bg-gray-100 rounded">
                    <Play className="w-4 h-4 text-gray-600" />
                  </button>
                  <button className="p-1 hover:bg-gray-100 rounded">
                    <RotateCcw className="w-4 h-4 text-gray-600" />
                  </button>
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  )
}

// Camera Analytics Component
const CameraAnalytics: React.FC = () => {
  const analyticsData = [
    { zone: 'Main Entrance', detection: 95, occupancy: 78, alerts: 2 },
    { zone: 'Food Court', detection: 92, occupancy: 89, alerts: 5 },
    { zone: 'Fashion District', detection: 88, occupancy: 65, alerts: 1 },
    { zone: 'Electronics Zone', detection: 91, occupancy: 72, alerts: 3 },
    { zone: 'Parking Areas', detection: 85, occupancy: 45, alerts: 0 },
    { zone: 'Emergency Exits', detection: 98, occupancy: 12, alerts: 0 }
  ]

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">AI Detection Performance</h3>
        <div className="space-y-4">
          {analyticsData.map((data, index) => (
            <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div className="flex-1">
                <h4 className="font-medium text-gray-900 mb-2">{data.zone}</h4>
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <p className="text-xs text-gray-600">Detection Accuracy</p>
                    <div className="flex items-center space-x-2">
                      <div className="w-16 bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-green-600 h-2 rounded-full" 
                          style={{ width: `${data.detection}%` }}
                        ></div>
                      </div>
                      <span className="text-sm font-medium">{data.detection}%</span>
                    </div>
                  </div>
                  <div>
                    <p className="text-xs text-gray-600">Occupancy Level</p>
                    <div className="flex items-center space-x-2">
                      <div className="w-16 bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-blue-600 h-2 rounded-full" 
                          style={{ width: `${data.occupancy}%` }}
                        ></div>
                      </div>
                      <span className="text-sm font-medium">{data.occupancy}%</span>
                    </div>
                  </div>
                  <div>
                    <p className="text-xs text-gray-600">Active Alerts</p>
                    <span className={`text-sm font-medium ${
                      data.alerts > 3 ? 'text-red-600' : 
                      data.alerts > 0 ? 'text-orange-600' : 'text-green-600'
                    }`}>
                      {data.alerts} alerts
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Heat Map */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Traffic Heat Map</h3>
        <div className="grid grid-cols-4 gap-4">
          {[
            { area: 'A1', intensity: 85, label: 'Main Entry' },
            { area: 'A2', intensity: 92, label: 'Escalator' },
            { area: 'B1', intensity: 78, label: 'Fashion' },
            { area: 'B2', intensity: 95, label: 'Food Court' },
            { area: 'C1', intensity: 65, label: 'Electronics' },
            { area: 'C2', intensity: 72, label: 'Books' },
            { area: 'D1', intensity: 45, label: 'Services' },
            { area: 'D2', intensity: 38, label: 'Parking' }
          ].map((area, index) => (
            <div
              key={index}
              className={`aspect-square rounded-lg flex items-center justify-center text-white font-medium ${
                area.intensity > 80 ? 'bg-red-500' :
                area.intensity > 60 ? 'bg-orange-500' :
                area.intensity > 40 ? 'bg-yellow-500' :
                'bg-green-500'
              }`}
            >
              <div className="text-center">
                <div className="text-lg font-bold">{area.area}</div>
                <div className="text-xs">{area.intensity}%</div>
                <div className="text-xs mt-1">{area.label}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

// Alert Center Component
const AlertCenter: React.FC = () => {
  const alerts = [
    {
      id: 1,
      type: 'security',
      severity: 'high',
      camera: 'Food Court Camera 2',
      message: 'Unattended bag detected for >10 minutes',
      time: '14:23:45',
      status: 'active'
    },
    {
      id: 2,
      type: 'crowd',
      severity: 'medium',
      camera: 'Main Entrance',
      message: 'High crowd density detected - potential bottleneck',
      time: '14:15:22',
      status: 'investigating'
    },
    {
      id: 3,
      type: 'technical',
      severity: 'low',
      camera: 'Parking B1 Camera 3',
      message: 'Camera offline - maintenance required',
      time: '13:45:10',
      status: 'acknowledged'
    },
    {
      id: 4,
      type: 'behavior',
      severity: 'high',
      camera: 'Electronics Zone',
      message: 'Suspicious behavior pattern detected',
      time: '12:30:15',
      status: 'resolved'
    }
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">Active Alerts & Incidents</h3>
        <div className="flex items-center space-x-2">
          <select className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option>All Severities</option>
            <option>High Priority</option>
            <option>Medium Priority</option>
            <option>Low Priority</option>
          </select>
          <button className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 flex items-center">
            <Bell className="w-4 h-4 mr-2" />
            Acknowledge All
          </button>
        </div>
      </div>

      <div className="space-y-4">
        {alerts.map((alert) => (
          <motion.div
            key={alert.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="bg-white rounded-xl shadow-sm border border-gray-200 p-6"
          >
            <div className="flex items-start justify-between">
              <div className="flex items-start space-x-4">
                <div className={`w-3 h-3 rounded-full mt-2 ${
                  alert.severity === 'high' ? 'bg-red-500' :
                  alert.severity === 'medium' ? 'bg-orange-500' :
                  'bg-yellow-500'
                }`}></div>
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    <h4 className="font-semibold text-gray-900">{alert.camera}</h4>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      alert.severity === 'high' ? 'bg-red-100 text-red-700' :
                      alert.severity === 'medium' ? 'bg-orange-100 text-orange-700' :
                      'bg-yellow-100 text-yellow-700'
                    }`}>
                      {alert.severity.toUpperCase()}
                    </span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      alert.status === 'active' ? 'bg-red-100 text-red-700' :
                      alert.status === 'investigating' ? 'bg-blue-100 text-blue-700' :
                      alert.status === 'acknowledged' ? 'bg-yellow-100 text-yellow-700' :
                      'bg-green-100 text-green-700'
                    }`}>
                      {alert.status.toUpperCase()}
                    </span>
                  </div>
                  <p className="text-gray-700 mb-2">{alert.message}</p>
                  <div className="flex items-center space-x-4 text-sm text-gray-500">
                    <span className="flex items-center">
                      <Clock className="w-4 h-4 mr-1" />
                      {alert.time}
                    </span>
                    <span className="flex items-center">
                      <Target className="w-4 h-4 mr-1" />
                      {alert.type}
                    </span>
                  </div>
                </div>
              </div>
              <div className="flex space-x-2">
                <button className="px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm">
                  View Feed
                </button>
                <button className="px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 text-sm">
                  Acknowledge
                </button>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  )
}

// System Health Component
const SystemHealth: React.FC = () => {
  const systemMetrics = [
    { name: 'CPU Usage', value: 67, unit: '%', status: 'normal' },
    { name: 'Memory Usage', value: 45, unit: '%', status: 'normal' },
    { name: 'Storage', value: 78, unit: '%', status: 'warning' },
    { name: 'Network', value: 92, unit: '%', status: 'good' },
    { name: 'Camera Uptime', value: 99.2, unit: '%', status: 'excellent' },
    { name: 'AI Processing', value: 85, unit: '%', status: 'normal' }
  ]

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {systemMetrics.map((metric, index) => (
          <div key={index} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h4 className="font-semibold text-gray-900">{metric.name}</h4>
              <div className={`w-3 h-3 rounded-full ${
                metric.status === 'excellent' ? 'bg-green-500' :
                metric.status === 'good' ? 'bg-blue-500' :
                metric.status === 'normal' ? 'bg-yellow-500' :
                metric.status === 'warning' ? 'bg-orange-500' :
                'bg-red-500'
              }`}></div>
            </div>
            <div className="mb-3">
              <div className="flex items-baseline space-x-1">
                <span className="text-3xl font-bold text-gray-900">{metric.value}</span>
                <span className="text-sm text-gray-500">{metric.unit}</span>
              </div>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className={`h-2 rounded-full ${
                  metric.status === 'excellent' ? 'bg-green-500' :
                  metric.status === 'good' ? 'bg-blue-500' :
                  metric.status === 'normal' ? 'bg-yellow-500' :
                  metric.status === 'warning' ? 'bg-orange-500' :
                  'bg-red-500'
                }`}
                style={{ width: `${Math.min(metric.value, 100)}%` }}
              ></div>
            </div>
          </div>
        ))}
      </div>

      {/* Hardware Status */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Hardware Status</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium text-gray-900 mb-3">Server Infrastructure</h4>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Cpu className="w-4 h-4 text-blue-600" />
                  <span className="text-sm">Processing Units</span>
                </div>
                <span className="text-sm font-medium text-green-600">8/8 Online</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <HardDrive className="w-4 h-4 text-purple-600" />
                  <span className="text-sm">Storage Arrays</span>
                </div>
                <span className="text-sm font-medium text-green-600">4/4 Healthy</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Wifi className="w-4 h-4 text-orange-600" />
                  <span className="text-sm">Network Switches</span>
                </div>
                <span className="text-sm font-medium text-green-600">12/12 Active</span>
              </div>
            </div>
          </div>
          <div>
            <h4 className="font-medium text-gray-900 mb-3">Camera Network</h4>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Camera className="w-4 h-4 text-green-600" />
                  <span className="text-sm">HD Cameras</span>
                </div>
                <span className="text-sm font-medium text-green-600">124/130 Online</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Signal className="w-4 h-4 text-blue-600" />
                  <span className="text-sm">4K Cameras</span>
                </div>
                <span className="text-sm font-medium text-green-600">24/26 Online</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Monitor className="w-4 h-4 text-purple-600" />
                  <span className="text-sm">AI Edge Devices</span>
                </div>
                <span className="text-sm font-medium text-orange-600">15/16 Active</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
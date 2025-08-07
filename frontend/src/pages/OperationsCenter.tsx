import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  Activity, AlertTriangle, CheckCircle, Clock, Settings, Users, 
  TrendingUp, Database, Server, Cpu, HardDrive, Wifi, Shield,
  Zap, BarChart3, PieChart, LineChart, Target, Globe, Bell,
  RefreshCw, Download, Filter, Search, Calendar, Eye,
  Play, Pause, Square, RotateCcw, Maximize, Minimize
} from 'lucide-react'
import { useTranslation } from '@/contexts/TranslationContext'
import { toast } from 'react-hot-toast'
import { showAlert } from '@/lib/alertService'

export const OperationsCenter: React.FC = () => {
  const { t } = useTranslation()
  const [selectedView, setSelectedView] = useState('overview')
  const [timeRange, setTimeRange] = useState('24h')
  const [autoRefresh, setAutoRefresh] = useState(true)

  const views = [
    { id: 'overview', label: 'System Overview', icon: Activity },
    { id: 'performance', label: 'Performance', icon: TrendingUp },
    { id: 'infrastructure', label: 'Infrastructure', icon: Server },
    { id: 'security', label: 'Security', icon: Shield },
    { id: 'alerts', label: 'Alerts & Monitoring', icon: Bell }
  ]

  const timeRanges = [
    { value: '1h', label: 'Last Hour' },
    { value: '24h', label: 'Last 24 Hours' },
    { value: '7d', label: 'Last 7 Days' },
    { value: '30d', label: 'Last 30 Days' }
  ]

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Real-time Operations Center</h1>
          <p className="text-gray-600 mt-1">Live monitoring, system health, and operational intelligence</p>
        </div>
        <div className="flex items-center space-x-3">
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {timeRanges.map(range => (
              <option key={range.value} value={range.value}>{range.label}</option>
            ))}
          </select>
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={`px-3 py-2 rounded-lg flex items-center ${
              autoRefresh 
                ? 'bg-green-100 text-green-700 border border-green-300' 
                : 'bg-gray-100 text-gray-600 border border-gray-300'
            }`}
          >
            {autoRefresh ? <Play className="w-4 h-4 mr-1" /> : <Pause className="w-4 h-4 mr-1" />}
            Auto-refresh
          </button>
          <button 
            onClick={() => {
              toast.success('Generating operations report...')
              setTimeout(() => {
                const blob = new Blob(['Operations Center Report - ' + new Date().toLocaleDateString()], { type: 'text/plain' })
                const url = window.URL.createObjectURL(blob)
                const a = document.createElement('a')
                a.href = url
                a.download = `operations-report-${new Date().toISOString().split('T')[0]}.xlsx`
                a.click()
                window.URL.revokeObjectURL(url)
                toast.success('Operations report exported successfully!')
              }, 2000)
            }}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center"
          >
            <Download className="w-4 h-4 mr-2" />
            Export Report
          </button>
        </div>
      </div>

      {/* System Status Banner */}
      <div className="bg-gradient-to-r from-green-600 via-blue-600 to-purple-600 rounded-xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center">
              <CheckCircle className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-lg font-semibold">All Systems Operational</h3>
              <p className="text-white/80">
                Infrastructure running smoothly • No critical alerts • Performance optimal
              </p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-2xl font-bold">99.8%</p>
            <p className="text-white/80 text-sm">System Uptime</p>
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <SystemMetricCard
          title="Active Users"
          value="2,847"
          change="+5.2%"
          trend="up"
          icon={Users}
          color="blue"
        />
        <SystemMetricCard
          title="System Load"
          value="67%"
          change="-2.1%"
          trend="down"
          icon={Cpu}
          color="green"
        />
        <SystemMetricCard
          title="Response Time"
          value="184ms"
          change="+12ms"
          trend="up"
          icon={Zap}
          color="orange"
        />
        <SystemMetricCard
          title="Error Rate"
          value="0.03%"
          change="-0.01%"
          trend="down"
          icon={AlertTriangle}
          color="red"
        />
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
      {selectedView === 'overview' && <SystemOverview />}
      {selectedView === 'performance' && <PerformanceMonitoring />}
      {selectedView === 'infrastructure' && <InfrastructureStatus />}
      {selectedView === 'security' && <SecurityDashboard />}
      {selectedView === 'alerts' && <AlertsMonitoring />}
    </div>
  )
}

// System Metric Card Component
const SystemMetricCard: React.FC<{
  title: string
  value: string
  change: string
  trend: 'up' | 'down'
  icon: any
  color: string
}> = ({ title, value, change, trend, icon: Icon, color }) => (
  <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
    <div className="flex items-center justify-between">
      <div>
        <p className="text-sm font-medium text-gray-600">{title}</p>
        <p className="text-3xl font-bold text-gray-900">{value}</p>
        <p className={`text-sm ${trend === 'up' ? 'text-green-600' : 'text-red-600'}`}>
          {change} from last period
        </p>
      </div>
      <div className={`w-12 h-12 bg-${color}-100 rounded-lg flex items-center justify-center`}>
        <Icon className={`w-6 h-6 text-${color}-600`} />
      </div>
    </div>
  </div>
)

// System Overview Component
const SystemOverview: React.FC = () => {
  const services = [
    { name: 'API Gateway', status: 'healthy', uptime: '99.9%', responseTime: '42ms' },
    { name: 'Database Cluster', status: 'healthy', uptime: '99.8%', responseTime: '8ms' },
    { name: 'Authentication Service', status: 'healthy', uptime: '100%', responseTime: '12ms' },
    { name: 'Analytics Engine', status: 'warning', uptime: '97.2%', responseTime: '156ms' },
    { name: 'Notification Service', status: 'healthy', uptime: '99.5%', responseTime: '23ms' },
    { name: 'File Storage', status: 'healthy', uptime: '99.9%', responseTime: '34ms' }
  ]

  return (
    <div className="space-y-6">
      {/* Service Status Grid */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Service Status</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {services.map((service, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.1 }}
              className="p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow"
            >
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium text-gray-900">{service.name}</h4>
                <div className={`w-3 h-3 rounded-full ${
                  service.status === 'healthy' ? 'bg-green-500' :
                  service.status === 'warning' ? 'bg-yellow-500' :
                  'bg-red-500'
                }`}></div>
              </div>
              <div className="space-y-1 text-sm text-gray-600">
                <div className="flex justify-between">
                  <span>Uptime:</span>
                  <span className="font-medium">{service.uptime}</span>
                </div>
                <div className="flex justify-between">
                  <span>Response:</span>
                  <span className="font-medium">{service.responseTime}</span>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Real-time Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Traffic Overview</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Requests/hour</span>
              <span className="font-bold text-blue-600">847,293</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Bandwidth</span>
              <span className="font-bold text-green-600">2.3 GB/h</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Cache Hit Rate</span>
              <span className="font-bold text-purple-600">94.2%</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Error Rate</span>
              <span className="font-bold text-red-600">0.03%</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Resource Usage</h3>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-600">CPU Usage</span>
                <span className="font-medium">67%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-blue-600 h-2 rounded-full" style={{ width: '67%' }}></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-600">Memory</span>
                <span className="font-medium">73%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-green-600 h-2 rounded-full" style={{ width: '73%' }}></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-600">Storage</span>
                <span className="font-medium">45%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-purple-600 h-2 rounded-full" style={{ width: '45%' }}></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-600">Network I/O</span>
                <span className="font-medium">28%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-orange-600 h-2 rounded-full" style={{ width: '28%' }}></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

// Performance Monitoring Component
const PerformanceMonitoring: React.FC = () => (
  <div className="space-y-6">
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance Analytics</h3>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="space-y-4">
          <h4 className="font-medium text-gray-900">Application Performance</h4>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">Avg Response Time</span>
              <span className="font-medium">184ms</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Throughput</span>
              <span className="font-medium">1,247 req/s</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Error Rate</span>
              <span className="font-medium">0.03%</span>
            </div>
          </div>
        </div>
        
        <div className="space-y-4">
          <h4 className="font-medium text-gray-900">Database Performance</h4>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">Query Time</span>
              <span className="font-medium">8.2ms</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Connections</span>
              <span className="font-medium">47/100</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Deadlocks</span>
              <span className="font-medium">0</span>
            </div>
          </div>
        </div>
        
        <div className="space-y-4">
          <h4 className="font-medium text-gray-900">Network Performance</h4>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">Latency</span>
              <span className="font-medium">23ms</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Bandwidth</span>
              <span className="font-medium">2.3 GB/h</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Packet Loss</span>
              <span className="font-medium">0.01%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
)

// Infrastructure Status Component
const InfrastructureStatus: React.FC = () => {
  const servers = [
    { name: 'Web Server 01', status: 'online', cpu: 45, memory: 67, disk: 23 },
    { name: 'Web Server 02', status: 'online', cpu: 52, memory: 71, disk: 28 },
    { name: 'Database Master', status: 'online', cpu: 73, memory: 84, disk: 45 },
    { name: 'Database Replica', status: 'online', cpu: 23, memory: 34, disk: 45 },
    { name: 'Cache Server', status: 'maintenance', cpu: 0, memory: 0, disk: 67 },
    { name: 'Load Balancer', status: 'online', cpu: 12, memory: 23, disk: 15 }
  ]

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Server Infrastructure</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {servers.map((server, index) => (
            <div key={index} className="p-4 border border-gray-200 rounded-lg">
              <div className="flex items-center justify-between mb-3">
                <h4 className="font-medium text-gray-900">{server.name}</h4>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  server.status === 'online' ? 'bg-green-100 text-green-700' :
                  server.status === 'maintenance' ? 'bg-yellow-100 text-yellow-700' :
                  'bg-red-100 text-red-700'
                }`}>
                  {server.status}
                </span>
              </div>
              
              <div className="space-y-2">
                <div>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-gray-600">CPU</span>
                    <span>{server.cpu}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-1.5">
                    <div 
                      className={`h-1.5 rounded-full ${server.cpu > 80 ? 'bg-red-500' : server.cpu > 60 ? 'bg-yellow-500' : 'bg-green-500'}`}
                      style={{ width: `${server.cpu}%` }}
                    ></div>
                  </div>
                </div>
                
                <div>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-gray-600">Memory</span>
                    <span>{server.memory}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-1.5">
                    <div 
                      className={`h-1.5 rounded-full ${server.memory > 80 ? 'bg-red-500' : server.memory > 60 ? 'bg-yellow-500' : 'bg-green-500'}`}
                      style={{ width: `${server.memory}%` }}
                    ></div>
                  </div>
                </div>
                
                <div>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-gray-600">Disk</span>
                    <span>{server.disk}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-1.5">
                    <div 
                      className={`h-1.5 rounded-full ${server.disk > 80 ? 'bg-red-500' : server.disk > 60 ? 'bg-yellow-500' : 'bg-green-500'}`}
                      style={{ width: `${server.disk}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

// Security Dashboard Component
const SecurityDashboard: React.FC = () => {
  const securityMetrics = [
    { label: 'Threats Blocked', value: '1,247', color: 'red' },
    { label: 'Security Scans', value: '23', color: 'blue' },
    { label: 'Vulnerabilities', value: '2', color: 'yellow' },
    { label: 'Compliance', value: '98.5%', color: 'green' }
  ]

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {securityMetrics.map((metric, index) => (
          <div key={index} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="text-center">
              <p className="text-sm font-medium text-gray-600 mb-2">{metric.label}</p>
              <p className={`text-2xl font-bold text-${metric.color}-600`}>{metric.value}</p>
            </div>
          </div>
        ))}
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Security Events</h3>
        <div className="space-y-3">
          {[
            { type: 'warning', message: 'Multiple failed login attempts detected', time: '2 minutes ago' },
            { type: 'info', message: 'Security scan completed successfully', time: '15 minutes ago' },
            { type: 'success', message: 'SSL certificate renewed', time: '1 hour ago' },
            { type: 'warning', message: 'Unusual API access pattern detected', time: '2 hours ago' }
          ].map((event, index) => (
            <div key={index} className="flex items-center p-3 bg-gray-50 rounded-lg">
              <div className={`w-2 h-2 rounded-full mr-3 ${
                event.type === 'success' ? 'bg-green-500' :
                event.type === 'warning' ? 'bg-yellow-500' :
                event.type === 'error' ? 'bg-red-500' :
                'bg-blue-500'
              }`}></div>
              <div className="flex-1">
                <p className="text-sm text-gray-900">{event.message}</p>
                <p className="text-xs text-gray-500">{event.time}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

// Alerts Monitoring Component
const AlertsMonitoring: React.FC = () => {
  const alerts = [
    {
      id: '1',
      severity: 'high',
      title: 'High CPU Usage on Database Server',
      description: 'CPU usage has exceeded 85% for the past 10 minutes',
      time: '5 minutes ago',
      status: 'active'
    },
    {
      id: '2', 
      severity: 'medium',
      title: 'Memory Usage Warning',
      description: 'Memory usage on Web Server 02 is at 78%',
      time: '12 minutes ago',
      status: 'acknowledged'
    },
    {
      id: '3',
      severity: 'low',
      title: 'SSL Certificate Expiring Soon',
      description: 'SSL certificate for api.domain.com expires in 15 days',
      time: '1 hour ago', 
      status: 'active'
    }
  ]

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Active System Alerts</h3>
          <div className="flex items-center space-x-2">
            <button 
              onClick={() => {
                toast.success('Opening alert configuration...')
                setTimeout(() => {
                  showAlert(
                    'Alert Configuration Panel',
                    '✓ CPU Usage Threshold: 85%\n✓ Memory Warning: 80%\n✓ Disk Space Alert: 90%\n✓ Response Time Limit: 500ms\n✓ Error Rate Threshold: 1%\n\nConfiguration saved successfully!',
                    'success'
                  )
                  toast.success('Alert settings configured!')
                }, 1500)
              }}
              className="px-3 py-2 text-sm bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200"
            >
              Configure Alerts
            </button>
            <button 
              onClick={() => {
                toast.success('Loading alert history...')
                setTimeout(() => {
                  showAlert(
                    'Alert History (Last 7 Days)',
                    '• High CPU usage - Database Server (resolved)\n• Memory warning - Web Server 02 (active)\n• SSL certificate renewal reminder (completed)\n• Disk space warning - Storage Node 3 (resolved)\n• Network latency spike (auto-resolved)\n\nTotal alerts: 15 | Resolved: 12 | Active: 3',
                    'info'
                  )
                  toast.success('Alert history loaded!')
                }, 1500)
              }}
              className="px-3 py-2 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
            >
              View History
            </button>
          </div>
        </div>

        <div className="space-y-3">
          {alerts.map((alert) => (
            <div key={alert.id} className="p-4 border border-gray-200 rounded-lg hover:shadow-sm transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3">
                  <div className={`w-3 h-3 rounded-full mt-1 ${
                    alert.severity === 'high' ? 'bg-red-500' :
                    alert.severity === 'medium' ? 'bg-yellow-500' :
                    'bg-blue-500'
                  }`}></div>
                  <div>
                    <h4 className="font-medium text-gray-900">{alert.title}</h4>
                    <p className="text-sm text-gray-600 mt-1">{alert.description}</p>
                    <p className="text-xs text-gray-500 mt-2">{alert.time}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    alert.status === 'active' ? 'bg-red-100 text-red-700' :
                    alert.status === 'acknowledged' ? 'bg-yellow-100 text-yellow-700' :
                    'bg-green-100 text-green-700'
                  }`}>
                    {alert.status}
                  </span>
                  <button className="p-1 hover:bg-gray-100 rounded">
                    <Settings className="w-4 h-4 text-gray-400" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default OperationsCenter
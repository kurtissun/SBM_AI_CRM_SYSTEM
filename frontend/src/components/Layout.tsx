import React, { useState } from 'react'
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Home, Users, Target, BarChart3, Route, MessageSquare, Activity,
  FileText, Building2, Camera, Globe, Gift, ShoppingBag, TrendingUp,
  Mic, Settings, Menu, X, Search, Bell, User, ChevronRight,
  Sparkles, Brain, Store, LogOut, HelpCircle, ChevronDown
} from 'lucide-react'
import { useAuthStore } from '@/stores/authStore'
import { AIChat } from './AIChat'
import { NotificationPanel } from './NotificationPanel'
import { GlobalSearch } from './GlobalSearch'

interface NavItem {
  id: string
  label: string
  icon: React.ElementType
  path: string
  badge?: number
  children?: NavItem[]
}

const navigationItems: NavItem[] = [
  { id: 'dashboard', label: 'Dashboard', icon: Home, path: '/' },
  { id: 'customers', label: 'Customer Intelligence', icon: Users, path: '/customers' },
  { id: 'campaigns', label: 'Campaign Center', icon: Target, path: '/campaigns', badge: 3 },
  { id: 'segmentation', label: 'Segmentation Studio', icon: Brain, path: '/segmentation' },
  { id: 'analytics', label: 'Analytics & Insights', icon: BarChart3, path: '/analytics' },
  { id: 'journeys', label: 'Journey & Automation', icon: Route, path: '/journeys' },
  { id: 'ai-assistant', label: 'AI Assistant', icon: MessageSquare, path: '/ai-assistant' },
  { id: 'operations', label: 'Operations Center', icon: Activity, path: '/operations', badge: 7 },
  { id: 'reports', label: 'Reports Studio', icon: FileText, path: '/reports' },
  { id: 'mall-operations', label: 'Mall Operations', icon: Building2, path: '/mall-operations' },
  { id: 'camera', label: 'Camera Intelligence', icon: Camera, path: '/camera' },
  { id: 'chinese-market', label: 'Chinese Market', icon: Globe, path: '/chinese-market' },
  { id: 'loyalty', label: 'Loyalty & VIP', icon: Gift, path: '/loyalty' },
  { id: 'retail-intelligence', label: 'Retail Intelligence', icon: ShoppingBag, path: '/retail-intelligence' },
  { id: 'simulator', label: 'Economic Simulator', icon: TrendingUp, path: '/simulator' },
  { id: 'voice-of-customer', label: 'Voice of Customer', icon: Mic, path: '/voice-of-customer' },
  { id: 'admin', label: 'Admin Center', icon: Settings, path: '/admin' },
]

export const Layout: React.FC = () => {
  const location = useLocation()
  const navigate = useNavigate()
  const { user, logout } = useAuthStore()
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false)
  const [showAIChat, setShowAIChat] = useState(false)
  const [showNotifications, setShowNotifications] = useState(false)
  const [showSearch, setShowSearch] = useState(false)
  const [showUserMenu, setShowUserMenu] = useState(false)

  const isActive = (path: string) => {
    if (path === '/') return location.pathname === '/'
    return location.pathname.startsWith(path)
  }

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <motion.aside
        initial={false}
        animate={{ width: isSidebarCollapsed ? 64 : 256 }}
        transition={{ duration: 0.3, ease: 'easeInOut' }}
        className="bg-gradient-to-b from-dark-100 to-dark-200 text-white flex flex-col overflow-hidden"
      >
        {/* Logo */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-white/10">
          <Link to="/" className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <Store className="w-6 h-6 text-white" />
            </div>
            {!isSidebarCollapsed && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                <h1 className="text-xl font-bold">SBM AI CRM</h1>
              </motion.div>
            )}
          </Link>
          <button
            onClick={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
            className="p-1.5 hover:bg-white/10 rounded-lg transition-colors"
          >
            <Menu className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto py-4 px-2">
          {navigationItems.map((item) => (
            <Link
              key={item.id}
              to={item.path}
              className={`
                flex items-center px-3 py-2.5 mb-1 rounded-lg transition-all duration-200
                ${isActive(item.path)
                  ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg'
                  : 'hover:bg-white/10 text-gray-300 hover:text-white'
                }
              `}
            >
              <item.icon className="w-5 h-5 flex-shrink-0" />
              {!isSidebarCollapsed && (
                <>
                  <span className="ml-3 flex-1">{item.label}</span>
                  {item.badge && (
                    <span className="bg-red-500 text-white text-xs px-2 py-0.5 rounded-full">
                      {item.badge}
                    </span>
                  )}
                </>
              )}
            </Link>
          ))}
        </nav>

        {/* User section */}
        <div className="border-t border-white/10 p-4">
          <div className="flex items-center">
            <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-blue-500 rounded-full flex items-center justify-center">
              <User className="w-5 h-5 text-white" />
            </div>
            {!isSidebarCollapsed && (
              <div className="ml-3 flex-1">
                <p className="text-sm font-medium">{user?.name || 'User'}</p>
                <p className="text-xs text-gray-400">{user?.email}</p>
              </div>
            )}
          </div>
        </div>
      </motion.aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top bar */}
        <header className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-6">
          <div className="flex items-center flex-1">
            <button
              onClick={() => setShowSearch(true)}
              className="flex items-center space-x-2 px-4 py-2 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
            >
              <Search className="w-4 h-4 text-gray-500" />
              <span className="text-sm text-gray-600">Search...</span>
              <kbd className="hidden sm:inline-block px-2 py-0.5 text-xs bg-white rounded border border-gray-300">
                ⌘K
              </kbd>
            </button>
          </div>

          <div className="flex items-center space-x-4">
            {/* AI Assistant */}
            <button
              onClick={() => setShowAIChat(!showAIChat)}
              className="relative p-2 hover:bg-gray-100 rounded-lg transition-colors"
              title="AI Assistant"
            >
              <Sparkles className="w-5 h-5 text-gray-600" />
              <span className="absolute top-0 right-0 w-2 h-2 bg-green-500 rounded-full"></span>
            </button>

            {/* Notifications */}
            <button
              onClick={() => setShowNotifications(!showNotifications)}
              className="relative p-2 hover:bg-gray-100 rounded-lg transition-colors"
              title="Notifications"
            >
              <Bell className="w-5 h-5 text-gray-600" />
              <span className="absolute top-0 right-0 w-2 h-2 bg-red-500 rounded-full"></span>
            </button>

            {/* Help */}
            <button
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              title="Help"
            >
              <HelpCircle className="w-5 h-5 text-gray-600" />
            </button>

            {/* User menu */}
            <div className="relative">
              <button
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="flex items-center space-x-2 p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <div className="w-8 h-8 bg-gradient-to-br from-green-500 to-blue-500 rounded-full flex items-center justify-center">
                  <User className="w-4 h-4 text-white" />
                </div>
                <ChevronDown className="w-4 h-4 text-gray-600" />
              </button>

              <AnimatePresence>
                {showUserMenu && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1"
                  >
                    <Link
                      to="/admin"
                      className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      onClick={() => setShowUserMenu(false)}
                    >
                      <Settings className="w-4 h-4 mr-2" />
                      Settings
                    </Link>
                    <hr className="my-1 border-gray-200" />
                    <button
                      onClick={() => {
                        logout()
                        navigate('/login')
                      }}
                      className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 w-full text-left"
                    >
                      <LogOut className="w-4 h-4 mr-2" />
                      Logout
                    </button>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-50">
          <Outlet />
        </main>
      </div>

      {/* AI Chat Panel */}
      <AnimatePresence>
        {showAIChat && (
          <AIChat onClose={() => setShowAIChat(false)} />
        )}
      </AnimatePresence>

      {/* Notifications Panel */}
      <AnimatePresence>
        {showNotifications && (
          <NotificationPanel onClose={() => setShowNotifications(false)} />
        )}
      </AnimatePresence>

      {/* Global Search Modal */}
      <AnimatePresence>
        {showSearch && (
          <GlobalSearch onClose={() => setShowSearch(false)} />
        )}
      </AnimatePresence>
    </div>
  )
}
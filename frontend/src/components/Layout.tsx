import React, { useState, useRef } from 'react'
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { createPortal } from 'react-dom'
import {
  Home, Users, Target, BarChart3, Route, MessageSquare, Activity,
  FileText, Building2, Camera, Globe, Gift, ShoppingBag, TrendingUp,
  Mic, Settings, Menu, X, Search, Bell, User, ChevronRight,
  Sparkles, Brain, Store, LogOut, HelpCircle, ChevronDown
} from 'lucide-react'
import { useAuthStore } from '@/stores/authStore'
import { useTranslation } from '@/contexts/TranslationContext'
import { useTheme } from '@/contexts/ThemeContext'
import { AIChat } from './AIChat'
import { NotificationPanel } from './NotificationPanel'
import { GlobalSearch } from './GlobalSearch'
import { LanguageToggle } from './LanguageToggle'

interface NavItem {
  id: string
  label: string
  icon: React.ElementType
  path: string
  badge?: number
  children?: NavItem[]
}

const getNavigationItems = (t: (key: string) => string): NavItem[] => [
  { id: 'dashboard', label: t('nav.dashboard'), icon: Home, path: '/' },
  { id: 'customers', label: t('nav.customers'), icon: Users, path: '/customers' },
  { id: 'campaigns', label: t('nav.campaigns'), icon: Target, path: '/campaigns', badge: 3 },
  { id: 'segmentation', label: t('nav.segmentation'), icon: Brain, path: '/segmentation' },
  { id: 'analytics', label: t('nav.analytics'), icon: BarChart3, path: '/analytics' },
  { id: 'journeys', label: t('nav.journeys'), icon: Route, path: '/journeys' },
  { id: 'ai-assistant', label: t('nav.aiAssistant'), icon: MessageSquare, path: '/ai-assistant' },
  { id: 'operations', label: t('nav.operations'), icon: Activity, path: '/operations', badge: 7 },
  { id: 'reports', label: t('nav.reports'), icon: FileText, path: '/reports' },
  { id: 'mall-operations', label: t('nav.mallOperations'), icon: Building2, path: '/mall-operations' },
  { id: 'camera', label: t('nav.camera'), icon: Camera, path: '/camera' },
  { id: 'chinese-market', label: t('nav.chineseMarket'), icon: Globe, path: '/chinese-market' },
  { id: 'loyalty', label: t('nav.loyalty'), icon: Gift, path: '/loyalty' },
  { id: 'retail-intelligence', label: t('nav.retailIntelligence'), icon: ShoppingBag, path: '/retail-intelligence' },
  { id: 'simulator', label: t('nav.simulator'), icon: TrendingUp, path: '/simulator' },
  { id: 'voice-of-customer', label: t('nav.voiceOfCustomer'), icon: Mic, path: '/voice-of-customer' },
  { id: 'admin', label: t('nav.admin'), icon: Settings, path: '/admin' },
]

export const Layout: React.FC = () => {
  const location = useLocation()
  const navigate = useNavigate()
  const { user, logout } = useAuthStore()
  const { t } = useTranslation()
  const { theme, customBackground, backgroundStyle } = useTheme()
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false)
  const [showAIChat, setShowAIChat] = useState(false)
  const [showNotifications, setShowNotifications] = useState(false)
  const [showSearch, setShowSearch] = useState(false)
  const [showUserMenu, setShowUserMenu] = useState(false)
  const userMenuButtonRef = useRef<HTMLButtonElement>(null)

  console.log('🎨 Layout Debug:', { user, location: location.pathname })

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
        className="bg-gradient-to-b from-gray-900 to-gray-800 text-white flex flex-col overflow-hidden"
      >
        {/* Logo */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-white/10">
          <Link to="/" className="flex items-center space-x-3">
            <img 
              src="/SBM_logo.png" 
              alt="SBM Logo" 
              className="w-16 h-16 object-contain rounded-lg"
            />
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
          {getNavigationItems(t).map((item) => (
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
            {user?.profilePicture ? (
              <img
                src={user.profilePicture}
                alt="Profile"
                className="w-10 h-10 rounded-full object-cover border-2 border-white/20"
              />
            ) : (
              <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-blue-500 rounded-full flex items-center justify-center">
                <User className="w-5 h-5 text-white" />
              </div>
            )}
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
        <header 
          className={`h-16 border-b flex items-center justify-between px-6 relative ${
            theme === 'dark' 
              ? 'border-gray-700' 
              : 'border-gray-200'
          } ${customBackground ? 'glass-enhanced' : theme === 'dark' ? 'bg-gray-800' : 'bg-white'}`}
          style={customBackground ? {
            ...backgroundStyle,
            backgroundAttachment: 'fixed',
            backgroundSize: 'cover',
            backgroundPosition: 'center',
            backgroundRepeat: 'no-repeat'
          } : {}}
        >
          {/* Background overlay for better readability */}
          {customBackground && (
            <div className={`absolute inset-0 z-0 ${
              theme === 'dark' 
                ? 'bg-gray-900/80 backdrop-blur-md' 
                : 'bg-white/80 backdrop-blur-md'
            }`} />
          )}
          <div className="flex items-center flex-1 relative z-10">
            <button
              onClick={() => setShowSearch(true)}
              className={`flex items-center space-x-2 px-6 py-2 rounded-lg transition-all duration-200 w-80 max-w-md border bg-transparent ${
                customBackground
                  ? (theme === 'dark' 
                    ? 'text-gray-300 border-white/40 hover:border-white/60 focus:border-blue-400'
                    : 'text-gray-700 border-gray-800/40 hover:border-gray-800/60 focus:border-blue-600')
                  : (theme === 'dark'
                    ? 'text-gray-300 border-gray-400 hover:border-gray-300 focus:border-blue-500'
                    : 'text-gray-700 border-gray-600 hover:border-gray-700 focus:border-blue-500')
              } focus:outline-none focus:ring-2 focus:ring-blue-500/20`}
            >
              <Search className={`w-4 h-4 flex-shrink-0 ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`} />
              <span className={`text-sm flex-1 text-left truncate ${theme === 'dark' ? 'text-gray-300' : 'text-gray-600'}`}>{t('layout.searchPlaceholder')}</span>
              <kbd className={`hidden sm:inline-block px-2 py-0.5 text-xs rounded border bg-transparent flex-shrink-0 ${
                customBackground
                  ? (theme === 'dark' 
                    ? 'border-white/40 text-gray-300'
                    : 'border-gray-800/40 text-gray-700')
                  : (theme === 'dark' 
                    ? 'border-gray-400 text-gray-300'
                    : 'border-gray-600 text-gray-600')
              }`}>
                Cmd+K
              </kbd>
            </button>
          </div>

          <div className="flex items-center space-x-4 relative z-20">
            {/* AI Assistant */}
            <button
              onClick={() => setShowAIChat(!showAIChat)}
              className={`relative p-2 rounded-lg transition-colors ${
                theme === 'dark' 
                  ? 'hover:bg-gray-700' 
                  : 'hover:bg-gray-100'
              }`}
              title={t('layout.aiAssistant')}
            >
              <Sparkles className={`w-5 h-5 ${theme === 'dark' ? 'text-gray-300' : 'text-gray-600'}`} />
              <span className="absolute top-0 right-0 w-2 h-2 bg-green-500 rounded-full"></span>
            </button>

            {/* Notifications */}
            <button
              onClick={() => setShowNotifications(!showNotifications)}
              className={`relative p-2 rounded-lg transition-colors ${
                theme === 'dark' 
                  ? 'hover:bg-gray-700' 
                  : 'hover:bg-gray-100'
              }`}
              title={t('layout.notifications')}
            >
              <Bell className={`w-5 h-5 ${theme === 'dark' ? 'text-gray-300' : 'text-gray-600'}`} />
              <span className="absolute top-0 right-0 w-2 h-2 bg-red-500 rounded-full"></span>
            </button>

            {/* Language Toggle */}
            <LanguageToggle />

            {/* Help */}
            <button
              className={`p-2 rounded-lg transition-colors ${
                theme === 'dark' 
                  ? 'hover:bg-gray-700' 
                  : 'hover:bg-gray-100'
              }`}
              title={t('layout.help')}
            >
              <HelpCircle className={`w-5 h-5 ${theme === 'dark' ? 'text-gray-300' : 'text-gray-600'}`} />
            </button>

            {/* User menu */}
            <div className="relative">
              <button
                ref={userMenuButtonRef}
                onClick={() => setShowUserMenu(!showUserMenu)}
                className={`flex items-center space-x-2 p-2 rounded-lg transition-colors ${
                  theme === 'dark' 
                    ? 'hover:bg-gray-700' 
                    : 'hover:bg-gray-100'
                }`}
              >
                {user?.profilePicture ? (
                  <img
                    src={user.profilePicture}
                    alt="Profile"
                    className={`w-8 h-8 rounded-full object-cover border-2 ${
                      theme === 'dark' ? 'border-gray-600' : 'border-gray-200'
                    }`}
                  />
                ) : (
                  <div className="w-8 h-8 bg-gradient-to-br from-green-500 to-blue-500 rounded-full flex items-center justify-center">
                    <User className="w-4 h-4 text-white" />
                  </div>
                )}
                <ChevronDown className={`w-4 h-4 ${theme === 'dark' ? 'text-gray-300' : 'text-gray-600'}`} />
              </button>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main 
          className={`flex-1 overflow-x-hidden overflow-y-auto ${
            theme === 'dark' ? 'bg-gray-900' : 'bg-gray-50'
          }`}
          style={customBackground ? backgroundStyle : {}}
        >
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

      {/* User Menu Dropdown Portal */}
      {showUserMenu && userMenuButtonRef.current && createPortal(
        <AnimatePresence>
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className={`fixed w-48 rounded-lg shadow-xl border py-1 z-[99999] ${
              theme === 'dark' 
                ? 'bg-gray-800 border-gray-600' 
                : 'bg-white border-gray-200'
            }`}
            style={{
              top: userMenuButtonRef.current.getBoundingClientRect().bottom + 8,
              right: window.innerWidth - userMenuButtonRef.current.getBoundingClientRect().right,
              boxShadow: theme === 'dark' 
                ? '0 20px 25px -5px rgba(0, 0, 0, 0.6), 0 10px 10px -5px rgba(0, 0, 0, 0.4)' 
                : '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)'
            }}
          >
            <Link
              to="/settings"
              className={`flex items-center px-4 py-2 text-sm transition-colors ${
                theme === 'dark'
                  ? 'text-gray-200 hover:bg-gray-700'
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
              onClick={() => setShowUserMenu(false)}
            >
              <Settings className="w-4 h-4 mr-2" />
              {t('layout.settings')}
            </Link>
            <hr className={`my-1 ${theme === 'dark' ? 'border-gray-600' : 'border-gray-200'}`} />
            <button
              onClick={() => {
                setShowUserMenu(false)
                logout()
                navigate('/login')
              }}
              className={`flex items-center px-4 py-2 text-sm w-full text-left transition-colors ${
                theme === 'dark'
                  ? 'text-gray-200 hover:bg-gray-700'
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              <LogOut className="w-4 h-4 mr-2" />
              {t('layout.logout')}
            </button>
          </motion.div>
        </AnimatePresence>,
        document.body
      )}
    </div>
  )
}
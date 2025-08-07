import React, { useEffect } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './stores/authStore'
import { Layout } from './components/Layout'
import { LoginPage } from './pages/auth/LoginPage'
import { LoadingScreen } from './components/LoadingScreen'
import { ErrorBoundary } from './components/ErrorBoundary'
import { TranslationProvider } from './contexts/TranslationContext'
import { ThemeProvider } from './contexts/ThemeContext'
import { AlertProvider } from './components/providers/AlertProvider'
import { Dashboard } from './pages/Dashboard'
import { CustomerIntelligence } from './pages/CustomerIntelligence'
import { CampaignCenter } from './pages/CampaignCenter'
import { SegmentationStudio } from './pages/SegmentationStudio'
import { AnalyticsCenter } from './pages/AnalyticsCenter'
import { JourneyAutomation } from './pages/JourneyAutomation'
import { AIAssistant } from './pages/AIAssistant'
import { OperationsCenter } from './pages/OperationsCenter'
import { ReportsStudio } from './pages/ReportsStudio'
import { MallOperations } from './pages/MallOperations'
import { CameraIntelligence } from './pages/CameraIntelligence'
import { ChineseMarket } from './pages/ChineseMarket'
import { LoyaltyManagement } from './pages/LoyaltyManagement'
import { RetailIntelligence } from './pages/RetailIntelligence'
import { EconomicSimulator } from './pages/EconomicSimulator'
import { VoiceOfCustomer } from './pages/VoiceOfCustomer'
import { Settings } from './pages/Settings'
import CreateCampaign from './pages/CreateCampaign'
import CampaignIntelligence from './pages/CampaignIntelligence'
import CalendarPage from './pages/CalendarPage'

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isInitialized } = useAuthStore(state => ({
    isAuthenticated: state.isAuthenticated,
    isInitialized: state.isInitialized
  }))
  
  console.log('🛡️ ProtectedRoute Debug:', { isAuthenticated, isInitialized })
  
  // Show loading while checking auth
  if (!isInitialized) {
    console.log('⏳ Showing loading screen - not initialized')
    return <LoadingScreen message="Initializing..." />
  }
  
  if (!isAuthenticated) {
    console.log('🔄 Redirecting to login - not authenticated')
    return <Navigate to="/login" replace />
  }
  
  console.log('✅ Showing protected content - authenticated')
  return (
    <ErrorBoundary>
      {children}
    </ErrorBoundary>
  )
}

function App() {
  const checkAuth = useAuthStore(state => state.checkAuth)
  
  useEffect(() => {
    checkAuth()
  }, [checkAuth])

  return (
    <TranslationProvider>
      <ThemeProvider>
        <AlertProvider>
          <ErrorBoundary>
          <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }
          >
        <Route index element={<Dashboard />} />
        <Route path="customers/*" element={<CustomerIntelligence />} />
        <Route path="campaigns" element={<CampaignCenter />} />
        <Route path="campaigns/new" element={<CreateCampaign />} />
        <Route path="campaigns/intelligence" element={<CampaignIntelligence />} />
        <Route path="calendar" element={<CalendarPage />} />
        <Route path="segmentation/*" element={<SegmentationStudio />} />
        <Route path="analytics/*" element={<AnalyticsCenter />} />
        <Route path="journeys/*" element={<JourneyAutomation />} />
        <Route path="ai-assistant/*" element={<AIAssistant />} />
        <Route path="operations/*" element={<OperationsCenter />} />
        <Route path="reports/*" element={<ReportsStudio />} />
        <Route path="mall-operations/*" element={<MallOperations />} />
        <Route path="camera/*" element={<CameraIntelligence />} />
        <Route path="chinese-market/*" element={<ChineseMarket />} />
        <Route path="loyalty/*" element={<LoyaltyManagement />} />
        <Route path="retail-intelligence/*" element={<RetailIntelligence />} />
        <Route path="simulator/*" element={<EconomicSimulator />} />
        <Route path="voice-of-customer/*" element={<VoiceOfCustomer />} />
        <Route path="admin/*" element={<Settings />} />
        <Route path="settings/*" element={<Settings />} />
        </Route>
          </Routes>
          </ErrorBoundary>
        </AlertProvider>
      </ThemeProvider>
    </TranslationProvider>
  )
}

export default App
import React, { createContext, useContext, useEffect, useState } from 'react'
import { useAuthStore } from '@/stores/authStore'
import axios from 'axios'

type ThemeType = 'light' | 'dark' | 'auto' | 'pure-black' | 'pure-white'

interface ThemeContextType {
  theme: ThemeType
  customBackground: string | null
  backgroundStyle: React.CSSProperties
  isTransitioning: boolean
  applyBackground: (background: string | null) => void
  setTheme: (theme: ThemeType) => void
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined)

export const useTheme = () => {
  const context = useContext(ThemeContext)
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider')
  }
  return context
}

interface ThemeProviderProps {
  children: React.ReactNode
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  const { user } = useAuthStore()
  const [theme, setThemeState] = useState<ThemeType>('dark')
  const [customBackground, setCustomBackground] = useState<string | null>(null)
  const [backgroundStyle, setBackgroundStyle] = useState<React.CSSProperties>({})
  const [isTransitioning, setIsTransitioning] = useState(false)

  // Load user theme preferences
  useEffect(() => {
    const loadUserTheme = async () => {
      if (user) {
        try {
          const response = await axios.get('/api/user/profile')
          const profile = response.data
          setThemeState(profile.theme || 'dark')
          setCustomBackground(profile.custom_background || null)
        } catch (error) {
          console.error('Failed to load user theme:', error)
        }
      }
    }
    
    loadUserTheme()
  }, [user])

  // Apply background style
  useEffect(() => {
    if (customBackground) {
      if (customBackground.startsWith('data:image')) {
        // Base64 image
        setBackgroundStyle({
          backgroundImage: `url(${customBackground})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundRepeat: 'no-repeat',
          backgroundAttachment: 'fixed'
        })
      } else if (customBackground.startsWith('linear-gradient')) {
        // CSS gradient
        setBackgroundStyle({
          background: customBackground,
          backgroundAttachment: 'fixed'
        })
      } else {
        setBackgroundStyle({})
      }
    } else {
      setBackgroundStyle({})
    }
  }, [customBackground])

  // Apply theme to document
  useEffect(() => {
    const root = document.documentElement
    
    // Remove all theme classes first
    root.classList.remove('dark', 'light', 'pure-black', 'pure-white')
    
    if (theme === 'dark') {
      root.classList.add('dark')
    } else if (theme === 'light') {
      root.classList.add('light')
    } else if (theme === 'pure-black') {
      root.classList.add('pure-black', 'dark')
      // Override custom background with pure black
      if (customBackground) {
        setCustomBackground(null)
      }
    } else if (theme === 'pure-white') {
      root.classList.add('pure-white', 'light')
      // Override custom background with pure white
      if (customBackground) {
        setCustomBackground(null)
      }
    } else {
      // Auto mode - follow system preference
      const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      if (isDark) {
        root.classList.add('dark')
      } else {
        root.classList.add('light')
      }
    }
  }, [theme, customBackground])

  const applyBackground = (background: string | null) => {
    setCustomBackground(background)
  }

  const setTheme = (newTheme: ThemeType) => {
    setIsTransitioning(true)
    
    // Show loading for a smooth transition
    setTimeout(() => {
      setThemeState(newTheme)
      
      // Hide loading after theme is applied
      setTimeout(() => {
        setIsTransitioning(false)
      }, 300)
    }, 100)
  }

  const value: ThemeContextType = {
    theme,
    customBackground,
    backgroundStyle,
    isTransitioning,
    applyBackground,
    setTheme
  }

  return (
    <ThemeContext.Provider value={value}>
      <div className="min-h-screen transition-all duration-300">
        {children}
        
        {/* Theme Transition Loading Overlay */}
        <div className={`theme-transition ${isTransitioning ? 'active' : ''}`}>
          <div className="flex flex-col items-center space-y-4">
            <div className="theme-transition-spinner"></div>
            <p className="text-white text-sm font-medium">Switching theme...</p>
          </div>
        </div>
      </div>
    </ThemeContext.Provider>
  )
}
import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import axios from 'axios'
import { toast } from 'react-hot-toast'

interface User {
  id: string
  email: string
  name: string
  role: string
  permissions: string[]
}

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  checkAuth: () => void
  updateToken: (token: string) => void
}

// Configure axios defaults
axios.defaults.baseURL = '/api'
axios.interceptors.request.use(
  config => {
    const token = useAuthStore.getState().token
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => Promise.reject(error)
)

axios.interceptors.response.use(
  response => {
    // Check for token refresh in headers
    const newToken = response.headers['x-new-access-token']
    if (newToken) {
      useAuthStore.getState().updateToken(newToken)
    }
    return response
  },
  error => {
    if (error.response?.status === 401) {
      useAuthStore.getState().logout()
      toast.error('Session expired. Please login again.')
    }
    return Promise.reject(error)
  }
)

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,

      login: async (email: string, password: string) => {
        set({ isLoading: true })
        try {
          const response = await axios.post('/auth/login', { email, password })
          const { user, access_token } = response.data
          
          set({
            user,
            token: access_token,
            isAuthenticated: true,
            isLoading: false,
          })
          
          toast.success(`Welcome back, ${user.name}!`)
        } catch (error: any) {
          set({ isLoading: false })
          toast.error(error.response?.data?.detail || 'Login failed')
          throw error
        }
      },

      logout: () => {
        set({
          user: null,
          token: null,
          isAuthenticated: false,
        })
        window.location.href = '/login'
      },

      checkAuth: () => {
        const state = get()
        if (state.token && !state.isAuthenticated) {
          set({ isAuthenticated: true })
        }
      },

      updateToken: (token: string) => {
        set({ token })
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ 
        token: state.token,
        user: state.user,
      }),
    }
  )
)
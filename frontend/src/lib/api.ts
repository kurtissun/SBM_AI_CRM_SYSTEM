import axios from 'axios'

// Create axios instance with base configuration
const axiosInstance = axios.create({
  baseURL: '/',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Add request interceptor to include auth token
axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Add response interceptor for error handling
axiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const api = {
  get: async (url: string) => {
    const response = await axiosInstance.get(url)
    return response.data
  },
  
  post: async (url: string, data?: any) => {
    const response = await axiosInstance.post(url, data)
    return response.data
  },
  
  put: async (url: string, data?: any) => {
    const response = await axiosInstance.put(url, data)
    return response.data
  },
  
  delete: async (url: string) => {
    const response = await axiosInstance.delete(url)
    return response.data
  }
}

export default api
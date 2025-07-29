import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 4000,
    host: true, // Listen on all network interfaces 
    strictPort: false, // Try different ports if 4000 is busy
    cors: true, // Enable CORS for VPN compatibility
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
      '/auth': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
        changeOrigin: true,
      },
    },
    hmr: {
      port: 24678, // Different port for HMR to avoid conflicts
    },
  },
  preview: {
    port: 4173,
    host: true,
    cors: true,
  },
})
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
    host: 'localhost', // Explicit localhost binding
    strictPort: true, // Force port 4000 only
    cors: true, // Enable CORS for VPN compatibility
    open: false, // Don't auto-open browser
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
        secure: false,
      },
      '/auth': {
        target: 'http://localhost:8080',
        changeOrigin: true,
        secure: false,
      },
      '/ws': {
        target: 'ws://localhost:8080',
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
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true
  },
  preview: {
    port: 8080,
    host: true,
    allowedHosts: [
      'localhost',
      '127.0.0.1',
      '*.railway.app',
      'aichatbot-production-3c7f.up.railway.app'
    ]
  },
  build: {
    outDir: 'dist',
    sourcemap: true
  }
})

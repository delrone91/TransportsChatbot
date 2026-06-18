import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/auth': { target: 'http://127.0.0.1:5001', changeOrigin: true, timeout: 90000 },
      '/chat': { target: 'http://127.0.0.1:5001', changeOrigin: true, timeout: 90000 },
      '/sessions': { target: 'http://127.0.0.1:5001', changeOrigin: true, timeout: 90000 },
    },
  },
})

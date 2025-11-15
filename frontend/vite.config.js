import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,     // allows Railway to bind to 0.0.0.0
    port: 5173,     // default dev port (Railway will override for prod)
  },
  preview: {
    host: true,
    port: 4173,     // preview server (Railway uses this for production)
  }
})

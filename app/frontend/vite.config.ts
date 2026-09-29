import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// En desarrollo, /api/* se redirige al backend FastAPI (sin CORS).
// En producción el frontend llama directo a VITE_API_URL (ver src/api/client.ts).
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    strictPort: true,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})

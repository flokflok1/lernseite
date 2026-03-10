import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],

  resolve: {
    alias: {
      '@': fileURLToPath(new URL('../src', import.meta.url))
    }
  },

  server: {
    port: 5173,
    host: '0.0.0.0',

    // Proxy API requests to backend
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false,
        ws: true, // WebSocket support
        configure: (proxy, _options) => {
          proxy.on('error', (err, _req, _res) => {
            console.log('[Vite Proxy] Error:', err.message)
          })
          proxy.on('proxyReq', (proxyReq, req, _res) => {
            console.log('[Vite Proxy] Request:', req.method, req.url, '→', proxyReq.path)
            // Disable gzip for SSE — compression buffers the stream
            if (req.headers.accept?.includes('text/event-stream')) {
              proxyReq.removeHeader('Accept-Encoding')
            }
          })
          proxy.on('proxyRes', (proxyRes, req, res) => {
            console.log('[Vite Proxy] Response:', req.method, req.url, '→', proxyRes.statusCode)
            // Flush SSE events immediately instead of buffering
            if (proxyRes.headers['content-type']?.includes('text/event-stream')) {
              proxyRes.on('data', () => {
                if (typeof (res as any).flushHeaders === 'function') {
                  (res as any).flushHeaders()
                }
              })
            }
          })
        }
      },

      // Proxy health check endpoint
      '/health': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false
      },

      // Proxy setup wizard endpoint
      '/setup': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false
      },

      // Proxy Socket.IO for real-time features
      '/socket.io': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        ws: true
      }
    }
  },

  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          'vue-vendor': ['vue', 'vue-router', 'pinia'],
          'ui-vendor': ['@headlessui/vue']
        }
      }
    }
  }
})

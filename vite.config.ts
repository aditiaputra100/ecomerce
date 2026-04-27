/// <reference types="vitest/config" />

import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const backendPort = Number(env.PORT ?? 8000)
  const frontendPort = Number(env.VITE_PORT ?? 5173)

  return {
    plugins: [react()],
    publicDir: 'resources/public',
    build: {
      outDir: 'dist',
      emptyOutDir: true,
    },
    server: {
      host: true,
      proxy: {
        '/api': {
          target: `http://localhost:${backendPort}`,
          changeOrigin: true,
        },
      },
      port: frontendPort,
    },
    preview: {
      host: true,
      proxy: {
        '/api': {
          target: `http://localhost:${backendPort}`,
          changeOrigin: true,
        },
      },
      port: frontendPort,
    },
    test: {
      environment: 'jsdom',
      globals: true,
      css: true,
      setupFiles: 'test/frontend/setup.ts',
      include: ['resources/src/**/*.test.{ts,tsx}', 'test/frontend/**/*.test.{ts,tsx}'],
    },
  }
})

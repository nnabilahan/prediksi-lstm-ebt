import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const defaultAllowedHosts = ['localhost', '127.0.0.1', '.loca.lt', '.localtunnel.me']
  const allowedHosts = (env.VITE_ALLOWED_HOSTS || defaultAllowedHosts.join(','))
    .split(',')
    .map((host) => host.trim())
    .filter(Boolean)

  return {
    plugins: [react()],
    server: {
      host: '0.0.0.0',
      port: 5173,
      allowedHosts,
    },
    preview: {
      host: '0.0.0.0',
      port: 4173,
    },
  }
})

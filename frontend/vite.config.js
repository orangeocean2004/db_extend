import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
    plugins: [vue()],
    server: {
        port: 5173,
        proxy: {
            '/api': {
                target: 'http://localhost:8000', // 与后端一致，后端已允许 http://localhost:5173
                changeOrigin: true
            }
        }
    }
})
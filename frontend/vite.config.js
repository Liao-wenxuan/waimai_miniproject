import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import basicSsl from '@vitejs/plugin-basic-ssl'
import Components from 'unplugin-vue-components/vite'
import { VantResolver } from '@vant/auto-import-resolver'

export default defineConfig({
  plugins: [
    vue(),
    // 自动生成自签名证书启用 HTTPS
    // 浏览器 Geolocation API 要求安全上下文（HTTPS 或 localhost）
    // Chrome 128+ 对 localhost 的 HTTP 定位也有限制，HTTPS 最稳妥
    basicSsl(),
    Components({
      resolvers: [VantResolver()]
    })
  ],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true
      },
      '/socket.io': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        ws: true
      }
    }
  }
})

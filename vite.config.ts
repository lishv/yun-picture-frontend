import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  //实际使用存在问题
  // server: {
  //   // 拦截所有以 /api 开头的请求
  //   proxy: {
  //     //这里改成你真实的后端端口,仅测试,实际开发还是nginx代理转发
  //     '/api': 'http://localhost:8123'
  //     // changeOrigin: true,              //开启虚拟主机代理,后端以为请求是来自目标服务器自身的
  //     // rewrite: (path) => path.replace(/^\/api/, ''), // 匹配后把 /api 去掉传给后端
  //   },
  // },
  plugins: [vue(), vueDevTools()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
})

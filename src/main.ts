import { createApp } from 'vue'
import { createPinia } from 'pinia'
import Antd from 'ant-design-vue'// 引入 Ant Design Vue 组件库
import 'ant-design-vue/dist/reset.css'// 引入 Ant Design Vue 组件库的样式
import  '@/access.ts'
import App from './App.vue'
import router from './router'



const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(Antd)// 全局注册 Ant Design Vue 组件库

app.mount('#app')



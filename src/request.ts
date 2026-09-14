import axios from 'axios'
import { message } from 'ant-design-vue'

// 区分开发和生产环境
// 本地开发直接打到 localhost:8123，生产环境留空走同源相对路径（由 Nginx 统一反向代理 /api）
const DEV_BASE_URL = 'http://localhost:8123'
const PROD_BASE_URL = ''

// 创建 Axios 实例
const myAxios = axios.create({
  baseURL: import.meta.env.DEV ? DEV_BASE_URL : PROD_BASE_URL,
  timeout: 10000,
  withCredentials: true, // 跨域请求时是否需要使用凭证-token
})
//直接复制得到的代码
// 全局请求拦截器
myAxios.interceptors.request.use(
  function (config) {
    // Do something before request is sent
    return config
  },
  function (error) {
    // Do something with request error
    return Promise.reject(error)
  },
)

// 全局响应拦截器
myAxios.interceptors.response.use(
  function (response) {
    const { data } = response
    // 未登录
    if (data && data.code === 40100) {
      const requestUrl = response.request?.responseURL || response.config?.url || ''
      // 不是获取用户信息的请求，并且用户目前不是已经在用户登录页面，则跳转到登录页面
      if (
        !requestUrl.includes('user/get/login') &&
        !window.location.pathname.includes('/user/login')
      ) {
        message.warning('请先登录')
        window.location.href = `/user/login?redirect=${encodeURIComponent(window.location.href)}`
      }
    }
    return response
  },
  function (error) {
    // Any status codes that falls outside the range of 2xx cause this function to trigger
    // Do something with response error
    return Promise.reject(error)
  },
)

// 导出 Axios 实例
export default myAxios

import router from '@/router'
import { userLoginUsingPost } from '@/api/userController.ts'
import { useLoginUserStore } from '@/stores/useLoginUserStore.ts'
import { message } from 'ant-design-vue'

//是否为首次全局校验登录用户信息,避免重复获取
let firstFetchLoginUser = true
/**
 * 全局权限校验,每次页面切换时都会校验用户权限
 * @param to 目标路由
 * @param from 来源路由
 * @param next 继续路由函数
 */
router.beforeEach(async (to, from, next) => {
  const loginUserStore = useLoginUserStore()
  let loginUser = loginUserStore.loginUser
  // 确保页面首次加载时,能等待后端返回用户信息后再次校验
  if (firstFetchLoginUser) {
    try {
      await loginUserStore.fetchLoginUser()
    } catch (e) {
      console.error('获取登录用户信息失败:', e)
    }
    loginUser = loginUserStore.loginUser
    firstFetchLoginUser = false
  }
  // 自定义校验规则,如进入管理员可以访问/admin开头页面
  const toUrl = to.fullPath // 获取当前页面路由的路径
  if (toUrl.startsWith('/admin')) {
    if (!loginUser || loginUser.userRole !== 'admin') {
      message.error('您没有权限访问该页面')
      next({ path: `/user/login?redirect=${encodeURIComponent(to.fullPath)}` })
      return
    }
  }
  next()
})

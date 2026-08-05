import { ref, computed, type Ref } from 'vue'
import { defineStore } from 'pinia'
import { getLoginUserUsingGet } from '@/api/userController.ts'
//定义一个状态存储用户登录用户信息的状态
export const useLoginUserStore = defineStore('counter', () => {
  // 定义一个响应式数据 loginUser，初始值为 未登录,响应式数据即动态响应数据
  const loginUser: Ref<any, any> = ref<API.LoginUserVo>({
    userName: '未登录',
  })
  /**
   * 设置登录用户set
   */
  function setLoginUser(newLoginUser: any) {
    loginUser.value = newLoginUser
  }

  /**
   * 获取登录用户get
   */
  async function fetchLoginUser() {
    const res = await getLoginUserUsingGet()
    if (res.data.code === 0 && res.data.data) {
      loginUser.value = res.data.data
    }


    // const res=await getCurrentUser();
    // if(res.data.code===0&&res.data.data){
    //   loginUser.value=res.data.data
    // }
    // setTimeout(() => {
    //   loginUser.value={
    //     userName:'测试用户',
    //     id: 1 }},
    //   3000)
  }

  // 返回响应式数据 count、计算属性 doubleCount、方法 increment
  return { loginUser, setLoginUser, fetchLoginUser }
})

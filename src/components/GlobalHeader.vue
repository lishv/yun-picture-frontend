<template>
  <div id="globalHeader">
    <a-row :wrap="false">
      <a-col flex="250px">
        <router-link to="/">
          <div class="title-bar">
            <img class="logo" src="../assets/logo.svg" alt="logo" />
            <div class="title">绘灵云图片助手</div>
          </div>
        </router-link>
      </a-col>
      <a-col flex="auto">
        <a-menu
          v-model:selectedKeys="current"
          mode="horizontal"
          :items="items"
          @click="doMenuClick"
        />
      </a-col>
      <a-col flex="200px">
        <div class="user-login-status">
          <div v-if="loginUserStore.loginUser.id">
            <a-dropdown>
              <a-space>
                <a-avatar
                  v-if="loginUserStore.loginUser.userAvatar"
                  :src="loginUserStore.loginUser.userAvatar"
                />
                <a-avatar v-else>{{
                  (loginUserStore.loginUser.userName ?? '无名').slice(0, 2)
                }}</a-avatar>
                {{ displayUserName }}
              </a-space>
              <template #overlay>
                <a-menu>
                  <a-menu-item>
                    <router-link to="/my_space">
                      <UserOutlined />
                      我的空间
                    </router-link>
                  </a-menu-item>
                  <a-menu-item @click="openProfileModal('profile')">
                    <SettingOutlined />
                    个人设置
                  </a-menu-item>
                  <a-menu-item @click="openProfileModal('password')">
                    <KeyOutlined />
                    修改密码
                  </a-menu-item>
                  <a-menu-divider />
                  <a-menu-item @click="doLogout">
                    <LogoutOutlined />
                    退出登录
                  </a-menu-item>
                </a-menu>
              </template>
            </a-dropdown>
          </div>
          <div v-else>
            <a-button type="primary" href="/user/login">登录</a-button>
          </div>
        </div>
      </a-col>
    </a-row>
    <!-- 个人设置 / 修改密码 弹窗 -->
    <UserProfileModal ref="userProfileModalRef" />
  </div>
</template>

<script lang="ts" setup>
import { h, ref, computed } from 'vue'
import {
  HomeOutlined,
  LogoutOutlined,
  UserOutlined,
  SettingOutlined,
  KeyOutlined,
} from '@ant-design/icons-vue'
import { type MenuProps, message } from 'ant-design-vue'
import { useRouter } from 'vue-router'
import { useLoginUserStore } from '@/stores/useLoginUserStore.ts'
import { userLogoutUsingPost } from '@/api/userController.ts'
import UserProfileModal from '@/components/UserProfileModal.vue'

const userProfileModalRef = ref<InstanceType<typeof UserProfileModal>>()

const openProfileModal = (tab: 'profile' | 'password') => {
  userProfileModalRef.value?.openModal(tab)
}
const displayUserName = computed(() => {
  const name = loginUserStore.loginUser.userName ?? '无名'
  return name.length > 15 ? name.slice(0, 15) + '...' : name
})

const loginUserStore = useLoginUserStore() //重命名useLoginUserStore为loginUserStore
console.log(loginUserStore.loginUser)
//未经过滤的原始菜单
const orginItems = ref<MenuProps['items']>([
  {
    key: '/',
    icon: () => h(HomeOutlined),
    label: '主页',
    title: '主页',
  },
  {
    key: '/add_picture',
    label: '创建图片',
    title: '创建图片',
  },

  {
    key: '/admin/pictureManage',
    label: '图片管理',
    title: '图片管理',
  },
  {
    key: '/admin/userManage',
    label: '用户管理',
    title: '用户管理',
  },
  {
    key: '/admin/spaceManage',
    label: '空间管理',
    title: '空间管理',
  },
  // {
  //   key: '/about',
  //   label: '关于',
  //   title: '关于',
  // },
  {
    key: 'others',
    label: h('a', { href: 'https://github.com/lishv', target: '_blank' }, '关于'),
    title: '关于',
  },
])
//过滤后的 展示在路由菜单的数组
const items = computed(() => filterMenus(orginItems.value))
//过滤菜单项,根据用户角色显示不同的菜单
const filterMenus = (menus = [] as MenuProps['items']) => {
  return menus?.filter((menu) => {
    //管理员才能看到/admin开头的菜单
    if (menu?.key?.startsWith('/admin')) {
      const loginUser = loginUserStore.loginUser
      if (!loginUser || loginUser.userRole !== 'admin') return false
    }
    return true
  })
}
const router = useRouter()

//路由跳转事件
const doMenuClick = ({ key }) => router.push({ path: key })

const current = ref<string[]>([])
//钩子函数,路由跳转后更新当前选中项
router.afterEach((to, from, next) => {
  current.value = [to.path]
})
//用户注销
const doLogout = async () => {
  const res = await userLogoutUsingPost()
  if (res.data.code === 0) {
    loginUserStore.setLoginUser({
      userName: '未登录',
    })
    message.success('退出登录成功')
    router.push({ path: '/user/login' })
  } else {
    message.error('退出登录失败' + res.data.message)
  }
}
</script>

<style scoped>
#globalHeader .title-bar {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.title {
  color: rgba(255, 255, 255, 0.92);
  font-size: 18px;
  font-weight: 600;
  margin-left: 16px;
  letter-spacing: 0.5px;
}

.logo {
  height: 42px;
}

#globalHeader :deep(.ant-menu) {
  background: transparent !important;
  border-bottom: none !important;
  font-size: 15px;
}

#globalHeader :deep(.ant-menu-item) {
  color: rgba(255, 255, 255, 0.72) !important;
  transition: all 0.2s ease;
}

#globalHeader :deep(.ant-menu-item:hover) {
  color: #93c5fd !important;
}

#globalHeader :deep(.ant-menu-item-selected) {
  color: #ffffff !important;
  font-weight: 500;
}

#globalHeader :deep(.ant-menu-item-selected .anticon) {
  color: #60a5fa !important;
}

.user-login-status {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  color: rgba(255, 255, 255, 0.85);
}

.user-login-status :deep(.ant-space) {
  cursor: pointer;
  color: rgba(255, 255, 255, 0.85);
}
</style>

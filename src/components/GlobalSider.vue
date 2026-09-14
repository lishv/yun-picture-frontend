<template>
  <a-layout-sider
    v-if="loginUserStore.loginUser.id"
    id="globalSider"
    v-model:collapsed="collapsed"
    collapsible
    :width="200"
    :collapsed-width="64"
    breakpoint="lg"
    class="sider"
  >
    <a-menu
      v-model:selectedKeys="current"
      mode="inline"
      :items="menuItems"
      @click="doMenuClick"
    />
    <template #trigger>
      <div class="collapse-trigger-bar">
        <component :is="collapsed ? MenuUnfoldOutlined : MenuFoldOutlined" class="trigger-icon" />
        <span v-if="!collapsed" class="trigger-text">收起侧栏</span>
      </div>
    </template>
  </a-layout-sider>
</template>
<script lang="ts" setup>
import { computed, h, ref, watchEffect } from 'vue'
import {
  FolderOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  PictureOutlined,
  TeamOutlined,
  UserOutlined,
} from '@ant-design/icons-vue'
import { useRouter } from 'vue-router'
import { useLoginUserStore } from '@/stores/useLoginUserStore.ts'
import { SPACE_TYPE_ENUM } from '@/constants/space.ts'
import { listMyTeamSpaceUsingPost } from '@/api/spaceUserController.ts'
import { message } from 'ant-design-vue'

const loginUserStore = useLoginUserStore()

// 侧边栏折叠状态
const collapsed = ref(false)

// 固定的菜单列表
const fixedMenuItems = [
  {
    key: '/',
    icon: () => h(PictureOutlined),
    label: '公共图库',
  },
  {
    key: '/my_space',
    label: '我的空间',
    icon: () => h(UserOutlined),
  },
  {
    key: '/add_space?type=' + SPACE_TYPE_ENUM.TEAM,
    label: '创建团队',
    icon: () => h(TeamOutlined),
  },
]

const teamSpaceList = ref<API.SpaceUserVO[]>([])
const menuItems = computed(() => {
  // 如果用户没有团队空间，则只展示固定菜单
  if (teamSpaceList.value.length < 1) {
    return fixedMenuItems
  }
  // 如果用户有团队空间，则展示固定菜单和团队空间菜单
  // 展示团队空间分组
  const teamSpaceSubMenus = teamSpaceList.value.map((spaceUser) => {
    const space = spaceUser.space
    return {
      key: '/space/' + spaceUser.spaceId,
      label: space?.spaceName,
      icon: () => h(FolderOutlined),
    }
  })
  const teamSpaceMenuGroup = {
    type: 'group',
    label: '我的团队',
    key: 'teamSpace',
    children: teamSpaceSubMenus,
  }
  return [...fixedMenuItems, teamSpaceMenuGroup]
})

// 加载团队空间列表
const fetchTeamSpaceList = async () => {
  const res = await listMyTeamSpaceUsingPost()
  if (res.data.code === 0 && res.data.data) {
    teamSpaceList.value = res.data.data
  } else {
    message.error('加载我的团队空间失败，' + res.data.message)
  }
}

/**
 * 监听变量，改变时触发数据的重新加载
 */
watchEffect(() => {
  // 登录才加载
  if (loginUserStore.loginUser.id) {
    fetchTeamSpaceList()
  }
})

const router = useRouter()
// 当前要高亮的菜单项
const current = ref<string[]>([router.currentRoute.value.fullPath, router.currentRoute.value.path])
// 监听路由变化，更新高亮菜单项
router.afterEach((to) => {
  current.value = [to.fullPath, to.path]
})

// 路由跳转事件
const doMenuClick = ({ key }: { key: string }) => {
  // 忽略非路由路径（如分组标题 teamSpace）
  if (!key || !key.startsWith('/')) {
    return
  }
  router.push(key)
}
</script>

<style scoped>
#globalSider {
  position: sticky;
  top: 64px;
  height: calc(100vh - 64px);
  align-self: flex-start;
  z-index: 90;
  background: linear-gradient(180deg, #242632 0%, #1b1d25 50%, #15161d 100%);
  border-right: 1px solid rgba(255, 255, 255, 0.07);
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.25);
  transition: width 0.25s ease, min-width 0.25s ease, max-width 0.25s ease;
}

#globalSider :deep(.ant-layout-sider-children) {
  display: flex;
  flex-direction: column;
  height: calc(100% - 44px);
  overflow-y: auto;
  overflow-x: hidden;
}

/* 优雅暗色微滚动条 */
#globalSider :deep(.ant-layout-sider-children)::-webkit-scrollbar {
  width: 4px;
}

#globalSider :deep(.ant-layout-sider-children)::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.14);
  border-radius: 2px;
}

#globalSider :deep(.ant-layout-sider-children)::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.28);
}

#globalSider :deep(.ant-menu) {
  background: transparent !important;
  border-inline-end: none !important;
  padding: 8px 6px 0;
}

#globalSider :deep(.ant-menu-item) {
  border-radius: 8px;
  margin-bottom: 4px;
  color: rgba(255, 255, 255, 0.78);
  transition: all 0.2s ease;
}

#globalSider :deep(.ant-menu-item:hover) {
  color: #93c5fd !important;
  background: rgba(255, 255, 255, 0.06) !important;
}

#globalSider :deep(.ant-menu-item-selected) {
  background: rgba(59, 130, 246, 0.16) !important;
  border: 1px solid rgba(59, 130, 246, 0.3) !important;
  color: #93c5fd !important;
  font-weight: 500;
  box-shadow: 0 0 10px rgba(37, 99, 235, 0.2);
}

#globalSider :deep(.ant-menu-item-selected .anticon) {
  color: #60a5fa !important;
}

/* 分组标题（如“我的团队”）清晰优雅 */
#globalSider :deep(.ant-menu-item-group-title) {
  color: rgba(255, 255, 255, 0.52) !important;
  font-size: 13px !important;
  font-weight: 600 !important;
  letter-spacing: 0.5px;
  padding-left: 14px;
}

#globalSider :deep(.ant-layout-sider-trigger) {
  position: absolute !important;
  bottom: 0 !important;
  left: 0 !important;
  right: 0 !important;
  width: 100% !important;
  background: linear-gradient(180deg, #21232d 0%, #181920 100%) !important;
  border-top: 1px solid rgba(255, 255, 255, 0.08) !important;
  border-right: 1px solid rgba(255, 255, 255, 0.07) !important;
  color: rgba(255, 255, 255, 0.75) !important;
  height: 44px !important;
  line-height: 44px !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  transition: all 0.25s ease !important;
  cursor: pointer;
  z-index: 10;
}

#globalSider :deep(.ant-layout-sider-trigger:hover) {
  background: #2a2c38 !important;
  color: #60a5fa !important;
}

.collapse-trigger-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  font-size: 14px;
}

.trigger-icon {
  font-size: 15px;
  transition: transform 0.2s ease;
}

.trigger-text {
  font-size: 13px;
  letter-spacing: 0.5px;
  white-space: nowrap;
}
</style>

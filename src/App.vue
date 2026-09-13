<template>
  <a-config-provider :locale="zhCN" :theme="darkThemeConfig">
    <div id="app">
      <BasicLayout />
    </div>
  </a-config-provider>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import zhCN from 'ant-design-vue/es/locale/zh_CN'
import { theme } from 'ant-design-vue'
import BasicLayout from '@/layouts/BasicLayout.vue'

// 灰黑质感主题配置（舒适不刺眼、告别全黑与高反差）
const darkThemeConfig = reactive({
  algorithm: theme.darkAlgorithm,
  token: {
    colorPrimary: '#3b82f6',
    colorPrimaryHover: '#60a5fa',
    colorPrimaryActive: '#2563eb',
    colorBgBase: '#1e1f25',
    colorBgContainer: '#252732',
    colorBgLayout: '#1e1f25',
    colorBgElevated: '#2a2d3b',
    colorBorder: '#383a48',
    colorBorderSecondary: '#2e303d',
    colorText: 'rgba(255, 255, 255, 0.88)',
    colorTextSecondary: 'rgba(255, 255, 255, 0.62)',
    colorTextTertiary: 'rgba(255, 255, 255, 0.42)',
    borderRadius: 6,
  },
  components: {
    Button: {
      borderRadius: 6,
      controlOutline: 'rgba(59, 130, 246, 0.15)',
      defaultBorderColor: '#424555',
      defaultColor: 'rgba(255, 255, 255, 0.88)',
      defaultBg: '#2b2d38',
    },
    Menu: {
      colorItemBg: 'transparent',
      colorSubItemBg: 'transparent',
      colorItemBgSelected: 'rgba(59, 130, 246, 0.14)',
      colorItemTextSelected: '#93c5fd',
    },
    Tabs: {
      colorBorderSecondary: '#323544',
      colorPrimary: '#60a5fa',
    },
    Table: {
      colorBgContainer: '#242631',
      colorBorderSecondary: '#303342',
      colorFillAlter: '#282a36',
    },
  },
})
</script>

<style>
html,
body {
  margin: 0;
  padding: 0;
  background: linear-gradient(180deg, #22242e 0%, #17181f 40%, #121318 100%);
  background-attachment: fixed;
  color: rgba(255, 255, 255, 0.88);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial,
    sans-serif;
  min-height: 100vh;
}

/* 全局按钮边框精致化与层次感优化 */
.ant-btn {
  transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1) !important;
  font-weight: 500 !important;
}

/* 默认按钮（如“重置”）：清晰可见，不过度吸睛 */
.ant-btn-default {
  border: 1px solid #444758 !important;
  background: #2b2d38 !important;
  color: rgba(255, 255, 255, 0.88) !important;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.25) !important;
}

.ant-btn-default:hover,
.ant-btn-default:focus {
  border-color: #60a5fa !important;
  color: #93c5fd !important;
  background: #333644 !important;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.15) !important;
}

/* 普通主要按钮（如表单搜索、创建、提交等）：彻底去除突兀刺眼的纯亮蓝，换用内敛高级的岩青蓝质感 */
.ant-btn-primary:not(.ant-input-search-button) {
  background: linear-gradient(135deg, #2e4365 0%, #20314a 100%) !important;
  border: 1px solid #4a668e !important;
  color: #e5edff !important;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3) !important;
}

.ant-btn-primary:not(.ant-input-search-button):hover,
.ant-btn-primary:not(.ant-input-search-button):focus {
  background: linear-gradient(135deg, #37517c 0%, #263c5d 100%) !important;
  border-color: #60a5fa !important;
  color: #ffffff !important;
  box-shadow: 0 3px 12px rgba(37, 99, 235, 0.25) !important;
}

.ant-btn-primary:not(.ant-input-search-button):active {
  background: #1b2b42 !important;
}

/* 幽灵按钮（如“分析公共图库”、“分析全部空间”）：柔和半透明岩蓝，不刺眼不喧宾夺主 */
.ant-btn-background-ghost.ant-btn-primary {
  background: rgba(46, 67, 101, 0.22) !important;
  border: 1px solid #466085 !important;
  color: #b8d0f5 !important;
  box-shadow: none !important;
}

.ant-btn-background-ghost.ant-btn-primary:hover {
  background: rgba(46, 67, 101, 0.45) !important;
  border-color: #60a5fa !important;
  color: #ffffff !important;
  box-shadow: 0 0 10px rgba(59, 130, 246, 0.2) !important;
}

/* 危险按钮：柔和暗红边框 */
.ant-btn-dangerous.ant-btn-default {
  border: 1px solid rgba(239, 68, 68, 0.38) !important;
  background: rgba(239, 68, 68, 0.08) !important;
  color: #fca5a5 !important;
}

.ant-btn-dangerous.ant-btn-default:hover {
  border-color: #ef4444 !important;
  color: #f87171 !important;
  background: rgba(239, 68, 68, 0.16) !important;
}

/* 侧边栏与头部菜单选中项：柔和深灰微透，不生硬 */
.ant-menu-dark.ant-menu-inline .ant-menu-item-selected,
.ant-menu-inline .ant-menu-item-selected {
  background: rgba(59, 130, 246, 0.14) !important;
  border: 1px solid rgba(59, 130, 246, 0.25) !important;
  border-radius: 8px !important;
  color: #93c5fd !important;
  font-weight: 500 !important;
}

.ant-menu-horizontal > .ant-menu-item-selected::after {
  border-bottom-color: #60a5fa !important;
  border-bottom-width: 3px !important;
}

/* 表格视觉优化：微渐变卡片质感，解决空间管理刺眼高反差问题 */
.ant-table-wrapper .ant-table {
  background: linear-gradient(180deg, #262835 0%, #1f212a 100%) !important;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #333646;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
}

.ant-table-wrapper .ant-table-thead > tr > th {
  background: #2b2e3d !important;
  color: rgba(255, 255, 255, 0.78) !important;
  border-bottom: 1px solid #383c4e !important;
  font-weight: 600 !important;
}

.ant-table-wrapper .ant-table-tbody > tr > td {
  border-bottom: 1px solid #2d303f !important;
  color: rgba(255, 255, 255, 0.85) !important;
}

.ant-table-wrapper .ant-table-tbody > tr:hover > td {
  background: #2c2f3e !important;
}
</style>

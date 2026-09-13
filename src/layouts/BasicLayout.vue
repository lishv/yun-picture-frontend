<template>
  <div id="basicLayout">
    <a-layout style="min-height: 100vh">
      <a-layout-header class="header">
        <GlobalHeader />
      </a-layout-header>

      <a-layout has-sider class="main-layout">
        <GlobalSider class="sider" />
        <a-layout-content class="content">
          <router-view />
        </a-layout-content>
      </a-layout>

      <a-layout-footer class="footer">
        <a href="https://github.com/lishv" target="_blank">绘灵云图片协作平台 by xiaoli </a>
      </a-layout-footer>
    </a-layout>
  </div>
</template>

<script setup lang="ts">
import GlobalHeader from '@/components/GlobalHeader.vue'
import GlobalSider from '@/components/GlobalSider.vue'
</script>

<style scoped>
#basicLayout {
  min-height: 100vh;
  background: linear-gradient(180deg, #22242e 0%, #17181f 40%, #121318 100%);
}

#basicLayout .header {
  padding-inline: 20px;
  background: linear-gradient(180deg, #292c38 0%, #21232d 100%);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 4px 18px rgba(0, 0, 0, 0.35);
  color: rgba(255, 255, 255, 0.92);
  height: 64px;
  line-height: 64px;
  position: sticky;
  top: 0;
  z-index: 100;
}

#basicLayout .main-layout {
  flex: 1;
  background: transparent;
  position: relative;
}

#basicLayout .sider {
  position: sticky;
  top: 64px;
  height: calc(100vh - 64px);
  align-self: flex-start;
  z-index: 90;
  background: linear-gradient(180deg, #232530 0%, #191a22 100%);
  border-right: 1px solid rgba(255, 255, 255, 0.07);
  box-shadow: 2px 0 12px rgba(0, 0, 0, 0.2);
}

#basicLayout :deep(.ant-menu-root) {
  border-bottom: none !important;
  border-inline-end: none !important;
}

#basicLayout .content {
  padding: 24px 30px;
  background: radial-gradient(
      ellipse 90% 40% at 50% -8%,
      rgba(59, 130, 246, 0.12) 0%,
      rgba(35, 41, 58, 0.2) 35%,
      transparent 70%
    ),
    linear-gradient(180deg, rgba(30, 32, 42, 0.75) 0%, rgba(18, 19, 25, 0.95) 100%);
  min-height: calc(100vh - 64px - 56px);
}

#basicLayout .footer {
  background: linear-gradient(180deg, #1d1e26 0%, #14151b 100%);
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  padding: 16px 20px;
  text-align: center;
  color: rgba(255, 255, 255, 0.45);
}

#basicLayout .footer a {
  color: rgba(255, 255, 255, 0.65);
  text-decoration: none;
  transition: color 0.2s ease;
}

#basicLayout .footer a:hover {
  color: #60a5fa;
}
</style>

<template>
  <a-config-provider :locale="zhCN">
    <div id="app">
      <BasicLayout />
    </div>
  </a-config-provider>
</template>

<script setup lang="ts">
import zhCN from 'ant-design-vue/es/locale/zh_CN'
import BasicLayout from '@/layouts/BasicLayout.vue'
import { healthUsingGet } from '@/api/mainController.ts'
//已改为在全局校验access.ts中获取登录用户信息,无需重复获取
// import { useLoginUserStore } from '@/stores/useLoginUserStore.ts'
// const loginUserStore = useLoginUserStore() //重命名useLoginUserStore为loginUserStore
// //获取登录用户信息,存储到loginUserStore.loginUser
// loginUserStore.fetchLoginUser()
// //healthUsingGet().then(res => console.log(res))
</script>

<style scoped></style>

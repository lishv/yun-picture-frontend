<template>
  <div id="app">
    <BasicLayout/>
  </div>

</template>

<script setup lang="ts">
import BasicLayout from '@/layouts/BasicLayout.vue'
import { healthUsingGet } from '@/api/mainController.ts'
import {useLoginUserStore} from "@/stores/useLoginUserStore.ts";
const loginUserStore = useLoginUserStore();//重命名useLoginUserStore为loginUserStore
//获取登录用户信息,存储到loginUserStore.loginUser
loginUserStore.fetchLoginUser();
healthUsingGet().then(res => console.log(res))
</script>

<style scoped>

</style>

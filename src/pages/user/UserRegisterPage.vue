<template>
  <div id="userRegisterPage">
    <h2 class="title">绘灵云图片协作平台</h2>
    <div class="desc">一个免费的图片协作平台,支持用户之间的图片分享和协作</div>

    <a-form
      :model="emailFormState"
      name="emailRegister"
      autocomplete="off"
      @finish="handleEmailRegister"
    >
      <a-form-item
        name="userAccount"
        :rules="[
          { required: true, message: '请输入账号' },
          { min: 4, message: '账号长度不能小于4位' },
        ]"
      >
        <a-input
          v-model:value="emailFormState.userAccount"
          placeholder="请输入账号（不少于4位）"
        >
          <template #prefix><UserOutlined /></template>
        </a-input>
      </a-form-item>

      <a-form-item
        name="email"
        :rules="[
          { required: true, message: '请输入邮箱' },
          { type: 'email', message: '请输入合法的邮箱地址' },
        ]"
      >
        <a-input v-model:value="emailFormState.email" placeholder="请输入邮箱地址">
          <template #prefix><MailOutlined /></template>
        </a-input>
      </a-form-item>

      <a-form-item
        name="code"
        :rules="[
          { required: true, message: '请输入6位数字验证码' },
          { len: 6, message: '验证码为6位数字' },
        ]"
      >
        <div class="code-input-group">
          <a-input
            v-model:value="emailFormState.code"
            placeholder="6位验证码"
            maxlength="6"
          >
            <template #prefix><SafetyCertificateOutlined /></template>
          </a-input>
          <a-button
            class="send-code-btn"
            :disabled="countDown > 0 || sendingCode"
            :loading="sendingCode"
            @click="sendEmailCode"
          >
            {{ countDown > 0 ? `${countDown}s 后重试` : '获取验证码' }}
          </a-button>
        </div>
      </a-form-item>

      <a-form-item
        name="userPassword"
        :rules="[
          { required: true, message: '请输入密码' },
          { min: 8, message: '密码长度不能小于8位' },
        ]"
      >
        <a-input-password
          v-model:value="emailFormState.userPassword"
          placeholder="设置密码（不少于8位）"
        >
          <template #prefix><LockOutlined /></template>
        </a-input-password>
      </a-form-item>

      <a-form-item
        name="checkPassword"
        :rules="[
          { required: true, message: '请确认密码' },
          { min: 8, message: '确认密码长度不能小于8位' },
        ]"
      >
        <a-input-password
          v-model:value="emailFormState.checkPassword"
          placeholder="再次输入密码"
        >
          <template #prefix><LockOutlined /></template>
        </a-input-password>
      </a-form-item>

      <div class="tips">
        已有账号?
        <RouterLink to="/user/login">去登录</RouterLink>
      </div>

      <a-form-item>
        <a-button
          type="primary"
          html-type="submit"
          style="width: 100%"
          :loading="submitting"
        >
          注册
        </a-button>
      </a-form-item>
    </a-form>
  </div>
</template>

<script lang="ts" setup>
import { reactive, ref, onUnmounted } from 'vue'
import {
  emailRegisterUsingPost,
  sendEmailCodeUsingPost,
} from '@/api/userController.ts'
import { message } from 'ant-design-vue'
import {
  UserOutlined,
  LockOutlined,
  MailOutlined,
  SafetyCertificateOutlined,
} from '@ant-design/icons-vue'
import router from '@/router'

// 邮箱注册表单数据
const emailFormState = reactive<API.UserEmailRegisterRequest>({
  userAccount: '',
  email: '',
  code: '',
  userPassword: '',
  checkPassword: '',
})

// 倒计时与发送状态
const countDown = ref(0)
const sendingCode = ref(false)
const submitting = ref(false)
let timer: ReturnType<typeof setInterval> | null = null

// 发送邮箱验证码
const sendEmailCode = async () => {
  const email = emailFormState.email?.trim()
  if (!email) {
    message.warning('请先输入邮箱地址')
    return
  }
  const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
  if (!emailPattern.test(email)) {
    message.warning('请输入有效的邮箱格式')
    return
  }

  sendingCode.value = true
  try {
    const res = await sendEmailCodeUsingPost({
      email,
      biz: 'register',
    })
    if (res.data.code === 0) {
      message.success('验证码已发送至您的邮箱，5分钟内有效')
      countDown.value = 60
      timer = setInterval(() => {
        countDown.value--
        if (countDown.value <= 0) {
          if (timer) clearInterval(timer)
          timer = null
        }
      }, 1000)
    } else {
      message.error('发送验证码失败：' + res.data.message)
    }
  } catch (error: any) {
    message.error('发送验证码异常：' + error.message)
  } finally {
    sendingCode.value = false
  }
}

// 提交邮箱注册
const handleEmailRegister = async () => {
  if (emailFormState.userPassword !== emailFormState.checkPassword) {
    message.error('两次输入密码不一致')
    return
  }
  submitting.value = true
  try {
    const res = await emailRegisterUsingPost(emailFormState)
    if (res.data.code === 0 && res.data.data) {
      message.success('注册成功，请登录')
      router.push({
        path: '/user/login',
        replace: true,
      })
    } else {
      message.error('注册失败：' + res.data.message)
    }
  } catch (error: any) {
    message.error('注册异常：' + error.message)
  } finally {
    submitting.value = false
  }
}

onUnmounted(() => {
  if (timer) {
    clearInterval(timer)
    timer = null
  }
})
</script>

<style scoped>
#userRegisterPage {
  max-width: 380px;
  margin: 0 auto;
}
.title {
  text-align: center;
  margin-bottom: 16px;
}
.desc {
  text-align: center;
  color: #bbb;
  margin-bottom: 24px;
}
.code-input-group {
  display: flex;
  gap: 8px;
}
.send-code-btn {
  flex-shrink: 0;
  min-width: 104px;
}
.tips {
  text-align: right;
  color: #bbb;
  font-size: 13px;
  margin-bottom: 16px;
}
</style>

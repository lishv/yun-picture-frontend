<template>
  <div id="userLoginPage">
    <h2 class="title">绘灵云图片助手</h2>
    <div class="desc">一个免费的图片协作平台,支持用户之间的图片分享和协作</div>
    <a-form :model="formState" name="basic" autocomplete="off" @finish="handleSubmit">
      <a-form-item
        label="用户账号"
        name="userAccount"
        :rules="[{ required: true, message: '请输入账号' }]"
      >
        <a-input v-model:value="formState.userAccount" placeholder="请输入账号" />
      </a-form-item>

      <a-form-item
        label="用户密码"
        name="userPassword"
        :rules="[
          { required: true, message: '请输入密码' },
          { min: 8, message: '密码长度不能小于8位' },
        ]"
      >
        <a-input-password v-model:value="formState.userPassword" placeholder="请输入密码" />
      </a-form-item>

      <div class="tips-row">
        <a class="forget-password-link" @click="openResetModal">忘记密码？</a>
        <div class="register-tips">
          没有账号?
          <RouterLink to="/user/register">去注册</RouterLink>
        </div>
      </div>

      <a-form-item>
        <a-button type="primary" html-type="submit" style="width: 100%" :loading="loginLoading">
          登录
        </a-button>
      </a-form-item>
    </a-form>

    <!-- 邮箱验证码找回密码弹窗 -->
    <a-modal
      v-model:open="resetModalVisible"
      title="找回密码 / 邮箱重置密码"
      :footer="null"
      width="440px"
      destroy-on-close
    >
      <a-form
        layout="vertical"
        :model="resetForm"
        :rules="resetRules"
        autocomplete="off"
        @finish="handleResetPassword"
      >
        <a-form-item label="绑定邮箱" name="email">
          <a-input v-model:value="resetForm.email" placeholder="请输入注册时绑定的邮箱地址">
            <template #prefix><MailOutlined /></template>
          </a-input>
        </a-form-item>

        <a-form-item label="邮箱验证码" name="code">
          <div class="code-input-group">
            <a-input
              v-model:value="resetForm.code"
              placeholder="6位验证码"
              maxlength="6"
            >
              <template #prefix><SafetyCertificateOutlined /></template>
            </a-input>
            <a-button
              class="send-code-btn"
              :disabled="countDown > 0 || sendingCode"
              :loading="sendingCode"
              @click="sendResetCode"
            >
              {{ countDown > 0 ? `${countDown}s 后重试` : '获取验证码' }}
            </a-button>
          </div>
        </a-form-item>

        <a-form-item label="新密码" name="newPassword">
          <a-input-password
            v-model:value="resetForm.newPassword"
            placeholder="设置新密码（不少于 8 位）"
          >
            <template #prefix><LockOutlined /></template>
          </a-input-password>
        </a-form-item>

        <a-form-item label="确认新密码" name="checkPassword">
          <a-input-password
            v-model:value="resetForm.checkPassword"
            placeholder="请再次输入新密码"
          >
            <template #prefix><LockOutlined /></template>
          </a-input-password>
        </a-form-item>

        <a-form-item>
          <a-space style="width: 100%; justify-content: flex-end">
            <a-button @click="resetModalVisible = false">取消</a-button>
            <a-button type="primary" html-type="submit" :loading="resetting">
              确认修改密码
            </a-button>
          </a-space>
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script lang="ts" setup>
import { reactive, ref, onUnmounted } from 'vue'
import {
  userLoginUsingPost,
  sendEmailCodeUsingPost,
  emailResetPasswordUsingPost,
} from '@/api/userController.ts'
import { useLoginUserStore } from '@/stores/useLoginUserStore.ts'
import { message } from 'ant-design-vue'
import {
  MailOutlined,
  SafetyCertificateOutlined,
  LockOutlined,
} from '@ant-design/icons-vue'
import router from '@/router'

// 用于接收用户登录请求参数
const formState = reactive<API.UserLoginRequest>({
  userAccount: '',
  userPassword: '',
})
const loginUserStore = useLoginUserStore()
const loginLoading = ref(false)

// 找回密码弹窗相关状态
const resetModalVisible = ref(false)
const countDown = ref(0)
const sendingCode = ref(false)
const resetting = ref(false)
let timer: ReturnType<typeof setInterval> | null = null

const resetForm = reactive<API.UserEmailResetPasswordRequest>({
  email: '',
  code: '',
  newPassword: '',
  checkPassword: '',
})

// 打开找回密码弹窗
const openResetModal = () => {
  resetForm.email = ''
  resetForm.code = ''
  resetForm.newPassword = ''
  resetForm.checkPassword = ''
  resetModalVisible.value = true
}

// 找回密码校验规则
const resetRules = {
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱格式', trigger: 'blur' },
  ],
  code: [
    { required: true, message: '请输入邮箱验证码', trigger: 'blur' },
    { len: 6, message: '验证码为 6 位数字', trigger: 'blur' },
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 8, message: '新密码不能少于 8 位', trigger: 'blur' },
  ],
  checkPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: async (_rule: any, value: string) => {
        if (!value) {
          return Promise.reject('请确认新密码')
        }
        if (value !== resetForm.newPassword) {
          return Promise.reject('两次输入的新密码不一致')
        }
        return Promise.resolve()
      },
      trigger: 'blur',
    },
  ],
}

// 发送找回密码验证码
const sendResetCode = async () => {
  const email = resetForm.email?.trim()
  if (!email) {
    message.warning('请先输入绑定邮箱地址')
    return
  }
  const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
  if (!emailPattern.test(email)) {
    message.warning('请输入合法的邮箱格式')
    return
  }

  sendingCode.value = true
  try {
    const res = await sendEmailCodeUsingPost({
      email,
      biz: 'reset_password',
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

// 提交重置密码
const handleResetPassword = async () => {
  if (resetForm.newPassword !== resetForm.checkPassword) {
    message.error('两次输入的新密码不一致')
    return
  }
  resetting.value = true
  try {
    const res = await emailResetPasswordUsingPost(resetForm)
    if (res.data.code === 0) {
      message.success('密码重置成功，请使用新密码登录')
      resetModalVisible.value = false
    } else {
      message.error('重置密码失败：' + res.data.message)
    }
  } catch (error: any) {
    message.error('重置密码异常：' + error.message)
  } finally {
    resetting.value = false
  }
}

// 登录提交
const handleSubmit = async (values: any) => {
  loginLoading.value = true
  try {
    const res = await userLoginUsingPost(values)
    if (res.data.code === 0 && res.data.data) {
      await loginUserStore.fetchLoginUser()
      message.success('登录成功')
      router.push({
        path: '/',
        replace: true,
      })
    } else {
      message.error('登录失败：' + res.data.message)
    }
  } catch (error: any) {
    message.error('登录异常：' + error.message)
  } finally {
    loginLoading.value = false
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
#userLoginPage {
  max-width: 360px;
  margin: 0 auto;
}
.title {
  text-align: center;
  margin-bottom: 16px;
}
.desc {
  text-align: center;
  color: #bbb;
  margin-bottom: 16px;
}
.tips-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  font-size: 13px;
}
.forget-password-link {
  color: #1890ff;
  cursor: pointer;
}
.forget-password-link:hover {
  text-decoration: underline;
}
.register-tips {
  color: #bbb;
}
.code-input-group {
  display: flex;
  gap: 8px;
}
.send-code-btn {
  flex-shrink: 0;
  min-width: 104px;
}
</style>

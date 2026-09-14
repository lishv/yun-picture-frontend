<template>
  <a-modal
    v-model:open="visible"
    :title="activeKey === 'password' ? '修改密码' : '个人设置'"
    :footer="null"
    width="520px"
    destroy-on-close
  >
    <a-tabs v-model:activeKey="activeKey">
      <!-- 修改个人资料 & 头像 -->
      <a-tab-pane key="profile" tab="个人信息">
        <a-form layout="vertical" :model="profileForm" @finish="handleUpdateProfile">
          <!-- 头像设置与预览 -->
          <a-form-item label="用户头像">
            <div class="avatar-edit-wrapper">
              <a-avatar
                :size="72"
                :src="profileForm.userAvatar"
                class="avatar-preview"
              >
                {{ (profileForm.userName || '用户').slice(0, 2) }}
              </a-avatar>
              <div class="avatar-input-group">
                <a-input
                  v-model:value="profileForm.userAvatar"
                  placeholder="请输入或粘贴头像图片 URL 地址"
                  allow-clear
                />
                <div class="avatar-upload-action">
                  <a-upload
                    :show-upload-list="false"
                    :custom-request="handleUploadAvatar"
                    :before-upload="beforeAvatarUpload"
                  >
                    <a-button size="small" :loading="uploadingAvatar">
                      <template #icon><UploadOutlined /></template>
                      上传本地头像
                    </a-button>
                  </a-upload>
                  <span class="tip-text">支持 jpg / png 格式，不超过 5MB</span>
                </div>
              </div>
            </div>
          </a-form-item>

          <a-form-item label="用户 ID">
            <a-input
              :value="loginUserStore.loginUser.id ? String(loginUserStore.loginUser.id) : ''"
              readonly
              placeholder="暂无用户 ID"
            >
              <template #addonAfter>
                <a-tooltip title="点击复制用户 ID">
                  <span class="copy-btn" @click="copyUserId">
                    <CopyOutlined />
                    <span>复制</span>
                  </span>
                </a-tooltip>
              </template>
            </a-input>
          </a-form-item>

          <a-form-item label="用户账号">
            <a-input :value="loginUserStore.loginUser.userAccount" disabled />
          </a-form-item>

          <a-form-item
            label="用户昵称"
            name="userName"
            :rules="[{ required: true, message: '请输入用户昵称' }]"
          >
            <a-input
              v-model:value="profileForm.userName"
              placeholder="请输入昵称"
              maxlength="30"
              show-count
            />
          </a-form-item>

          <a-form-item label="用户简介" name="userProfile">
            <a-textarea
              v-model:value="profileForm.userProfile"
              placeholder="介绍一下自己吧"
              :rows="3"
              maxlength="200"
              show-count
            />
          </a-form-item>

          <a-form-item>
            <a-space style="width: 100%; justify-content: flex-end">
              <a-button @click="visible = false">取消</a-button>
              <a-button type="primary" html-type="submit" :loading="savingProfile">
                保存资料
              </a-button>
            </a-space>
          </a-form-item>
        </a-form>
      </a-tab-pane>

      <!-- 修改密码 -->
      <a-tab-pane key="password" tab="修改密码">
        <a-form
          layout="vertical"
          :model="passwordForm"
          :rules="passwordRules"
          @finish="handleChangePassword"
        >
          <a-form-item label="原密码" name="oldPassword">
            <a-input-password
              v-model:value="passwordForm.oldPassword"
              placeholder="请输入当前的原密码"
            />
          </a-form-item>

          <a-form-item label="新密码" name="newPassword">
            <a-input-password
              v-model:value="passwordForm.newPassword"
              placeholder="请输入新密码（不少于 8 位）"
            />
          </a-form-item>

          <a-form-item label="确认新密码" name="checkPassword">
            <a-input-password
              v-model:value="passwordForm.checkPassword"
              placeholder="请再次输入新密码"
            />
          </a-form-item>

          <a-form-item>
            <a-space style="width: 100%; justify-content: flex-end">
              <a-button @click="visible = false">取消</a-button>
              <a-button type="primary" html-type="submit" :loading="savingPassword">
                确认修改
              </a-button>
            </a-space>
          </a-form-item>
        </a-form>
      </a-tab-pane>
    </a-tabs>
  </a-modal>
</template>

<script lang="ts" setup>
import { reactive, ref } from 'vue'
import { message } from 'ant-design-vue'
import type { UploadProps } from 'ant-design-vue'
import { CopyOutlined, UploadOutlined } from '@ant-design/icons-vue'
import { useLoginUserStore } from '@/stores/useLoginUserStore.ts'
import {
  changePasswordUsingPost,
  editUserUsingPost,
  uploadUserAvatarUsingPost,
} from '@/api/userController.ts'

const loginUserStore = useLoginUserStore()
const visible = ref(false)
const activeKey = ref('profile')

// 复制用户 ID
const copyUserId = async () => {
  const userId = loginUserStore.loginUser.id
  if (!userId) {
    message.warning('未获取到用户 ID')
    return
  }
  const text = String(userId)
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text)
    } else {
      // 兼容非 HTTPS 环境（如通过 IP 访问）
      const textArea = document.createElement('textarea')
      textArea.value = text
      textArea.style.position = 'fixed'
      textArea.style.opacity = '0'
      textArea.style.left = '-9999px'
      document.body.appendChild(textArea)
      textArea.focus()
      textArea.select()
      document.execCommand('copy')
      document.body.removeChild(textArea)
    }
    message.success('用户 ID 已复制到剪贴板')
  } catch (err) {
    message.error('复制失败，请手动选中文本复制')
  }
}

// 个人资料表单
const profileForm = reactive<API.UserEditRequest>({
  userName: '',
  userAvatar: '',
  userProfile: '',
})

// 密码表单
const passwordForm = reactive<API.UserChangePasswordRequest>({
  oldPassword: '',
  newPassword: '',
  checkPassword: '',
})

const savingProfile = ref(false)
const savingPassword = ref(false)
const uploadingAvatar = ref(false)

// 打开弹窗并根据传入的 tab 显示对应页面
const openModal = (tab: 'profile' | 'password' = 'profile') => {
  activeKey.value = tab
  const curUser = loginUserStore.loginUser
  profileForm.userName = curUser.userName || ''
  profileForm.userAvatar = curUser.userAvatar || ''
  profileForm.userProfile = curUser.userProfile || ''
  passwordForm.oldPassword = ''
  passwordForm.newPassword = ''
  passwordForm.checkPassword = ''
  visible.value = true
}

defineExpose({
  openModal,
})

// 头像上传前校验
const beforeAvatarUpload = (file: any) => {
  const isJpgOrPng = file.type === 'image/jpeg' || file.type === 'image/png' || file.type === 'image/webp'
  if (!isJpgOrPng) {
    message.error('只支持上传 JPG/PNG/WEBP 格式的图片！')
    return false
  }
  const isLt5M = file.size / 1024 / 1024 < 5
  if (!isLt5M) {
    message.error('头像大小不能超过 5MB！')
    return false
  }
  return true
}

// 执行头像上传（独立存储到 avatar/ 专属目录）
const handleUploadAvatar = async ({ file }: any) => {
  uploadingAvatar.value = true
  try {
    const res = await uploadUserAvatarUsingPost(file)
    if (res.data.code === 0 && res.data.data) {
      profileForm.userAvatar = res.data.data
      message.success('头像上传成功')
    } else {
      message.error('头像上传失败：' + (res.data.message || '未知错误'))
    }
  } catch (error: any) {
    message.error('头像上传异常：' + error.message)
  } finally {
    uploadingAvatar.value = false
  }
}

// 提交个人资料与头像修改
const handleUpdateProfile = async () => {
  savingProfile.value = true
  try {
    const res = await editUserUsingPost(profileForm)
    if (res.data.code === 0) {
      message.success('个人资料更新成功')
      // 重新获取登录用户信息，刷新前端全局状态
      await loginUserStore.fetchLoginUser()
      visible.value = false
    } else {
      message.error('修改失败：' + res.data.message)
    }
  } catch (error: any) {
    message.error('修改失败：' + error.message)
  } finally {
    savingProfile.value = false
  }
}

// 密码校验规则
const passwordRules = {
  oldPassword: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 8, message: '新密码不能少于 8 位', trigger: 'blur' },
  ],
  checkPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: async (_rule: any, value: string) => {
        if (!value) {
          return Promise.reject('请再次输入新密码')
        }
        if (value !== passwordForm.newPassword) {
          return Promise.reject('两次输入的新密码不一致')
        }
        return Promise.resolve()
      },
      trigger: 'blur',
    },
  ],
}

// 提交密码修改
const handleChangePassword = async () => {
  if (passwordForm.newPassword === passwordForm.oldPassword) {
    message.warning('新密码不能与原密码相同')
    return
  }
  savingPassword.value = true
  try {
    const res = await changePasswordUsingPost(passwordForm)
    if (res.data.code === 0) {
      message.success('密码修改成功，请妥善保管新密码')
      visible.value = false
    } else {
      message.error('密码修改失败：' + res.data.message)
    }
  } catch (error: any) {
    message.error('密码修改失败：' + error.message)
  } finally {
    savingPassword.value = false
  }
}
</script>

<style scoped>
.avatar-edit-wrapper {
  display: flex;
  align-items: center;
  gap: 16px;
}

.avatar-preview {
  flex-shrink: 0;
  border: 1px solid #e8e8e8;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.avatar-input-group {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.avatar-upload-action {
  display: flex;
  align-items: center;
  gap: 10px;
}

.tip-text {
  font-size: 12px;
  color: #8c8c8c;
}

.copy-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  color: #1890ff;
  user-select: none;
  font-size: 13px;
  transition: color 0.2s;
}

.copy-btn:hover {
  color: #40a9ff;
}
</style>

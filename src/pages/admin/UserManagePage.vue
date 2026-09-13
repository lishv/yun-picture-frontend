<template>
  <div id="userManagePage">
    <!-- 搜索表单-->
    <a-form layout="inline" :model="searchParams" @finish="doSearch">
      <a-form-item label="账号">
        <a-input v-model:value="searchParams.userAccount" placeholder="输入账号" allow-clear />
      </a-form-item>
      <a-form-item label="用户名">
        <a-input v-model:value="searchParams.userName" placeholder="输入用户名" allow-clear />
      </a-form-item>
      <a-form-item label="邮箱">
        <a-input v-model:value="searchParams.email" placeholder="输入邮箱" allow-clear />
      </a-form-item>
      <a-form-item>
        <a-button type="primary" html-type="submit">搜索</a-button>
      </a-form-item>
    </a-form>
    <div style="margin-bottom: 16px" />
    <!-- 用户列表表格 -->
    <a-table
      :columns="columns"
      :data-source="dataList"
      :pagination="pagination"
      @change="doTableChange"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.dataIndex === 'userAvatar'">
          <a-image :src="record.userAvatar" width="64px" :preview-src-list="[record.userAvatar]" />
        </template>
        <template v-else-if="column.dataIndex === 'userName'">
          <a-tooltip :title="record.userName">
            <span>{{ getDisplayName(record.userName) }}</span>
          </a-tooltip>
        </template>
        <template v-else-if="column.dataIndex === 'email'">
          <span v-if="record.email">{{ record.email }}</span>
          <span v-else style="color: #bbb">未绑定</span>
        </template>
        <template v-else-if="column.dataIndex === 'userRole'">
          <div v-if="record.userRole === 'admin'">
            <a-tag color="red">管理员</a-tag>
          </div>
          <div v-else>
            <a-tag color="blue">普通用户</a-tag>
          </div>
        </template>
        <template v-else-if="column.dataIndex === 'createTime'">
          {{ dayjs(record.createTime).format('YYYY-MM-DD HH:mm:ss') }}
        </template>

        <template v-else-if="column.key === 'action'">
          <a-space wrap>
            <a-popconfirm
              title="确定将该用户的密码重置为默认密码（12345678）吗？"
              ok-text="确定"
              cancel-text="取消"
              @confirm="doResetPassword(record.id)"
            >
              <a-button type="link">重置密码</a-button>
            </a-popconfirm>
            <a-popconfirm
              title="确定要删除该用户吗？"
              ok-text="确定"
              cancel-text="取消"
              @confirm="doDelete(record.id)"
            >
              <a-button danger type="link">删除</a-button>
            </a-popconfirm>
          </a-space>
        </template>
      </template>
    </a-table>
  </div>
</template>
<script lang="ts" setup>
import { computed, onMounted, reactive, ref } from 'vue'
import {
  deleteUserUsingPost,
  listUserVoByPageUsingPost,
  resetUserPasswordUsingPost,
} from '@/api/userController.ts'
import { message } from 'ant-design-vue'
import dayjs from 'dayjs'
const columns = [
  {
    title: 'id',
    dataIndex: 'id',
  },
  {
    title: '账号',
    dataIndex: 'userAccount',
  },
  {
    title: '用户名',
    dataIndex: 'userName',
  },
  {
    title: '邮箱',
    dataIndex: 'email',
  },
  {
    title: '头像',
    dataIndex: 'userAvatar',
  },
  {
    title: '简介',
    dataIndex: 'userProfile',
  },
  {
    title: '用户角色',
    dataIndex: 'userRole',
  },
  {
    title: '创建时间',
    dataIndex: 'createTime',
  },

  {
    title: '操作',
    key: 'action',
  },
]
const dataList = ref<API.UserVO[]>([])
const total = ref(0)

//搜索条件
const searchParams = reactive<API.UserQueryRequest>({
  current: 1,
  pageSize: 10,
  sortField: 'createTime',
  sortOrder: 'ascend',
})
//分页配置,表格的自带属性
const pagination = computed(() => {
  return {
    current: searchParams.current,
    pageSize: searchParams.pageSize,
    total: total.value,
    showSizeChanger: true,
    showTotal: (total) => `共 ${total} 条`,
  }
})
const doSearch = () => {
  //搜索时,重置分页为第一页
  searchParams.current = 1
  fetchData()
}
const doTableChange = (page: any) => {
  searchParams.current = page.current
  searchParams.pageSize = page.pageSize
  fetchData()
}
//获取数据
const fetchData = async () => {
  const res = await listUserVoByPageUsingPost(searchParams)
  if (res.data.code === 0 && res.data.data) {
    dataList.value = res.data.data.records ?? []
    total.value = res.data.data.total ?? 0
  } else {
    message.error('获取数据失败' + res.data.message)
  }
}

const getDisplayName = (name: string | undefined) => {
  if (!name) return '无名'
  return name.length > 15 ? name.slice(0, 15) + '...' : name
}
const doDelete = async (id: string) => {
  if (!id) return
  const res = await deleteUserUsingPost({ id })
  if (res.data.code === 0) {
    message.success('删除成功')
    fetchData()
  } else {
    message.error('删除失败' + res.data.message)
  }
}

const doResetPassword = async (id: any) => {
  if (!id) return
  const res = await resetUserPasswordUsingPost({ id })
  if (res.data.code === 0) {
    message.success('重置密码成功，默认密码为：12345678')
  } else {
    message.error('重置密码失败，' + res.data.message)
  }
}
//页面加载时获取数据
onMounted(() => {
  fetchData()
})
</script>

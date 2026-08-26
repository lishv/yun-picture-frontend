<template>
  <div id="addPictureBatchPage">
    <h2 style="margin-bottom: 16px">批量创建</h2>
    <!-- 图片信息表单 -->
    <a-form name="formData" layout="vertical" :model="formData" @finish="handleSubmit">
      <a-form-item name="searchText" label="关键词">
        <a-input v-model:value="formData.searchText" placeholder="请输入关键词" allow-clear />
      </a-form-item>
      <a-form-item >
        <a-space align="start">
          <a-form-item name="count" label="抓取数量">
            <a-input-number
              v-model:value="formData.count"
              placeholder="请输入数量"
              :min="1"
              :max="30"
              style="width: 180px"
            />
          </a-form-item>

          <a-form-item name="offset" label="跳过数量">
            <a-input-number
              v-model:value="formData.offset"
              placeholder="请输入数量"
              :min="0"
              style="width: 180px"
            />
          </a-form-item>
        </a-space>
      </a-form-item>
      <a-form-item name="namePrefix" label="名称前缀">
        <a-input
          v-model:value="formData.namePrefix"
          placeholder="请输入名称前缀，会自动补充序号"
          allow-clear
        />
      </a-form-item>

      <a-form-item name="category" label="分类">
        <a-auto-complete
          v-model:value="formData.category"
          placeholder="请输入分类"
          :options="categoryOptions"
          allow-clear
        />
      </a-form-item>

      <a-form-item name="tags" label="标签">
        <a-select
          v-model:value="formData.tags"
          mode="tags"
          placeholder="请输入标签"
          :options="tagOptions"
          allow-clear
        />
      </a-form-item>

      <a-form-item>
        <a-button type="primary" html-type="submit" style="width: 100%" :loading="loading">
          执行任务
        </a-button>
      </a-form-item>
    </a-form>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { message } from 'ant-design-vue'
import {
  getPictureVoByIdUsingGet,
  listPictureTagCategoryUsingGet,
  uploadPictureByBatchUsingPost,
} from '@/api/pictureController.ts'
import { useRoute, useRouter } from 'vue-router'

const formData = reactive({
  searchText: '',
  count: 10,
  offset: 0,
  namePrefix: '',
  category: '',
  tags: [] as string[],
})
// 提交任务状态
const loading = ref(false)
const categoryOptions = ref<{ value: string; label: string }[]>([])
const tagOptions = ref<{ value: string; label: string }[]>([])
const router = useRouter()

const getTagCategoryOptions = async () => {
  const res = await listPictureTagCategoryUsingGet()

  if (res.data.code === 0 && res.data.data) {
    tagOptions.value = (res.data.data.tagList ?? []).map((data: string) => ({
      value: data,
      label: data,
    }))

    categoryOptions.value = (res.data.data.categoryList ?? []).map((data: string) => ({
      value: data,
      label: data,
    }))
  } else {
    message.error('获取标签分类列表失败，' + res.data.message)
  }
}
/**
 * 提交表单
 * @param values
 */
const handleSubmit = async () => {
  loading.value = true

  try {
    const res = await uploadPictureByBatchUsingPost({
      searchText: formData.searchText,
      count: formData.count,
      offset: formData.offset,
      namePrefix: formData.namePrefix,
      category: formData.category,
      tags: formData.tags.length > 0 ? JSON.stringify(formData.tags) : undefined,
    })

    if (res.data.code === 0 && res.data.data) {
      message.success(`创建成功，共 ${res.data.data} 条`)

      router.push({
        path: `/`,
      })
    } else {
      message.error('创建失败，' + res.data.message)
    }
  } finally {
    loading.value = false
  }
}
onMounted(() => {
  getTagCategoryOptions()
})
</script>

<style scoped>
#addPictureBatchPage {
  max-width: 720px;
  margin: 0 auto;
}
</style>

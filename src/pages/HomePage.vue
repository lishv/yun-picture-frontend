<template>
  <div id="homePage">
    <!-- 搜索框 -->
    <div class="search-bar">
      <a-input-search
        v-model:value="searchParams.searchText"
        placeholder="从海量图片中搜索"
        enter-button="搜索"
        size="large"
        @search="doSearch"
      />
    </div>

    <!-- 分类和标签筛选 -->
    <a-tabs v-model:active-key="selectedCategory" class="category-tabs" @change="doSearch">
      <a-tab-pane key="all" tab="全部" />
      <a-tab-pane v-for="category in categoryList" :key="category" :tab="category" />
    </a-tabs>

    <div class="tag-bar">
      <span class="tag-label">标签：</span>

      <a-space :size="[4, 10]" wrap>
        <a-checkable-tag
          v-for="(tag, index) in tagList"
          :key="tag"
          v-model:checked="selectedTagList[index]"
          class="filter-tag"
          @change="doSearch"
        >
          {{ tag }}
        </a-checkable-tag>
      </a-space>
    </div>

    <!-- 图片列表 -->
    <PictureList :data-list="dataList" :loading="loading && dataList.length === 0" />

    <!-- 下拉加载触发区域 -->
    <div ref="loadMoreTrigger" class="load-more-trigger">
      <a-spin v-if="loading && dataList.length > 0" />

      <span v-else-if="!hasMore && dataList.length > 0" class="load-status"> 没有更多图片了 </span>

      <span v-else-if="!loading && dataList.length === 0" class="load-status"> 暂无图片 </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { message } from 'ant-design-vue'
import { useRoute, useRouter } from 'vue-router'
import {
  listPictureTagCategoryUsingGet,
  listPictureVoByCursorUsingPost,
} from '@/api/pictureController.ts'
import PictureList from '@/components/PictureList.vue'

const route = useRoute()
const router = useRouter()

const dataList = ref<API.PictureVO[]>([])
const loading = ref(false)
const hasMore = ref(true)

const nextCursorCreateTime = ref<string>()
const nextCursorId =  ref<string>()
const searchParams = reactive<API.PictureCursorQueryRequest>({
  searchText: undefined,
  pageSize: 20,
})

const categoryList = ref<string[]>([])
const selectedCategory = ref('all')
const tagList = ref<string[]>([])
const selectedTagList = ref<boolean[]>([])

const loadMoreTrigger = ref<HTMLElement>()
let observer: IntersectionObserver | undefined
let initialized = false
let queryGeneration = 0

const getSelectedTags = () => {
  return tagList.value.filter((_, index) => selectedTagList.value[index])
}

const normalizeQuery = (query: Record<string, unknown>) => {
  return {
    searchText: typeof query.searchText === 'string' ? query.searchText : '',
    category: typeof query.category === 'string' ? query.category : '',
    tags: typeof query.tags === 'string' ? query.tags : '',
  }
}

const syncSearchParamsToUrl = async () => {
  const selectedTags = getSelectedTags()

  const targetQuery = {
    searchText: searchParams.searchText?.trim() || undefined,
    category: selectedCategory.value === 'all' ? undefined : selectedCategory.value,
    tags: selectedTags.length > 0 ? selectedTags.join(',') : undefined,
  }

  const currentKey = JSON.stringify(normalizeQuery(route.query))
  const targetKey = JSON.stringify(normalizeQuery(targetQuery))

  if (currentKey === targetKey) {
    await resetAndFetchData()
    return
  }

  await router.replace({
    query: targetQuery,
  })
}

const restoreSearchParamsFromUrl = () => {
  searchParams.searchText =
    typeof route.query.searchText === 'string' ? route.query.searchText : undefined

  selectedCategory.value = typeof route.query.category === 'string' ? route.query.category : 'all'

  const selectedTags =
    typeof route.query.tags === 'string'
      ? route.query.tags
          .split(',')
          .map((tag) => tag.trim())
          .filter(Boolean)
      : []

  selectedTagList.value = tagList.value.map((tag) => selectedTags.includes(tag))
}

const getTagCategoryOptions = async () => {
  try {
    const res = await listPictureTagCategoryUsingGet()

    if (res.data.code === 0 && res.data.data) {
      tagList.value = res.data.data.tagList ?? []
      categoryList.value = res.data.data.categoryList ?? []
      return
    }

    message.error('获取标签分类列表失败，' + res.data.message)
  } catch {
    message.error('获取标签分类列表失败，请检查网络')
  }
}

const loadMore = async () => {
  if (loading.value || !hasMore.value) {
    return
  }

  const currentGeneration = queryGeneration
  loading.value = true

  try {
    const res = await listPictureVoByCursorUsingPost({
      searchText: searchParams.searchText?.trim() || undefined,
      category: selectedCategory.value === 'all' ? undefined : selectedCategory.value,
      tags: getSelectedTags(),
      pageSize: searchParams.pageSize,
      cursorCreateTime: nextCursorCreateTime.value,
      cursorId: nextCursorId.value,
    })

    if (currentGeneration !== queryGeneration) {
      return
    }

    if (res.data.code !== 0 || !res.data.data) {
      message.error('获取图片失败，' + res.data.message)
      return
    }

    const records = res.data.data.records ?? []

    const existingIds = new Set(
      dataList.value
        .map((picture) => picture.id)
        .filter(Boolean)
        .map(String),
    )

    const newRecords = records.filter((picture) => {
      if (!picture.id) {
        return false
      }

      const id = String(picture.id)

      if (existingIds.has(id)) {
        return false
      }

      existingIds.add(id)
      return true
    })

    dataList.value.push(...newRecords)

    hasMore.value = res.data.data.hasMore ?? false

    nextCursorCreateTime.value = res.data.data.nextCursorCreateTime

    nextCursorId.value = res.data.data.nextCursorId
  } catch {
    if (currentGeneration === queryGeneration) {
      message.error('获取图片失败，请检查网络')
    }
  } finally {
    if (currentGeneration === queryGeneration) {
      loading.value = false
    }
  }
}

const resetAndFetchData = async () => {
  queryGeneration += 1
  dataList.value = []
  nextCursorCreateTime.value = undefined
  nextCursorId.value = undefined
  hasMore.value = true
  loading.value = false

  await loadMore()
}

const doSearch = async () => {
  await syncSearchParamsToUrl()
}

watch(
  () => route.fullPath,
  async () => {
    if (!initialized) {
      return
    }

    restoreSearchParamsFromUrl()
    await resetAndFetchData()
  },
)

const setupIntersectionObserver = async () => {
  await nextTick()

  if (!loadMoreTrigger.value) {
    return
  }

  observer = new IntersectionObserver(
    ([entry]) => {
      if (entry?.isIntersecting) {
        loadMore()
      }
    },
    {
      rootMargin: '300px 0px',
    },
  )

  observer.observe(loadMoreTrigger.value)
}

onMounted(async () => {
  await getTagCategoryOptions()
  restoreSearchParamsFromUrl()

  initialized = true

  await resetAndFetchData()
  await setupIntersectionObserver()
})

onBeforeUnmount(() => {
  queryGeneration += 1
  observer?.disconnect()
})
</script>

<style scoped>
#homePage {
  margin-bottom: 16px;
}

#homePage .search-bar {
  max-width: 550px;
  margin: 0 auto 16px;
}

#homePage .tag-bar {
  margin-bottom: 16px;
}

/* 放大分类文字 */
#homePage .category-tabs :deep(.ant-tabs-tab-btn) {
  font-size: 18px;
}

/* 放大“标签：”文字 */
#homePage .tag-label {
  margin-right: 8px;
  font-size: 18px;
}

/* 放大每一个标签文字 */
#homePage .filter-tag {
  padding: 2px 8px;
  font-size: 16px;
  line-height: 24px;
}

.load-more-trigger {
  display: flex;
  min-height: 72px;
  align-items: center;
  justify-content: center;
}

.load-status {
  color: #8c8c8c;
  font-size: 14px;
}
</style>

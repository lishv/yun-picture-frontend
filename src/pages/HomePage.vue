<template>
  <div id="homePage">
    <!-- 顶部视觉横幅与强化搜索区（彻底解决页面空旷、单调、搜索框过窄问题） -->
    <div class="search-hero-section">
      <div class="hero-title-wrap">
        <h1 class="hero-title">海量高清图片 · 绘聚创作灵感</h1>
        <p class="hero-subtitle">创意素材多维检索 · 空间多人实时协同</p>
      </div>

      <!-- 搜索框：按照用户红框要求拓展到全宽，按钮消除生硬蓝块 -->
      <div class="search-bar">
        <a-input-search
          v-model:value="searchParams.searchText"
          placeholder="搜索高清壁纸、摄影大图、设计插画、表情包、免抠素材..."
          enter-button="搜 索"
          size="large"
          @search="doSearch"
        />
      </div>

      <!-- 热门关键词快捷检索，丰富空旷区域 -->
      <div class="quick-keywords">
        <span class="quick-title">热门搜索：</span>
        <span
          v-for="kw in hotKeywords"
          :key="kw"
          class="quick-kw-item"
          @click="quickSearch(kw)"
        >
          {{ kw }}
        </span>
      </div>
    </div>

    <!-- 筛选面板区：将原本散落的分类与标签整合进现代暗色卡片，界面层次更丰富不单调 -->
    <div class="filter-panel">
      <!-- 分类和标签筛选 -->
      <a-tabs v-model:active-key="selectedCategory" class="category-tabs" @change="doSearch">
        <a-tab-pane key="all" tab="全部" />
        <a-tab-pane v-for="category in categoryList" :key="category" :tab="category" />
      </a-tabs>

      <div class="tag-bar">
        <span class="tag-label">
          <TagsOutlined class="tag-icon" />标签：
        </span>

        <a-space :size="[6, 10]" wrap>
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
import { TagsOutlined } from '@ant-design/icons-vue'
import { useRoute, useRouter } from 'vue-router'
import {
  listPictureTagCategoryUsingGet,
  listPictureVoByCursorUsingPost,
} from '@/api/pictureController.ts'
import PictureList from '@/components/PictureList.vue'

const route = useRoute()
const router = useRouter()

// 热门搜索推荐词
const hotKeywords = ['壁纸', '摄影', '插画', '高清', '艺术', '风景', '设计', '头像']
const quickSearch = (kw: string) => {
  searchParams.searchText = kw
  doSearch()
}

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

/* 顶部视觉横幅区（彻底解决空旷单调感，提升品牌质感） */
.search-hero-section {
  position: relative;
  text-align: center;
  padding: 38px 24px 30px;
  margin-bottom: 24px;
  border-radius: 16px;
  background: radial-gradient(
      ellipse at 50% 20%,
      rgba(59, 130, 246, 0.14) 0%,
      transparent 65%
    ),
    linear-gradient(180deg, rgba(38, 42, 54, 0.65) 0%, rgba(22, 24, 32, 0.65) 100%);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.09);
  box-shadow: 0 12px 36px rgba(0, 0, 0, 0.35);
  overflow: hidden;
}

.hero-title {
  font-size: 26px;
  font-weight: 700;
  color: #ffffff;
  letter-spacing: 1.2px;
  margin-bottom: 8px;
  background: linear-gradient(180deg, #ffffff 0%, rgba(255, 255, 255, 0.82) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-subtitle {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.52);
  margin-bottom: 22px;
  letter-spacing: 0.5px;
}

/* 搜索框：按照用户红框要求拓展到全宽，并去除生硬纯蓝矩形块 */
.search-bar {
  width: 100%;
  max-width: 980px;
  margin: 0 auto;
}

.search-bar :deep(.ant-input-search) {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
  border-radius: 10px;
}

.search-bar :deep(.ant-input-group .ant-input) {
  height: 50px;
  font-size: 15px;
  padding-left: 20px;
  border-radius: 10px 0 0 10px !important;
  background: rgba(22, 24, 32, 0.85) !important;
  border: 1px solid rgba(255, 255, 255, 0.12) !important;
  border-right: none !important;
  color: #ffffff !important;
  transition: all 0.25s ease;
}

.search-bar :deep(.ant-input-group .ant-input::placeholder) {
  color: rgba(255, 255, 255, 0.42);
}

.search-bar :deep(.ant-input-group .ant-input:focus),
.search-bar :deep(.ant-input-group .ant-input:hover) {
  border-color: #3b82f6 !important;
}

/* 搜索按钮：由生硬刺眼的纯色平铺矩形改为优雅微光渐变 */
.search-bar :deep(.ant-input-search-button) {
  height: 50px !important;
  padding: 0 32px !important;
  font-size: 16px !important;
  font-weight: 500 !important;
  letter-spacing: 1px !important;
  border-radius: 0 10px 10px 0 !important;
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
  border: 1px solid rgba(255, 255, 255, 0.18) !important;
  color: #ffffff !important;
  box-shadow: 0 2px 10px rgba(37, 99, 235, 0.3) !important;
  transition: all 0.25s ease !important;
}

.search-bar :deep(.ant-input-search-button:hover) {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
  border-color: rgba(255, 255, 255, 0.38) !important;
  box-shadow: 0 4px 18px rgba(37, 99, 235, 0.5) !important;
}

/* 热门搜索推荐 */
.quick-keywords {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 14px;
}

.quick-title {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.45);
}

.quick-kw-item {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.72);
  background: rgba(255, 255, 255, 0.07);
  border: 1px solid rgba(255, 255, 255, 0.12);
  padding: 3px 12px;
  border-radius: 14px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.quick-kw-item:hover {
  color: #93c5fd;
  background: rgba(37, 99, 235, 0.22);
  border-color: rgba(59, 130, 246, 0.45);
  transform: translateY(-1px);
}

/* 整合后的筛选控制台（避免零散空旷，渐变黑质感） */
.filter-panel {
  background: linear-gradient(180deg, rgba(38, 41, 53, 0.7) 0%, rgba(25, 27, 35, 0.7) 100%);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 18px 24px 22px;
  margin-bottom: 24px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
}

.category-tabs {
  margin-bottom: 12px;
}

.category-tabs :deep(.ant-tabs-nav) {
  margin-bottom: 12px;
}

.category-tabs :deep(.ant-tabs-tab) {
  padding: 8px 16px;
  font-size: 16px;
  color: rgba(255, 255, 255, 0.65);
  transition: all 0.2s ease;
}

.category-tabs :deep(.ant-tabs-tab:hover) {
  color: #93c5fd;
}

.category-tabs :deep(.ant-tabs-tab-active .ant-tabs-tab-btn) {
  color: #ffffff !important;
  font-weight: 600;
}

.category-tabs :deep(.ant-tabs-ink-bar) {
  background: linear-gradient(90deg, #3b82f6, #60a5fa) !important;
  height: 3px !important;
  border-radius: 3px;
  box-shadow: 0 0 10px rgba(59, 130, 246, 0.6);
}

.tag-bar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
}

.tag-label {
  margin-right: 8px;
  font-size: 15px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.88);
  display: inline-flex;
  align-items: center;
}

.tag-icon {
  margin-right: 4px;
  color: #60a5fa;
}

/* 优化标签边框与对比度，清晰醒目 */
.filter-tag {
  padding: 4px 12px;
  font-size: 14px;
  line-height: 20px;
  border-radius: 6px;
  border: 1px solid #3c3c4c !important;
  background: #22222b !important;
  color: rgba(255, 255, 255, 0.82) !important;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.filter-tag:hover {
  border-color: #60a5fa !important;
  color: #93c5fd !important;
  background: #2a2a38 !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

#homePage :deep(.ant-tag-checkable-checked) {
  background-color: rgba(37, 99, 235, 0.22) !important;
  border-color: #3b82f6 !important;
  color: #93c5fd !important;
  font-weight: 500;
  box-shadow: 0 0 8px rgba(37, 99, 235, 0.35);
}

.load-more-trigger {
  display: flex;
  min-height: 72px;
  align-items: center;
  justify-content: center;
}

.load-status {
  color: rgba(255, 255, 255, 0.45);
  font-size: 14px;
}
</style>

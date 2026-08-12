<template>
  <div class="picture-list">
    <div v-if="loading && dataList.length === 0" class="initial-loading">
      <a-spin size="large" />
    </div>

    <div v-else ref="waterfallRef" class="waterfall">
      <article
        v-for="picture in dataList"
        :key="String(picture.id)"
        class="picture-card"
        tabindex="0"
        @click="doClickPicture(picture)"
        @keydown.enter="doClickPicture(picture)"
        @keydown.space.prevent="doClickPicture(picture)"
      >
        <img
          class="picture-image"
          :src="picture.thumbnailUrl ?? picture.url"
          :alt="picture.name ?? '图片'"
          loading="lazy"
          :style="getImageStyle(picture)"
          @load="updateCardSpan"
        />

        <div class="picture-overlay">
          <div class="picture-info">
            <div class="picture-name">
              {{ picture.name ?? '未命名图片' }}
            </div>

            <div class="picture-tags">
              <a-tag v-if="picture.category" class="category-tag" color="green">
                {{ picture.category }}
              </a-tag>

              <a-tag v-for="tag in picture.tags" :key="tag" class="picture-tag">
                {{ tag }}
              </a-tag>
            </div>
          </div>

          <div v-if="showOp" class="picture-actions">
            <a-tooltip title="分享">
              <button
                type="button"
                class="action-button"
                aria-label="分享图片"
                @click="doShare(picture, $event)"
              >
                <ShareAltOutlined />
              </button>
            </a-tooltip>

            <a-tooltip title="以图搜图">
              <button
                type="button"
                class="action-button"
                aria-label="以图搜图"
                @click="doSearch(picture, $event)"
              >
                <SearchOutlined />
              </button>
            </a-tooltip>

            <a-tooltip v-if="canEdit" title="编辑">
              <button
                type="button"
                class="action-button"
                aria-label="编辑图片"
                @click="doEdit(picture, $event)"
              >
                <EditOutlined />
              </button>
            </a-tooltip>

            <a-tooltip v-if="canDelete" title="删除">
              <button
                type="button"
                class="action-button danger"
                aria-label="删除图片"
                @click="doDelete(picture, $event)"
              >
                <DeleteOutlined />
              </button>
            </a-tooltip>
          </div>
        </div>
      </article>
    </div>

    <ShareModal ref="shareModalRef" :link="shareLink" />
  </div>
</template>

<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, ref, watch, type CSSProperties } from 'vue'
import { useRouter } from 'vue-router'
import {
  DeleteOutlined,
  EditOutlined,
  SearchOutlined,
  ShareAltOutlined,
} from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import { deletePictureUsingPost } from '@/api/pictureController.ts'
import ShareModal from '@/components/ShareModal.vue'

interface Props {
  dataList?: API.PictureVO[]
  loading?: boolean
  showOp?: boolean
  canEdit?: boolean
  canDelete?: boolean
  onReload?: () => void
}

const props = withDefaults(defineProps<Props>(), {
  dataList: () => [],
  loading: false,
  showOp: false,
  canEdit: false,
  canDelete: false,
})

const router = useRouter()
const waterfallRef = ref<HTMLElement>()

let resizeObserver: ResizeObserver | undefined
let resizeAnimationFrame: number | undefined

const getImageStyle = (picture: API.PictureVO): CSSProperties => {
  if (!picture.picWidth || !picture.picHeight) {
    return {}
  }

  return {
    aspectRatio: `${picture.picWidth} / ${picture.picHeight}`,
  }
}

/**
 * 根据卡片实际高度计算 Grid 行跨度。
 */
const updateCardElementSpan = (card: HTMLElement) => {
  const waterfall = waterfallRef.value

  if (!waterfall) {
    return
  }

  const waterfallStyle = window.getComputedStyle(waterfall)

  const rowHeight = Number.parseFloat(waterfallStyle.gridAutoRows) || 8

  const rowGap = Number.parseFloat(waterfallStyle.rowGap) || 16

  const cardHeight = card.getBoundingClientRect().height

  const rowSpan = Math.ceil((cardHeight + rowGap) / (rowHeight + rowGap))

  card.style.gridRowEnd = `span ${Math.max(rowSpan, 1)}`
}

/**
 * 图片加载完成后计算所在卡片的跨度。
 */
const updateCardSpan = (event: Event) => {
  const image = event.currentTarget

  if (!(image instanceof HTMLImageElement)) {
    return
  }

  const card = image.closest<HTMLElement>('.picture-card')

  if (card) {
    updateCardElementSpan(card)
  }
}

/**
 * 重新计算全部图片卡片。
 */
const updateAllCardSpans = async () => {
  await nextTick()

  const waterfall = waterfallRef.value

  if (!waterfall) {
    return
  }

  waterfall.querySelectorAll<HTMLElement>('.picture-card').forEach(updateCardElementSpan)
}

/**
 * 列宽变化时重新计算卡片高度。
 */
const scheduleCardSpanUpdate = () => {
  if (resizeAnimationFrame !== undefined) {
    cancelAnimationFrame(resizeAnimationFrame)
  }

  resizeAnimationFrame = requestAnimationFrame(() => {
    updateAllCardSpans()
    resizeAnimationFrame = undefined
  })
}

watch(
  () => props.dataList.length,
  () => {
    updateAllCardSpans()
  },
  {
    flush: 'post',
  },
)

onMounted(async () => {
  await updateAllCardSpans()

  if (!waterfallRef.value) {
    return
  }

  resizeObserver = new ResizeObserver(scheduleCardSpanUpdate)

  resizeObserver.observe(waterfallRef.value)
})

onBeforeUnmount(() => {
  resizeObserver?.disconnect()

  if (resizeAnimationFrame !== undefined) {
    cancelAnimationFrame(resizeAnimationFrame)
  }
})

const doClickPicture = (picture: API.PictureVO) => {
  if (!picture.id) {
    return
  }

  router.push({
    path: `/picture/${picture.id}`,
  })
}

const doSearch = (picture: API.PictureVO, event: MouseEvent) => {
  event.stopPropagation()

  if (!picture.id) {
    return
  }

  window.open(`/search_picture?pictureId=${picture.id}`, '_blank', 'noopener,noreferrer')
}

const doEdit = (picture: API.PictureVO, event: MouseEvent) => {
  event.stopPropagation()

  if (!picture.id) {
    return
  }

  router.push({
    path: '/add_picture',
    query: {
      id: String(picture.id),
      spaceId: picture.spaceId ? String(picture.spaceId) : undefined,
    },
  })
}

const doDelete = async (picture: API.PictureVO, event: MouseEvent) => {
  event.stopPropagation()

  if (!picture.id) {
    return
  }

  try {
    const res = await deletePictureUsingPost({
      id: picture.id,
    })

    if (res.data.code === 0) {
      message.success('删除成功')
      props.onReload?.()
      return
    }

    message.error('删除失败，' + res.data.message)
  } catch {
    message.error('删除失败，请检查网络')
  }
}

const shareModalRef = ref<InstanceType<typeof ShareModal>>()

const shareLink = ref<string>()

const doShare = (picture: API.PictureVO, event: MouseEvent) => {
  event.stopPropagation()

  if (!picture.id) {
    return
  }

  shareLink.value = `${window.location.origin}/picture/${picture.id}`

  shareModalRef.value?.openModal()
}
</script>

<style scoped>
.picture-list {
  width: 100%;
}

.initial-loading {
  display: flex;
  min-height: 240px;
  align-items: center;
  justify-content: center;
}

/*
 * 横向优先的 Grid 瀑布流：
 * 数据顺序 1、2、3、4 会先横向排列为 1 2 3，再排下一行。
 */
.waterfall {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  grid-auto-flow: row;
  grid-auto-rows: 8px;
  gap: 16px;
  align-items: start;
}

.picture-card {
  position: relative;
  width: 100%;
  min-width: 0;
  margin: 0;
  overflow: hidden;
  cursor: pointer;
  background: #f5f5f5;
  border-radius: 6px;
}

.picture-card:focus-visible {
  outline: 2px solid #1677ff;
  outline-offset: 2px;
}

.picture-image {
  display: block;
  width: 100%;
  height: auto;
  object-fit: cover;
}

.picture-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 12px;
  color: #fff;
  background: linear-gradient(
    to top,
    rgba(0, 0, 0, 0.82) 0%,
    rgba(0, 0, 0, 0.4) 38%,
    transparent 65%
  );
  opacity: 0;
  transition: opacity 180ms ease;
}

.picture-card:hover .picture-overlay,
.picture-card:focus-visible .picture-overlay {
  opacity: 1;
}

.picture-info {
  margin-top: auto;
}

.picture-name {
  overflow: hidden;
  margin-bottom: 8px;
  color: #fff;
  font-size: 15px;
  font-weight: 600;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.picture-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.picture-tags :deep(.ant-tag) {
  max-width: 100%;
  overflow: hidden;
  margin-inline-end: 0;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 分类标签保持主要视觉层级 */
.picture-tags :deep(.category-tag) {
  font-weight: 500;
}

/*
 * 普通标签使用低对比度半透明背景：
 * 能适应浅色和深色图片，但不会比分类标签更显眼。
 */
.picture-tags :deep(.picture-tag) {
  color: rgba(255, 255, 255, 0.92);
  background: rgba(24, 24, 24, 0.48);
  border-color: rgba(255, 255, 255, 0.35);
  backdrop-filter: blur(3px);
  -webkit-backdrop-filter: blur(3px);
}

.picture-actions {
  display: flex;
  align-self: flex-end;
  gap: 6px;
  order: -1;
}

.action-button {
  display: inline-flex;
  width: 32px;
  height: 32px;
  align-items: center;
  justify-content: center;
  padding: 0;
  color: #fff;
  background: rgba(0, 0, 0, 0.48);
  border: 0;
  border-radius: 4px;
  cursor: pointer;
}

.action-button:hover,
.action-button:focus-visible {
  background: rgba(0, 0, 0, 0.72);
}

.action-button.danger:hover,
.action-button.danger:focus-visible {
  background: #ff4d4f;
}

@media (max-width: 1600px) {
  .waterfall {
    grid-template-columns: repeat(5, minmax(0, 1fr));
  }
}

@media (max-width: 1200px) {
  .waterfall {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}

@media (max-width: 992px) {
  .waterfall {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 768px) {
  .waterfall {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12px;
  }
}

@media (max-width: 480px) {
  .waterfall {
    grid-template-columns: minmax(0, 1fr);
  }
}

@media (hover: none) {
  .picture-overlay {
    opacity: 1;
  }
}

@media (prefers-reduced-motion: reduce) {
  .picture-overlay {
    transition: none;
  }
}
</style>

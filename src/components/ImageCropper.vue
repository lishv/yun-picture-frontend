<template>
  <a-modal
    v-model:open="visible"
    class="image-cropper"
    title="编辑图片"
    :width="720"
    :footer="false"
    @cancel="closeModal"
  >
    <!-- 图片裁切组件 -->
    <div class="cropper-container">
      <vue-cropper
        ref="cropperRef"
        :img="props.imageUrl"
        output-type="png"
        :info="true"
        :can-move-box="true"
        :fixed-box="false"
        :auto-crop="true"
        :center-box="true"
        @img-load="onImageLoaded"
      />
    </div>

    <div class="image-edit-spacing" />

    <!-- 团队空间协同编辑操作 -->
    <div v-if="isTeamSpace" class="image-edit-actions">
      <a-space>
        <a-button v-if="editingUser" disabled> {{ editingUser.userName }} 正在编辑 </a-button>

        <a-button v-if="canEnterEdit" type="primary" ghost @click="enterEdit"> 进入编辑 </a-button>

        <a-button v-if="canExitEdit" danger ghost @click="exitEdit"> 退出编辑 </a-button>
      </a-space>
    </div>

    <div class="image-edit-spacing" />

    <!-- 图片操作 -->
    <div class="image-cropper-actions">
      <a-space>
        <a-button :disabled="!canEdit" @click="rotateLeft"> 向左旋转 </a-button>

        <a-button :disabled="!canEdit" @click="rotateRight"> 向右旋转 </a-button>

        <a-button :disabled="!canEdit" @click="changeScale(1)"> 放大 </a-button>

        <a-button :disabled="!canEdit" @click="changeScale(-1)"> 缩小 </a-button>

        <a-button type="primary" :loading="loading" :disabled="!canEdit" @click="handleConfirm">
          确认
        </a-button>
      </a-space>
    </div>
  </a-modal>
</template>

<script lang="ts" setup>
import { computed, nextTick, onUnmounted, ref, watchEffect } from 'vue'
import { storeToRefs } from 'pinia'
import { message } from 'ant-design-vue'
import { uploadPictureUsingPost } from '@/api/pictureController.ts'
import { useLoginUserStore } from '@/stores/useLoginUserStore.ts'
import PictureEditWebSocket from '@/utils/pictureEditWebSocket.ts'
import { PICTURE_EDIT_ACTION_ENUM, PICTURE_EDIT_MESSAGE_TYPE_ENUM } from '@/constants/picture.ts'
import { SPACE_TYPE_ENUM } from '@/constants/space.ts'

interface Props {
  imageUrl?: string
  picture?: API.PictureVO
  spaceId?: number
  space?: API.SpaceVO
  onSuccess?: (newPicture: API.PictureVO) => void
}

const props = defineProps<Props>()

/**
 * 图片裁切器引用
 */
const cropperRef = ref()

/**
 * 弹窗是否显示
 */
const visible = ref(false)

/**
 * 上传状态
 */
const loading = ref(false)

/**
 * 图片是否已经加载完成
 */
const imageLoaded = ref(false)

/**
 * 图片加载完成前收到的远程操作
 */
const pendingEditActions: string[] = []

/**
 * WebSocket 实例
 */
let websocket: PictureEditWebSocket | null = null

/**
 * 当前登录用户
 *
 * 使用 storeToRefs，避免拿到登录用户的旧快照。
 */
const loginUserStore = useLoginUserStore()
const { loginUser } = storeToRefs(loginUserStore)

/**
 * 当前正在编辑图片的用户
 */
const editingUser = ref<API.UserVO>()

/**
 * 判断两个用户 ID 是否相同。
 *
 * 后端 WebSocket 会将 Long 序列化为字符串，
 * 而前端接口类型中可能定义为 number，
 * 因此这里统一转成字符串比较。
 */
const isSameUser = (firstId: unknown, secondId: unknown) => {
  if (firstId === undefined || firstId === null) {
    return false
  }

  if (secondId === undefined || secondId === null) {
    return false
  }

  return String(firstId) === String(secondId)
}

/**
 * 是否为团队空间
 */
const isTeamSpace = computed(() => {
  return props.space?.spaceType === SPACE_TYPE_ENUM.TEAM
})

/**
 * 当前用户是否可以进入编辑状态
 */
const canEnterEdit = computed(() => {
  return !editingUser.value
})

/**
 * 当前用户是否可以退出编辑状态
 */
const canExitEdit = computed(() => {
  return isSameUser(editingUser.value?.id, loginUser.value?.id)
})

/**
 * 当前用户是否可以执行图片编辑操作
 */
const canEdit = computed(() => {
  // 非团队空间默认允许编辑
  if (!isTeamSpace.value) {
    return true
  }

  // 团队空间只有当前编辑者可以操作
  return isSameUser(editingUser.value?.id, loginUser.value?.id)
})

/**
 * 向后端发送图片编辑操作
 *
 * @param action 编辑操作
 */
const sendEditAction = (action: string) => {
  if (!websocket) {
    return
  }

  websocket.sendMessage({
    type: PICTURE_EDIT_MESSAGE_TYPE_ENUM.EDIT_ACTION,
    editAction: action,
  })
}

/**
 * 只在当前页面应用图片操作。
 *
 * 该方法不会再次向后端发送 WebSocket 消息，
 * 用于处理其他用户发送的操作和状态回放。
 *
 * @param action 编辑操作
 */
const applyEditAction = (action: string) => {
  switch (action) {
    case PICTURE_EDIT_ACTION_ENUM.ROTATE_LEFT:
      cropperRef.value?.rotateLeft()
      break

    case PICTURE_EDIT_ACTION_ENUM.ROTATE_RIGHT:
      cropperRef.value?.rotateRight()
      break

    case PICTURE_EDIT_ACTION_ENUM.ZOOM_IN:
      cropperRef.value?.changeScale(1)
      break

    case PICTURE_EDIT_ACTION_ENUM.ZOOM_OUT:
      cropperRef.value?.changeScale(-1)
      break
  }
}

/**
 * 应用远程操作。
 *
 * 如果图片尚未加载完成，则先保存到等待队列中。
 *
 * @param action 编辑操作
 */
const applyOrQueueEditAction = (action?: string) => {
  if (!action) {
    return
  }

  if (!imageLoaded.value || !cropperRef.value) {
    pendingEditActions.push(action)
    return
  }

  applyEditAction(action)
}

/**
 * vue-cropper 图片加载完成事件
 *
 * vue-cropper 成功时会传递字符串 success，
 * 加载失败时会传递 error。
 *
 * @param status 图片加载状态
 */
const onImageLoaded = (status: unknown) => {
  if (status !== 'success') {
    imageLoaded.value = false
    return
  }

  imageLoaded.value = true

  // 取出图片加载之前收到的所有操作
  const actions = pendingEditActions.splice(0, pendingEditActions.length)

  // 按原来的顺序依次应用
  actions.forEach((action) => {
    applyEditAction(action)
  })
}

/**
 * 放大或缩小图片
 *
 * @param num 大于 0 表示放大，小于 0 表示缩小
 */
const changeScale = (num: number) => {
  if (!canEdit.value || !imageLoaded.value || !cropperRef.value) {
    return
  }

  cropperRef.value.changeScale(num)

  if (num > 0) {
    sendEditAction(PICTURE_EDIT_ACTION_ENUM.ZOOM_IN)
  } else {
    sendEditAction(PICTURE_EDIT_ACTION_ENUM.ZOOM_OUT)
  }
}

/**
 * 向左旋转
 */
const rotateLeft = () => {
  if (!canEdit.value || !imageLoaded.value || !cropperRef.value) {
    return
  }

  cropperRef.value.rotateLeft()
  sendEditAction(PICTURE_EDIT_ACTION_ENUM.ROTATE_LEFT)
}

/**
 * 向右旋转
 */
const rotateRight = () => {
  if (!canEdit.value || !imageLoaded.value || !cropperRef.value) {
    return
  }

  cropperRef.value.rotateRight()
  sendEditAction(PICTURE_EDIT_ACTION_ENUM.ROTATE_RIGHT)
}

/**
 * 关闭弹窗
 */
const closeModal = () => {
  visible.value = false

  if (websocket) {
    websocket.disconnect()
    websocket = null
  }

  editingUser.value = undefined
  imageLoaded.value = false
  pendingEditActions.length = 0
}

/**
 * 上传裁切后的图片
 *
 * @param file 图片文件
 */
const handleUpload = async ({ file }: { file: File }) => {
  loading.value = true

  try {
    const params: API.PictureUploadRequest = {}

    if (props.picture?.id !== undefined) {
      params.id = props.picture.id
    }

    if (props.spaceId !== undefined) {
      params.spaceId = props.spaceId
    }

    const res = await uploadPictureUsingPost(params, {}, file)

    if (res.data.code === 0 && res.data.data) {
      message.success('图片上传成功')

      // 将最新图片传给父组件
      props.onSuccess?.(res.data.data)

      closeModal()
    } else {
      message.error('图片上传失败，' + res.data.message)
    }
  } catch (error: any) {
    console.error('图片上传失败', error)

    message.error('图片上传失败，' + error.message)
  } finally {
    loading.value = false
  }
}

/**
 * 确认裁切
 */
const handleConfirm = () => {
  if (!canEdit.value || !imageLoaded.value || !cropperRef.value) {
    return
  }

  cropperRef.value.getCropBlob((blob: Blob | null) => {
    if (!blob) {
      message.error('获取裁切图片失败')
      return
    }

    const fileName = `${props.picture?.name || 'image'}.png`

    const file = new File([blob], fileName, {
      type: blob.type || 'image/png',
    })

    void handleUpload({
      file,
    })
  })
}

/**
 * 打开编辑弹窗
 */
const openModal = async () => {
  // 清理上一次打开时的临时状态
  imageLoaded.value = false
  pendingEditActions.length = 0
  editingUser.value = undefined

  // 先让 Modal 渲染出来
  visible.value = true

  // 等待 Modal 和 vue-cropper 完成渲染
  await nextTick()

  // 重新加载当前图片并恢复初始裁切状态
  cropperRef.value?.refresh()
}

/**
 * 初始化 WebSocket
 */
const initWebsocket = () => {
  const pictureId = props.picture?.id

  if (pictureId === undefined || !visible.value || !isTeamSpace.value) {
    return
  }

  // 释放上一次连接
  if (websocket) {
    websocket.disconnect()
    websocket = null
  }

  websocket = new PictureEditWebSocket(pictureId)

  /*
   * 必须先注册监听器，再调用 connect。
   * 否则连接建立后，后端立即发送的 SYNC_STATE 可能被遗漏。
   */

  /**
   * 普通通知
   */
  websocket.on(PICTURE_EDIT_MESSAGE_TYPE_ENUM.INFO, (msg) => {
    console.log('收到通知消息：', msg)

    if (msg?.message) {
      message.info(msg.message)
    }
  })

  /**
   * 错误通知
   */
  websocket.on(PICTURE_EDIT_MESSAGE_TYPE_ENUM.ERROR, (msg) => {
    console.error('收到错误消息：', msg)

    if (msg?.message) {
      message.error(msg.message)
    }
  })

  /**
   * 同步当前编辑状态
   */
  websocket.on(PICTURE_EDIT_MESSAGE_TYPE_ENUM.SYNC_STATE, (msg) => {
    console.log('收到当前编辑状态：', msg)

    // 回显当前正在编辑的用户
    editingUser.value = msg?.user ?? undefined

    // SYNC_STATE 携带完整的操作快照
    pendingEditActions.length = 0

    const editActions: unknown[] = Array.isArray(msg?.editActions) ? msg.editActions : []

    editActions.forEach((action) => {
      if (typeof action === 'string') {
        applyOrQueueEditAction(action)
      }
    })
  })

  /**
   * 有用户进入编辑状态
   */
  websocket.on(PICTURE_EDIT_MESSAGE_TYPE_ENUM.ENTER_EDIT, (msg) => {
    console.log('收到进入编辑状态的消息：', msg)

    if (msg?.message) {
      message.info(msg.message)
    }

    editingUser.value = msg?.user ?? undefined
  })

  /**
   * 接收其他用户执行的图片操作
   *
   * 后端已经排除了操作发起者，
   * 因此这里仅应用操作，不再次发送。
   */
  websocket.on(PICTURE_EDIT_MESSAGE_TYPE_ENUM.EDIT_ACTION, (msg) => {
    console.log('收到编辑操作的消息：', msg)

    if (msg?.message) {
      message.info(msg.message)
    }

    applyOrQueueEditAction(typeof msg?.editAction === 'string' ? msg.editAction : undefined)
  })

  /**
   * 当前编辑者退出编辑状态
   */
  websocket.on(PICTURE_EDIT_MESSAGE_TYPE_ENUM.EXIT_EDIT, async (msg) => {
    console.log('收到退出编辑状态的消息：', msg)

    if (msg?.message) {
      message.info(msg.message)
    }

    editingUser.value = undefined
    pendingEditActions.length = 0
    imageLoaded.value = false

    await nextTick()

    // 清除未保存的临时编辑状态
    cropperRef.value?.refresh()
  })

  // 所有事件注册完成后再连接
  websocket.connect()
}

/**
 * 监听团队空间、弹窗状态和当前图片。
 */
watchEffect(() => {
  const pictureId = props.picture?.id

  if (isTeamSpace.value && visible.value && pictureId !== undefined) {
    initWebsocket()
  } else if (websocket) {
    websocket.disconnect()
    websocket = null
  }
})

/**
 * 进入图片编辑状态
 */
const enterEdit = () => {
  if (!websocket) {
    return
  }

  websocket.sendMessage({
    type: PICTURE_EDIT_MESSAGE_TYPE_ENUM.ENTER_EDIT,
  })
}

/**
 * 退出图片编辑状态
 */
const exitEdit = () => {
  if (!websocket) {
    return
  }

  websocket.sendMessage({
    type: PICTURE_EDIT_MESSAGE_TYPE_ENUM.EXIT_EDIT,
  })
}

/**
 * 暴露给父组件。
 *
 * [AddPicturePage.vue] 通过 imageCropperRef.value.openModal()
 * 调用此方法。
 */
defineExpose({
  openModal,
})

/**
 * 组件销毁时释放 WebSocket 和临时状态
 */
onUnmounted(() => {
  if (websocket) {
    websocket.disconnect()
    websocket = null
  }

  editingUser.value = undefined
  imageLoaded.value = false
  pendingEditActions.length = 0
})
</script>

<style>
/*
 * vue-cropper 内部根节点的高度是 100%，
 * 所以必须给父容器一个明确的高度。
 */
.cropper-container {
  width: 100%;
  height: 400px;
  overflow: hidden;
}

.cropper-container .vue-cropper {
  width: 100%;
  height: 100%;
}

.image-edit-spacing {
  height: 16px;
}

.image-edit-actions,
.image-cropper-actions {
  text-align: center;
}
</style>

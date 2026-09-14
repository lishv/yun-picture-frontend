/**
 * 格式化文件大小
 * @param size
 */
export const formatSize = (size?: number) => {
  if (!size) return '未知'
  if (size < 1024) return size + ' B'
  if (size < 1024 * 1024) return (size / 1024).toFixed(2) + ' KB'
  return (size / (1024 * 1024)).toFixed(2) + ' MB'
}

/**
 * 下载图片（兼容 PC 与移动端）
 * @param url 图片下载地址
 * @param fileName 要保存为的文件名
 */
export async function downloadImage(url?: string, fileName?: string) {
  if (!url) {
    return
  }

  // 从 url 中提取扩展名，例如 .webp 或 .jpg
  const cleanUrl = url.split('?')[0]
  const extMatch = cleanUrl.match(/\.([a-zA-Z0-9]+)$/)
  const ext = extMatch ? `.${extMatch[1]}` : ''

  // 拼接合理的文件名
  let finalFileName = fileName
  if (!finalFileName) {
    finalFileName = cleanUrl.substring(cleanUrl.lastIndexOf('/') + 1) || `image${ext || '.png'}`
  } else if (ext && !finalFileName.toLowerCase().endsWith(ext.toLowerCase())) {
    finalFileName = `${finalFileName}${ext}`
  }

  try {
    // 优先异步 fetch 转 blob，绕过浏览器的跨域 download 限制，并避免移动端同步 XHR 被拦截
    const res = await fetch(url, { mode: 'cors' })
    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`)
    }
    const blob = await res.blob()
    const blobUrl = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.style.display = 'none'
    a.href = blobUrl
    a.download = finalFileName
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    setTimeout(() => {
      window.URL.revokeObjectURL(blobUrl)
    }, 1000)
  } catch (err) {
    console.warn('Blob 下载失败，降级为在新窗口打开：', err)
    // 移动端或受限环境（如微信浏览器）降级：新窗口打开原图，支持用户长按保存
    const a = document.createElement('a')
    a.href = url
    a.target = '_blank'
    a.rel = 'noopener noreferrer'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
  }
}

/**
 * 将颜色值转换为标准 #RRGGBB 格式
 * @param input
 */
export function toHexColor(input: string) {
  // 去掉 0x 前缀
  const colorValue = input.startsWith('0x') ? input.slice(2) : input

  // 将剩余部分解析为十六进制数，再转成 6 位十六进制字符串
  const hexColor = parseInt(colorValue, 16).toString(16).padStart(6, '0')

  // 返回标准 #RRGGBB 格式
  return `#${hexColor}`
}

import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
//一个状态存储一类要共享的数据(存一类常量)
export const useCounterStore = defineStore('counter', () => {

  // 定义一个响应式数据 count，初始值为 0
  const count = ref(0)

  // 定义一个计算属性 doubleCount，返回 count 的两倍getter
  const doubleCount = computed(() => count.value * 2)

  // 定义一个方法 increment，用于增加 count 的值
  function increment() {
    count.value++
  }

  // 返回响应式数据 count、计算属性 doubleCount、方法 increment
  return { count, doubleCount, increment }
})

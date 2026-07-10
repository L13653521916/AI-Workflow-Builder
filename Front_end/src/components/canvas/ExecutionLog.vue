<template>
  <div
    class="border-t border-gray-200 bg-white shrink-0 flex flex-col relative"
    :style="{ height: collapsed ? '36px' : `${panelHeight}px` }"
  >
    <!-- 顶部高度拖拽条 -->
    <div
      v-if="!collapsed"
      class="absolute top-0 left-0 right-0 h-2 -translate-y-1/2 z-10 flex items-center justify-center cursor-ns-resize group"
      title="拖拽调整高度"
      @mousedown.stop="onHeightDragStart"
    >
      <div class="w-16 h-1 rounded-full bg-gray-300 group-hover:bg-blue-400 transition-colors" />
    </div>

    <div
      class="h-9 px-4 flex items-center justify-between hover:bg-gray-50 shrink-0 select-none"
      :class="collapsed ? 'cursor-pointer' : ''"
      @click="collapsed ? (collapsed = false) : undefined"
    >
      <div
        class="flex items-center gap-2 text-sm font-medium text-gray-700 cursor-pointer"
        @click.stop="collapsed = !collapsed"
      >
        <span>{{ collapsed ? '▶' : '▼' }}</span>
        执行日志
        <span v-if="isExecuting" class="text-xs text-yellow-600 animate-pulse">执行中...</span>
        <span v-else-if="logs.length" class="text-xs text-gray-400">({{ logs.length }} 条)</span>
      </div>
      <div class="flex items-center gap-2">
        <el-button v-if="!collapsed && logs.length" link size="small" @click.stop="emit('clear')">
          清空
        </el-button>
        <el-button link size="small" @click.stop="emit('history')">
          运行历史
        </el-button>
      </div>
    </div>

    <div v-if="!collapsed" class="flex-1 flex overflow-hidden min-h-0">
      <!-- 日志列表 -->
      <div class="flex-1 overflow-y-auto px-4 pb-3 font-mono text-xs space-y-1 min-w-0">
        <div v-if="logs.length === 0" class="text-gray-400 py-4 text-center text-sm font-sans">
          点击「运行」开始执行工作流，日志将在此显示
        </div>
        <div
          v-for="(log, i) in logs"
          :key="i"
          class="flex gap-2 py-0.5 leading-relaxed cursor-pointer hover:bg-gray-50 rounded px-1"
          @click="log.node_id && emit('selectNode', log.node_id)"
        >
          <span class="text-gray-400 shrink-0">{{ formatTime(log.time) }}</span>
          <span class="shrink-0 font-semibold" :class="levelClass(log.level)">[{{ log.level }}]</span>
          <span class="text-gray-700">{{ log.message }}</span>
        </div>
      </div>

      <!-- 右侧输出区（可拖拽宽度） -->
      <template v-if="showOutputPanel">
        <div
          class="w-1.5 shrink-0 cursor-col-resize hover:bg-blue-200 bg-gray-100 flex items-center justify-center group"
          title="拖拽调整宽度"
          @mousedown.stop="onOutputWidthDragStart"
        >
          <div class="w-0.5 h-8 rounded-full bg-gray-300 group-hover:bg-blue-400" />
        </div>
        <div
          class="border-l border-gray-200 overflow-y-auto p-3 shrink-0 flex flex-col min-h-0"
          :style="{ width: `${outputWidth}px` }"
        >
          <div class="text-xs font-medium text-gray-500 mb-2 shrink-0">
            {{ selectedOutput !== null ? '节点输出' : '最终输出' }}
          </div>
          <pre
            class="text-xs p-2 rounded overflow-auto flex-1 whitespace-pre-wrap min-h-0"
            :class="selectedOutput !== null ? 'bg-gray-50' : 'bg-green-50'"
          >{{ formatOutput(displayOutput) }}</pre>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import type { ExecutionLogEntry } from '@/types/execution'

const STORAGE_KEY = 'canvas_execution_log_layout'

const props = defineProps<{
  selectedNodeId?: string | null
}>()

const emit = defineEmits<{
  clear: []
  history: []
  selectNode: [nodeId: string]
}>()

const store = useStore()
const collapsed = ref(false)
const panelHeight = ref(200)
const outputWidth = ref(288)

const MIN_HEIGHT = 120
const MAX_HEIGHT = 560
const MIN_OUTPUT_WIDTH = 200
const MAX_OUTPUT_WIDTH = 720

const logs = computed<ExecutionLogEntry[]>(() => store.state.canvas.executionLogs)
const isExecuting = computed(() => store.state.canvas.isExecuting)
const finalOutput = computed(() => store.state.canvas.finalOutput)
const nodeOutputs = computed(() => store.state.canvas.nodeOutputs)

const selectedOutput = computed(() => {
  if (!props.selectedNodeId) return null
  return nodeOutputs.value[props.selectedNodeId] ?? null
})

const showOutputPanel = computed(
  () => selectedOutput.value !== null || finalOutput.value !== null
)

const displayOutput = computed(
  () => selectedOutput.value ?? finalOutput.value
)

onMounted(() => {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved) {
      const { height, width } = JSON.parse(saved)
      if (height) panelHeight.value = clamp(height, MIN_HEIGHT, MAX_HEIGHT)
      if (width) outputWidth.value = clamp(width, MIN_OUTPUT_WIDTH, MAX_OUTPUT_WIDTH)
    }
  } catch {
    // ignore
  }
})

function persistLayout() {
  localStorage.setItem(
    STORAGE_KEY,
    JSON.stringify({ height: panelHeight.value, width: outputWidth.value })
  )
}

function clamp(val: number, min: number, max: number) {
  return Math.min(max, Math.max(min, val))
}

function onHeightDragStart(e: MouseEvent) {
  const startY = e.clientY
  const startH = panelHeight.value

  const onMove = (ev: MouseEvent) => {
    const delta = startY - ev.clientY
    panelHeight.value = clamp(startH + delta, MIN_HEIGHT, MAX_HEIGHT)
  }
  const onUp = () => {
    document.removeEventListener('mousemove', onMove)
    document.removeEventListener('mouseup', onUp)
    document.body.style.cursor = ''
    document.body.style.userSelect = ''
    persistLayout()
  }

  document.body.style.cursor = 'ns-resize'
  document.body.style.userSelect = 'none'
  document.addEventListener('mousemove', onMove)
  document.addEventListener('mouseup', onUp)
}

function onOutputWidthDragStart(e: MouseEvent) {
  const startX = e.clientX
  const startW = outputWidth.value

  const onMove = (ev: MouseEvent) => {
    const delta = startX - ev.clientX
    outputWidth.value = clamp(startW + delta, MIN_OUTPUT_WIDTH, MAX_OUTPUT_WIDTH)
  }
  const onUp = () => {
    document.removeEventListener('mousemove', onMove)
    document.removeEventListener('mouseup', onUp)
    document.body.style.cursor = ''
    document.body.style.userSelect = ''
    persistLayout()
  }

  document.body.style.cursor = 'col-resize'
  document.body.style.userSelect = 'none'
  document.addEventListener('mousemove', onMove)
  document.addEventListener('mouseup', onUp)
}

function formatTime(t: string) {
  try {
    return new Date(t).toLocaleTimeString('zh-CN', { hour12: false })
  } catch {
    return t
  }
}

function levelClass(level: string) {
  const map: Record<string, string> = {
    info: 'text-blue-500',
    success: 'text-green-600',
    error: 'text-red-500',
    warning: 'text-yellow-600',
  }
  return map[level] || 'text-gray-500'
}

function formatOutput(val: any): string {
  if (val === null || val === undefined) return ''
  if (typeof val === 'string') return val
  return JSON.stringify(val, null, 2)
}
</script>

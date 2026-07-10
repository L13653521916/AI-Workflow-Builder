<template>
  <div
    class="border-2 border-dashed rounded-lg p-8 text-center transition-colors"
    :class="isDragging ? 'border-blue-400 bg-blue-50' : 'border-gray-300 hover:border-gray-400'"
    @dragover.prevent="isDragging = true"
    @dragleave.prevent="isDragging = false"
    @drop.prevent="onDrop"
  >
    <input
      ref="fileInput"
      type="file"
      class="hidden"
      :accept="accept"
      :multiple="multiple"
      @change="onFileSelect"
    />

    <div class="text-gray-400 mb-3">
      <div class="text-3xl mb-2">📄</div>
      <p class="text-sm">拖拽文件到此处，或</p>
    </div>

    <el-button size="small" @click="fileInput?.click()">选择文件</el-button>
    <p class="text-xs text-gray-400 mt-3">支持 {{ acceptLabel }} 格式</p>

    <div v-if="uploading" class="mt-4">
      <el-progress :percentage="progress" :stroke-width="6" />
      <p class="text-xs text-gray-500 mt-1">上传中...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const props = withDefaults(defineProps<{
  accept?: string
  acceptLabel?: string
  multiple?: boolean
  uploading?: boolean
  progress?: number
}>(), {
  accept: '.pdf,.txt,.md',
  acceptLabel: 'PDF / TXT / MD',
  multiple: false,
  uploading: false,
  progress: 0,
})

const emit = defineEmits<{
  upload: [file: File]
}>()

const fileInput = ref<HTMLInputElement>()
const isDragging = ref(false)

const ALLOWED = ['.pdf', '.txt', '.md']

function validateFile(file: File): boolean {
  const ext = '.' + file.name.split('.').pop()?.toLowerCase()
  if (!ALLOWED.includes(ext)) {
    ElMessage.warning(`不支持的文件格式，仅支持 ${props.acceptLabel}`)
    return false
  }
  return true
}

function handleFiles(files: FileList | null) {
  if (!files || files.length === 0) return
  const file = files[0]
  if (validateFile(file)) {
    emit('upload', file)
  }
}

function onDrop(event: DragEvent) {
  isDragging.value = false
  handleFiles(event.dataTransfer?.files ?? null)
}

function onFileSelect(event: Event) {
  const input = event.target as HTMLInputElement
  handleFiles(input.files)
  input.value = ''
}
</script>

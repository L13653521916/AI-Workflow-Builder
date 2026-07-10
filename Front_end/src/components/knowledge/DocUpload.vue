<template>
  <div class="h-full flex flex-col">
    <div class="p-4 border-b border-gray-200 bg-white flex items-center gap-3">
      <el-button size="small" @click="emit('back')">
        ← 返回列表
      </el-button>
      <h2 class="text-lg font-semibold text-gray-800">{{ kb?.name || '知识库详情' }}</h2>
      <span v-if="kb" class="text-sm text-gray-400">{{ kb.docCount }} 篇文档</span>
    </div>

    <div class="flex-1 overflow-y-auto p-4 space-y-6">
      <div v-if="kb?.description" class="text-sm text-gray-500 bg-gray-50 rounded-lg p-3">
        {{ kb.description }}
      </div>

      <div>
        <h3 class="text-sm font-medium text-gray-700 mb-3">上传文档</h3>
        <FileUploader
          :uploading="uploading"
          :progress="uploadProgress"
          @upload="handleUpload"
        />
      </div>

      <div>
        <h3 class="text-sm font-medium text-gray-700 mb-3">文档列表</h3>
        <div v-if="loading" class="text-center text-gray-400 py-8">加载中...</div>
        <div v-else-if="documents.length === 0" class="text-center text-gray-400 py-8">
          暂无文档，请上传 PDF / TXT / MD 文件
        </div>
        <div v-else class="space-y-2">
          <div
            v-for="doc in documents"
            :key="doc.id"
            class="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50"
          >
            <div class="min-w-0 flex-1">
              <div class="text-sm font-medium text-gray-800 truncate">{{ doc.filename }}</div>
              <div class="text-xs text-gray-400 mt-1 flex items-center gap-3">
                <span
                  class="inline-flex items-center gap-1"
                  :class="statusColor(doc.status)"
                >
                  <span class="w-1.5 h-1.5 rounded-full bg-current"></span>
                  {{ statusLabel(doc.status) }}
                </span>
                <span>{{ formatDate(doc.createdAt) }}</span>
              </div>
            </div>
            <el-button
              type="danger"
              link
              size="small"
              @click="handleDelete(doc.id, doc.filename)"
            >
              删除
            </el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useStore } from 'vuex'
import { ElMessage, ElMessageBox } from 'element-plus'
import FileUploader from '@/components/common/FileUploader.vue'
import type { Document } from '@/types/knowledge'

const props = defineProps<{
  kbId: number
}>()

const emit = defineEmits<{
  back: []
}>()

const store = useStore()
const loading = ref(false)
const uploading = ref(false)
const uploadProgress = ref(0)

const kb = computed(() => store.getters['knowledge/currentKB'])
const documents = computed<Document[]>(() => store.state.knowledge.documents)

onMounted(async () => {
  store.commit('knowledge/SET_CURRENT_KB', props.kbId)
  loading.value = true
  try {
    await store.dispatch('knowledge/fetchDocuments', props.kbId)
  } finally {
    loading.value = false
  }
})

async function handleUpload(file: File) {
  uploading.value = true
  uploadProgress.value = 0
  try {
    await store.dispatch('knowledge/uploadDocument', {
      kbId: props.kbId,
      file,
      onProgress: (p: number) => { uploadProgress.value = p },
    })
    ElMessage.success('上传成功')
  } catch {
    // handled by interceptor
  } finally {
    uploading.value = false
    uploadProgress.value = 0
  }
}

async function handleDelete(docId: number, filename: string) {
  try {
    await ElMessageBox.confirm(`确定删除文档「${filename}」?`, '删除确认', { type: 'warning' })
  } catch {
    return
  }
  try {
    await store.dispatch('knowledge/deleteDocument', { kbId: props.kbId, docId })
    ElMessage.success('文档已删除')
  } catch {
    // handled by interceptor
  }
}

function statusLabel(status: string) {
  const map: Record<string, string> = {
    processing: '处理中',
    ready: '就绪',
    failed: '失败',
  }
  return map[status] || status
}

function statusColor(status: string) {
  const map: Record<string, string> = {
    processing: 'text-yellow-500',
    ready: 'text-green-500',
    failed: 'text-red-500',
  }
  return map[status] || 'text-gray-400'
}

function formatDate(t: string | null) {
  if (!t) return ''
  return new Date(t).toLocaleString('zh-CN', {
    month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit',
  })
}
</script>

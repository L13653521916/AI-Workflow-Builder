<template>
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    <div
      v-for="kb in knowledgeBases"
      :key="kb.id"
      class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
    >
      <h3 class="font-medium mb-2 text-gray-800">{{ kb.name }}</h3>
      <p class="text-sm text-gray-500 mb-3 line-clamp-2">{{ kb.description || '无描述' }}</p>
      <div class="flex items-center justify-between text-xs text-gray-400 mb-3">
        <span>{{ kb.docCount }} 篇文档</span>
        <span>{{ formatDate(kb.createdAt) }}</span>
      </div>
      <div class="flex gap-2">
        <el-button size="small" type="primary" plain @click="emit('manage', kb.id)">
          管理
        </el-button>
        <el-button size="small" type="danger" plain @click="emit('delete', kb.id)">
          删除
        </el-button>
      </div>
    </div>

    <div
      v-if="knowledgeBases.length === 0"
      class="col-span-full text-center text-gray-400 py-12"
    >
      暂无知识库，点击上方「新建知识库」创建
    </div>
  </div>
</template>

<script setup lang="ts">
import type { KnowledgeBase } from '@/types/knowledge'

defineProps<{
  knowledgeBases: KnowledgeBase[]
}>()

const emit = defineEmits<{
  manage: [id: number]
  delete: [id: number]
}>()

function formatDate(t: string | null) {
  if (!t) return ''
  return new Date(t).toLocaleString('zh-CN', {
    month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit',
  })
}
</script>

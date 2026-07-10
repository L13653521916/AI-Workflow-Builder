<template>
  <div class="w-64 border-r border-gray-200 flex flex-col bg-gray-50 shrink-0">
    <div class="p-3 border-b border-gray-200">
      <el-button type="primary" size="small" class="w-full" @click="$emit('create')">
        + 新建对话
      </el-button>
    </div>
    <div class="flex-1 overflow-y-auto">
      <div
        v-for="conv in conversations"
        :key="conv.id"
        class="group px-3 py-2.5 cursor-pointer hover:bg-gray-100 text-sm flex items-center justify-between transition-colors"
        :class="{ 'bg-blue-50 text-blue-600': conv.id === currentId }"
        @click="$emit('select', conv.id)"
      >
        <span class="truncate flex-1">{{ conv.title || '新对话' }}</span>
        <el-icon
          class="opacity-0 group-hover:opacity-100 shrink-0 ml-1 text-gray-400 hover:text-red-500"
          @click.stop="$emit('delete', conv.id)"
        >
          <Delete />
        </el-icon>
      </div>
      <div v-if="conversations.length === 0" class="p-4 text-gray-400 text-sm text-center">
        暂无对话
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Delete } from '@element-plus/icons-vue'
import type { Conversation } from '@/types/chat'

defineProps<{
  conversations: Conversation[]
  currentId: number | null
}>()

defineEmits<{
  create: []
  select: [id: number]
  delete: [id: number]
}>()
</script>
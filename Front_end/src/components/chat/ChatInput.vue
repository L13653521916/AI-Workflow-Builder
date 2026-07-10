<template>
  <div class="border-t border-gray-200 p-4">
    <div class="max-w-3xl mx-auto flex gap-2 items-end">
      <el-input
        v-model="text"
        type="textarea"
        :rows="1"
        :autosize="{ minRows: 1, maxRows: 5 }"
        placeholder="输入消息... (Enter 发送, Shift+Enter 换行)"
        resize="none"
        @keydown="handleKeydown"
        :disabled="disabled"
      />
      <el-button
        v-if="!disabled"
        type="primary"
        :disabled="!text.trim()"
        @click="handleSend"
      >
        发送
      </el-button>
      <el-button
        v-else
        type="danger"
        @click="$emit('stop')"
      >
        停止
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

defineProps<{ disabled: boolean }>()

const emit = defineEmits<{
  send: [content: string]
  stop: []
}>()

const text = ref('')

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSend()
  }
}

function handleSend() {
  const trimmed = text.value.trim()
  if (!trimmed) return
  emit('send', trimmed)
  text.value = ''
}
</script>
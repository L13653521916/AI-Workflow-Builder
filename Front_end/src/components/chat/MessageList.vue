<template>
  <div ref="listRef" class="flex-1 overflow-y-auto px-4 py-4 space-y-4">
    <MessageItem
      v-for="msg in messages"
      :key="msg.id"
      :message="msg"
      :streaming="loading && msg.id === lastMsgId && msg.role === 'assistant'"
    />
    <div v-if="loading && !hasAssistantMsg" class="flex items-center gap-2 text-gray-400 text-sm pl-11">
      <div class="flex gap-1">
        <span class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style="animation-delay:0ms"></span>
        <span class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style="animation-delay:150ms"></span>
        <span class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style="animation-delay:300ms"></span>
      </div>
      AI 正在思考...
    </div>
    <div ref="bottomAnchor"></div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch, nextTick } from 'vue'
import type { Message } from '@/types/chat'
import MessageItem from './MessageItem.vue'

const props = defineProps<{
  messages: Message[]
  loading: boolean
}>()

const listRef = ref<HTMLDivElement>()
const bottomAnchor = ref<HTMLDivElement>()

const lastMsgId = computed(() => {
  const msgs = props.messages
  return msgs.length > 0 ? msgs[msgs.length - 1].id : null
})

const hasAssistantMsg = computed(() => {
  return props.messages.some(m => m.role === 'assistant' && m.content)
})

function scrollToBottom() {
  nextTick(() => {
    bottomAnchor.value?.scrollIntoView({ behavior: 'smooth' })
  })
}

watch(() => props.messages.length, scrollToBottom)
watch(() => props.messages[props.messages.length - 1]?.content, scrollToBottom)
</script>
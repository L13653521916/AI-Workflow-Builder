<template>
  <div class="flex gap-3" :class="isUser ? 'flex-row-reverse' : ''">
    <div
      class="w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium shrink-0"
      :class="isUser ? 'bg-blue-500 text-white' : 'bg-emerald-500 text-white'"
    >
      {{ isUser ? 'U' : 'AI' }}
    </div>
    <div
      class="max-w-[75%] rounded-2xl px-4 py-2.5 text-sm"
      :class="isUser
        ? 'bg-blue-500 text-white rounded-tr-sm'
        : 'bg-gray-100 text-gray-800 rounded-tl-sm'"
    >
      <template v-if="message.role === 'assistant'">
        <MarkdownRenderer :content="message.content" />
        <span v-if="streaming" class="inline-block w-0.5 h-4 bg-gray-600 ml-0.5 animate-pulse align-middle"></span>
      </template>
      <template v-else-if="message.role === 'system'">
        <span class="text-gray-500 italic">{{ message.content }}</span>
      </template>
      <template v-else>
        <div class="whitespace-pre-wrap">{{ message.content }}</div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Message } from '@/types/chat'
import MarkdownRenderer from '@/components/common/MarkdownRenderer.vue'

const props = defineProps<{
  message: Message
  streaming?: boolean
}>()

const isUser = computed(() => props.message.role === 'user')
</script>
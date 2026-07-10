<template>
  <div class="h-full flex">
    <ConversationList
      :conversations="conversations"
      :current-id="currentId"
      @create="handleCreate"
      @select="handleSelect"
      @delete="handleDelete"
    />
    <div class="flex-1 flex flex-col min-w-0">
      <MessageList :messages="messages" :loading="loading" />
      <ChatInput :disabled="loading" @send="handleSend" @stop="handleStop" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { ElMessageBox } from 'element-plus'
import ConversationList from '@/components/chat/ConversationList.vue'
import MessageList from '@/components/chat/MessageList.vue'
import ChatInput from '@/components/chat/ChatInput.vue'

const store = useStore()

const conversations = computed(() => store.state.chat.conversations)
const currentId = computed(() => store.state.chat.currentConversationId)
const messages = computed(() => store.getters['chat/currentMessages'])
const loading = computed(() => store.state.chat.isLoading)

onMounted(() => {
  store.dispatch('chat/fetchConversations')
})

function handleCreate() {
  store.dispatch('chat/createConversation')
}

function handleSelect(id: number) {
  store.dispatch('chat/selectConversation', id)
}

async function handleDelete(id: number) {
  try {
    await ElMessageBox.confirm('确定删除该对话?', '提示', { type: 'warning' })
    store.dispatch('chat/deleteConversation', id)
  } catch {
    // cancelled
  }
}

function handleSend(content: string) {
  if (!currentId.value) {
    store.dispatch('chat/createConversation').then(() => {
      store.dispatch('chat/sendMessage', content)
    })
  } else {
    store.dispatch('chat/sendMessage', content)
  }
}

function handleStop() {
  store.dispatch('chat/stopStreaming')
}
</script>
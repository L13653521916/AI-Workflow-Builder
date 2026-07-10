import { Module } from 'vuex'
import type { RootState } from '../index'
import type { Conversation, Message } from '@/types/chat'
import * as chatApi from '@/api/chat'
import { sendSSEMessage } from '@/utils/sse'

export interface ChatState {
  conversations: Conversation[]
  currentConversationId: number | null
  isLoading: boolean
  streamingContent: string
  activeController: AbortController | null
}

const chat: Module<ChatState, RootState> = {
  namespaced: true,

  state: () => ({
    conversations: [],
    currentConversationId: null,
    isLoading: false,
    streamingContent: '',
    activeController: null,
  }),

  getters: {
    currentConversation(state): Conversation | undefined {
      return state.conversations.find(c => c.id === state.currentConversationId)
    },
    currentMessages(state): Message[] {
      const conv = state.conversations.find(c => c.id === state.currentConversationId)
      return conv?.messages ?? []
    },
  },

  mutations: {
    SET_CONVERSATIONS(state, list: Conversation[]) {
      state.conversations = list
    },
    SET_CURRENT_CONVERSATION(state, id: number | null) {
      state.currentConversationId = id
    },
    ADD_CONVERSATION(state, conv: Conversation) {
      state.conversations.unshift(conv)
    },
    UPDATE_CONVERSATION(state, updated: Conversation) {
      const idx = state.conversations.findIndex(c => c.id === updated.id)
      if (idx !== -1) Object.assign(state.conversations[idx], updated)
    },
    SET_MESSAGES(state, { conversationId, messages }: { conversationId: number; messages: Message[] }) {
      const conv = state.conversations.find(c => c.id === conversationId)
      if (conv) conv.messages = messages
    },
    APPEND_MESSAGE(state, { conversationId, message }: { conversationId: number; message: Message }) {
      const conv = state.conversations.find(c => c.id === conversationId)
      if (conv) {
        if (!conv.messages) conv.messages = []
        conv.messages.push(message)
      }
    },
    SET_LOADING(state, val: boolean) {
      state.isLoading = val
    },
    SET_STREAMING(state, content: string) {
      state.streamingContent = content
    },
    APPEND_STREAMING(state, chunk: string) {
      state.streamingContent += chunk
    },
    CLEAR_STREAMING(state) {
      state.streamingContent = ''
    },
    SET_CONTROLLER(state, ctrl: AbortController | null) {
      state.activeController = ctrl
    },
    REMOVE_CONVERSATION(state, id: number) {
      state.conversations = state.conversations.filter(c => c.id !== id)
      if (state.currentConversationId === id) {
        state.currentConversationId = state.conversations[0]?.id ?? null
      }
    },
  },

  actions: {
    async fetchConversations({ commit }) {
      const list = await chatApi.getConversations()
      // 逐个加载消息,失败的跳过不阻塞
      const withMessages = await Promise.allSettled(
        list.map(async (conv) => {
          try {
            const detail = await chatApi.getConversationDetail(conv.id)
            return { ...conv, messages: detail.messages } as Conversation
          } catch {
            return { ...conv, messages: [] } as Conversation
          }
        }),
      )
      const results = withMessages
        .filter((r): r is PromiseFulfilledResult<Conversation> => r.status === 'fulfilled')
        .map(r => r.value)
      commit('SET_CONVERSATIONS', results)
    },

    async createConversation({ commit }, title?: string) {
      const conv = await chatApi.createConversation(title)
      conv.messages = []
      commit('ADD_CONVERSATION', conv)
      commit('SET_CURRENT_CONVERSATION', conv.id)
      return conv
    },

    async selectConversation({ commit, state }, id: number) {
      commit('SET_CURRENT_CONVERSATION', id)
      const conv = state.conversations.find(c => c.id === id)
      if (conv && (!conv.messages || conv.messages.length === 0)) {
        try {
          const detail = await chatApi.getConversationDetail(id)
          commit('SET_MESSAGES', { conversationId: id, messages: detail.messages })
        } catch {
          // 静默失败
        }
      }
    },

    async sendMessage({ commit, state, dispatch }, content: string) {
      const convId = state.currentConversationId
      if (!convId) {
        await dispatch('createConversation')
        return dispatch('sendMessage', content)
      }

      // 先把用户消息写入 UI
      const userMsg: Message = {
        id: Date.now(),
        conversation_id: convId,
        role: 'user',
        content,
        created_at: new Date().toISOString(),
      }
      commit('APPEND_MESSAGE', { conversationId: convId, message: userMsg })
      commit('SET_LOADING', true)
      commit('SET_STREAMING', '')

      // 创建占位 assistant 消息
      const assistantMsg: Message = {
        id: Date.now() + 1,
        conversation_id: convId,
        role: 'assistant',
        content: '',
        created_at: new Date().toISOString(),
      }
      commit('APPEND_MESSAGE', { conversationId: convId, message: assistantMsg })

      const controller = sendSSEMessage(
        convId,
        content,
        (event) => {
          if (event.type === 'delta' && event.content) {
            commit('APPEND_STREAMING', event.content)
            assistantMsg.content = state.streamingContent
          } else if (event.type === 'done') {
            assistantMsg.id = event.message_id ?? assistantMsg.id
            assistantMsg.created_at = event.created_at ?? assistantMsg.created_at
            assistantMsg.content = state.streamingContent
            commit('CLEAR_STREAMING')
            commit('SET_LOADING', false)
            commit('SET_CONTROLLER', null)
            dispatch('refreshConversationTitle', convId)
          } else if (event.type === 'error') {
            assistantMsg.content = `错误: ${event.content}`
            commit('CLEAR_STREAMING')
            commit('SET_LOADING', false)
            commit('SET_CONTROLLER', null)
          }
        },
        () => {
          assistantMsg.content = assistantMsg.content || '网络错误,请重试'
          commit('CLEAR_STREAMING')
          commit('SET_LOADING', false)
          commit('SET_CONTROLLER', null)
        },
      )
      commit('SET_CONTROLLER', controller)
    },

    async refreshConversationTitle({ commit }, convId: number) {
      try {
        const detail = await chatApi.getConversationDetail(convId)
        commit('UPDATE_CONVERSATION', { id: convId, title: detail.title, updated_at: detail.updated_at })
      } catch {
        // 静默
      }
    },

    stopStreaming({ state, commit }) {
      state.activeController?.abort()
      commit('SET_CONTROLLER', null)
      commit('SET_LOADING', false)
    },

    async deleteConversation({ commit }, id: number) {
      await chatApi.deleteConversation(id)
      commit('REMOVE_CONVERSATION', id)
    },
  },
}

export default chat
import request from '@/utils/request'
import type { Conversation, ConversationDetail, Message } from '@/types/chat'

export function getConversations(): Promise<Conversation[]> {
  return request.get('/chat/conversations')
}

export function createConversation(title = '新对话'): Promise<Conversation> {
  return request.post('/chat/conversations', { title })
}

export function getConversationDetail(id: number): Promise<ConversationDetail> {
  return request.get(`/chat/conversations/${id}`)
}

export function deleteConversation(id: number): Promise<void> {
  return request.delete(`/chat/conversations/${id}`)
}

/** 返回 EventSource URL 字符串供 sse.ts 使用 */
export function sendMessageStreamUrl(conversationId: number): string {
  return `/api/chat/conversations/${conversationId}/messages`
}

/** 非流式发送(备用) */
export function sendMessage(conversationId: number, content: string): Promise<Message> {
  return request.post(`/chat/conversations/${conversationId}/messages`, { content })
}
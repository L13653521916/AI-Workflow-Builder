export interface Message {
  id: number
  conversation_id: number
  role: 'user' | 'assistant' | 'system'
  content: string
  created_at: string | null
}

export interface Conversation {
  id: number
  title: string
  created_at: string | null
  updated_at: string | null
  messages?: Message[]
}

export interface ConversationDetail extends Conversation {
  messages: Message[]
}
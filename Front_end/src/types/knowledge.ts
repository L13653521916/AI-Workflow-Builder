export interface KnowledgeBase {
  id: number
  name: string
  description: string
  docCount: number
  createdAt: string
}

export interface Document {
  id: number
  filename: string
  chunkCount: number
  status: 'processing' | 'ready' | 'failed'
  createdAt: string
}
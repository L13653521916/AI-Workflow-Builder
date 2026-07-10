import request from '@/utils/request'
import type { KnowledgeBase, Document } from '@/types/knowledge'

export function getKnowledgeBases(): Promise<KnowledgeBase[]> {
  return request.get('/knowledge')
}

export function createKnowledgeBase(data: { name: string; description: string }): Promise<KnowledgeBase> {
  return request.post('/knowledge', data)
}

export function deleteKnowledgeBase(id: number): Promise<any> {
  return request.delete(`/knowledge/${id}`)
}

export function getDocuments(kbId: number): Promise<Document[]> {
  return request.get(`/knowledge/${kbId}/documents`)
}

export function uploadDocument(kbId: number, file: File, onProgress?: (pct: number) => void): Promise<Document> {
  const formData = new FormData()
  formData.append('file', file)
  return request.post(`/knowledge/${kbId}/upload`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (e) => {
      if (e.total && onProgress) {
        onProgress(Math.round((e.loaded / e.total) * 100))
      }
    }
  })
}

export function deleteDocument(kbId: number, docId: number): Promise<any> {
  return request.delete(`/knowledge/${kbId}/documents/${docId}`)
}
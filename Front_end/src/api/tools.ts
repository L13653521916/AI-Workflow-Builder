import request from '@/utils/request'
import type { Tool, ToolCreateBody, ToolHandler } from '@/types/tools'

export function getTools(category?: string): Promise<Tool[]> {
  const params = category ? { category } : {}
  return request.get('/tools', { params })
}

export function getToolHandlers(): Promise<ToolHandler[]> {
  return request.get('/tools/handlers')
}

export function getToolDetail(id: number): Promise<Tool> {
  return request.get(`/tools/${id}`)
}

export function createTool(data: ToolCreateBody): Promise<Tool> {
  return request.post('/tools', data)
}

export function deleteTool(id: number): Promise<any> {
  return request.delete(`/tools/${id}`)
}

export function testTool(id: number, params: Record<string, any>): Promise<any> {
  return request.post(`/tools/${id}/test`, { params })
}

export type { Tool }

import request from '@/utils/request'
import type {
  ModelProfile,
  ModelProfileDetail,
  ModelProfileCreateBody,
  ModelProfileUpdateBody,
} from '@/types/models'

export function getModelProfiles(): Promise<ModelProfile[]> {
  return request.get('/models')
}

export function getModelProfile(id: number): Promise<ModelProfileDetail> {
  return request.get(`/models/${id}`)
}

export function createModelProfile(data: ModelProfileCreateBody): Promise<ModelProfileDetail> {
  return request.post('/models', data)
}

export function updateModelProfile(id: number, data: ModelProfileUpdateBody): Promise<ModelProfileDetail> {
  return request.put(`/models/${id}`, data)
}

export function deleteModelProfile(id: number): Promise<any> {
  return request.delete(`/models/${id}`)
}

export function testModelProfile(id: number, message?: string): Promise<any> {
  return request.post(`/models/${id}/test`, { message: message || '你好，请回复 OK' }, { skipLoading: true })
}

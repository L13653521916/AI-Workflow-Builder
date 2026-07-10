import request from '@/utils/request'
import type { Workflow, WorkflowCreateBody, WorkflowUpdateBody } from '@/types/workflow'

export function getWorkflows(): Promise<Workflow[]> {
  return request.get('/workflows')
}

export function getWorkflow(id: number): Promise<Workflow> {
  return request.get(`/workflows/${id}`)
}

export function createWorkflow(data: WorkflowCreateBody): Promise<Workflow> {
  return request.post('/workflows', data)
}

export function updateWorkflow(id: number, data: WorkflowUpdateBody): Promise<Workflow> {
  return request.put(`/workflows/${id}`, data)
}

export function deleteWorkflow(id: number): Promise<any> {
  return request.delete(`/workflows/${id}`)
}
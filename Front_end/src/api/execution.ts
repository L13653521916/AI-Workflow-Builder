import request from '@/utils/request'
import type { WorkflowRunDetail, WorkflowRunSummary } from '@/types/execution'
import type { CanvasEdge, CanvasNode } from '@/types/workflow'

export function getWorkflowRuns(workflowId: number): Promise<WorkflowRunSummary[]> {
  return request.get(`/workflows/${workflowId}/runs`)
}

export function getWorkflowRun(workflowId: number, runId: number): Promise<WorkflowRunDetail> {
  return request.get(`/workflows/${workflowId}/runs/${runId}`)
}

export function getRunWorkflowUrl(workflowId: number): string {
  return `/api/workflows/${workflowId}/run`
}

export interface RunWorkflowPayload {
  input?: any
  graph_json?: { nodes: CanvasNode[]; edges: CanvasEdge[] }
}

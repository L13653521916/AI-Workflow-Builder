export type NodeExecStatus = 'idle' | 'running' | 'success' | 'failed'

export interface ExecutionLogEntry {
  time: string
  level: 'info' | 'success' | 'error' | 'warning'
  message: string
  node_id?: string | null
}

export interface WorkflowRunSummary {
  id: number
  workflow_id: number
  status: string
  input_json: any
  output_json: any
  started_at: string | null
  finished_at: string | null
}

export interface WorkflowRunDetail extends WorkflowRunSummary {
  logs_json: ExecutionLogEntry[]
}

export type WorkflowSSEEventType =
  | 'run_start'
  | 'node_start'
  | 'node_success'
  | 'node_failed'
  | 'log'
  | 'done'
  | 'error'

export interface WorkflowSSEEvent {
  type: WorkflowSSEEventType
  run_id?: number
  workflow_id?: number
  node_id?: string
  node_type?: string
  label?: string
  output?: any
  error?: string
  content?: string
  message?: string
  level?: string
  time?: string
  status?: string
}

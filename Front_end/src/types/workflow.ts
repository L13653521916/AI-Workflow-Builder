// ── 节点类型枚举 ─────────────────────────────────────
export type NodeType = 'start' | 'llm' | 'rag' | 'tool' | 'condition' | 'end'

// ── 画布上的节点（用于 store / Vue Flow）─────────────
export interface CanvasNode {
  id: string
  type: NodeType
  label: string
  config: Record<string, any>
  position: { x: number; y: number }
}

// ── 画布上的边 ───────────────────────────────────────
export interface CanvasEdge {
  id: string
  source: string
  sourceHandle?: string
  target: string
  targetHandle?: string
  label?: string
}

// ── 后端 Workflow 模型（与 schema.py WorkflowResponse 对齐）─
export interface Workflow {
  id: number
  name: string
  description: string
  graph_json: {
    nodes: CanvasNode[]
    edges: CanvasEdge[]
  }
  status: 'draft' | 'published'
  created_at: string
  updated_at: string | null
}

// ── 创建 / 更新请求体 ────────────────────────────────
export interface WorkflowCreateBody {
  name: string
  description?: string
}

export interface WorkflowUpdateBody {
  name?: string
  description?: string
  graph_json?: { nodes: CanvasNode[]; edges: CanvasEdge[] }
  status?: 'draft' | 'published'
}
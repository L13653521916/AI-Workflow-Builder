import * as workflowApi from '@/api/workflow'
import * as executionApi from '@/api/execution'
import { runWorkflowSSE } from '@/utils/workflowSse'
import type { CanvasNode, CanvasEdge } from '@/types/workflow'
import type { ExecutionLogEntry, NodeExecStatus, WorkflowRunSummary } from '@/types/execution'

function normalizeNode(raw: any): CanvasNode {
  if (raw.data && raw.label === undefined) {
    const { label, ...config } = raw.data
    return {
      id: raw.id,
      type: raw.type,
      label: label || raw.type,
      config,
      position: raw.position || { x: 0, y: 0 },
    }
  }
  return {
    id: raw.id,
    type: raw.type,
    label: raw.label || raw.type,
    config: raw.config || {},
    position: raw.position || { x: 0, y: 0 },
  }
}

export default {
  namespaced: true,

  state: () => ({
    workflowId: null as number | null,
    workflowName: '未命名工作流',
    workflowDescription: '',
    nodes: [] as CanvasNode[],
    edges: [] as CanvasEdge[],
    selectedNodeId: null as string | null,
    selectedEdgeId: null as string | null,
    isDirty: false,
    saving: false,
    loadVersion: 0,
    // Phase 7: execution
    isExecuting: false,
    nodeExecStatus: {} as Record<string, NodeExecStatus>,
    nodeOutputs: {} as Record<string, any>,
    executionLogs: [] as ExecutionLogEntry[],
    currentRunId: null as number | null,
    finalOutput: null as any,
    runHistory: [] as WorkflowRunSummary[],
  }),

  getters: {
    selectedNode(state): CanvasNode | null {
      if (!state.selectedNodeId) return null
      return state.nodes.find((n) => n.id === state.selectedNodeId) || null
    },
    selectedEdge(state): CanvasEdge | null {
      if (!state.selectedEdgeId) return null
      return state.edges.find((e) => e.id === state.selectedEdgeId) || null
    },
  },

  mutations: {
    SET_WORKFLOW_META(
      state,
      payload: { id?: number | null; name?: string; description?: string }
    ) {
      if (payload.id !== undefined && payload.id !== 0) {
        state.workflowId = payload.id
      }
      if (payload.name !== undefined) state.workflowName = payload.name
      if (payload.description !== undefined) state.workflowDescription = payload.description
      state.isDirty = true
    },

    SET_WORKFLOW_ID(state, id: number) {
      state.workflowId = id
    },

    LOAD_WORKFLOW(
      state,
      payload: {
        id: number
        name: string
        description?: string
        nodes: any[]
        edges: CanvasEdge[]
      }
    ) {
      state.workflowId = payload.id
      state.workflowName = payload.name
      state.workflowDescription = payload.description || ''
      state.nodes = (payload.nodes || []).map(normalizeNode)
      state.edges = payload.edges || []
      state.selectedNodeId = null
      state.selectedEdgeId = null
      state.isDirty = false
      state.loadVersion++
    },

    RESET(state) {
      state.workflowId = null
      state.workflowName = '未命名工作流'
      state.workflowDescription = ''
      state.nodes = []
      state.edges = []
      state.selectedNodeId = null
      state.selectedEdgeId = null
      state.isDirty = false
      state.loadVersion++
    },

    SET_SELECTED_NODE(state, id: string | null) {
      state.selectedNodeId = id
      if (id) state.selectedEdgeId = null
    },

    SET_SELECTED_EDGE(state, id: string | null) {
      state.selectedEdgeId = id
      if (id) state.selectedNodeId = null
    },

    ADD_NODE(state, node: CanvasNode) {
      state.nodes.push(node)
      state.isDirty = true
    },

    UPDATE_NODE(state, node: CanvasNode) {
      const idx = state.nodes.findIndex((n) => n.id === node.id)
      if (idx !== -1) {
        state.nodes[idx] = { ...node }
        state.isDirty = true
      }
    },

    SYNC_NODE_POSITIONS(
      state,
      positions: { id: string; position: { x: number; y: number } }[]
    ) {
      let changed = false
      for (const { id, position } of positions) {
        const node = state.nodes.find((n) => n.id === id)
        if (
          node &&
          (node.position.x !== position.x || node.position.y !== position.y)
        ) {
          node.position = { ...position }
          changed = true
        }
      }
      if (changed) state.isDirty = true
    },

    REMOVE_NODE(state, id: string) {
      state.nodes = state.nodes.filter((n) => n.id !== id)
      state.edges = state.edges.filter((e) => e.source !== id && e.target !== id)
      if (state.selectedNodeId === id) state.selectedNodeId = null
      state.isDirty = true
    },

    ADD_EDGE(state, edge: CanvasEdge) {
      const exists = state.edges.some(
        (e) =>
          e.source === edge.source &&
          e.target === edge.target &&
          e.sourceHandle === edge.sourceHandle &&
          e.targetHandle === edge.targetHandle
      )
      if (!exists) {
        state.edges.push(edge)
        state.isDirty = true
      }
    },

    REMOVE_EDGE(state, id: string) {
      state.edges = state.edges.filter((e) => e.id !== id)
      if (state.selectedEdgeId === id) state.selectedEdgeId = null
      state.isDirty = true
    },

    SET_EDGES(state, edges: CanvasEdge[]) {
      state.edges = edges
      state.isDirty = true
    },

    SET_DIRTY(state, val: boolean) {
      state.isDirty = val
    },

    SET_SAVING(state, val: boolean) {
      state.saving = val
    },

    RESET_EXECUTION(state) {
      state.nodeExecStatus = {}
      state.nodeOutputs = {}
      state.executionLogs = []
      state.currentRunId = null
      state.finalOutput = null
    },

    SET_EXECUTING(state, val: boolean) {
      state.isExecuting = val
    },

    SET_NODE_EXEC_STATUS(state, payload: { nodeId: string; status: NodeExecStatus }) {
      state.nodeExecStatus[payload.nodeId] = payload.status
    },

    SET_NODE_OUTPUT(state, payload: { nodeId: string; output: any }) {
      state.nodeOutputs[payload.nodeId] = payload.output
    },

    ADD_EXECUTION_LOG(state, entry: ExecutionLogEntry) {
      state.executionLogs.push(entry)
    },

    SET_CURRENT_RUN_ID(state, id: number | null) {
      state.currentRunId = id
    },

    SET_FINAL_OUTPUT(state, output: any) {
      state.finalOutput = output
    },

    SET_RUN_HISTORY(state, runs: WorkflowRunSummary[]) {
      state.runHistory = runs
    },
  },

  actions: {
    newCanvas({ commit }) {
      commit('RESET')
    },

    async load({ commit }, id: number) {
      const wf = await workflowApi.getWorkflow(id)
      const graph = wf.graph_json || {}
      commit('LOAD_WORKFLOW', {
        id: wf.id,
        name: wf.name,
        description: wf.description,
        nodes: graph.nodes || [],
        edges: graph.edges || [],
      })
    },

    async save({ state, commit }) {
      commit('SET_SAVING', true)
      try {
        const graph_json = {
          nodes: state.nodes,
          edges: state.edges,
        }
        const body = {
          name: state.workflowName || '未命名工作流',
          description: state.workflowDescription,
          graph_json,
        }

        if (state.workflowId) {
          await workflowApi.updateWorkflow(state.workflowId, body)
        } else {
          const wf = await workflowApi.createWorkflow({
            name: body.name,
            description: body.description,
          })
          commit('SET_WORKFLOW_ID', wf.id)
          await workflowApi.updateWorkflow(wf.id, body)
        }
        commit('SET_DIRTY', false)
      } finally {
        commit('SET_SAVING', false)
      }
    },

    async deleteWorkflow({ state, commit }, id: number) {
      await workflowApi.deleteWorkflow(id)
      if (state.workflowId === id) {
        commit('RESET')
      }
    },

    async fetchRunHistory({ state, commit }) {
      if (!state.workflowId) return
      const runs = await executionApi.getWorkflowRuns(state.workflowId)
      commit('SET_RUN_HISTORY', runs)
    },

    runWorkflow({ state, commit }, payload: { input?: any } = {}) {
      if (!state.workflowId) {
        return Promise.reject(new Error('请先保存工作流'))
      }

      const input_data = payload?.input ?? {}

      commit('RESET_EXECUTION')
      commit('SET_EXECUTING', true)

      const workflowId = state.workflowId
      const graph_json = { nodes: state.nodes, edges: state.edges }

      return new Promise<void>((resolve, reject) => {
        runWorkflowSSE(
          workflowId,
          { input: input_data, graph_json },
          (event) => {
            switch (event.type) {
              case 'run_start':
                commit('SET_CURRENT_RUN_ID', event.run_id ?? null)
                break
              case 'node_start':
                if (event.node_id) {
                  commit('SET_NODE_EXEC_STATUS', { nodeId: event.node_id, status: 'running' })
                }
                break
              case 'node_success':
                if (event.node_id) {
                  commit('SET_NODE_EXEC_STATUS', { nodeId: event.node_id, status: 'success' })
                  commit('SET_NODE_OUTPUT', { nodeId: event.node_id, output: event.output })
                }
                break
              case 'node_failed':
                if (event.node_id) {
                  commit('SET_NODE_EXEC_STATUS', { nodeId: event.node_id, status: 'failed' })
                  if (event.error) {
                    commit('SET_NODE_OUTPUT', { nodeId: event.node_id, output: { error: event.error } })
                  }
                }
                break
              case 'log':
                commit('ADD_EXECUTION_LOG', {
                  time: event.time || new Date().toISOString(),
                  level: (event.level as ExecutionLogEntry['level']) || 'info',
                  message: event.message || '',
                  node_id: event.node_id,
                })
                break
              case 'done':
                commit('SET_FINAL_OUTPUT', event.output)
                commit('SET_EXECUTING', false)
                resolve()
                break
              case 'error':
                commit('SET_EXECUTING', false)
                reject(new Error(event.content || '执行失败'))
                break
            }
          },
          () => {
            commit('SET_EXECUTING', false)
            reject(new Error('SSE 连接失败'))
          },
        )
      })
    },
  },
}

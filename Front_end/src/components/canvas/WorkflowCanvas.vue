<template>
  <div
    class="flex-1 h-full relative"
    tabindex="0"
    @drop="onDrop"
    @dragover="onDragOver"
    @keydown="onKeyDown"
  >
    <VueFlow
      :key="store.state.canvas.loadVersion"
      v-model:nodes="flowNodes"
      v-model:edges="flowEdges"
      :node-types="(nodeTypes as any)"
      class="workflow-canvas bg-gray-50"
      :fit-view-on-init="false"
      :default-edge-options="{ type: 'smoothstep' }"
      @connect="onConnect"
      @node-click="onNodeClick"
      @edge-click="onEdgeClick"
      @pane-click="onPaneClick"
      @node-drag-stop="onNodeDragStop"
    >
      <Background :gap="16" pattern-color="#d1d5db" />
      <MiniMap />
    </VueFlow>

    <div
      v-if="store.state.canvas.nodes.length === 0"
      class="absolute inset-0 flex items-center justify-center pointer-events-none"
    >
      <div class="text-center text-gray-400">
        <div class="text-4xl mb-2 font-light">+</div>
        <p class="text-sm">从左侧拖拽节点到画布</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, markRaw, watch, nextTick } from 'vue'
import {
  VueFlow,
  useVueFlow,
  type Connection,
  type Edge,
  type EdgeMouseEvent,
  type Node,
  type NodeDragEvent,
  type NodeMouseEvent,
} from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { MiniMap } from '@vue-flow/minimap'
import { useStore } from 'vuex'
import type { CanvasNode, CanvasEdge } from '@/types/workflow'

import StartNode from './nodes/StartNode.vue'
import LLMNode from './nodes/LLMNode.vue'
import RAGNode from './nodes/RAGNode.vue'
import ToolNode from './nodes/ToolNode.vue'
import ConditionNode from './nodes/ConditionNode.vue'
import EndNode from './nodes/EndNode.vue'

const store = useStore()
const { screenToFlowCoordinate, fitView } = useVueFlow()

const nodeTypes = {
  start: markRaw(StartNode),
  llm: markRaw(LLMNode),
  rag: markRaw(RAGNode),
  tool: markRaw(ToolNode),
  condition: markRaw(ConditionNode),
  end: markRaw(EndNode),
}

function toFlowNode(node: CanvasNode) {
  return {
    id: node.id,
    type: node.type,
    position: { x: node.position.x, y: node.position.y },
    data: { label: node.label, ...node.config },
  }
}

const flowNodes = computed({
  get: () => store.state.canvas.nodes.map(toFlowNode),
  set: (nodes: Node[]) => {
    store.commit(
      'canvas/SYNC_NODE_POSITIONS',
      nodes.map((n: Node) => ({ id: n.id, position: n.position }))
    )
  },
})

const flowEdges = computed({
  get: () =>
    store.state.canvas.edges.map((e: CanvasEdge) => ({
      id: e.id,
      source: e.source,
      target: e.target,
      sourceHandle: e.sourceHandle,
      targetHandle: e.targetHandle,
      label: e.label,
      type: 'smoothstep',
      selected: e.id === store.state.canvas.selectedEdgeId,
      style: e.id === store.state.canvas.selectedEdgeId
        ? { stroke: '#3b82f6', strokeWidth: 2 }
        : undefined,
    })),
  set: (edges: Edge[]) => {
    store.commit(
      'canvas/SET_EDGES',
      edges.map((e: Edge) => ({
        id: e.id,
        source: e.source,
        target: e.target,
        sourceHandle: e.sourceHandle,
        targetHandle: e.targetHandle,
        label: e.label,
      }))
    )
  },
})

// 加载工作流后居中显示，但不改变节点相对位置
watch(
  () => store.state.canvas.workflowId,
  async (id) => {
    if (!id || store.state.canvas.nodes.length === 0) return
    await nextTick()
    fitView({ padding: 0.2, duration: 300 })
  }
)

function onDragOver(event: DragEvent) {
  event.preventDefault()
  if (event.dataTransfer) event.dataTransfer.dropEffect = 'move'
}

function onDrop(event: DragEvent) {
  event.preventDefault()
  const raw = event.dataTransfer?.getData('application/vueflow')
  if (!raw) return

  const nodeType = JSON.parse(raw)
  const position = screenToFlowCoordinate({
    x: event.clientX,
    y: event.clientY,
  })

  store.commit('canvas/ADD_NODE', {
    id: `node_${Date.now()}`,
    type: nodeType.type,
    label: nodeType.label,
    position,
    config: {},
  })
}

function onConnect(connection: Connection) {
  if (!connection.source || !connection.target) return
  store.commit('canvas/ADD_EDGE', {
    id: `edge_${Date.now()}`,
    source: connection.source,
    target: connection.target,
    sourceHandle: connection.sourceHandle ?? undefined,
    targetHandle: connection.targetHandle ?? undefined,
  } satisfies CanvasEdge)
}

function onNodeClick({ node }: NodeMouseEvent) {
  store.commit('canvas/SET_SELECTED_NODE', node.id)
}

function onEdgeClick({ edge }: EdgeMouseEvent) {
  store.commit('canvas/SET_SELECTED_EDGE', edge.id)
}

function onPaneClick() {
  store.commit('canvas/SET_SELECTED_NODE', null)
  store.commit('canvas/SET_SELECTED_EDGE', null)
}

function onNodeDragStop({ node }: NodeDragEvent) {
  store.commit('canvas/SYNC_NODE_POSITIONS', [{
    id: node.id,
    position: { x: node.position.x, y: node.position.y },
  }])
}

function onKeyDown(event: KeyboardEvent) {
  if (event.key !== 'Delete' && event.key !== 'Backspace') return
  const target = event.target as HTMLElement
  if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA') return

  const edgeId = store.state.canvas.selectedEdgeId
  if (edgeId) {
    event.preventDefault()
    store.commit('canvas/REMOVE_EDGE', edgeId)
  }
}
</script>

<style>
.workflow-canvas {
  width: 100%;
  height: 100%;
}
</style>

import { computed } from 'vue'
import { useStore } from 'vuex'
import type { NodeExecStatus } from '@/types/execution'

export function useNodeExecStatus(nodeId: string) {
  const store = useStore()
  const execStatus = computed<NodeExecStatus>(
    () => store.state.canvas.nodeExecStatus?.[nodeId] || 'idle'
  )
  return { execStatus }
}

export function nodeExecRingClass(status: NodeExecStatus, selected: boolean): string {
  if (status === 'running') return 'ring-2 ring-yellow-400 shadow-md bg-yellow-50/40'
  if (status === 'success') return 'ring-2 ring-green-500 shadow-md bg-green-50/40'
  if (status === 'failed') return 'ring-2 ring-red-500 shadow-md bg-red-50/40'
  return selected ? 'ring-2 ring-blue-500 shadow-md' : 'hover:shadow-md'
}

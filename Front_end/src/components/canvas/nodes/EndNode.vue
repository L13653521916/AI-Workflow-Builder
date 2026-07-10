<template>
  <div
    class="group rounded-lg shadow-sm min-w-[180px] transition-all duration-150 select-none"
    :class="nodeExecRingClass(execStatus, selected)"
  >
    <div class="px-3 py-2 bg-gray-100 border-b border-gray-200 rounded-t-lg flex items-center justify-between">
      <span class="text-xs font-semibold text-gray-600">{{ data.label }}</span>
      <button
        class="opacity-0 group-hover:opacity-100 text-gray-400 hover:text-red-500 transition-opacity text-xs leading-none px-1"
        @click.stop="handleDelete"
        title="删除节点"
      >&#10005;</button>
    </div>
    <div class="px-3 py-2 text-xs text-gray-600">
      <div class="flex items-center gap-1.5">
        <span class="inline-block w-2 h-2 rounded-full bg-gray-400"></span>
        输出结果
      </div>
    </div>
    <Handle type="target" :position="Position.Top" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Handle, Position, useNode } from '@vue-flow/core'
import { useStore } from 'vuex'
import { useNodeExecStatus, nodeExecRingClass } from '@/composables/useNodeExecStatus'

const store = useStore()
const { id } = useNode()
const { execStatus } = useNodeExecStatus(id)
const selected = computed(() => store.state.canvas.selectedNodeId === id)

defineProps<{ id: string; data: any }>()

function handleDelete() {
  store.commit('canvas/REMOVE_NODE', id)
}
</script>
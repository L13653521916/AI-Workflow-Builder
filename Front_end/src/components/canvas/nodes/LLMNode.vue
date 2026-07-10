<template>
  <div
    class="group rounded-lg shadow-sm min-w-[180px] transition-all duration-150 select-none"
    :class="nodeExecRingClass(execStatus, selected)"
  >
    <div class="px-3 py-2 bg-blue-50 border-b border-blue-200 rounded-t-lg flex items-center justify-between">
      <span class="text-xs font-semibold text-blue-700">{{ data.label }}</span>
      <button
        class="opacity-0 group-hover:opacity-100 text-gray-400 hover:text-red-500 transition-opacity text-xs leading-none px-1"
        @click.stop="handleDelete"
        title="删除节点"
      >&#10005;</button>
    </div>
    <div class="px-3 py-2 text-xs text-gray-600">
      <div class="flex items-center gap-1.5">
        <span class="inline-block w-2 h-2 rounded-full bg-blue-400"></span>
        配置: {{ profileLabel }}
      </div>
      <div v-if="data.prompt" class="mt-1 text-gray-400 truncate max-w-[160px]">
        {{ data.prompt }}
      </div>
    </div>
    <Handle type="target" :position="Position.Top" />
    <Handle type="source" :position="Position.Bottom" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Handle, Position } from '@vue-flow/core'
import { useStore } from 'vuex'
import { useNodeExecStatus, nodeExecRingClass } from '@/composables/useNodeExecStatus'

const props = defineProps<{
  id: string
  data: any
}>()

const store = useStore()
const { execStatus } = useNodeExecStatus(props.id)

const selected = computed(
  () => store.state.canvas.selectedNodeId === props.id
)

const profileLabel = computed(() => {
  if (props.data.modelProfileName) return props.data.modelProfileName
  const id = props.data.modelProfileId
  if (id) {
    const p = store.state.models?.profiles?.find((x: { id: number }) => x.id === id)
    if (p) return p.name
    return `配置 #${id}`
  }
  const def = store.state.models?.profiles?.find((x: { isDefault: boolean }) => x.isDefault)
  return def ? `默认 · ${def.name}` : '默认配置'
})

function handleDelete() {
  store.commit('canvas/REMOVE_NODE', props.id)
}
</script>
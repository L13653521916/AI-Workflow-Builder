<template>
  <div class="w-56 border-r border-gray-200 bg-white flex flex-col overflow-hidden shrink-0">
    <div class="p-3 border-b border-gray-200">
      <h3 class="text-xs font-semibold text-gray-500 uppercase tracking-wider">节点面板</h3>
    </div>

    <div class="flex-1 overflow-y-auto p-3 space-y-4">
      <div v-for="group in nodeGroups" :key="group.title">
        <div class="text-[11px] font-medium text-gray-400 mb-2">{{ group.title }}</div>
        <div class="space-y-1.5">
          <div
            v-for="node in group.nodes"
            :key="node.type"
            class="flex items-center gap-2.5 p-2 rounded-lg border border-gray-100 cursor-grab active:cursor-grabbing hover:border-blue-300 hover:bg-blue-50/50 transition-all select-none"
            draggable="true"
            @dragstart="onDragStart($event, node)"
          >
            <div
              class="w-7 h-7 rounded-md flex items-center justify-center text-white text-xs font-bold shrink-0"
              :class="node.color"
            >
              {{ node.icon }}
            </div>
            <div class="min-w-0">
              <div class="text-xs font-medium text-gray-700 truncate">{{ node.label }}</div>
              <div class="text-[10px] text-gray-400 truncate">{{ node.desc }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const nodeGroups = [
  {
    title: '流程控制',
    nodes: [
      { type: 'start', label: '起始', desc: '工作流入口', icon: 'S', color: 'bg-gray-500' },
      { type: 'end', label: '输出', desc: '工作流出口', icon: 'E', color: 'bg-gray-400' },
      { type: 'condition', label: '条件判断', desc: 'if/else 分支', icon: 'C', color: 'bg-purple-500' },
    ],
  },
  {
    title: 'AI 节点',
    nodes: [
      { type: 'llm', label: 'LLM 推理', desc: '调用大语言模型', icon: 'L', color: 'bg-blue-500' },
      { type: 'rag', label: 'RAG 检索', desc: '从知识库检索', icon: 'R', color: 'bg-green-500' },
    ],
  },
  {
    title: '工具',
    nodes: [
      { type: 'tool', label: '工具调用', desc: '调用外部工具', icon: 'T', color: 'bg-orange-500' },
    ],
  },
]

function onDragStart(event: DragEvent, node: { type: string; label: string }) {
  event.dataTransfer?.setData(
    'application/vueflow',
    JSON.stringify({ type: node.type, label: node.label })
  )
  if (event.dataTransfer) event.dataTransfer.effectAllowed = 'move'
}
</script>

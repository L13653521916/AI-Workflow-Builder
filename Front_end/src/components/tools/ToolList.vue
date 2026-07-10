<template>
  <div>
    <div class="flex items-center gap-2 mb-4 flex-wrap">
      <el-radio-group v-model="activeCategory" size="small">
        <el-radio-button label="">全部</el-radio-button>
        <el-radio-button
          v-for="cat in categories"
          :key="cat"
          :label="cat"
        >
          {{ categoryLabel(cat) }}
        </el-radio-button>
      </el-radio-group>
    </div>

    <div v-if="loading" class="text-center text-gray-400 py-12">加载中...</div>
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="tool in filteredTools"
        :key="tool.id"
        class="border border-gray-200 rounded-lg p-4 hover:shadow-md hover:border-orange-300 transition-all"
      >
        <div class="flex items-start justify-between mb-2">
          <h3 class="font-medium text-gray-800 cursor-pointer" @click="emit('select', tool)">
            {{ toolDisplayName(tool.name, tool.description) }}
          </h3>
          <span class="text-[10px] px-2 py-0.5 rounded-full bg-orange-50 text-orange-600 shrink-0">
            {{ categoryLabel(tool.category) }}
          </span>
        </div>
        <p class="text-sm text-gray-500 line-clamp-2 mb-3">{{ tool.description }}</p>
        <div class="flex gap-2">
          <el-button size="small" type="primary" plain @click="emit('select', tool)">
            查看详情
          </el-button>
          <el-button
            v-if="isCustomTool(tool)"
            size="small"
            type="danger"
            plain
            @click="emit('delete', tool)"
          >
            删除
          </el-button>
        </div>
      </div>
    </div>

    <div v-if="!loading && filteredTools.length === 0" class="text-center text-gray-400 py-12">
      暂无可用工具
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Tool } from '@/types/tools'
import { toolDisplayName, categoryLabel, BUILTIN_TOOL_NAMES } from '@/utils/toolLabels'

const props = defineProps<{
  tools: Tool[]
  loading?: boolean
}>()

const emit = defineEmits<{
  select: [tool: Tool]
  delete: [tool: Tool]
}>()

const activeCategory = ref('')

const categories = computed(() => {
  const cats = new Set(props.tools.map(t => t.category))
  return Array.from(cats).sort()
})

const filteredTools = computed(() => {
  if (!activeCategory.value) return props.tools
  return props.tools.filter(t => t.category === activeCategory.value)
})

function isCustomTool(tool: Tool) {
  return !BUILTIN_TOOL_NAMES.has(tool.name)
}
</script>

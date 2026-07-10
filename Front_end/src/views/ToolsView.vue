<template>
  <div class="h-full flex flex-col">
    <div class="p-4 border-b border-gray-200 bg-white shrink-0 flex items-center justify-between">
      <div>
        <h2 class="text-lg font-semibold text-gray-800">工具市场</h2>
        <p class="text-xs text-gray-400 mt-1">
          内置 9 种工具 + 支持自定义，可在画布 Tool 节点中调用
        </p>
      </div>
      <el-button type="primary" size="small" @click="showCreate = true">
        添加自定义工具
      </el-button>
    </div>
    <div class="flex-1 overflow-y-auto p-4">
      <ToolList
        :tools="tools"
        :loading="loading"
        @select="openDetail"
        @delete="handleDelete"
      />
    </div>
    <ToolDetail v-model:visible="showDetail" :tool="currentTool" />
    <ToolCreate
      v-model:visible="showCreate"
      :loading="creating"
      @create="handleCreate"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { ElMessage, ElMessageBox } from 'element-plus'
import ToolList from '@/components/tools/ToolList.vue'
import ToolDetail from '@/components/tools/ToolDetail.vue'
import ToolCreate from '@/components/tools/ToolCreate.vue'
import type { Tool } from '@/types/tools'
import { toolDisplayName } from '@/utils/toolLabels'

const store = useStore()
const tools = computed(() => store.state.tools.tools)
const loading = computed(() => store.state.tools.loading)

const showDetail = ref(false)
const showCreate = ref(false)
const creating = ref(false)
const currentTool = ref<Tool | null>(null)

onMounted(() => {
  store.dispatch('tools/fetchTools')
})

function openDetail(tool: Tool) {
  currentTool.value = tool
  showDetail.value = true
}

async function handleCreate(data: {
  name: string
  description: string
  category: string
  handler_name: string
}) {
  creating.value = true
  try {
    await store.dispatch('tools/createTool', data)
    showCreate.value = false
    ElMessage.success('自定义工具已创建')
  } catch {
    // interceptor
  } finally {
    creating.value = false
  }
}

async function handleDelete(tool: Tool) {
  try {
    await ElMessageBox.confirm(
      `确定删除自定义工具「${toolDisplayName(tool.name, tool.description)}」?`,
      '删除确认',
      { type: 'warning' }
    )
  } catch {
    return
  }
  try {
    await store.dispatch('tools/deleteTool', tool.id)
    ElMessage.success('已删除')
  } catch {
    // interceptor
  }
}
</script>

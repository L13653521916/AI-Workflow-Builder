<template>

  <div class="h-full flex flex-col">

    <!-- 顶部工具栏 -->

    <div class="h-11 border-b border-gray-200 flex items-center px-4 gap-3 bg-white shrink-0">

      <el-button size="small" @click="drawerVisible = true">

        <span class="mr-1">&#9776;</span> 工作流列表

      </el-button>

      <el-input

        v-model="workflowName"

        size="small"

        class="w-48"

        placeholder="未命名工作流"

      />

      <el-button size="small" type="primary" @click="handleSave" :loading="saving">

        保存

      </el-button>

      <el-button size="small" @click="handleNew">新建</el-button>

      <el-button

        size="small"

        type="success"

        :loading="isExecuting"

        :disabled="!canRun"

        @click="showRunDialog = true"

      >

        {{ isExecuting ? '执行中...' : '运行' }}

      </el-button>

      <span class="text-xs text-gray-400 ml-auto" v-if="isDirty">未保存</span>

      <span class="text-xs text-gray-400 ml-auto" v-else-if="workflowId">#{{ workflowId }}</span>

    </div>



    <!-- 三栏布局 + 日志 -->

    <div class="flex-1 flex flex-col overflow-hidden min-h-0">

      <div class="flex-1 flex overflow-hidden min-h-0">

        <NodePalette />

        <WorkflowCanvas class="flex-1" />

        <NodeConfigPanel />

      </div>

      <ExecutionLog

        :selected-node-id="selectedNodeId"

        @clear="clearLogs"

        @history="openHistory"

        @select-node="selectNodeFromLog"

      />

    </div>



    <!-- 工作流列表抽屉 -->

    <el-drawer v-model="drawerVisible" title="我的工作流" direction="ltr" size="320px">

      <div class="space-y-2">

        <div

          v-for="wf in workflowList"

          :key="wf.id"

          class="p-3 border border-gray-200 rounded-lg hover:border-blue-400 hover:shadow-sm transition-all flex items-start gap-2"

          :class="wf.id === workflowId ? 'border-blue-400 bg-blue-50' : ''"

        >

          <div class="flex-1 min-w-0 cursor-pointer" @click="loadWorkflow(wf.id)">

            <div class="font-medium text-sm text-gray-800">{{ wf.name }}</div>

            <div class="text-xs text-gray-400 mt-1">{{ wf.description || '暂无描述' }}</div>

            <div class="text-[11px] text-gray-300 mt-1">

              {{ formatTime(wf.updated_at || wf.created_at) }}

            </div>

          </div>

          <el-button type="danger" link size="small" class="shrink-0 mt-0.5" @click.stop="handleDelete(wf.id, wf.name)">

            删除

          </el-button>

        </div>

        <div v-if="workflowList.length === 0" class="text-center text-gray-400 text-sm py-8">暂无工作流</div>

      </div>

    </el-drawer>



    <!-- 运行历史抽屉 -->

    <el-drawer v-model="historyVisible" title="运行历史" direction="rtl" size="400px">

      <div class="space-y-2">

        <div

          v-for="run in runHistory"

          :key="run.id"

          class="p-3 border border-gray-200 rounded-lg cursor-pointer hover:border-blue-300"

          @click="viewRunDetail(run)"

        >

          <div class="flex items-center justify-between">

            <span class="text-sm font-medium">运行 #{{ run.id }}</span>

            <span class="text-xs px-2 py-0.5 rounded-full" :class="statusBadge(run.status)">

              {{ statusLabel(run.status) }}

            </span>

          </div>

          <div class="text-xs text-gray-400 mt-1">{{ formatTime(run.started_at) }}</div>

        </div>

        <div v-if="runHistory.length === 0" class="text-center text-gray-400 py-8">暂无运行记录</div>

      </div>

    </el-drawer>



    <!-- 运行输入对话框 -->

    <el-dialog v-model="showRunDialog" title="运行工作流" width="420px">

      <el-form label-position="top" size="small">

        <el-form-item label="输入内容">

          <el-input

            v-model="runInput"

            type="textarea"

            :rows="4"

            placeholder="工作流起始输入，将传入起始节点"

          />

        </el-form-item>

      </el-form>

      <template #footer>

        <el-button @click="showRunDialog = false">取消</el-button>

        <el-button type="success" :loading="isExecuting" @click="handleRun">开始运行</el-button>

      </template>

    </el-dialog>



    <!-- 运行详情对话框 -->

    <el-dialog v-model="runDetailVisible" title="运行详情" width="560px">

      <div v-if="runDetail" class="space-y-3 text-sm">

        <div class="flex gap-4 text-gray-500 text-xs">

          <span>状态: {{ statusLabel(runDetail.status) }}</span>

          <span>开始: {{ formatTime(runDetail.started_at) }}</span>

        </div>

        <div>

          <div class="font-medium text-gray-700 mb-1">输入</div>

          <pre class="bg-gray-50 p-2 rounded text-xs overflow-auto max-h-32">{{ JSON.stringify(runDetail.input_json, null, 2) }}</pre>

        </div>

        <div>

          <div class="font-medium text-gray-700 mb-1">输出</div>

          <pre class="bg-green-50 p-2 rounded text-xs overflow-auto max-h-40">{{ JSON.stringify(runDetail.output_json, null, 2) }}</pre>

        </div>

        <div>

          <div class="font-medium text-gray-700 mb-1">日志</div>

          <div class="max-h-48 overflow-y-auto space-y-1 text-xs font-mono">

            <div v-for="(log, i) in runDetail.logs_json || []" :key="i" class="text-gray-600">

              [{{ log.level }}] {{ log.message }}

            </div>

          </div>

        </div>

      </div>

    </el-dialog>

  </div>

</template>



<script setup lang="ts">

import { ref, computed, onMounted } from 'vue'

import { useStore } from 'vuex'

import { ElMessage, ElMessageBox } from 'element-plus'

import NodePalette from '@/components/canvas/NodePalette.vue'

import WorkflowCanvas from '@/components/canvas/WorkflowCanvas.vue'

import NodeConfigPanel from '@/components/canvas/NodeConfigPanel.vue'

import ExecutionLog from '@/components/canvas/ExecutionLog.vue'

import * as workflowApi from '@/api/workflow'

import * as executionApi from '@/api/execution'

import type { WorkflowRunDetail, WorkflowRunSummary } from '@/types/execution'



const store = useStore()



const workflowName = computed({

  get: () => store.state.canvas.workflowName,

  set: (val: string) => store.commit('canvas/SET_WORKFLOW_META', {

    id: store.state.canvas.workflowId || 0,

    name: val,

    description: store.state.canvas.workflowDescription,

  }),

})



const workflowId = computed(() => store.state.canvas.workflowId)

const isDirty = computed(() => store.state.canvas.isDirty)

const saving = computed(() => store.state.canvas.saving)

const isExecuting = computed(() => store.state.canvas.isExecuting)

const runHistory = computed(() => store.state.canvas.runHistory)

const selectedNodeId = computed(() => store.state.canvas.selectedNodeId)



const hasStartNode = computed(() =>

  store.state.canvas.nodes.some((n: { type: string }) => n.type === 'start')

)

const canRun = computed(() => !!workflowId.value && hasStartNode.value && !isExecuting.value)



const drawerVisible = ref(false)

const historyVisible = ref(false)

const showRunDialog = ref(false)

const runDetailVisible = ref(false)

const runInput = ref('你好，请处理这个输入')

const workflowList = ref<any[]>([])

const runDetail = ref<WorkflowRunDetail | null>(null)



async function fetchWorkflows() {

  try {

    workflowList.value = await workflowApi.getWorkflows()

  } catch {

    ElMessage.error('加载工作流列表失败')

  }

}



onMounted(() => {
  fetchWorkflows()
  store.dispatch('models/fetchProfiles')
})



async function handleSave() {

  try {

    await store.dispatch('canvas/save')

    ElMessage.success('保存成功')

    fetchWorkflows()

  } catch {

    ElMessage.error('保存失败')

  }

}



async function loadWorkflow(id: number) {

  if (isDirty.value) {

    try {

      await ElMessageBox.confirm('当前有未保存的更改,确定离开?', '提示', {

        confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning',

      })

    } catch { return }

  }

  try {

    await store.dispatch('canvas/load', id)

    store.commit('canvas/RESET_EXECUTION')

    drawerVisible.value = false

    ElMessage.success('工作流已加载')

  } catch {

    ElMessage.error('加载失败')

  }

}



async function handleNew() {

  if (isDirty.value) {

    try {

      await ElMessageBox.confirm('当前有未保存的更改,确定新建?', '提示', {

        confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning',

      })

    } catch { return }

  }

  store.dispatch('canvas/newCanvas')

  store.commit('canvas/RESET_EXECUTION')

}



async function handleDelete(id: number, name: string) {

  try {

    await ElMessageBox.confirm(`确定删除工作流「${name}」? 此操作不可恢复。`, '删除确认', {

      confirmButtonText: '删除', cancelButtonText: '取消', type: 'warning',

    })

  } catch { return }

  try {

    await store.dispatch('canvas/deleteWorkflow', id)

    ElMessage.success('工作流已删除')

    fetchWorkflows()

  } catch {

    ElMessage.error('删除失败')

  }

}



async function handleRun() {

  if (isDirty.value) {

    try {

      await store.dispatch('canvas/save')

    } catch {

      ElMessage.error('请先保存工作流')

      return

    }

  }

  if (!workflowId.value) {

    ElMessage.warning('请先保存工作流')

    return

  }

  if (!hasStartNode.value) {

    ElMessage.warning('工作流需要至少一个起始节点')

    return

  }



  showRunDialog.value = false

  try {

    await store.dispatch('canvas/runWorkflow', { input: runInput.value })

    ElMessage.success('工作流执行完成')

    await store.dispatch('canvas/fetchRunHistory')

  } catch (e: any) {

    ElMessage.error(e?.message || '执行失败')

    await store.dispatch('canvas/fetchRunHistory')

  }

}



function clearLogs() {

  store.commit('canvas/RESET_EXECUTION')

}



async function openHistory() {

  if (!workflowId.value) {

    ElMessage.warning('请先保存并选择工作流')

    return

  }

  await store.dispatch('canvas/fetchRunHistory')

  historyVisible.value = true

}



function selectNodeFromLog(nodeId: string) {

  store.commit('canvas/SET_SELECTED_NODE', nodeId)

}



async function viewRunDetail(run: WorkflowRunSummary) {

  if (!workflowId.value) return

  try {

    runDetail.value = await executionApi.getWorkflowRun(workflowId.value, run.id)

    runDetailVisible.value = true

  } catch {

    ElMessage.error('加载运行详情失败')

  }

}



function statusLabel(status: string) {

  const map: Record<string, string> = {

    running: '执行中', success: '成功', failed: '失败',

  }

  return map[status] || status

}



function statusBadge(status: string) {

  const map: Record<string, string> = {

    running: 'bg-yellow-100 text-yellow-700',

    success: 'bg-green-100 text-green-700',

    failed: 'bg-red-100 text-red-700',

  }

  return map[status] || 'bg-gray-100 text-gray-600'

}



function formatTime(t: string | null) {

  if (!t) return ''

  return new Date(t).toLocaleString('zh-CN', {

    month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit',

  })

}

</script>


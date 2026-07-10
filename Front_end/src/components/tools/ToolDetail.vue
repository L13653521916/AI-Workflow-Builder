<template>
  <el-drawer
    :model-value="visible"
    :title="displayName(tool?.name || '')"
    direction="rtl"
    size="480px"
    @update:model-value="emit('update:visible', $event)"
  >
    <div v-if="tool" class="space-y-5">
      <div>
        <span class="text-[10px] px-2 py-0.5 rounded-full bg-orange-50 text-orange-600">
          {{ categoryLabelFn(tool.category) }}
        </span>
        <p class="text-sm text-gray-600 mt-3">{{ tool.description }}</p>
      </div>

      <div>
        <h4 class="text-sm font-medium text-gray-700 mb-2">参数定义</h4>
        <pre class="bg-gray-50 p-3 rounded text-xs overflow-auto max-h-40 border border-gray-100">{{ JSON.stringify(tool.schema, null, 2) }}</pre>
      </div>

      <div>
        <h4 class="text-sm font-medium text-gray-700 mb-3">在线测试</h4>
        <el-form label-position="top" size="small">
          <el-form-item
            v-for="field in schemaFields"
            :key="field.key"
            :label="field.label"
            :required="field.required"
          >
            <el-input
              v-if="field.type === 'string' && field.key !== 'code'"
              v-model="testParams[field.key]"
              :placeholder="field.description"
            />
            <el-input
              v-else-if="field.key === 'code'"
              v-model="testParams[field.key]"
              type="textarea"
              :rows="5"
              placeholder="输入 Python 代码，如 print('hello')"
            />
            <el-input
              v-else
              v-model="testParams[field.key]"
              type="textarea"
              :rows="2"
              :placeholder="field.description"
            />
          </el-form-item>
          <el-button type="primary" :loading="testing" @click="runTest">
            运行测试
          </el-button>
        </el-form>
      </div>

      <div v-if="testResult !== null">
        <h4 class="text-sm font-medium text-gray-700 mb-2">测试结果</h4>
        <p
          v-if="resultHint"
          class="text-xs text-amber-600 bg-amber-50 border border-amber-200 rounded p-2 mb-2"
        >
          {{ resultHint }}
        </p>
        <div
          class="p-3 rounded text-xs overflow-auto max-h-64 border"
          :class="testSuccess ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'"
        >
          <pre>{{ JSON.stringify(testResult, null, 2) }}</pre>
        </div>
      </div>
    </div>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import * as toolsApi from '@/api/tools'
import type { Tool } from '@/types/tools'
import { toolDisplayName, categoryLabel } from '@/utils/toolLabels'

const props = defineProps<{
  visible: boolean
  tool: Tool | null
}>()

const emit = defineEmits<{
  'update:visible': [val: boolean]
}>()

const testParams = ref<Record<string, string>>({})
const testing = ref(false)
const testResult = ref<any>(null)
const testSuccess = ref(true)

const resultHint = computed(() => testResult.value?.hint || '')

const DISPLAY_NAMES: Record<string, string> = {}

const schemaFields = computed(() => {
  if (!props.tool?.schema?.properties) return []
  const required: string[] = props.tool.schema.required || []
  return Object.entries(props.tool.schema.properties).map(([key, val]: [string, any]) => ({
    key,
    label: val.description || key,
    description: val.description || '',
    type: val.type || 'string',
    required: required.includes(key),
  }))
})

watch(() => props.tool, (t) => {
  testParams.value = {}
  testResult.value = null
  if (t?.schema?.properties) {
    for (const [key, val] of Object.entries(t.schema.properties) as [string, any][]) {
      testParams.value[key] = val.default !== undefined ? String(val.default) : ''
    }
  }
}, { immediate: true })

function displayName(name: string) {
  return toolDisplayName(name, props.tool?.description)
}

function categoryLabelFn(cat: string) {
  return categoryLabel(cat)
}

async function runTest() {
  if (!props.tool) return
  testing.value = true
  testResult.value = null
  try {
    const params: Record<string, any> = { ...testParams.value }
    if (props.tool.name === 'http_request' && params.headers) {
      try { params.headers = JSON.parse(params.headers) } catch { /* keep string */ }
    }
    const res = await toolsApi.testTool(props.tool.id, params)
    testSuccess.value = res.success
    testResult.value = res.success ? res.result : { error: res.error }
    if (!res.success) ElMessage.warning(res.error || '测试失败')
    else ElMessage.success('测试完成')
  } catch {
    testSuccess.value = false
    testResult.value = { error: '请求失败' }
  } finally {
    testing.value = false
  }
}
</script>

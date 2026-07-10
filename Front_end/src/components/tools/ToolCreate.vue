<template>
  <el-dialog
    :model-value="visible"
    title="添加自定义工具"
    width="480px"
    @update:model-value="emit('update:visible', $event)"
  >
    <el-form label-position="top" size="small">
      <el-form-item label="工具标识名" required>
        <el-input
          v-model="form.name"
          placeholder="英文标识，如 my_api_tool"
          maxlength="80"
        />
        <p class="text-xs text-gray-400 mt-1">唯一标识，创建后不可修改</p>
      </el-form-item>
      <el-form-item label="显示描述" required>
        <el-input v-model="form.description" placeholder="工具用途说明" />
      </el-form-item>
      <el-form-item label="分类">
        <el-select v-model="form.category" class="w-full">
          <el-option label="自定义" value="custom" />
          <el-option label="API" value="api" />
          <el-option label="文本" value="text" />
          <el-option label="数据" value="data" />
          <el-option label="实用" value="utility" />
        </el-select>
      </el-form-item>
      <el-form-item label="底层能力" required>
        <el-select v-model="form.handler_name" class="w-full" placeholder="选择复用的执行能力">
          <el-option
            v-for="h in handlers"
            :key="h.name"
            :label="h.label"
            :value="h.name"
          />
        </el-select>
        <p class="text-xs text-gray-400 mt-1">
          自定义工具复用已有执行引擎，例如基于 HTTP 请求封装你的专属 API
        </p>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="emit('update:visible', false)">取消</el-button>
      <el-button type="primary" :loading="loading" @click="handleSubmit">创建</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { reactive, watch, ref } from 'vue'
import { ElMessage } from 'element-plus'
import * as toolsApi from '@/api/tools'
import type { ToolHandler } from '@/types/tools'

const props = defineProps<{
  visible: boolean
  loading?: boolean
}>()

const emit = defineEmits<{
  'update:visible': [val: boolean]
  create: [data: { name: string; description: string; category: string; handler_name: string }]
}>()

const handlers = ref<ToolHandler[]>([])
const form = reactive({
  name: '',
  description: '',
  category: 'custom',
  handler_name: 'http_request',
})

watch(() => props.visible, async (val) => {
  if (val) {
    form.name = ''
    form.description = ''
    form.category = 'custom'
    form.handler_name = 'http_request'
    try {
      handlers.value = await toolsApi.getToolHandlers()
    } catch {
      handlers.value = []
    }
  }
})

function handleSubmit() {
  if (!form.name.trim() || !/^[a-zA-Z][a-zA-Z0-9_]*$/.test(form.name.trim())) {
    ElMessage.warning('标识名需以字母开头，仅含字母、数字、下划线')
    return
  }
  if (!form.description.trim()) {
    ElMessage.warning('请填写描述')
    return
  }
  if (!form.handler_name) {
    ElMessage.warning('请选择底层能力')
    return
  }
  emit('create', { ...form, name: form.name.trim(), description: form.description.trim() })
}
</script>

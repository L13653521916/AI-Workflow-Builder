<template>
  <el-dialog
    :model-value="visible"
    title="新建知识库"
    width="420px"
    @update:model-value="emit('update:visible', $event)"
  >
    <el-form :model="form" label-width="60px" @submit.prevent>
      <el-form-item label="名称" required>
        <el-input v-model="form.name" placeholder="请输入知识库名称" maxlength="100" />
      </el-form-item>
      <el-form-item label="描述">
        <el-input
          v-model="form.description"
          type="textarea"
          :rows="3"
          placeholder="可选描述"
          maxlength="500"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="emit('update:visible', false)">取消</el-button>
      <el-button type="primary" :loading="loading" @click="handleSubmit">创建</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { reactive, watch } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps<{
  visible: boolean
  loading?: boolean
}>()

const emit = defineEmits<{
  'update:visible': [val: boolean]
  create: [data: { name: string; description: string }]
}>()

const form = reactive({ name: '', description: '' })

watch(() => props.visible, (val) => {
  if (val) {
    form.name = ''
    form.description = ''
  }
})

function handleSubmit() {
  if (!form.name.trim()) {
    ElMessage.warning('请输入知识库名称')
    return
  }
  emit('create', { name: form.name.trim(), description: form.description.trim() })
}
</script>

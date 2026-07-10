<template>
  <div class="h-full flex flex-col">
    <div class="p-4 border-b border-gray-200 bg-white shrink-0">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-lg font-semibold text-gray-800">模型管理</h2>
          <p class="text-xs text-gray-400 mt-1">
            配置 LLM 推理节点的连接信息与高级策略，前端配置优先于后端默认设置
          </p>
        </div>
        <el-button type="primary" size="small" @click="openCreate">
          添加模型
        </el-button>
      </div>
    </div>

    <div class="flex-1 overflow-y-auto p-4">
      <!-- 配置说明 -->
      <div class="mb-4 p-3 bg-blue-50 border border-blue-100 rounded-lg text-sm text-blue-800">
        <p class="font-medium mb-1">已实现的可配置项</p>
        <p class="text-xs text-blue-600 leading-relaxed">
          连接：模型类型、Base URL、API Key、模型 ID ·
          上下文：Token 预算分配、压缩策略 ·
          历史：滑动窗口 / 摘要 / 向量检索 ·
          Agent：ReAct / Plan-Execute / Tool-Calling、工具白名单、最大迭代 ·
          可观测：步骤追踪、工具调用链日志
        </p>
        <p class="text-xs text-blue-500 mt-1">
          暂未纳入：LoRA 端点切换、多模型按任务路由、状态图可视化（需独立运行时引擎支持）
        </p>
      </div>

      <ModelList
        :profiles="profiles"
        :loading="loading"
        @edit="openEdit"
        @delete="handleDelete"
        @test="handleTest"
      />
    </div>

    <ModelEditor
      v-model:visible="showEditor"
      :profile="editingProfile"
      :saving="saving"
      @save="handleSave"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { ElMessage, ElMessageBox } from 'element-plus'
import ModelList from '@/components/models/ModelList.vue'
import ModelEditor from '@/components/models/ModelEditor.vue'
import type { ModelProfile, ModelProfileCreateBody } from '@/types/models'
import * as modelsApi from '@/api/models'

const store = useStore()
const profiles = computed(() => store.state.models.profiles)
const loading = computed(() => store.state.models.loading)

const showEditor = ref(false)
const editingProfile = ref<ModelProfile | null>(null)
const saving = ref(false)

onMounted(() => {
  store.dispatch('models/fetchProfiles')
})

function openCreate() {
  editingProfile.value = null
  showEditor.value = true
}

function openEdit(profile: ModelProfile) {
  store.dispatch('models/fetchProfileDetail', profile.id).then((detail) => {
    editingProfile.value = detail
    showEditor.value = true
  })
}

async function handleSave(data: ModelProfileCreateBody) {
  saving.value = true
  try {
    if (editingProfile.value?.id) {
      await store.dispatch('models/updateProfile', { id: editingProfile.value.id, data })
      ElMessage.success('模型配置已更新')
    } else {
      await store.dispatch('models/createProfile', data)
      ElMessage.success('模型配置已创建')
    }
    showEditor.value = false
  } catch {
    // interceptor
  } finally {
    saving.value = false
  }
}

async function handleDelete(profile: ModelProfile) {
  try {
    await ElMessageBox.confirm(
      `确定删除模型配置「${profile.name}」?`,
      '删除确认',
      { type: 'warning' }
    )
  } catch {
    return
  }
  try {
    await store.dispatch('models/deleteProfile', profile.id)
    ElMessage.success('已删除')
  } catch {
    // interceptor
  }
}

async function handleTest(profile: ModelProfile) {
  try {
    const res = await modelsApi.testModelProfile(profile.id)
    if (res.success) {
      ElMessage.success(`连接成功：${(res.reply || '').slice(0, 80)}`)
    } else {
      ElMessage.error(`连接失败：${res.error}`)
    }
  } catch {
    // interceptor
  }
}
</script>

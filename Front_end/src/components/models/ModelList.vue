<template>
  <div>
    <div v-if="loading" class="text-center text-gray-400 py-12">加载中...</div>
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="profile in profiles"
        :key="profile.id"
        class="border border-gray-200 rounded-lg p-4 hover:shadow-md hover:border-blue-300 transition-all relative"
      >
        <div v-if="profile.isDefault" class="absolute top-3 right-3">
          <span class="text-[10px] px-2 py-0.5 rounded-full bg-blue-50 text-blue-600">默认</span>
        </div>
        <div class="flex items-start gap-3 mb-3">
          <div
            class="w-10 h-10 rounded-lg bg-blue-500 text-white flex items-center justify-center font-bold text-lg shrink-0"
          >
            L
          </div>
          <div class="min-w-0 flex-1 pr-12">
            <h3 class="font-medium text-gray-800 truncate">{{ profile.name }}</h3>
            <p class="text-xs text-gray-400 mt-0.5">{{ providerLabel(profile.provider) }}</p>
          </div>
        </div>
        <div class="text-sm text-gray-500 space-y-1 mb-3">
          <p class="truncate"><span class="text-gray-400">模型：</span>{{ profile.modelId }}</p>
          <p class="truncate"><span class="text-gray-400">API：</span>{{ profile.apiKeyMasked || '未设置' }}</p>
          <p class="text-xs text-gray-400">
            Agent：{{ agentModeLabel(profile.config?.agent?.mode) }}
            · 历史：{{ historyStrategyLabel(profile.config?.history?.strategy) }}
          </p>
        </div>
        <div class="flex gap-2">
          <el-button size="small" type="primary" plain @click="emit('edit', profile)">
            配置
          </el-button>
          <el-button size="small" plain @click="emit('test', profile)">
            测试连接
          </el-button>
          <el-button size="small" type="danger" plain @click="emit('delete', profile)">
            删除
          </el-button>
        </div>
      </div>
    </div>

    <div v-if="!loading && profiles.length === 0" class="text-center text-gray-400 py-16">
      <p class="mb-2">暂无模型配置</p>
      <p class="text-sm">点击右上角「添加模型」创建 LLM 推理配置</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ModelProfile } from '@/types/models'
import { PROVIDER_PRESETS } from '@/types/models'

defineProps<{
  profiles: ModelProfile[]
  loading: boolean
}>()

const emit = defineEmits<{
  edit: [profile: ModelProfile]
  delete: [profile: ModelProfile]
  test: [profile: ModelProfile]
}>()

function providerLabel(provider: string) {
  return PROVIDER_PRESETS[provider as keyof typeof PROVIDER_PRESETS]?.label || provider
}

function agentModeLabel(mode?: string) {
  const map: Record<string, string> = {
    react: 'ReAct',
    plan_execute: 'Plan-Execute',
    tool_calling: 'Tool-Calling',
  }
  return map[mode || ''] || mode || '-'
}

function historyStrategyLabel(strategy?: string) {
  const map: Record<string, string> = {
    sliding_window: '滑动窗口',
    summarize: '摘要压缩',
    vector_retrieval: '向量检索',
  }
  return map[strategy || ''] || strategy || '-'
}
</script>

<template>
  <el-drawer
    :model-value="visible"
    :title="isEdit ? '编辑模型配置' : '添加模型配置'"
    size="560px"
    destroy-on-close
    @close="emit('update:visible', false)"
  >
    <el-form label-position="top" size="small" class="pr-2">
      <!-- 基础连接 -->
      <div class="mb-4">
        <h4 class="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
          <span class="w-1 h-4 bg-blue-500 rounded"></span>
          连接配置
        </h4>
        <el-form-item label="配置名称" required>
          <el-input v-model="form.name" placeholder="如：生产环境千问" />
        </el-form-item>
        <el-form-item label="模型类型" required>
          <el-select v-model="form.provider" class="w-full" @change="onProviderChange">
            <el-option
              v-for="(preset, key) in PROVIDER_PRESETS"
              :key="key"
              :label="preset.label"
              :value="key"
            />
          </el-select>
          <p v-if="PROVIDER_PRESETS[form.provider]?.hint" class="text-xs text-gray-400 mt-1">
            {{ PROVIDER_PRESETS[form.provider].hint }}
          </p>
        </el-form-item>
        <el-form-item label="Base URL" required>
          <el-input v-model="form.base_url" placeholder="https://api.example.com/v1" />
        </el-form-item>
        <el-form-item label="API Key" required>
          <el-input
            v-model="form.api_key"
            type="password"
            show-password
            placeholder="sk-..."
          />
        </el-form-item>
        <el-form-item label="模型 ID" required>
          <el-input v-model="form.model_id" placeholder="如 qwen-plus / gpt-4o-mini" />
        </el-form-item>
        <el-form-item>
          <el-checkbox v-model="form.is_default">设为默认模型</el-checkbox>
        </el-form-item>
      </div>

      <!-- 上下文管理 -->
      <div class="mb-4 border-t border-gray-100 pt-4">
        <h4 class="text-sm font-semibold text-gray-700 mb-1 flex items-center gap-2">
          <span class="w-1 h-4 bg-green-500 rounded"></span>
          上下文管理
        </h4>
        <p class="text-xs text-gray-400 mb-3">控制 Token 预算分配与超长上下文处理方式</p>
        <el-form-item label="最大上下文 Token">
          <el-input-number v-model="form.config.context.maxContextTokens" :min="1024" :max="128000" :step="1024" class="w-full" />
        </el-form-item>
        <el-form-item label="Token 预算分配（System / User / Tool / RAG）">
          <div class="grid grid-cols-2 gap-2 w-full">
            <div>
              <span class="text-xs text-gray-400">System</span>
              <el-slider v-model="form.config.context.systemTokenRatio" :min="0" :max="50" :step="5" show-input input-size="small" />
            </div>
            <div>
              <span class="text-xs text-gray-400">User</span>
              <el-slider v-model="form.config.context.userTokenRatio" :min="0" :max="80" :step="5" show-input input-size="small" />
            </div>
            <div>
              <span class="text-xs text-gray-400">Tool</span>
              <el-slider v-model="form.config.context.toolTokenRatio" :min="0" :max="40" :step="5" show-input input-size="small" />
            </div>
            <div>
              <span class="text-xs text-gray-400">RAG</span>
              <el-slider v-model="form.config.context.ragTokenRatio" :min="0" :max="50" :step="5" show-input input-size="small" />
            </div>
          </div>
          <p class="text-xs text-gray-400 mt-1">
            当前合计 {{ ratioSum }}%（建议接近 100%）
          </p>
        </el-form-item>
        <el-form-item label="上下文压缩策略">
          <el-select v-model="form.config.context.compressionStrategy" class="w-full">
            <el-option label="不压缩（超出则截断报错）" value="none" />
            <el-option label="截断最早消息" value="truncate_oldest" />
            <el-option label="摘要压缩历史" value="summarize" />
          </el-select>
        </el-form-item>
      </div>

      <!-- 历史对话 -->
      <div class="mb-4 border-t border-gray-100 pt-4">
        <h4 class="text-sm font-semibold text-gray-700 mb-1 flex items-center gap-2">
          <span class="w-1 h-4 bg-purple-500 rounded"></span>
          历史对话策略
        </h4>
        <p class="text-xs text-gray-400 mb-3">多轮对话时如何选取与压缩历史消息</p>
        <el-form-item label="历史策略">
          <el-radio-group v-model="form.config.history.strategy">
            <el-radio value="sliding_window">滑动窗口</el-radio>
            <el-radio value="summarize">摘要压缩</el-radio>
            <el-radio value="vector_retrieval">向量检索历史</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="最大保留消息数">
          <el-input-number v-model="form.config.history.maxMessages" :min="2" :max="100" />
        </el-form-item>
        <el-form-item v-if="form.config.history.strategy === 'sliding_window'" label="滑动窗口大小">
          <el-input-number v-model="form.config.history.windowSize" :min="2" :max="50" />
        </el-form-item>
      </div>

      <!-- Agent 行为 -->
      <div class="mb-4 border-t border-gray-100 pt-4">
        <h4 class="text-sm font-semibold text-gray-700 mb-1 flex items-center gap-2">
          <span class="w-1 h-4 bg-orange-500 rounded"></span>
          Agent 行为
        </h4>
        <p class="text-xs text-gray-400 mb-3">工作流 LLM 节点调用时的推理模式与工具约束</p>
        <el-form-item label="推理模式">
          <el-select v-model="form.config.agent.mode" class="w-full">
            <el-option label="ReAct（推理 + 行动交替）" value="react" />
            <el-option label="Plan-Execute（先规划后执行）" value="plan_execute" />
            <el-option label="Tool-Calling（直接工具调用）" value="tool_calling" />
          </el-select>
        </el-form-item>
        <el-form-item label="工具白名单（留空表示允许全部）">
          <el-select
            v-model="form.config.agent.toolWhitelist"
            multiple
            filterable
            allow-create
            default-first-option
            class="w-full"
            placeholder="输入工具名后回车添加"
          />
        </el-form-item>
        <el-form-item label="最大迭代次数">
          <el-input-number v-model="form.config.agent.maxIterations" :min="1" :max="50" />
        </el-form-item>
      </div>

      <!-- 可观测性 -->
      <div class="mb-4 border-t border-gray-100 pt-4">
        <h4 class="text-sm font-semibold text-gray-700 mb-1 flex items-center gap-2">
          <span class="w-1 h-4 bg-gray-500 rounded"></span>
          可观测性
        </h4>
        <p class="text-xs text-gray-400 mb-3">执行时的日志与追踪开关（配置项，运行时在执行日志中体现）</p>
        <el-form-item>
          <el-checkbox v-model="form.config.observability.enableTracing">启用步骤追踪（记录每步延迟）</el-checkbox>
        </el-form-item>
        <el-form-item>
          <el-checkbox v-model="form.config.observability.logToolCalls">记录工具调用链</el-checkbox>
        </el-form-item>
      </div>
    </el-form>

    <template #footer>
      <div class="flex justify-end gap-2">
        <el-button @click="emit('update:visible', false)">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">
          保存
        </el-button>
      </div>
    </template>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import type { ModelProfile, ModelProvider, ModelConfig } from '@/types/models'
import { DEFAULT_MODEL_CONFIG, PROVIDER_PRESETS } from '@/types/models'

const props = defineProps<{
  visible: boolean
  profile: ModelProfile | null
  saving?: boolean
}>()

const emit = defineEmits<{
  'update:visible': [val: boolean]
  save: [data: {
    name: string
    provider: ModelProvider
    base_url: string
    api_key: string
    model_id: string
    config_json: ModelConfig
    is_default: boolean
  }]
}>()

const isEdit = computed(() => !!props.profile?.id)

function cloneConfig(cfg?: ModelConfig): ModelConfig {
  return JSON.parse(JSON.stringify(cfg || DEFAULT_MODEL_CONFIG))
}

const form = ref({
  name: '',
  provider: 'qianwen' as ModelProvider,
  base_url: PROVIDER_PRESETS.qianwen.baseUrl,
  api_key: '',
  model_id: PROVIDER_PRESETS.qianwen.modelId,
  is_default: false,
  config: cloneConfig(),
})

const ratioSum = computed(() => {
  const c = form.value.config.context
  return c.systemTokenRatio + c.userTokenRatio + c.toolTokenRatio + c.ragTokenRatio
})

watch(
  () => [props.visible, props.profile] as const,
  ([vis, profile]) => {
    if (!vis) return
    if (profile) {
      const detail = profile as ModelProfile & { apiKey?: string }
      form.value = {
        name: profile.name,
        provider: profile.provider,
        base_url: profile.baseUrl,
        api_key: detail.apiKey || '',
        model_id: profile.modelId,
        is_default: profile.isDefault,
        config: cloneConfig(profile.config),
      }
    } else {
      form.value = {
        name: '',
        provider: 'qianwen',
        base_url: PROVIDER_PRESETS.qianwen.baseUrl,
        api_key: '',
        model_id: PROVIDER_PRESETS.qianwen.modelId,
        is_default: false,
        config: cloneConfig(),
      }
    }
  },
  { immediate: true }
)

function onProviderChange(provider: ModelProvider) {
  const preset = PROVIDER_PRESETS[provider]
  if (provider !== 'custom') {
    form.value.base_url = preset.baseUrl
    if (preset.modelId) form.value.model_id = preset.modelId
  }
}

function handleSave() {
  if (!form.value.name.trim()) {
    ElMessage.warning('请输入配置名称')
    return
  }
  if (!form.value.base_url.trim()) {
    ElMessage.warning('请输入 Base URL')
    return
  }
  if (!form.value.api_key.trim()) {
    ElMessage.warning('请输入 API Key')
    return
  }
  if (!form.value.model_id.trim()) {
    ElMessage.warning('请输入模型 ID')
    return
  }
  emit('save', {
    name: form.value.name.trim(),
    provider: form.value.provider,
    base_url: form.value.base_url.trim(),
    api_key: form.value.api_key.trim(),
    model_id: form.value.model_id.trim(),
    config_json: form.value.config,
    is_default: form.value.is_default,
  })
}
</script>

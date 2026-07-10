<template>
  <div class="w-80 border-l border-gray-200 bg-white flex flex-col overflow-hidden">
    <div class="p-3 border-b border-gray-200">
      <h3 class="text-xs font-semibold text-gray-500 uppercase tracking-wider">
        {{ selectedEdge ? '连线配置' : '节点配置' }}
      </h3>
    </div>

    <div class="flex-1 overflow-y-auto p-4">
      <!-- 连线选中 -->
      <template v-if="selectedEdge">
        <div class="text-sm text-gray-600 space-y-3">
          <p>
            <span class="text-gray-400">来源：</span>{{ selectedEdge.source }}
          </p>
          <p>
            <span class="text-gray-400">目标：</span>{{ selectedEdge.target }}
          </p>
          <p class="text-xs text-gray-400">提示：选中连线后按 Delete 键也可删除</p>
          <el-button type="danger" class="w-full" @click="deleteEdge">
            删除此连线
          </el-button>
        </div>
      </template>

      <template v-else-if="selectedNode">
        <el-form label-position="top" size="small">
          <!-- 通用: 节点名称 -->
          <el-form-item label="节点名称">
            <el-input v-model="label" placeholder="输入节点名称" />
          </el-form-item>

          <!-- ── LLM 节点 ── -->
          <template v-if="selectedNode.type === 'llm'">
            <el-form-item label="模型配置">
              <el-select v-model="modelProfileId" class="w-full" placeholder="选择已保存的模型配置" clearable>
                <el-option
                  v-for="p in modelProfiles"
                  :key="p.id"
                  :label="profileOptionLabel(p)"
                  :value="p.id"
                />
                <el-option
                  v-if="modelProfiles.length === 0"
                  label="暂无配置，请先在「模型」页创建"
                  :value="0"
                  disabled
                />
              </el-select>
              <p class="text-xs text-gray-400 mt-1">
                留空则使用默认模型配置；连接信息与高级策略来自「模型」页
              </p>
            </el-form-item>
            <el-form-item label="System Prompt">
              <el-input v-model="systemPrompt" type="textarea" :rows="3" placeholder="系统提示词" />
            </el-form-item>
            <el-form-item label="Prompt 模板">
              <el-input v-model="prompt" type="textarea" :rows="4" placeholder="使用 {{input}} 引用上游输出" />
            </el-form-item>
            <el-form-item label="温度">
              <el-slider v-model="temperature" :min="0" :max="2" :step="0.1" show-input input-size="small" />
            </el-form-item>
            <el-form-item label="最大 Token">
              <el-input-number v-model="maxTokens" :min="256" :max="8192" :step="256" />
            </el-form-item>
          </template>

          <!-- ── RAG 节点 ── -->
          <template v-if="selectedNode.type === 'rag'">
            <el-form-item label="知识库">
              <el-select v-model="knowledgeBase" class="w-full" placeholder="选择知识库">
                <el-option
                  v-for="kb in knowledgeBases"
                  :key="kb.id"
                  :label="kb.name"
                  :value="kb.id"
                />
                <el-option v-if="knowledgeBases.length === 0" label="暂无知识库，请先在知识库页创建" value="" disabled />
              </el-select>
            </el-form-item>
            <el-form-item label="检索数量 (Top K)">
              <el-input-number v-model="topK" :min="1" :max="20" />
            </el-form-item>
            <el-form-item label="相似度阈值">
              <el-slider v-model="scoreThreshold" :min="0" :max="1" :step="0.05" show-input input-size="small" />
            </el-form-item>
          </template>

          <!-- ── Tool 节点 ── -->
          <template v-if="selectedNode.type === 'tool'">
            <el-form-item label="选择工具">
              <el-select v-model="toolName" class="w-full" placeholder="选择工具">
                <el-option
                  v-for="t in availableTools"
                  :key="t.id"
                  :label="toolDisplayName(t.name, t.description)"
                  :value="t.name"
                />
                <el-option v-if="availableTools.length === 0" label="暂无工具，请先在工具页查看" value="" disabled />
              </el-select>
            </el-form-item>
            <el-form-item v-if="toolName === 'http_request'" label="请求 URL">
              <el-input v-model="toolUrl" placeholder="https://api.example.com/..." />
            </el-form-item>
            <el-form-item label="参数 (JSON)">
              <el-input v-model="toolParams" type="textarea" :rows="3" placeholder='{"query": "关键词"} 或 {"code": "1+2"}' />
            </el-form-item>
          </template>

          <!-- ── Condition 节点 ── -->
          <template v-if="selectedNode.type === 'condition'">
            <el-form-item label="条件表达式">
              <el-input v-model="condition" type="textarea" :rows="3" placeholder="例如: output.length > 100" />
            </el-form-item>
            <el-form-item label="True 分支标签">
              <el-input v-model="trueLabel" placeholder="通过" />
            </el-form-item>
            <el-form-item label="False 分支标签">
              <el-input v-model="falseLabel" placeholder="不通过" />
            </el-form-item>
          </template>

          <!-- ── Start 节点 ── -->
          <template v-if="selectedNode.type === 'start'">
            <el-form-item label="输入参数定义">
              <el-input v-model="startParams" type="textarea" :rows="4" placeholder='{"input": {"type": "string"}}' />
            </el-form-item>
          </template>

          <!-- ── End 节点 ── -->
          <template v-if="selectedNode.type === 'end'">
            <el-form-item label="输出格式">
              <el-select v-model="outputFormat" class="w-full">
                <el-option label="直接输出" value="raw" />
                <el-option label="Markdown" value="markdown" />
                <el-option label="JSON" value="json" />
              </el-select>
            </el-form-item>
            <el-form-item label="输出模板">
              <el-input v-model="outputTemplate" type="textarea" :rows="3" placeholder="可选,使用 {{output}} 引用上游结果" />
            </el-form-item>
          </template>

          <!-- 保存按钮 -->
          <el-form-item>
            <el-button type="primary" class="w-full" @click="saveConfig">保存配置</el-button>
          </el-form-item>
        </el-form>
      </template>

      <div v-else class="text-gray-400 text-sm text-center mt-12">
        <div class="text-3xl mb-2">+</div>
        <p>点击节点查看配置</p>
        <p class="text-xs mt-2">点击连线可删除</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch, onMounted } from 'vue'
import { useStore } from 'vuex'
import { ElMessage } from 'element-plus'
import { toolDisplayName } from '@/utils/toolLabels'
import { PROVIDER_PRESETS } from '@/types/models'
import type { ModelProfile } from '@/types/models'

const store = useStore()
const selectedNode = computed(() => store.getters['canvas/selectedNode'])
const selectedEdge = computed(() => store.getters['canvas/selectedEdge'])
const knowledgeBases = computed(() => store.state.knowledge?.knowledgeBases || [])
const availableTools = computed(() => store.state.tools?.tools || [])
const modelProfiles = computed(() => store.state.models?.profiles || [])

onMounted(() => {
  if (knowledgeBases.value.length === 0) {
    store.dispatch('knowledge/fetchKnowledgeBases')
  }
  if (availableTools.value.length === 0) {
    store.dispatch('tools/fetchTools')
  }
  if (modelProfiles.value.length === 0) {
    store.dispatch('models/fetchProfiles')
  }
})

function profileOptionLabel(p: ModelProfile) {
  const provider = PROVIDER_PRESETS[p.provider]?.label || p.provider
  const tag = p.isDefault ? ' [默认]' : ''
  return `${p.name} (${provider} · ${p.modelId})${tag}`
}

// ── 通用字段 ────────────────────────────────────────
const label = ref('')
const modelProfileId = ref<number | null>(null)
const prompt = ref('')
const systemPrompt = ref('')
const temperature = ref(0.7)
const maxTokens = ref(2048)
const knowledgeBase = ref<number | null>(null)
const topK = ref(3)
const scoreThreshold = ref(0.5)
const toolName = ref('')
const toolUrl = ref('')
const toolParams = ref('{}')
const condition = ref('')
const trueLabel = ref('是')
const falseLabel = ref('否')
const startParams = ref('{}')
const outputFormat = ref('raw')
const outputTemplate = ref('')

// ── 切换节点时填充 ──────────────────────────────────
watch(selectedNode, (node) => {
  if (!node) return
  label.value = node.label
  const c = node.config || {}
  modelProfileId.value = c.modelProfileId ?? null
  prompt.value = c.prompt || ''
  systemPrompt.value = c.systemPrompt || ''
  temperature.value = c.temperature ?? 0.7
  maxTokens.value = c.maxTokens ?? 2048
  knowledgeBase.value = c.knowledgeBase ?? null
  topK.value = c.topK ?? 3
  scoreThreshold.value = c.scoreThreshold ?? 0.5
  toolName.value = c.tool || ''
  toolUrl.value = c.toolUrl || ''
  toolParams.value = typeof c.toolParams === 'string' ? c.toolParams : JSON.stringify(c.toolParams || {}, null, 2)
  condition.value = c.condition || ''
  trueLabel.value = c.trueLabel || '是'
  falseLabel.value = c.falseLabel || '否'
  startParams.value = typeof c.startParams === 'string' ? c.startParams : JSON.stringify(c.startParams || {}, null, 2)
  outputFormat.value = c.outputFormat || 'raw'
  outputTemplate.value = c.outputTemplate || ''
}, { immediate: true })

// ── 保存配置到 store ────────────────────────────────
function saveConfig() {
  if (!selectedNode.value) return
  const profile = modelProfileId.value
    ? modelProfiles.value.find((p: ModelProfile) => p.id === modelProfileId.value)
    : modelProfiles.value.find((p: ModelProfile) => p.isDefault)
  store.commit('canvas/UPDATE_NODE', {
    ...selectedNode.value,
    label: label.value,
    config: {
      ...selectedNode.value.config,
      modelProfileId: modelProfileId.value || undefined,
      modelProfileName: profile?.name,
      prompt: prompt.value,
      systemPrompt: systemPrompt.value,
      temperature: temperature.value,
      maxTokens: maxTokens.value,
      knowledgeBase: knowledgeBase.value,
      topK: topK.value,
      scoreThreshold: scoreThreshold.value,
      tool: toolName.value,
      toolUrl: toolUrl.value,
      toolParams: toolParams.value,
      condition: condition.value,
      trueLabel: trueLabel.value,
      falseLabel: falseLabel.value,
      startParams: startParams.value,
      outputFormat: outputFormat.value,
      outputTemplate: outputTemplate.value,
    }
  })
  ElMessage.success('配置已保存')
}

function deleteEdge() {
  if (!selectedEdge.value) return
  store.commit('canvas/REMOVE_EDGE', selectedEdge.value.id)
  ElMessage.success('连线已删除')
}
</script>
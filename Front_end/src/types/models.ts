export type ModelProvider = 'qianwen' | 'deepseek' | 'gpt' | 'claude' | 'custom'

export type CompressionStrategy = 'none' | 'truncate_oldest' | 'summarize'
export type HistoryStrategy = 'sliding_window' | 'summarize' | 'vector_retrieval'
export type AgentMode = 'react' | 'plan_execute' | 'tool_calling'

export interface ModelContextConfig {
  maxContextTokens: number
  systemTokenRatio: number
  userTokenRatio: number
  toolTokenRatio: number
  ragTokenRatio: number
  compressionStrategy: CompressionStrategy
}

export interface ModelHistoryConfig {
  strategy: HistoryStrategy
  maxMessages: number
  windowSize: number
}

export interface ModelAgentConfig {
  mode: AgentMode
  toolWhitelist: string[]
  maxIterations: number
}

export interface ModelObservabilityConfig {
  enableTracing: boolean
  logToolCalls: boolean
}

export interface ModelConfig {
  context: ModelContextConfig
  history: ModelHistoryConfig
  agent: ModelAgentConfig
  observability: ModelObservabilityConfig
}

export interface ModelProfile {
  id: number
  name: string
  provider: ModelProvider
  baseUrl: string
  apiKeyMasked: string
  modelId: string
  config: ModelConfig
  isDefault: boolean
  createdAt?: string
  updatedAt?: string
}

export interface ModelProfileDetail extends ModelProfile {
  apiKey: string
}

export interface ModelProfileCreateBody {
  name: string
  provider: ModelProvider
  base_url: string
  api_key: string
  model_id: string
  config_json?: ModelConfig
  is_default?: boolean
}

export interface ModelProfileUpdateBody {
  name?: string
  provider?: ModelProvider
  base_url?: string
  api_key?: string
  model_id?: string
  config_json?: ModelConfig
  is_default?: boolean
}

export const DEFAULT_MODEL_CONFIG: ModelConfig = {
  context: {
    maxContextTokens: 8192,
    systemTokenRatio: 10,
    userTokenRatio: 60,
    toolTokenRatio: 10,
    ragTokenRatio: 20,
    compressionStrategy: 'none',
  },
  history: {
    strategy: 'sliding_window',
    maxMessages: 20,
    windowSize: 10,
  },
  agent: {
    mode: 'tool_calling',
    toolWhitelist: [],
    maxIterations: 10,
  },
  observability: {
    enableTracing: true,
    logToolCalls: true,
  },
}

export const PROVIDER_PRESETS: Record<
  ModelProvider,
  { label: string; baseUrl: string; modelId: string; hint?: string }
> = {
  qianwen: {
    label: '通义千问',
    baseUrl: 'https://dashscope.aliyuncs.com/compatible-mode/v1',
    modelId: 'qwen-plus',
    hint: '阿里云百炼 OpenAI 兼容接口',
  },
  deepseek: {
    label: 'DeepSeek',
    baseUrl: 'https://api.deepseek.com/v1',
    modelId: 'deepseek-chat',
  },
  gpt: {
    label: 'OpenAI GPT',
    baseUrl: 'https://api.openai.com/v1',
    modelId: 'gpt-4o-mini',
  },
  claude: {
    label: 'Claude',
    baseUrl: 'https://api.anthropic.com/v1',
    modelId: 'claude-3-5-sonnet-20241022',
    hint: '需使用 OpenAI 兼容代理网关',
  },
  custom: {
    label: '自定义导入',
    baseUrl: '',
    modelId: '',
    hint: '自行填写 Base URL 与模型 ID',
  },
}

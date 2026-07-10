export interface Tool {
  id: number
  name: string
  description: string
  category: string
  schema: Record<string, any>
}

export const CATEGORY_LABELS: Record<string, string> = {
  search: '搜索',
  code: '代码',
  api: 'API',
  text: '文本',
  data: '数据',
  utility: '实用',
  custom: '自定义',
}

export interface ToolHandler {
  name: string
  label: string
}

export interface ToolCreateBody {
  name: string
  description: string
  category: string
  handler_name: string
  schema_json?: Record<string, any>
}

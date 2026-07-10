import { CATEGORY_LABELS } from '@/types/tools'

const BUILTIN_DISPLAY: Record<string, string> = {
  web_search: 'Web 搜索',
  code_exec: 'Python 代码执行',
  http_request: 'HTTP 请求',
  json_parse: 'JSON 解析',
  text_split: '文本分割',
  string_replace: '字符串替换',
  current_time: '获取当前时间',
  regex_match: '正则匹配',
  text_length: '文本统计',
}

export function toolDisplayName(name: string, description?: string): string {
  return BUILTIN_DISPLAY[name] || description || name
}

export function categoryLabel(cat: string): string {
  return CATEGORY_LABELS[cat] || cat
}

export const BUILTIN_TOOL_NAMES = new Set(Object.keys(BUILTIN_DISPLAY))

import store from '@/store'

export type SSEEventType = 'delta' | 'done' | 'error'

export interface SSEEvent {
  type: SSEEventType
  content?: string
  message_id?: number
  created_at?: string
}

export function sendSSEMessage(
  conversationId: number,
  content: string,
  onEvent: (event: SSEEvent) => void,
  onError?: (err: Event) => void,
): AbortController {
  const controller = new AbortController()
  const token = store.state.auth.token

  fetch(`/api/chat/conversations/${conversationId}/messages`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ content }),
    signal: controller.signal,
  }).then(async (response) => {
    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: '请求失败' }))
      onEvent({ type: 'error', content: err.detail || '请求失败' })
      return
    }

    const reader = response.body?.getReader()
    if (!reader) return

    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        const trimmed = line.trim()
        if (!trimmed.startsWith('data: ')) continue
        try {
          const event: SSEEvent = JSON.parse(trimmed.slice(6))
          onEvent(event)
        } catch {
          // ignore malformed lines
        }
      }
    }
  }).catch((err) => {
    if (err.name !== 'AbortError') {
      onError?.(err)
    }
  })

  return controller
}
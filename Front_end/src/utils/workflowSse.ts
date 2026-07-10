import store from '@/store'
import type { WorkflowSSEEvent } from '@/types/execution'
import type { RunWorkflowPayload } from '@/api/execution'

export function runWorkflowSSE(
  workflowId: number,
  payload: RunWorkflowPayload,
  onEvent: (event: WorkflowSSEEvent) => void,
  onError?: (err: Event) => void,
): AbortController {
  const controller = new AbortController()
  const token = store.state.auth.token

  fetch(`/api/workflows/${workflowId}/run`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(payload),
    signal: controller.signal,
  }).then(async (response) => {
    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: '执行请求失败' }))
      onEvent({ type: 'error', content: err.detail || '执行请求失败' })
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
          const event: WorkflowSSEEvent = JSON.parse(trimmed.slice(6))
          onEvent(event)
        } catch {
          // ignore
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

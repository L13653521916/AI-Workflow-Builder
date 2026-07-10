<template>
  <div class="markdown-body" v-html="html"></div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { marked } from 'marked'
import hljs from 'highlight.js'
import 'highlight.js/styles/github-dark.css'

marked.setOptions({
  gfm: true,
  breaks: true,
})

const renderer = new marked.Renderer()
renderer.code = ({ text, lang }: { text: string; lang?: string }) => {
  const language = lang && hljs.getLanguage(lang) ? lang : 'plaintext'
  const highlighted = hljs.highlight(text, { language }).value
  return `<pre><code class="hljs language-${language}">${highlighted}</code></pre>`
}

const props = defineProps<{ content: string }>()

const html = computed(() => {
  return marked.parse(props.content || '', { renderer }) as string
})
</script>

<style scoped>
.markdown-body {
  font-size: 0.875rem;
  line-height: 1.7;
  word-break: break-word;
}
.markdown-body :deep(pre) {
  background: #1e1e1e;
  color: #d4d4d4;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  overflow-x: auto;
  margin: 0.5rem 0;
}
.markdown-body :deep(code) {
  font-family: 'Fira Code', 'Consolas', monospace;
  font-size: 0.8125rem;
}
.markdown-body :deep(:not(pre) > code) {
  background: #f0f0f0;
  padding: 0.15rem 0.35rem;
  border-radius: 0.25rem;
  color: #d63384;
}
.markdown-body :deep(p) {
  margin: 0.4rem 0;
}
.markdown-body :deep(ul),
.markdown-body :deep(ol) {
  padding-left: 1.5rem;
  margin: 0.4rem 0;
}
.markdown-body :deep(blockquote) {
  border-left: 3px solid #dfe2e5;
  padding-left: 0.75rem;
  color: #6a737d;
  margin: 0.5rem 0;
}
.markdown-body :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 0.5rem 0;
}
.markdown-body :deep(th),
.markdown-body :deep(td) {
  border: 1px solid #dfe2e5;
  padding: 0.4rem 0.6rem;
  text-align: left;
}
.markdown-body :deep(th) {
  background: #f6f8fa;
}
</style>
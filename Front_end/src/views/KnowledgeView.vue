<template>
  <div class="h-full flex flex-col">
  <!-- 列表视图 -->
  <template v-if="!currentKbId">
    <div class="p-4 border-b border-gray-200 flex items-center gap-4 bg-white shrink-0">
      <h2 class="text-lg font-semibold text-gray-800">知识库管理</h2>
      <el-button type="primary" size="small" @click="showCreate = true">
        新建知识库
      </el-button>
    </div>
    <div class="flex-1 overflow-y-auto p-4">
      <KBList
        :knowledge-bases="knowledgeBases"
        @manage="openDetail"
        @delete="deleteKB"
      />
    </div>
  </template>

  <!-- 详情视图 -->
  <DocUpload
    v-else
    :kb-id="currentKbId"
    @back="currentKbId = null"
  />

  <KBCreate
    v-model:visible="showCreate"
    :loading="creating"
    @create="handleCreate"
  />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { ElMessage, ElMessageBox } from 'element-plus'
import KBList from '@/components/knowledge/KBList.vue'
import KBCreate from '@/components/knowledge/KBCreate.vue'
import DocUpload from '@/components/knowledge/DocUpload.vue'

const store = useStore()
const knowledgeBases = computed(() => store.state.knowledge.knowledgeBases)

const showCreate = ref(false)
const creating = ref(false)
const currentKbId = ref<number | null>(null)

onMounted(() => {
  store.dispatch('knowledge/fetchKnowledgeBases')
})

function openDetail(id: number) {
  currentKbId.value = id
}

async function handleCreate(data: { name: string; description: string }) {
  creating.value = true
  try {
    await store.dispatch('knowledge/createKnowledgeBase', data)
    showCreate.value = false
    ElMessage.success('创建成功')
  } catch {
    // handled by interceptor
  } finally {
    creating.value = false
  }
}

async function deleteKB(id: number) {
  const kb = knowledgeBases.value.find((k: { id: number }) => k.id === id)
  try {
    await ElMessageBox.confirm(
      `确定删除知识库「${kb?.name || ''}」? 所有文档将一并删除。`,
      '删除确认',
      { type: 'warning' }
    )
  } catch {
    return
  }
  try {
    await store.dispatch('knowledge/deleteKnowledgeBase', id)
    if (currentKbId.value === id) currentKbId.value = null
    ElMessage.success('删除成功')
  } catch {
    // handled by interceptor
  }
}
</script>

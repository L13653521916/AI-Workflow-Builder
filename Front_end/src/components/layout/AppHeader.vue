<template>
  <header class="h-14 bg-white border-b border-gray-200 flex items-center px-3 sm:px-4 shrink-0">
    <div class="flex items-center gap-3 sm:gap-8 h-full min-w-0 flex-1">
      <span class="font-bold text-base sm:text-lg text-blue-600 select-none shrink-0">
        AI Workflow Builder
      </span>
      <nav class="flex gap-0.5 sm:gap-1 h-full overflow-x-auto scrollbar-hide min-w-0">
        <router-link
          v-for="tab in tabs"
          :key="tab.path"
          :to="tab.path"
          class="px-2 sm:px-4 h-full flex items-center text-xs sm:text-sm font-medium transition-colors whitespace-nowrap shrink-0"
          :class="isActive(tab.path) ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-600 hover:text-gray-900'"
        >
          {{ tab.label }}
        </router-link>
      </nav>
    </div>

    <div class="ml-2 flex items-center gap-2 shrink-0">
      <el-dropdown trigger="click" @command="handleCommand">
        <span class="cursor-pointer text-xs sm:text-sm text-gray-700 hover:text-gray-900 flex items-center gap-1 max-w-[100px] sm:max-w-none truncate">
          {{ username }}
          <el-icon><ArrowDown /></el-icon>
        </span>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="logout">退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useStore } from 'vuex'
import { ArrowDown } from '@element-plus/icons-vue'

const route = useRoute()
const store = useStore()

const username = computed(() => store.state.auth.user?.username || '用户')

const tabs = [
  { path: '/chat', label: '聊天' },
  { path: '/canvas', label: '画布' },
  { path: '/knowledge', label: '知识库' },
  { path: '/tools', label: '工具' },
  { path: '/models', label: '模型' },
]

function isActive(path: string) {
  return route.path === path
}

function handleCommand(cmd: string) {
  if (cmd === 'logout') {
    store.dispatch('auth/logout')
  }
}
</script>

<style scoped>
.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
.scrollbar-hide::-webkit-scrollbar {
  display: none;
}
</style>

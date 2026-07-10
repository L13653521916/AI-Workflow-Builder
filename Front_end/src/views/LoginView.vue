<template>
  <div class="auth-page">
    <div class="auth-wrapper">
      <form class="auth-form" @submit.prevent="handleLogin">
        <h1>Login</h1>
        <p class="auth-subtitle">AI Workflow Builder</p>

        <div class="auth-input-box">
          <input
            v-model="form.username"
            type="text"
            required
            placeholder=" "
            autocomplete="username"
          />
          <label>Username</label>
          <el-icon class="auth-icon"><User /></el-icon>
        </div>
        <p v-if="errors.username" class="auth-error">{{ errors.username }}</p>

        <div class="auth-input-box">
          <input
            v-model="form.password"
            type="password"
            required
            placeholder=" "
            autocomplete="current-password"
          />
          <label>Password</label>
          <el-icon class="auth-icon"><Lock /></el-icon>
        </div>
        <p v-if="errors.password" class="auth-error">{{ errors.password }}</p>

        <div class="auth-row">
          <span />
          <a @click.prevent="onForgotPassword">Forgot password?</a>
        </div>

        <button type="submit" class="auth-btn" :disabled="loading">
          {{ loading ? 'Logging in...' : 'Login' }}
        </button>

        <div class="auth-signup-link">
          <p>Don't have an account? <router-link to="/register">Create one.</router-link></p>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useStore } from 'vuex'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import '@/assets/auth.css'

const store = useStore()
const loading = ref(false)

const form = reactive({
  username: '',
  password: '',
})

const errors = reactive({
  username: '',
  password: '',
})

function validate(): boolean {
  errors.username = ''
  errors.password = ''
  let ok = true
  if (!form.username.trim()) {
    errors.username = '请输入用户名'
    ok = false
  }
  if (!form.password) {
    errors.password = '请输入密码'
    ok = false
  }
  return ok
}

async function handleLogin() {
  if (!validate()) return
  loading.value = true
  try {
    await store.dispatch('auth/login', { ...form })
  } catch {
    // handled by interceptor
  } finally {
    loading.value = false
  }
}

function onForgotPassword() {
  ElMessage.info('请联系管理员重置密码')
}
</script>

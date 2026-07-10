<template>
  <div class="auth-page">
    <div class="auth-wrapper">
      <form class="auth-form" @submit.prevent="handleRegister">
        <h1>Register</h1>
        <p class="auth-subtitle">Create your AI Workflow Builder account</p>

        <div class="auth-input-box">
          <input v-model="form.username" type="text" required placeholder=" " autocomplete="username" />
          <label>Username</label>
          <el-icon class="auth-icon"><User /></el-icon>
        </div>
        <p v-if="errors.username" class="auth-error">{{ errors.username }}</p>

        <div class="auth-input-box">
          <input v-model="form.email" type="email" required placeholder=" " autocomplete="email" />
          <label>Email</label>
          <el-icon class="auth-icon"><Message /></el-icon>
        </div>
        <p v-if="errors.email" class="auth-error">{{ errors.email }}</p>

        <div class="auth-input-box">
          <input v-model="form.password" type="password" required placeholder=" " autocomplete="new-password" />
          <label>Password</label>
          <el-icon class="auth-icon"><Lock /></el-icon>
        </div>
        <p v-if="errors.password" class="auth-error">{{ errors.password }}</p>

        <div class="auth-input-box">
          <input v-model="form.confirmPassword" type="password" required placeholder=" " autocomplete="new-password" />
          <label>Confirm Password</label>
          <el-icon class="auth-icon"><Lock /></el-icon>
        </div>
        <p v-if="errors.confirmPassword" class="auth-error">{{ errors.confirmPassword }}</p>

        <button type="submit" class="auth-btn" :disabled="loading">
          {{ loading ? 'Creating...' : 'Create Account' }}
        </button>

        <div class="auth-signup-link">
          <p>Already have an account? <router-link to="/login">Login</router-link></p>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'
import { ElMessage } from 'element-plus'
import { User, Lock, Message } from '@element-plus/icons-vue'
import '@/assets/auth.css'

const router = useRouter()
const store = useStore()
const loading = ref(false)

const form = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
})

const errors = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
})

function validate(): boolean {
  Object.assign(errors, { username: '', email: '', password: '', confirmPassword: '' })
  let ok = true
  if (!form.username.trim()) { errors.username = '请输入用户名'; ok = false }
  if (!form.email.trim()) { errors.email = '请输入邮箱'; ok = false }
  else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) { errors.email = '邮箱格式不正确'; ok = false }
  if (!form.password) { errors.password = '请输入密码'; ok = false }
  if (form.password !== form.confirmPassword) { errors.confirmPassword = '两次密码不一致'; ok = false }
  return ok
}

async function handleRegister() {
  if (!validate()) return
  loading.value = true
  try {
    await store.dispatch('auth/register', {
      username: form.username,
      email: form.email,
      password: form.password,
    })
    ElMessage.success('注册成功，请登录')
    router.push('/login')
  } catch {
    // handled by interceptor
  } finally {
    loading.value = false
  }
}
</script>

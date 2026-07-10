import axios, { type InternalAxiosRequestConfig } from 'axios'
import { ElLoading, ElMessage } from 'element-plus'
import store from '@/store'

declare module 'axios' {
  export interface InternalAxiosRequestConfig {
    skipLoading?: boolean
    skipErrorToast?: boolean
  }
}

const request = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

let loadingCount = 0
let loadingInstance: ReturnType<typeof ElLoading.service> | null = null

function startLoading() {
  if (loadingCount === 0) {
    loadingInstance = ElLoading.service({
      lock: true,
      text: '加载中...',
      background: 'rgba(0, 0, 0, 0.25)',
    })
  }
  loadingCount++
}

function stopLoading() {
  loadingCount = Math.max(0, loadingCount - 1)
  if (loadingCount === 0 && loadingInstance) {
    loadingInstance.close()
    loadingInstance = null
  }
}

function getErrorMessage(error: any): string {
  const detail = error.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return detail.map((item: any) => item.msg || item.message || String(item)).join('；')
  }
  if (error.message === 'Network Error') return '网络连接失败，请检查后端服务'
  if (error.code === 'ECONNABORTED') return '请求超时，请稍后重试'
  return error.message || '请求失败'
}

request.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = store.state.auth.token
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    if (!config.skipLoading) {
      startLoading()
    }
    return config
  },
  (error) => {
    stopLoading()
    return Promise.reject(error)
  }
)

request.interceptors.response.use(
  (response) => {
    if (!response.config.skipLoading) {
      stopLoading()
    }
    return response.data
  },
  (error) => {
    if (!error.config?.skipLoading) {
      stopLoading()
    }

    const msg = getErrorMessage(error)
    const status = error.response?.status

    if (status === 401) {
      const isAuthPage = window.location.pathname === '/login' || window.location.pathname === '/register'
      store.dispatch('auth/logout')
      if (!isAuthPage) {
        ElMessage.error('登录已过期，请重新登录')
        window.location.href = '/login'
      } else if (!error.config?.skipErrorToast) {
        ElMessage.error(msg)
      }
    } else if (!error.config?.skipErrorToast) {
      ElMessage.error(msg)
    }

    return Promise.reject(error)
  }
)

export default request

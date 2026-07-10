import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'
import store from './store'
import './assets/tailwind.css'
import '@vue-flow/core/dist/style.css'
import '@vue-flow/core/dist/theme-default.css'

import '@vue-flow/controls/dist/style.css'
import '@vue-flow/minimap/dist/style.css'

const app = createApp(App)
app.use(ElementPlus)
app.use(router)
app.use(store)
app.mount('#app')

// 刷新页面后从 token 恢复用户信息
if (store.state.auth.token) {
  store.dispatch('auth/fetchUser').catch(() => {})
}
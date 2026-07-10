import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import store from '@/store'
import MainLayout from '@/views/MainLayout.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/RegisterView.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: MainLayout,
    meta: { requiresAuth: true },
    redirect: '/chat',
    children: [
      {
        path: 'chat',
        name: 'Chat',
        component: () => import('@/views/ChatView.vue')
      },
      {
        path: 'canvas',
        name: 'Canvas',
        component: () => import('@/views/CanvasView.vue')
      },
      {
        path: 'knowledge',
        name: 'Knowledge',
        component: () => import('@/views/KnowledgeView.vue')
      },
      {
        path: 'tools',
        name: 'Tools',
        component: () => import('@/views/ToolsView.vue')
      },
      {
        path: 'models',
        name: 'Models',
        component: () => import('@/views/ModelsView.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, _from, next) => {
  const token = store.state.auth.token
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else if ((to.path === '/login' || to.path === '/register') && token) {
    next('/chat')
  } else {
    next()
  }
})

export default router
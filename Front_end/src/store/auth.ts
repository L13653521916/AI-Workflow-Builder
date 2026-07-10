import { Module } from 'vuex'
import type { RootState } from '../index'
import type { User } from '@/types/auth'
import * as authApi from '@/api/auth'
import router from '@/router'

export interface AuthState {
  token: string | null
  user: User | null
}

const auth: Module<AuthState, RootState> = {
  namespaced: true,

  state: () => ({
    token: localStorage.getItem('token'),
    user: null
  }),

  getters: {
    isLoggedIn: (state) => !!state.token,
    currentUser: (state) => state.user
  },

  mutations: {
    SET_TOKEN(state, token: string) {
      state.token = token
      localStorage.setItem('token', token)
    },
    SET_USER(state, user: User) {
      state.user = user
    },
    CLEAR_AUTH(state) {
      state.token = null
      state.user = null
      localStorage.removeItem('token')
    }
  },

  actions: {
    async login({ commit }, { username, password }) {
      const res = await authApi.login({ username, password })
      commit('SET_TOKEN', res.access_token)
      const user = await authApi.getMe()
      commit('SET_USER', user)
      router.push('/chat')
    },

    async register(_, data) {
      await authApi.register(data)
    },

    async fetchUser({ commit }) {
      try {
        const user = await authApi.getMe()
        commit('SET_USER', user)
      } catch {
        commit('CLEAR_AUTH')
      }
    },

    logout({ commit }) {
      commit('CLEAR_AUTH')
      router.push('/login')
    }
  }
}

export default auth
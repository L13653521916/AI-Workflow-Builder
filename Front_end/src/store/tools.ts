import { Module } from 'vuex'
import type { RootState } from '../index'
import type { Tool } from '@/types/tools'
import * as toolsApi from '@/api/tools'

export interface ToolsState {
  tools: Tool[]
  loading: boolean
}

const tools: Module<ToolsState, RootState> = {
  namespaced: true,

  state: () => ({
    tools: [],
    loading: false,
  }),

  getters: {
    categories(state): string[] {
      const cats = new Set(state.tools.map(t => t.category))
      return Array.from(cats).sort()
    },
    getToolByName: (state) => (name: string) => {
      return state.tools.find(t => t.name === name)
    },
  },

  mutations: {
    SET_TOOLS(state, list: Tool[]) {
      state.tools = list
    },
    ADD_TOOL(state, tool: Tool) {
      state.tools.unshift(tool)
    },
    REMOVE_TOOL(state, id: number) {
      state.tools = state.tools.filter(t => t.id !== id)
    },
    SET_LOADING(state, val: boolean) {
      state.loading = val
    },
  },

  actions: {
    async fetchTools({ commit }, category?: string) {
      commit('SET_LOADING', true)
      try {
        const list = await toolsApi.getTools(category)
        commit('SET_TOOLS', list)
      } finally {
        commit('SET_LOADING', false)
      }
    },

    async createTool({ commit }, data: import('@/types/tools').ToolCreateBody) {
      const tool = await toolsApi.createTool(data)
      commit('ADD_TOOL', tool)
      return tool
    },

    async deleteTool({ commit }, id: number) {
      await toolsApi.deleteTool(id)
      commit('REMOVE_TOOL', id)
    },
  },
}

export default tools

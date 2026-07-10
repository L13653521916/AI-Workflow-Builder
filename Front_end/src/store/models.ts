import { Module } from 'vuex'
import type { RootState } from '../index'
import type { ModelProfile, ModelProfileDetail, ModelProfileCreateBody, ModelProfileUpdateBody } from '@/types/models'
import * as modelsApi from '@/api/models'

export interface ModelsState {
  profiles: ModelProfile[]
  loading: boolean
}

const models: Module<ModelsState, RootState> = {
  namespaced: true,

  state: () => ({
    profiles: [],
    loading: false,
  }),

  getters: {
    defaultProfile(state): ModelProfile | undefined {
      return state.profiles.find(p => p.isDefault)
    },
    getProfileById: (state) => (id: number) => {
      return state.profiles.find(p => p.id === id)
    },
  },

  mutations: {
    SET_PROFILES(state, list: ModelProfile[]) {
      state.profiles = list
    },
    ADD_PROFILE(state, profile: ModelProfile) {
      state.profiles.unshift(profile)
    },
    UPDATE_PROFILE(state, profile: ModelProfile) {
      const idx = state.profiles.findIndex(p => p.id === profile.id)
      if (idx >= 0) state.profiles.splice(idx, 1, profile)
    },
    REMOVE_PROFILE(state, id: number) {
      state.profiles = state.profiles.filter(p => p.id !== id)
    },
    SET_LOADING(state, val: boolean) {
      state.loading = val
    },
  },

  actions: {
    async fetchProfiles({ commit }) {
      commit('SET_LOADING', true)
      try {
        const list = await modelsApi.getModelProfiles()
        commit('SET_PROFILES', list)
      } finally {
        commit('SET_LOADING', false)
      }
    },

    async createProfile({ commit, dispatch }, data: ModelProfileCreateBody) {
      const profile = await modelsApi.createModelProfile(data)
      await dispatch('fetchProfiles')
      return profile
    },

    async updateProfile({ commit, dispatch }, { id, data }: { id: number; data: ModelProfileUpdateBody }) {
      const profile = await modelsApi.updateModelProfile(id, data)
      commit('UPDATE_PROFILE', profile)
      await dispatch('fetchProfiles')
      return profile
    },

    async deleteProfile({ commit }, id: number) {
      await modelsApi.deleteModelProfile(id)
      commit('REMOVE_PROFILE', id)
    },

    async fetchProfileDetail(_ctx, id: number): Promise<ModelProfileDetail> {
      return modelsApi.getModelProfile(id)
    },
  },
}

export default models

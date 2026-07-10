import { Module } from 'vuex'
import type { RootState } from '../index'
import type { KnowledgeBase, Document } from '@/types/knowledge'
import * as kbApi from '@/api/knowledge'

export interface KnowledgeState {
  knowledgeBases: KnowledgeBase[]
  currentKBId: number | null
  documents: Document[]
  loading: boolean
}

const knowledge: Module<KnowledgeState, RootState> = {
  namespaced: true,

  state: () => ({
    knowledgeBases: [],
    currentKBId: null,
    documents: [],
    loading: false
  }),

  getters: {
    currentKB(state): KnowledgeBase | undefined {
      return state.knowledgeBases.find(kb => kb.id === state.currentKBId)
    }
  },

  mutations: {
    SET_KNOWLEDGE_BASES(state, list: KnowledgeBase[]) {
      state.knowledgeBases = list
    },
    SET_CURRENT_KB(state, id: number) {
      state.currentKBId = id
    },
    ADD_KNOWLEDGE_BASE(state, kb: KnowledgeBase) {
      state.knowledgeBases.unshift(kb)
    },
    REMOVE_KNOWLEDGE_BASE(state, id: number) {
      state.knowledgeBases = state.knowledgeBases.filter(kb => kb.id !== id)
      if (state.currentKBId === id) state.currentKBId = null
    },
    SET_DOCUMENTS(state, docs: Document[]) {
      state.documents = docs
    },
    ADD_DOCUMENT(state, doc: Document) {
      state.documents.push(doc)
    },
    REMOVE_DOCUMENT(state, docId: number) {
      state.documents = state.documents.filter(d => d.id !== docId)
    },
    UPDATE_KB_DOC_COUNT(state, { id, count }: { id: number; count: number }) {
      const kb = state.knowledgeBases.find(k => k.id === id)
      if (kb) kb.docCount = count
    },
    SET_LOADING(state, val: boolean) {
      state.loading = val
    },
  },

  actions: {
    async fetchKnowledgeBases({ commit }) {
      commit('SET_LOADING', true)
      try {
        const list = await kbApi.getKnowledgeBases()
        commit('SET_KNOWLEDGE_BASES', list)
      } finally {
        commit('SET_LOADING', false)
      }
    },

    async createKnowledgeBase({ commit }, data: { name: string; description: string }) {
      const kb = await kbApi.createKnowledgeBase(data)
      commit('ADD_KNOWLEDGE_BASE', kb)
      return kb
    },

    async deleteKnowledgeBase({ commit }, id: number) {
      await kbApi.deleteKnowledgeBase(id)
      commit('REMOVE_KNOWLEDGE_BASE', id)
    },

    async fetchDocuments({ commit }, kbId: number) {
      const docs = await kbApi.getDocuments(kbId)
      commit('SET_DOCUMENTS', docs)
    },

    async uploadDocument({ commit, state }, { kbId, file, onProgress }: { kbId: number; file: File; onProgress?: (p: number) => void }) {
      const doc = await kbApi.uploadDocument(kbId, file, onProgress)
      commit('ADD_DOCUMENT', doc)
      const kb = state.knowledgeBases.find(k => k.id === kbId)
      if (kb) {
        commit('UPDATE_KB_DOC_COUNT', { id: kbId, count: kb.docCount + 1 })
      }
      return doc
    },

    async deleteDocument({ commit, state }, { kbId, docId }: { kbId: number; docId: number }) {
      await kbApi.deleteDocument(kbId, docId)
      commit('REMOVE_DOCUMENT', docId)
      const kb = state.knowledgeBases.find(k => k.id === kbId)
      if (kb) {
        commit('UPDATE_KB_DOC_COUNT', { id: kbId, count: Math.max(kb.docCount - 1, 0) })
      }
    }
  }
}

export default knowledge
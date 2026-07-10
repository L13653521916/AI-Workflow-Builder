import { createStore } from 'vuex'
import auth from './auth'
import chat from './chat'
import canvas from './canvas'
import knowledge from './knowledge'
import tools from './tools'
import models from './models'

export interface RootState {
  auth: any
  chat: any
  canvas: any
  knowledge: any
  tools: any
  models: any
}

const store = createStore<RootState>({
  modules: {
    auth,
    chat,
    canvas,
    knowledge,
    tools,
    models,
  }
})

export default store
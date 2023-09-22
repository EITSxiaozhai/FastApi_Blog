import { createStore } from 'vuex'

export default createStore({
  state: {
    token: '', // 初始状态为空令牌
  },
  mutations: {
    setToken(state, token) {
      state.token = token;
    },
  },
  getters: {
    getToken(state) {
      return state.token;
    },
  },
  actions: {
    // 其他操作...
  },
  modules: {
    // 其他模块...
  }
})

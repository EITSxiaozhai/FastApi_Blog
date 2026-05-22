import { createStore as createVuexStore } from 'vuex'

const store = createVuexStore({
  state: {
    user: null,
    isAuthenticated: false
  },
  mutations: {
    setUser(state, user) {
      state.user = user
      state.isAuthenticated = !!user
    }
  },
  actions: {
    async login({ commit }, credentials) {
      // 实现登录逻辑
    },
    async logout({ commit }) {
      commit('setUser', null)
    }
  }
})

export default store 
import { createStore } from 'vuex';

export default createStore({
  state: {
  selectedBlog: null, // 存储选定的博客详情数据
},
  mutations: {
    SET_SELECTED_BLOG(state, blog) {
    state.selectedBlog = blog;
  },
  },
  actions: {
    setPersistentData({ commit }, data) {
      commit('SET_PERSISTENT_DATA', data);
    },
  },
});

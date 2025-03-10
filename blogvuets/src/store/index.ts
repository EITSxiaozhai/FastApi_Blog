import {createStore} from 'vuex';
import createPersistedState from "vuex-persistedstate";

// export default createStore({
//   // ...其他配置
//   plugins: [createPersistedState()],
// });
export default createStore({
    plugins: [createPersistedState()],
    state: {
        token: '', // 初始状态为空令牌
        username: '', // 添加一个用于用户名的新属性
        lastVisitedRoute: '',
        PagingRecord: '',
    },
    mutations: {
        setLastVisitedRoute(state, route) {
            state.lastVisitedRoute = route;
        },
        setPagingRecord(state, pagingRecord) {
            state.PagingRecord = pagingRecord;
        },
        setTokenAndUsername(state, {token, username}) {
            state.token = token;
            state.username = username;
        },
        setToken(state, token) {
            state.token = token;
        },
        setUsername(state, username) {
            state.username = username;
        },
    },
    getters: {
        getLastVisitedRoute: (state) => {
            return state.lastVisitedRoute;
        },
        getToken(state) {
            return state.token;
        },
        getPagingRecord: (state) => {
            return state.PagingRecord;
        },
        getUsername(state) {
            // Example getter
            return state.username
        },
    },
    actions: {
        // 其他操作...
    },
    modules: {
        // 其他模块...
    }
});
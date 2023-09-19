import {createStore} from 'vuex';

// 在你的 Vuex store 中添加一个状态来保存需要缓存的组件数据
const store = createStore({
    state: {
        cachedComponents: {},
    },
    mutations: {
        cacheComponentData(state, {route, data}) {
            state.cachedComponents[route.path] = data;
        },
        clearCachedComponentData(state, route) {
            delete state.cachedComponents[route.path];
        },
    },
});

// 在需要缓存的组件中，使用生命周期钩子来处理缓存逻辑
export default {
    beforeRouteEnter(to, from, next) {
        // 如果之前有缓存的数据，传递给组件
        if (store.state.cachedComponents[to.path]) {
            next((vm) => {
                vm.setData(store.state.cachedComponents[to.path]);
            });
        } else {
            // 没有缓存数据，正常进入组件
            next();
        }
    },
    beforeRouteLeave(to, from, next) {
        // 在离开组件前，缓存组件的数据
        store.commit('cacheComponentData', {
            route: to,
            data: this.getData(), // 获取组件需要缓存的数据
        });
        next();
    },
    methods: {
        getData() {
            // 返回组件需要缓存的数据
            // 例如：从 API 请求数据或者获取组件状态
        },
        setData(data) {
            // 将缓存的数据设置到组件状态中
        },
    },
};

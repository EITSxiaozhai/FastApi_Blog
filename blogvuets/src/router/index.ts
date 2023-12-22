import { createRouter, createWebHistory } from 'vue-router';
import BlogDetail from '../views/BlogDetail.vue';
import Index from '../views/IndexPage.vue';  // 修改相对路径
import UserLogin from '../views/user/UserLogin.vue';  // 修改相对路径
import UserReg from '../views/user/UserReg.vue';  // 修改相对路径

const router = createRouter({
    history: createWebHistory('/'),
    routes: [
        {
            path: '/',
            component: Index,
            name: 'home',
            meta: {
                cacheable: true,
                title: '首页'
            },
        },
        {
            path: '/blog',
            component: Index,
            name: 'home',
            meta: {
                cacheable: true,
                title: 'Exploit的Blog',
                keepAlive: true,
            },
        },
        {
            path: '/blog/:blogId',
            component: BlogDetail,
            meta: {
                cacheable: false,
                title: '详情页'
            },
        },
        {
            path: '/login',
            component: UserLogin,
            meta: {
                cacheable: false,
                title: '登录页面'
            },
        },
        {
            path: '/reg',
            component: UserReg,
            meta: {
                cacheable: false,
                title: '注册页面'
            },
        },
    ]
});

export default router;

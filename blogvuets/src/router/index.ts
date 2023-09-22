import {createRouter, createWebHistory} from 'vue-router'
import BlogDetail from '../views/BlogDetail.vue'
import Index from "../views/IndexPage.vue"
import Iogin from "../views/user/Userlogin.vue"
import userReg from "../views/user/Userreg.vue"

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: "/",
            component: Index,
            name: "home",
            meta: {
                cacheable: true, // 添加缓存标志
                title: '首页'
            },
        },
        {
            path: '/blog',
            component: Index,
            name: "home", // 重复使用 Index 组件
            meta: {
                cacheable: true, // 添加缓存标志
                title: 'Exploit的Blog',
                keepAlive: true,
            },
        },
        {
            path: '/blog/:blogId',
            component: BlogDetail,
            meta: {
                cacheable: false, // 不缓存该组件
                title: '详情页'
            },
        },
        {
            path: '/login',
            component: Iogin,
            meta: {
                cacheable: false, // 不缓存该组件
                title: '登录页面'
            },
        },
        {
            path: '/reg',
            component: userReg,
            meta: {
                cacheable: false, // 不缓存该组件
                title: '注册页面'
            },
        },
    ]
})

export default router;

import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import HomeView from '../views/IndexPage.vue'
import BlogDetail from '../views/BlogDetail.vue'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  {
            path: '/blog/:blogId',
            component: BlogDetail,
            meta: {
                cacheable: false, // 不缓存该组件
                title: '详情页'
            },
  },
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router

import { createRouter, createWebHistory } from 'vue-router'
import BlogDetail from '../views/BlogDetail.vue'
import Index from "@/views/Index.vue";
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path:"/"
    },
    {
      path:'/blog',
      component: Index,
      name:"home"
    },
    {
    path: '/blog/:blogId',
    component: BlogDetail
    }
  ]
})

export default router

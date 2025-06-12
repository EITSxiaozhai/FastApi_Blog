import { createRouter as createVueRouter, createWebHistory } from 'vue-router'

const router = createVueRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: () => import('./pages/index/+Page.vue')
    },
    {
      path: '/blog/:id',
      component: () => import('./pages/blog/@blogId/+Page.vue')
    },
    {
      path: '/about',
      component: () => import('./pages/about-me/+Page.vue')
    }
  ]
})

export default router 
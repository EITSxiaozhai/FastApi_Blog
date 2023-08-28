import { createRouter, createWebHistory } from 'vue-router'
import BlogDetail from '../views/BlogDetail.vue'
import Index from "@/views/Index.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      component: Index,
      name: "home",
      meta: {
        cacheable: true, // 添加缓存标志
      },
    },
    {
      path: '/blog',
      component: Index,
      name: "home", // 重复使用 Index 组件
      meta: {
        cacheable: true, // 添加缓存标志
      },
    },
    {
      path: '/blog/:blogId',
      component: BlogDetail,
      meta: {
        cacheable: false, // 不缓存该组件
      },
    },
  ]
})

// 在路由守卫中处理页面缓存
router.beforeEach((to, from, next) => {
  if (to.meta.cacheable) {
    // 如果目标路由需要缓存，你可以在这里执行一些缓存逻辑
    // 例如将组件的状态存储到 Vuex 中
    // 或者将组件实例保存到一个缓存对象中
    // 注意：你可能需要在组件销毁时移除缓存数据，以防止内存泄漏
  }
  next();
});

export default router;

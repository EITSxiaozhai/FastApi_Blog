import { createRouter, createWebHistory } from 'vue-router';
import BlogDetail from '../views/BlogDetail.vue';
import Index from '../views/IndexPage.vue';
import UserLogin from '../views/user/UserLogin.vue';
import UserReg from '../views/user/UserReg.vue';

const router = createRouter({
  history: createWebHistory('/'),
  routes: [
    {
      path: '/',
      component: Index,
      name: 'home',
      meta: {
        cacheable: true,
        title: 'Exp1oit的Blog',
        // description: 'Exploit的Blog',
        keepAlive: true,
      },
    },
    {
      path: '/blog/:blogId',
      component: BlogDetail,
      meta: {
        cacheable: false,
        title: 'Blog详情',
        // description: '这是 Blog 详情页面的描述文本',
      },
    },
    {
      path: '/login',
      component: UserLogin,
      meta: {
        cacheable: false,
        title: 'Exp1oit 登录页面',
        // description: 'Exp1oit 登录页面',
      },
    },
    {
      path: '/reg',
      component: UserReg,
      meta: {
        cacheable: false,
        title: 'Exp1oit 注册页面',
        // description: 'Exp1oit 注册页面',
      },
    },
  ]
});

router.beforeEach((to:any) => {
  if (to.meta.title) {
    document.title = to.meta.title;
  }
});

router.beforeEach((to,from,next) => {
  if (to.matched.length === 0){
    from.path? next({path:from.path}) : next('/');
  }else {
    next();
  }
});

export default router;

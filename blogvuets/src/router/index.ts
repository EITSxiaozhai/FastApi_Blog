import {createRouter, createWebHistory} from 'vue-router';
import BlogDetail from '../views/BlogPages/BlogDetail.vue';
import Index from '../views/BlogPages/IndexPage.vue';
import UserLogin from '../views/user/UserLogin.vue';
import UserReg from '../views/user/UserReg.vue';
import error from '../views/errorpage/Error.vue';
import OAuthCallback from '@/views/user/OAuthCallback.vue';

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
                title: '页面加载中-Pageloading',
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
        {
            path: '/errorpage',
            component: error,
            name: 'errorPage',
            meta: {
                cacheable: false,
                title: "404页面未找到"
            },
        },
        {
            path: '/oauth-callback',
            component : OAuthCallback ,
            meta: {
                requiresAuth: false,
                hideHeader: true,
                title: "授权成功等待跳转",
            }
        }
    ]
});

router.beforeEach((to: any) => {
    if (to.meta.title) {
        document.title = to.meta.title;
    }
});

router.beforeEach((to, from, next) => {
    if (to.matched.length === 0) {
        from.path ? next({path: from.path}) : next('/');
    } else {
        next();
    }
});

export default router;

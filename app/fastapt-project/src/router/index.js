import Vue from 'vue'
import VueRouter from 'vue-router'
import Home from '../views/HomePage.vue'
//1 注入插件
Vue.use(VueRouter)

//2 定义路由
const routes =  [
      //添加映射关系
  {
	//默认首页
    path: '/',
    redirect: '/home'
  }, {

    path: '/home',
    component: Home
  },
]

//3 创建router实例
const router = new VueRouter({
  mode: 'history', //history模式
  routes
})

//4 导出router实例
export default router
import App from './App.vue'
import { createApp } from 'vue'
import Layui from '@layui/layui-vue'
import '@layui/layui-vue/lib/index.css'
import router from "./route" //匹配自己项目所对应的路径

createApp(App).use(router).mount("#app") //使用配置的路由
createApp(App).use(Layui).mount('#app')
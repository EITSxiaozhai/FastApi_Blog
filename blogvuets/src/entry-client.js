import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import { createHead } from '@unhead/vue'
import './assets/css/css-vars.css'  // 导入基础 CSS 变量

const app = createApp(App)
const head = createHead()

app.use(router)
app.use(store)
app.use(ElementPlus)
app.use(head)

// 恢复服务端状态
if (window.__INITIAL_STATE__) {
  store.replaceState(window.__INITIAL_STATE__)
}

router.isReady().then(() => {
  app.mount('#app', true) // 启用水合模式
}) 
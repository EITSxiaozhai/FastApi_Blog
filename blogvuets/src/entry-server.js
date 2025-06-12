import { createApp as createVueApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import { createHead } from '@unhead/vue'

export async function createSSRApp() {
  const app = createVueApp(App)
  const head = createHead()
  
  app.use(router)
  app.use(store)
  app.use(ElementPlus)
  app.use(head)
  
  return { app, router, store }
} 
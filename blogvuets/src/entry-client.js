import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import { createHead } from '@unhead/vue'

const app = createApp(App)
const head = createHead()

app.use(router)
app.use(store)
app.use(ElementPlus)
app.use(head)

router.isReady().then(() => {
  app.mount('#app')
}) 
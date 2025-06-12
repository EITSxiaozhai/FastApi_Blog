import { createApp } from './main'
import { createRouter } from './router'
import { createStore } from './store'

const app = createApp()
const router = createRouter()
const store = createStore()

app.use(router)
app.use(store)

router.isReady().then(() => {
  app.mount('#app')
}) 
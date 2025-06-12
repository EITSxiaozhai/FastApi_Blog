import { createApp as createVueApp } from './main'
import { createRouter } from './router'
import { createStore } from './store'

export async function createApp() {
  const app = createVueApp()
  const router = createRouter()
  const store = createStore()

  app.use(router)
  app.use(store)

  return { app, router, store }
} 
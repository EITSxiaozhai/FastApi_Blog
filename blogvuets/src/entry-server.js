import { createApp } from './main'
import { createRouter } from './router'
import { createStore } from './store'

export async function createApp() {
  const app = createApp()
  const router = createRouter()
  const store = createStore()

  app.use(router)
  app.use(store)

  return { app, router, store }
} 
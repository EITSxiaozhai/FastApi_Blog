import { createServer } from 'vite'
import { createApp } from './dist/server/entry-server.js'

export default {
  async fetch(request, env, ctx) {
    try {
      const url = new URL(request.url)
      
      // 处理静态资源
      if (url.pathname.startsWith('/assets/') || url.pathname.startsWith('/images/')) {
        return env.ASSETS.fetch(request)
      }

      // 处理 SSR 请求
      const app = await createApp()
      const html = await app.renderToString()
      
      return new Response(html, {
        headers: {
          'content-type': 'text/html;charset=UTF-8',
        },
      })
    } catch (e) {
      return new Response('Internal Server Error', { status: 500 })
    }
  },
} 
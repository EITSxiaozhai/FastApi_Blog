import { createSSRApp } from './src/entry-server.js'

export default {
  async fetch(request, env, ctx) {
    try {
      const url = new URL(request.url)
      
      // 处理静态资源
      if (url.pathname.startsWith('/assets/') || url.pathname.startsWith('/images/')) {
        return env.ASSETS.fetch(request)
      }

      // 创建应用实例
      const { app, router, store } = await createSSRApp()
      
      // 设置路由
      router.push(url.pathname)
      await router.isReady()
      
      // 渲染应用
      const html = await app.render()
      
      // 返回完整的 HTML
      return new Response(
        `<!DOCTYPE html>
        <html>
          <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width,initial-scale=1">
            <title>FastAPI Blog</title>
            <link rel="stylesheet" href="/assets/index.css">
          </head>
          <body>
            <div id="app">${html}</div>
            <script type="module" src="/assets/entry-client.js"></script>
          </body>
        </html>`,
        {
          headers: {
            'content-type': 'text/html;charset=UTF-8',
          },
        }
      )
    } catch (e) {
      console.error(e)
      return new Response('Internal Server Error', { status: 500 })
    }
  },
} 
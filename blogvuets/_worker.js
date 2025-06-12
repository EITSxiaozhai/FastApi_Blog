import { renderToString } from 'vue/server-renderer'

export default {
  async fetch(request, env, ctx) {
    try {
      const url = new URL(request.url)
      const pathname = url.pathname
      
      // 处理静态资源
      if (pathname.startsWith('/assets/') || 
          pathname.startsWith('/static/') || 
          pathname.startsWith('/images/') ||
          pathname.endsWith('.ico') ||
          pathname.endsWith('.png') ||
          pathname.endsWith('.jpg') ||
          pathname.endsWith('.gif') ||
          pathname.endsWith('.css') ||
          pathname.endsWith('.js')) {
        return env.ASSETS.fetch(request)
      }

      // 动态导入服务端入口
      const { createApp } = await import('./assets/server.js')
      
      // 创建应用实例
      const { app, router, store } = await createApp()
      
      // 设置当前路由
      if (router) {
        router.push(pathname)
        await router.isReady()
      }
      
      // 服务端渲染
      const appHtml = await renderToString(app)
      
      // 获取初始状态
      const initialState = store ? store.state : {}
      
      // 构建完整的 HTML 响应
      const html = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FastAPI Blog</title>
    <link rel="stylesheet" href="/assets/main.css">
    <link rel="stylesheet" href="/assets/server.css">
</head>
<body>
    <div id="app">${appHtml}</div>
    <script>
        window.__INITIAL_STATE__ = ${JSON.stringify(initialState).replace(/</g, '\\u003c')}
    </script>
    <script type="module" src="/assets/client.js"></script>
</body>
</html>`
      
      return new Response(html, {
        headers: {
          'content-type': 'text/html;charset=UTF-8',
          'cache-control': 'public, max-age=300'
        },
      })
      
    } catch (error) {
      console.error('SSR Error:', error)
      
      // 返回基础 HTML 作为降级方案
      const fallbackHtml = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FastAPI Blog</title>
    <link rel="stylesheet" href="/assets/main.css">
</head>
<body>
    <div id="app"></div>
    <script type="module" src="/assets/client.js"></script>
</body>
</html>`
      
      return new Response(fallbackHtml, {
        headers: {
          'content-type': 'text/html;charset=UTF-8',
        },
      })
    }
  },
} 
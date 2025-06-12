import { renderToString } from 'vue/server-renderer'

// Polyfill for Node.js APIs that might be missing in Workers environment
if (typeof global === 'undefined') {
  globalThis.global = globalThis
}

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
          pathname.endsWith('.js') ||
          pathname.endsWith('.woff') ||
          pathname.endsWith('.woff2') ||
          pathname.endsWith('.ttf')) {
        return env.ASSETS.fetch(request)
      }

      // 设置全局 fetch（如果需要的话）
      if (!globalThis.fetch) {
        globalThis.fetch = fetch
      }

      let createApp
      try {
        // 尝试导入服务端入口
        const serverModule = await import('./assets/server.js')
        createApp = serverModule.createApp
        console.log('✅ 成功导入 server.js')
      } catch (serverError) {
        console.error('❌ 无法导入 server.js:', serverError)
        
        // 尝试其他可能的入口文件
        try {
          const indexModule = await import('./assets/index.js')
          createApp = indexModule.createApp
          console.log('✅ 从 index.js 导入成功')
        } catch (indexError) {
          console.error('❌ 无法导入 index.js:', indexError)
          throw new Error('无法找到有效的服务端入口模块')
        }
      }

      if (!createApp) {
        throw new Error('createApp 函数未找到')
      }
      
      // 创建应用实例
      const { app, router, store } = await createApp()
      
      // 设置当前路由
      if (router) {
        await router.push(pathname)
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
    <meta name="description" content="FastAPI Blog - 技术分享与知识记录">
    <title>FastAPI Blog</title>
    <link rel="preload" href="/assets/client.js" as="script">
    <style>
        body { margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
        .loading { display: flex; justify-content: center; align-items: center; min-height: 100vh; }
    </style>
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
          'cache-control': 'public, max-age=300, s-maxage=600',
          'x-powered-by': 'Vike-SSR-Cloudflare-Workers'
        },
      })
      
    } catch (error) {
      console.error('SSR Error:', error)
      console.error('Error stack:', error.stack)
      
      // 返回基础 HTML 作为降级方案
      const fallbackHtml = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FastAPI Blog</title>
    <style>
        body { margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
        .error-fallback {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 50vh;
            padding: 2rem;
            text-align: center;
        }
        .error-message {
            color: #666;
            margin-top: 1rem;
        }
    </style>
</head>
<body>
    <div id="app">
        <div class="error-fallback">
            <h1>正在加载...</h1>
            <p class="error-message">SSR 渲染失败，正在切换到客户端渲染模式</p>
            <p class="error-message">错误信息: ${error.message}</p>
        </div>
    </div>
    <script type="module" src="/assets/client.js"></script>
</body>
</html>`
      
      return new Response(fallbackHtml, {
        status: 200, // 返回 200 而不是 500，让客户端接管
        headers: {
          'content-type': 'text/html;charset=UTF-8',
        },
      })
    }
  },
} 
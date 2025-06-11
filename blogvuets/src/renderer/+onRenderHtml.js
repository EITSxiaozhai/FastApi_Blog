import { renderToString } from 'vue/server-renderer'
import { createSSRApp } from 'vue'
import { escapeInject, dangerouslySkipEscape } from 'vike/server'
import ElementPlus, { ID_INJECTION_KEY } from 'element-plus'
import UndrawUi from 'undraw-ui'

export { onRenderHtml }

async function onRenderHtml(pageContext) {
  const { Page, pageProps, data } = pageContext
  
  console.log('🔧 服务器端渲染 - pageProps:', pageProps)
  console.log('🔧 服务器端渲染 - data:', data)
  
  // 创建SSR应用，将data作为props传递
  const app = createSSRApp(Page, data || pageProps)
  
  // 提供Element Plus SSR ID注入器
  app.provide(ID_INJECTION_KEY, {
    prefix: Math.floor(Math.random() * 10000),
    current: 0,
  })
  
  // 添加插件（与原main.ts保持一致）
  app.use(ElementPlus)
  app.use(UndrawUi)
  
  // 渲染为HTML字符串
  const appHtml = await renderToString(app)

  const documentHtml = escapeInject`<!DOCTYPE html>
    <html lang="zh-CN">
      <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>关于我 - Exp1oit的Blog</title>
        <meta name="description" content="Exp1oit的个人博客" />
        
        <!-- Element Plus CSS -->
        <link rel="stylesheet" href="https://unpkg.com/element-plus/dist/index.css">
        <!-- Undraw UI CSS -->
        <link rel="stylesheet" href="https://unpkg.com/undraw-ui/dist/style.css">
        <!-- Animate CSS -->
        <link rel="stylesheet" href="https://unpkg.com/animate.css/animate.min.css">
        
        <style>
          body {
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background-color: #f5f5f5;
          }
          #app {
            min-height: 100vh;
            padding: 20px 0;
          }
          
          /* 暗色主题支持 */
          html.dark {
            background-color: #1a1a1a;
            color: #ffffff;
          }
          html.dark body {
            background-color: #1a1a1a;
          }
        </style>
      </head>
      <body>
        <div id="app">${dangerouslySkipEscape(appHtml)}</div>
        <script>
          // 将服务器端数据传递给客户端
          window.__VIKE_PAGE_PROPS__ = ${dangerouslySkipEscape(JSON.stringify(data || pageProps))}
        </script>
      </body>
    </html>`

  return {
    documentHtml,
    pageContext: {
      // 可以添加额外的context数据
    }
  }
} 
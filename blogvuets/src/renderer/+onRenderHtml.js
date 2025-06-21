import { renderToString } from 'vue/server-renderer'
import { createSSRApp } from 'vue'
import { escapeInject, dangerouslySkipEscape } from 'vike/server'
import ElementPlus, { ID_INJECTION_KEY } from 'element-plus'
import UndrawUi from 'undraw-ui'

export { onRenderHtml }

async function onRenderHtml(pageContext) {
  const { Page, pageProps, data, routeParams, urlPathname } = pageContext
  
  // 根据路由动态生成页面title
  const getPageTitle = () => {
    // 博客详情页
    if (urlPathname.startsWith('/blog/') && data?.blog?.title) {
      return `${data.blog.title} | Exp1oit 的技术博客`
    }
    
    // 首页
    if (urlPathname === '/') {
      const totalArticles = data?.stats?.articles || data?.articles?.length || 0
      return `Exp1oit 的技术博客 | ${totalArticles}篇原创文章 | Vue + FastAPI 全栈开发`
    }
    
    // 登录页
    if (urlPathname === '/login') {
      return '用户登录 | Exp1oit 的技术博客'
    }
    
    // 注册页
    if (urlPathname === '/reg') {
      return '用户注册 | Exp1oit 的技术博客'
    }
    
    // 关于我页面
    if (urlPathname === '/about-me') {
      return '关于我 | Exp1oit 的技术博客'
    }
    
    // 错误页面
    if (urlPathname === '/errorpage') {
      return '页面错误 | Exp1oit 的技术博客'
    }
    
    // OAuth回调页面
    if (urlPathname === '/oauth-callback') {
      return '登录中... | Exp1oit 的技术博客'
    }
    
    // 默认title
    return 'Exp1oit 的技术博客'
  }
  
  // 根据路由动态生成页面描述
  const getPageDescription = () => {
    // 博客详情页
    if (urlPathname.startsWith('/blog/') && data?.blog) {
      return data.blog.summary || data.blog.excerpt || '来自 Exp1oit 的技术博客'
    }
    
    // 首页
    if (urlPathname === '/') {
      const { pv = 0, uv = 0, articles = 0 } = data?.stats || {}
      return `专注于Vue、FastAPI、全栈开发的技术博客，${articles}篇原创文章，${pv}次浏览，${uv}位访客。分享前端后端最佳实践、SSR渲染、API设计等技术经验。`
    }
    
    // 登录页
    if (urlPathname === '/login') {
      return '登录 Exp1oit 的技术博客，获取更好的阅读体验'
    }
    
    // 注册页
    if (urlPathname === '/reg') {
      return '注册 Exp1oit 的技术博客账户，加入技术交流社区'
    }
    
    // 关于我页面
    if (urlPathname === '/about-me') {
      return '了解 Exp1oit，一个专注于全栈开发的技术博客作者，分享 Vue、FastAPI、TypeScript 等技术经验'
    }
    
    // 默认描述
    return 'Exp1oit 的技术博客，专注于全栈开发技术分享'
  }
  
  const pageTitle = getPageTitle()
  const pageDescription = getPageDescription()
  
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
        <title>${pageTitle}</title>
        <meta name="description" content="${pageDescription}" />
        
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
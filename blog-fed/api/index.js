import { renderPage } from 'vike/server'
import fs from 'node:fs'
import path from 'node:path'

export default async function handler(req, res) {
  const { url } = req
  const userAgent = req.headers['user-agent'] || ''
  
  try {
    // 静态资源直出（在函数内兜底提供），避免静态路由未命中导致 404/500
    if (
      url.startsWith('/assets/') ||
      url.startsWith('/entries/') ||
      url.startsWith('/static/') ||
      url === '/favicon.ico'
    ) {
      const filePathCandidates = [
        path.join(process.cwd(), 'dist', 'client', url),
        path.join(process.cwd(), 'dist', 'client', url.replace(/^\/+/, '')),
        // 某些构建会把资源放到 dist/client/client 下
        path.join(process.cwd(), 'dist', 'client', 'client', url.replace(/^\/+/, ''))
      ]
      let foundPath = null
      for (const p of filePathCandidates) {
        if (fs.existsSync(p) && fs.statSync(p).isFile()) {
          foundPath = p
          break
        }
      }
      if (foundPath) {
        const ext = path.extname(foundPath).toLowerCase()
        const contentType =
          ext === '.js' ? 'application/javascript; charset=utf-8' :
          ext === '.css' ? 'text/css; charset=utf-8' :
          ext === '.png' ? 'image/png' :
          ext === '.webp' ? 'image/webp' :
          ext === '.ico' ? 'image/x-icon' :
          ext === '.gif' ? 'image/gif' :
          ext === '.svg' ? 'image/svg+xml' :
          'application/octet-stream'
        res.setHeader('Cache-Control', 'public, max-age=31536000, immutable')
        res.setHeader('Content-Type', contentType)
        fs.createReadStream(foundPath).pipe(res)
        return
      }
      // 找不到时继续交给 SSR（以便返回 404 页）
    }

    const pageContextInit = {
      urlOriginal: url,
      userAgent
    }
    
    const pageContext = await renderPage(pageContextInit)
    
    if (pageContext.httpResponse) {
      const { statusCode, headers, body } = pageContext.httpResponse
      
      // 设置响应头
      if (headers) {
        Object.entries(headers).forEach(([name, value]) => {
          res.setHeader(name, value)
        })
      }
      
      res.status(statusCode || 200).send(body)
    } else {
      // 使用友好的404页面
      res.status(404).send(`
        <!DOCTYPE html>
        <html>
          <head>
            <meta charset="UTF-8">
            <title>页面未找到</title>
            <style>
              body { 
                font-family: system-ui, -apple-system, sans-serif;
                display: flex;
                align-items: center;
                justify-content: center;
                height: 100vh;
                margin: 0;
                background: #f5f5f5;
              }
              .error-container {
                text-align: center;
                padding: 2rem;
              }
              h1 { color: #333; }
              p { color: #666; }
            </style>
          </head>
          <body>
            <div class="error-container">
              <h1>404</h1>
              <p>抱歉，您访问的页面不存在</p>
            </div>
          </body>
        </html>
      `)
    }
  } catch (error) {

    // 生产环境中只记录错误，不在控制台显示详细信息
    if (process.env.NODE_ENV === 'development') {
      console.error('SSR Error:', error)
    }
    res.status(500).json({ 
      error: 'Internal Server Error',
      message: error.message
    })

    
    // 返回友好的错误页面
    res.status(500).send(`
      <!DOCTYPE html>
      <html>
        <head>
          <meta charset="UTF-8">
          <title>服务器错误</title>
          <style>
            body { 
              font-family: system-ui, -apple-system, sans-serif;
              display: flex;
              align-items: center;
              justify-content: center;
              height: 100vh;
              margin: 0;
              background: #f5f5f5;
            }
            .error-container {
              text-align: center;
              padding: 2rem;
            }
            h1 { color: #333; }
            p { color: #666; }
          </style>
        </head>
        <body>
          <div class="error-container">
            <h1>500</h1>
            <p>抱歉，服务器出现了一些问题</p>
          </div>
        </body>
      </html>
    `)
  }
} 
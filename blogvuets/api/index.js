import { renderPage } from 'vike/server'

export default async function handler(req, res) {
  const { url } = req
  const userAgent = req.headers['user-agent'] || ''
  
  try {
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
      res.status(404).send('Page not found')
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
  }
} 
import { createApp } from 'vue'
import ElementPlus, { ID_INJECTION_KEY } from 'element-plus'
import UndrawUi from 'undraw-ui'

export { onRenderClient }

async function onRenderClient(pageContext) {
  const { Page, pageProps, data } = pageContext
  
  // 优先使用服务器端传递的数据
  const clientData = window.__VIKE_PAGE_PROPS__ || data || pageProps
  
  // 只在开发环境中显示调试日志
  if (import.meta.env?.DEV) {
    console.log('🔧 客户端渲染 - pageContext:', pageContext)
    console.log('🔧 客户端渲染 - pageProps:', pageProps)
    console.log('🔧 客户端渲染 - data:', data)
    console.log('🔧 客户端渲染 - clientData:', clientData)
  }
  
  // 创建客户端应用，使用正确的数据
  const app = createApp(Page, clientData)
  
  // 提供Element Plus客户端ID注入器
  app.provide(ID_INJECTION_KEY, {
    prefix: Math.floor(Math.random() * 10000),
    current: 0,
  })
  
  // 添加插件（与服务器端保持一致）
  app.use(ElementPlus)
  app.use(UndrawUi)
  
  // 挂载到DOM（这会进行hydration）
  app.mount('#app')
} 
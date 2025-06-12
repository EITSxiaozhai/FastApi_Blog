import axios from 'axios'

// API配置
const apis = {
  production: 'https://blogapi-traefik.exploit-db.xyz/api/',
  development: 'http://127.0.0.1:8000/api/',
  test: 'http://192.168.0.150:49200/api/'
}

// 根据环境选择API地址
const getBaseURL = () => {
  // 在 Cloudflare Workers 环境中，总是使用生产环境 API
  if (typeof window === 'undefined') {
    // 服务器端环境 (SSR)
    console.log('🔧 SSR环境 - 使用生产API:', apis.production)
    return apis.production
  } else {
    // 客户端环境
    const isProduction = process.env.NODE_ENV === 'production' || 
                        window.location.hostname.includes('workers.dev') ||
                        window.location.hostname.includes('exploit-db.xyz')
    const apiUrl = isProduction ? apis.production : apis.development
    console.log('🔧 客户端环境 - API地址:', apiUrl)
    return apiUrl
  }
}

// 创建axios实例
const vikeApi = axios.create({
  baseURL: getBaseURL(),
  timeout: 15000, // 增加超时时间
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
})

// 请求拦截器
vikeApi.interceptors.request.use(
  config => {
    console.log(`🌐 API请求: ${config.method?.toUpperCase()} ${config.baseURL}${config.url}`)
    
    // 在服务器端添加必要的headers
    if (typeof window === 'undefined') {
      config.headers['User-Agent'] = 'Vike-Blog-SSR/1.0'
      config.headers['X-Forwarded-For'] = '127.0.0.1'
    }
    
    // 如果有token，添加到请求头
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('token')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
    }
    
    return config
  },
  error => {
    console.error('🚨 API请求拦截器错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
vikeApi.interceptors.response.use(
  response => {
    console.log(`✅ API响应成功: ${response.config.method?.toUpperCase()} ${response.config.url} - 状态: ${response.status}`)
    return response
  },
  error => {
    if (error.response) {
      const status = error.response.status
      console.error(`🚨 API错误 ${status}:`, {
        url: error.config?.url,
        method: error.config?.method,
        data: error.response.data,
        headers: error.response.headers
      })
      
      // 在客户端环境处理错误重定向
      if (typeof window !== 'undefined') {
        if (status === 404 || status === 500) {
          console.warn('⚠️ 严重错误，但不重定向到错误页面以避免影响用户体验')
          // window.location.href = '/errorpage'
        }
      }
    } else if (error.request) {
      console.error('🚨 网络错误 - 无响应:', {
        url: error.config?.url,
        method: error.config?.method,
        message: error.message,
        code: error.code
      })
    } else {
      console.error('🚨 请求配置错误:', error.message)
    }
    return Promise.reject(error)
  }
)

export default vikeApi

// 导出类型定义
export interface ApiResponse<T = any> {
  data: T
  status: number
  message?: string
}

// 通用API包装函数
export const apiWrapper = async <T>(apiCall: Promise<any>): Promise<T | null> => {
  try {
    const response = await apiCall
    console.log('✅ API包装器 - 调用成功:', {
      status: response.status,
      dataType: typeof response.data,
      hasData: !!response.data
    })
    return response.data
  } catch (error: any) {
    console.error('🚨 API包装器 - 调用失败:', {
      message: error?.message,
      code: error?.code,
      status: error?.response?.status,
      url: error?.config?.url
    })
    return null
  }
} 
import axios from 'axios'

// API配置
const apis = {
  production: 'https://blogapi-traefik.exploit-db.xyz/api/',
  development: 'http://127.0.0.1:8000/api/',
  test: 'http://192.168.0.150:49200/api/'
}

// 根据环境选择API地址
const getBaseURL = () => {
  if (typeof window === 'undefined') {
    // 服务器端环境
    return process.env.NODE_ENV === 'production' ? apis.production : apis.development
  } else {
    // 客户端环境
    return process.env.NODE_ENV === 'production' ? apis.production : apis.development
  }
}

// 创建axios实例
const vikeApi = axios.create({
  baseURL: getBaseURL(),
  timeout: 10000
})

// 请求拦截器
vikeApi.interceptors.request.use(
  config => {
    // 在服务器端添加必要的headers
    if (typeof window === 'undefined') {
      config.headers['User-Agent'] = 'Vike-Blog-SSR/1.0'
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
    return Promise.reject(error)
  }
)

// 响应拦截器
vikeApi.interceptors.response.use(
  response => {
    return response
  },
  error => {
    if (error.response) {
      const status = error.response.status
      // 在开发环境下才打印详细错误
      if (process.env.NODE_ENV === 'development') {
        console.error(`API Error ${status}:`, error.response.data)
      }
      
      // 在客户端环境处理错误重定向
      if (typeof window !== 'undefined') {
        if (status === 404 || status === 500) {
          // 使用更友好的错误页面
          window.location.href = '/errorpage'
        }
      }
    } else {
      // 只在开发环境下打印网络错误
      if (process.env.NODE_ENV === 'development') {
        console.error('Network/Request Error:', error.message)
      }
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
    return response.data
  } catch (error) {
    console.error('API调用失败:', error)
    return null
  }
} 
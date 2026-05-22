import vikeApi, { apiWrapper } from '@/utils/vikeApi'

// 用户相关类型定义
export interface LoginData {
  username: string
  password: string
  googlerecaptcha: string
}

export interface RegisterData {
  username: string
  email: string
  password: string
  confirmpassword: string
  googlerecaptcha: string
  EmailverificationCod: string
  UserAvatar?: string
}

export interface LoginResponse {
  success: boolean
  token: string
  username: string
  message?: string
}

export interface UserProfile {
  id: number
  username: string
  email: string
  avatar?: string
  createdAt: string
}

// 用户登录
export const userLogin = async (data: LoginData): Promise<LoginResponse | null> => {
  return apiWrapper<LoginResponse>(
    vikeApi.post('/generaluser/login', data)
  )
}

// 用户注册
export const userRegister = async (data: RegisterData): Promise<{
  Success: string
  message?: string
} | null> => {
  return apiWrapper(
    vikeApi.post('/generaluser/reguser', data)
  )
}

// 检查用户名是否存在
export const checkUsername = async (username: string): Promise<{
  exists: boolean
} | null> => {
  return apiWrapper(
    vikeApi.post('/generaluser/check-username', { username })
  )
}

// 发送邮箱验证码
export const sendEmailCode = async (email: string): Promise<{
  success: boolean
  message?: string
} | null> => {
  return apiWrapper(
    vikeApi.post('/generaluser/emailcod', { email })
  )
}

// 上传用户头像
export const uploadUserAvatar = async (formData: FormData): Promise<{
  url: string
  success: boolean
} | null> => {
  return apiWrapper(
    vikeApi.post('/generaluser/reg', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  )
}

// 获取GitHub登录二维码
export const getGithubQrcode = async (): Promise<{
  qrCodeUrl: string
  state: string
} | null> => {
  return apiWrapper(
    vikeApi.get('/generaluser/github-qrcode')
  )
}

// 检查GitHub登录状态
export const checkGithubLogin = async (state: string): Promise<{
  status: 'confirmed' | 'pending' | 'expired'
  token?: string
  username?: string
} | null> => {
  return apiWrapper(
    vikeApi.get('/generaluser/check-login', {
      params: { state }
    })
  )
}

// OAuth回调处理
export const processOAuthCallback = async (payload: string): Promise<{
  success: boolean
  token?: string
  username?: string
  message?: string
} | null> => {
  return apiWrapper(
    vikeApi.post('/generaluser/oauth-callback', { payload })
  )
}

// 解密OAuth参数
export const decryptOAuthPayload = async (payload: string): Promise<{
  valid: boolean
  data?: {
    state: string
    username?: string
  }
} | null> => {
  return apiWrapper(
    vikeApi.post('/decrypt', { payload })
  )
}

// 获取用户信息（需要token）
export const getUserProfile = async (token: string): Promise<UserProfile | null> => {
  return apiWrapper<UserProfile>(
    vikeApi.get('/generaluser/profile', {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
  )
}

// 刷新token
export const refreshToken = async (token: string): Promise<{
  token: string
  expires: string
} | null> => {
  return apiWrapper(
    vikeApi.post('/generaluser/refresh-token', {}, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
  )
} 
<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-header">
        <h1>欢迎回来</h1>
        <p>登录您的账户以继续</p>
      </div>

      <div class="login-content">
        <!-- GitHub 二维码登录 -->
        <div class="qrcode-section">
          <h3>扫码登录</h3>
          <div class="qrcode-container">
            <img
              v-if="qrCodeImage"
              :src="qrCodeImage"
              alt="GitHub扫码登录"
              class="qrcode-image"
            />
            <div v-else class="qrcode-loading">
              <el-icon class="is-loading"><Loading /></el-icon>
              <p>生成二维码中...</p>
            </div>
            
            <div v-if="isPolling" class="qrcode-status">
              <el-icon class="is-loading"><Loading /></el-icon>
              <p>等待扫码...</p>
            </div>
          </div>
          
          <div class="qrcode-tips">
            <p>✓ 使用 GitHub 扫码登录</p>
            <p>✓ 首次扫码将自动创建账号</p>
            <el-button 
              type="text" 
              @click="refreshQRCode"
              :loading="refreshingQR">
              刷新二维码
            </el-button>
          </div>
        </div>

        <el-divider>或</el-divider>

        <!-- 表单登录 -->
        <el-form 
          :model="loginForm" 
          :rules="rules"
          ref="loginFormRef"
          class="login-form" 
          label-width="0px"
          size="large">
          
          <el-form-item prop="username">
            <el-input 
              v-model="loginForm.username" 
              placeholder="请输入用户名"
              prefix-icon="User">
            </el-input>
          </el-form-item>
          
          <el-form-item prop="password">
            <el-input 
              v-model="loginForm.password" 
              placeholder="请输入密码"
              type="password"
              prefix-icon="Lock"
              show-password>
            </el-input>
          </el-form-item>

          <!-- reCAPTCHA -->
          <el-form-item prop="recaptcha">
            <div class="recaptcha-container">
              <div 
                id="recaptcha-container"
                class="recaptcha-placeholder">
                <!-- reCAPTCHA will be rendered here -->
                <p>reCAPTCHA 验证区域</p>
                <p style="font-size: 12px; color: #999;">
                  (Vike版本中，reCAPTCHA需要单独配置)
                </p>
              </div>
            </div>
          </el-form-item>

          <el-form-item>
            <el-button 
              type="primary" 
              @click="handleLogin"
              :loading="loginLoading"
              :disabled="!canLogin"
              style="width: 100%;">
              {{ loginLoading ? '登录中...' : '登录' }}
            </el-button>
          </el-form-item>

          <el-form-item>
            <div class="form-footer">
              <span>还没有账户？</span>
              <el-button type="text" @click="goToRegister">
                立即注册
              </el-button>
            </div>
          </el-form-item>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, computed, reactive } from 'vue'
import { ElMessage, ElNotification, ElLoading } from 'element-plus'
import { Loading, User, Lock } from '@element-plus/icons-vue'
// 导入API函数
import { userLogin, getGithubQrcode, checkGithubLogin } from '@/api/vikeUsers'

const loginForm = reactive({
  username: '',
  password: '',
  recaptcha: false
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度应在3-20个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6个字符', trigger: 'blur' }
  ]
}

const loginFormRef = ref()
const loginLoading = ref(false)
const qrCodeImage = ref('')
const githubLoginState = ref('')
const isPolling = ref(false)
const refreshingQR = ref(false)
let pollInterval = null

const canLogin = computed(() => {
  return loginForm.username && 
         loginForm.password && 
         loginForm.recaptcha && 
         !loginLoading.value
})

// 处理登录
const handleLogin = async () => {
  // 验证表单
  const valid = await loginFormRef.value.validate().catch(() => false)
  if (!valid) return

  try {
    loginLoading.value = true
    
    const result = await userLogin({
      username: loginForm.username,
      password: loginForm.password,
      googlerecaptcha: loginForm.recaptcha ? 'verified' : '' // 模拟验证码
    })
    
    if (result && result.success) {
      // 存储token和用户信息
      localStorage.setItem('token', result.token)
      localStorage.setItem('username', result.username)
      
      ElNotification({
        title: '登录成功',
        message: `欢迎回来，${result.username}！`,
        type: 'success',
        duration: 3000
      })
      
      // 跳转到首页
      setTimeout(() => {
        window.location.href = '/'
      }, 1000)
    } else {
      throw new Error(result?.message || '登录失败')
    }
    
  } catch (error) {
    console.error('登录失败:', error)
    ElNotification({
      title: '登录失败',
      message: error.message || '用户名或密码错误，请重试',
      type: 'error'
    })
  } finally {
    loginLoading.value = false
  }
}

// 获取GitHub登录二维码
const fetchGithubQRCode = async () => {
  try {
    refreshingQR.value = true
    qrCodeImage.value = ''
    githubLoginState.value = ''
    
    if (pollInterval) {
      clearInterval(pollInterval)
      isPolling.value = false
    }

    const result = await getGithubQrcode()
    
    if (result) {
      qrCodeImage.value = result.qrCodeUrl
      githubLoginState.value = result.state
      startPolling()
    } else {
      throw new Error('获取二维码失败')
    }
    
  } catch (error) {
    console.error('获取二维码失败:', error)
    ElMessage.error('获取二维码失败，3秒后重试')
    setTimeout(fetchGithubQRCode, 3000)
  } finally {
    refreshingQR.value = false
  }
}

// 刷新二维码
const refreshQRCode = () => {
  fetchGithubQRCode()
}

// 开始轮询检查登录状态
const startPolling = () => {
  isPolling.value = true
  
  pollInterval = setInterval(async () => {
    try {
      const result = await checkGithubLogin(githubLoginState.value)
      
      if (result?.status === 'confirmed') {
        clearInterval(pollInterval)
        isPolling.value = false
        
        // 存储登录信息
        localStorage.setItem('token', result.token)
        localStorage.setItem('username', result.username)
        
        ElNotification({
          title: '登录成功',
          message: `GitHub登录成功，欢迎 ${result.username}！`,
          type: 'success'
        })
        
        setTimeout(() => {
          window.location.href = '/'
        }, 1000)
      } else if (result?.status === 'expired') {
        clearInterval(pollInterval)
        isPolling.value = false
        ElMessage.warning('二维码已过期，正在刷新...')
        await fetchGithubQRCode()
      }
      
    } catch (error) {
      console.error('轮询错误:', error)
      // 发生错误时不停止轮询，继续尝试
    }
  }, 2000) // 每2秒检查一次
}

// 跳转到注册页
const goToRegister = () => {
  window.location.href = '/reg'
}

// 模拟reCAPTCHA验证
const initRecaptcha = () => {
  // 模拟reCAPTCHA加载完成
  setTimeout(() => {
    loginForm.recaptcha = true
    ElMessage.success('人机验证完成')
  }, 2000)
}

onMounted(() => {
  console.log('登录页面已加载')
  fetchGithubQRCode()
  initRecaptcha()
})

onBeforeUnmount(() => {
  if (pollInterval) {
    clearInterval(pollInterval)
  }
})
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-container {
  background: white;
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  padding: 40px;
  width: 100%;
  max-width: 450px;
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h1 {
  color: #2c3e50;
  margin-bottom: 10px;
  font-size: 2rem;
  font-weight: 700;
}

.login-header p {
  color: #7f8c8d;
  margin: 0;
}

.qrcode-section {
  text-align: center;
  margin-bottom: 20px;
}

.qrcode-section h3 {
  color: #34495e;
  margin-bottom: 15px;
  font-size: 1.1rem;
}

.qrcode-container {
  position: relative;
  margin-bottom: 15px;
}

.qrcode-image {
  width: 200px;
  height: 200px;
  border: 2px solid #e9ecef;
  border-radius: 10px;
  background: #f8f9fa;
}

.qrcode-loading,
.qrcode-status {
  width: 200px;
  height: 200px;
  border: 2px dashed #d6d6d6;
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
  background: #f8f9fa;
}

.qrcode-loading p,
.qrcode-status p {
  margin: 10px 0 0 0;
  color: #666;
  font-size: 14px;
}

.qrcode-tips {
  font-size: 12px;
  color: #666;
  line-height: 1.5;
}

.qrcode-tips p {
  margin: 5px 0;
}

.login-form {
  margin-top: 20px;
}

.recaptcha-container {
  width: 100%;
  display: flex;
  justify-content: center;
}

.recaptcha-placeholder {
  width: 304px;
  height: 78px;
  border: 2px dashed #d6d6d6;
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #f8f9fa;
  text-align: center;
}

.recaptcha-placeholder p {
  margin: 2px 0;
  color: #666;
}

.form-footer {
  text-align: center;
  color: #666;
  font-size: 14px;
}

.form-footer span {
  margin-right: 8px;
}

/* 响应式设计 */
@media (max-width: 480px) {
  .login-container {
    padding: 20px;
    margin: 10px;
  }
  
  .login-header h1 {
    font-size: 1.5rem;
  }
  
  .qrcode-image,
  .qrcode-loading,
  .qrcode-status {
    width: 150px;
    height: 150px;
  }
}

/* 动画效果 */
.login-container {
  animation: slideUp 0.5s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.el-form-item {
  margin-bottom: 20px;
}

.el-button {
  border-radius: 8px;
}
</style> 
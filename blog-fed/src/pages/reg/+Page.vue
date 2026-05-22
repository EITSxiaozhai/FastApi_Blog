<template>
  <div class="register-page">
    <div class="register-container">
      <div class="register-header">
        <h1>创建新账户</h1>
        <p>加入我们，开始您的博客之旅</p>
      </div>

      <el-form
        ref="registerFormRef"
        :model="registerForm"
        :rules="rules"
        class="register-form"
        label-width="100px"
        size="large">
        
        <!-- 用户名 -->
        <el-form-item label="用户名" prop="username">
          <el-input 
            v-model.trim="registerForm.username" 
            placeholder="请输入用户名 (6-18位，不含中文和空格)"
            prefix-icon="User"
            @blur="checkUsername">
            <template #suffix>
              <el-icon v-if="usernameChecking" class="is-loading">
                <Loading />
              </el-icon>
              <el-icon v-else-if="usernameValid === true" style="color: #67c23a">
                <Check />
              </el-icon>
              <el-icon v-else-if="usernameValid === false" style="color: #f56c6c">
                <Close />
              </el-icon>
            </template>
          </el-input>
        </el-form-item>

        <!-- 邮箱 -->
        <el-form-item label="邮箱" prop="email">
          <el-input 
            v-model.trim="registerForm.email" 
            placeholder="请输入邮箱地址"
            prefix-icon="Message"
            type="email">
          </el-input>
        </el-form-item>

        <!-- 邮箱验证码 -->
        <el-form-item label="邮箱验证码" prop="emailCode">
          <div class="code-input-container">
            <el-input 
              v-model.trim="registerForm.emailCode" 
              placeholder="请输入6位验证码"
              maxlength="6">
            </el-input>
                         <el-button 
               type="primary" 
               :disabled="!canSendCode || codeCountdown > 0"
               :loading="sendingCode"
               @click="sendEmailVerificationCode">
              {{ codeButtonText }}
            </el-button>
          </div>
        </el-form-item>

        <!-- 密码 -->
        <el-form-item label="密码" prop="password">
          <el-input 
            v-model.trim="registerForm.password" 
            placeholder="请输入密码 (至少6位)"
            type="password"
            prefix-icon="Lock"
            show-password>
          </el-input>
        </el-form-item>

        <!-- 确认密码 -->
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input 
            v-model.trim="registerForm.confirmPassword" 
            placeholder="请再次输入密码"
            type="password"
            prefix-icon="Lock"
            show-password>
          </el-input>
        </el-form-item>

        <!-- 头像上传 -->
        <el-form-item label="头像">
          <el-upload
            ref="avatarUpload"
            :show-file-list="false"
            :before-upload="beforeAvatarUpload"
            :on-success="handleAvatarSuccess"
            :on-error="handleAvatarError"
            action="#"
            :http-request="uploadAvatar"
            class="avatar-uploader">
            
            <img v-if="avatarUrl" :src="avatarUrl" class="avatar" />
            <div v-else class="avatar-placeholder">
              <el-icon class="avatar-uploader-icon">
                <Plus />
              </el-icon>
              <div class="upload-text">点击上传头像</div>
            </div>
          </el-upload>
          <div class="upload-tips">
            支持 JPG、PNG 格式，文件大小不超过 2MB
          </div>
        </el-form-item>

        <!-- reCAPTCHA -->
        <el-form-item label="人机验证" prop="recaptcha">
          <div class="recaptcha-container">
            <div class="recaptcha-placeholder" @click="completeRecaptcha">
              <el-icon v-if="!recaptchaCompleted">
                <span style="font-size: 20px;">🤖</span>
              </el-icon>
              <el-icon v-else style="color: #67c23a; font-size: 20px;">
                <Check />
              </el-icon>
              <span>{{ recaptchaCompleted ? '验证已完成' : '点击完成人机验证' }}</span>
            </div>
          </div>
        </el-form-item>

        <!-- 注册按钮 -->
        <el-form-item>
          <el-button 
            type="primary" 
            @click="handleRegister"
            :loading="registering"
            :disabled="!canRegister"
            style="width: 100%;">
            {{ registering ? '注册中...' : '注册' }}
          </el-button>
        </el-form-item>

        <!-- 登录链接 -->
        <el-form-item>
          <div class="form-footer">
            <span>已有账户？</span>
            <el-button type="text" @click="goToLogin">
              立即登录
            </el-button>
          </div>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, nextTick } from 'vue'
import { ElMessage, ElNotification } from 'element-plus'
import { Plus, Loading, Check, Close, User, Lock, Message } from '@element-plus/icons-vue'
import { debounce } from 'lodash-es'
// 导入API函数
import { checkUsername as apiCheckUsername, sendEmailCode, userRegister, uploadUserAvatar } from '@/api/vikeUsers'

const registerFormRef = ref()
const avatarUpload = ref()
const registering = ref(false)
const sendingCode = ref(false)
const codeCountdown = ref(0)
const usernameChecking = ref(false)
const usernameValid = ref(null)
const avatarUrl = ref('')
const recaptchaCompleted = ref(false)

const registerForm = reactive({
  username: '',
  email: '',
  emailCode: '',
  password: '',
  confirmPassword: '',
  avatar: '',
  recaptcha: false
})

// 验证码倒计时文本
const codeButtonText = computed(() => {
  return codeCountdown.value > 0 ? `${codeCountdown.value}s后重新发送` : '获取验证码'
})

// 是否可以发送验证码
const canSendCode = computed(() => {
  return registerForm.email && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(registerForm.email)
})

// 是否可以注册
const canRegister = computed(() => {
  return registerForm.username &&
         registerForm.email &&
         registerForm.emailCode &&
         registerForm.password &&
         registerForm.confirmPassword &&
         usernameValid.value === true &&
         recaptchaCompleted.value &&
         !registering.value
})

// 表单验证规则
const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { 
      pattern: /^[^\s\u4e00-\u9fa5]{6,18}$/,
      message: '用户名应为6-18位，不含中文和空格',
      trigger: 'blur'
    }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  emailCode: [
    { required: true, message: '请输入邮箱验证码', trigger: 'blur' },
    { len: 6, message: '验证码应为6位数字', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== registerForm.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 防抖检查用户名
const debouncedCheckUsername = debounce(async (username) => {
  if (!username || username.length < 6) {
    usernameValid.value = null
    return
  }

  usernameChecking.value = true
  
  try {
    const result = await apiCheckUsername(username)
    
    if (result) {
      usernameValid.value = !result.exists
      
      if (result.exists) {
        ElMessage.warning('用户名已被占用，请换一个试试')
      }
    } else {
      throw new Error('检查用户名失败')
    }
    
  } catch (error) {
    console.error('检查用户名时出错:', error)
    usernameValid.value = false
    ElMessage.error('检查用户名时出错，请稍后重试')
  } finally {
    usernameChecking.value = false
  }
}, 500)

// 检查用户名
const checkUsername = () => {
  if (registerForm.username) {
    debouncedCheckUsername(registerForm.username)
  } else {
    usernameValid.value = null
  }
}

// 发送邮箱验证码
const sendEmailVerificationCode = async () => {
  if (!canSendCode.value) return

  try {
    sendingCode.value = true
    
    const result = await sendEmailCode(registerForm.email)
    
    if (result && result.success) {
      ElMessage.success('验证码已发送到您的邮箱')
      
      // 开始倒计时
      codeCountdown.value = 60
      const timer = setInterval(() => {
        codeCountdown.value--
        if (codeCountdown.value <= 0) {
          clearInterval(timer)
        }
      }, 1000)
    } else {
      throw new Error(result?.message || '发送验证码失败')
    }
    
  } catch (error) {
    console.error('发送验证码失败:', error)
    ElMessage.error(error.message || '发送验证码失败，请稍后重试')
  } finally {
    sendingCode.value = false
  }
}

// 头像上传前检查
const beforeAvatarUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isImage) {
    ElMessage.error('只能上传图片文件')
    return false
  }
  if (!isLt2M) {
    ElMessage.error('图片大小不能超过 2MB')
    return false
  }
  return true
}

// 自定义上传
const uploadAvatar = async ({ file }) => {
  try {
    const formData = new FormData()
    formData.append('file', file)
    
    const result = await uploadUserAvatar(formData)
    
    if (result && result.success) {
      // 生成预览URL
      avatarUrl.value = URL.createObjectURL(file)
      registerForm.avatar = result.url
      
      ElMessage.success('头像上传成功')
    } else {
      throw new Error('头像上传失败')
    }
  } catch (error) {
    console.error('头像上传失败:', error)
    ElMessage.error('头像上传失败，请稍后重试')
  }
}

// 头像上传成功
const handleAvatarSuccess = () => {
  ElMessage.success('头像上传成功')
}

// 头像上传失败
const handleAvatarError = () => {
  ElMessage.error('头像上传失败')
}

// 完成人机验证
const completeRecaptcha = () => {
  if (!recaptchaCompleted.value) {
    // 模拟验证过程
    setTimeout(() => {
      recaptchaCompleted.value = true
      registerForm.recaptcha = true
      ElMessage.success('人机验证完成')
    }, 800)
  }
}

// 处理注册
const handleRegister = async () => {
  // 验证表单
  const valid = await registerFormRef.value.validate().catch(() => false)
  if (!valid) return

  try {
    registering.value = true
    
    ElMessage.info('正在创建账户...')
    
    const result = await userRegister({
      username: registerForm.username,
      email: registerForm.email,
      password: registerForm.password,
      confirmpassword: registerForm.confirmPassword,
      googlerecaptcha: recaptchaCompleted.value ? 'verified' : '',
      EmailverificationCod: registerForm.emailCode,
      UserAvatar: registerForm.avatar
    })
    
    if (result && result.Success === 'True') {
      ElNotification({
        title: '注册成功',
        message: '恭喜您成功注册！即将跳转到登录页面...',
        type: 'success',
        duration: 3000
      })
      
      // 跳转到登录页
      setTimeout(() => {
        window.location.href = '/login'
      }, 1500)
    } else {
      throw new Error(result?.message || '注册失败')
    }
    
  } catch (error) {
    console.error('注册失败:', error)
    ElNotification({
      title: '注册失败',
      message: error.message || '注册过程中发生错误，请稍后重试',
      type: 'error'
    })
  } finally {
    registering.value = false
  }
}

// 跳转到登录页
const goToLogin = () => {
  window.location.href = '/login'
}
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.register-container {
  background: white;
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  padding: 40px;
  width: 100%;
  max-width: 500px;
}

.register-header {
  text-align: center;
  margin-bottom: 30px;
}

.register-header h1 {
  color: #2c3e50;
  margin-bottom: 10px;
  font-size: 2rem;
  font-weight: 700;
}

.register-header p {
  color: #7f8c8d;
  margin: 0;
}

.register-form {
  margin-top: 20px;
}

.code-input-container {
  display: flex;
  gap: 10px;
  width: 100%;
}

.code-input-container .el-input {
  flex: 1;
}

.avatar-uploader {
  display: flex;
  justify-content: center;
}

.avatar,
.avatar-placeholder {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border: 2px dashed #d9d9d9;
  cursor: pointer;
  transition: all 0.3s;
}

.avatar {
  border: 2px solid #d9d9d9;
  object-fit: cover;
}

.avatar-placeholder:hover {
  border-color: #409eff;
}

.avatar-uploader-icon {
  font-size: 24px;
  color: #999;
}

.upload-text {
  margin-top: 5px;
  font-size: 12px;
  color: #999;
}

.upload-tips {
  margin-top: 8px;
  font-size: 12px;
  color: #999;
  text-align: center;
}

.recaptcha-container {
  width: 100%;
}

.recaptcha-placeholder {
  border: 2px dashed #d9d9d9;
  border-radius: 6px;
  padding: 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.recaptcha-placeholder:hover {
  border-color: #409eff;
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
@media (max-width: 580px) {
  .register-container {
    padding: 20px;
    margin: 10px;
  }
  
  .register-header h1 {
    font-size: 1.5rem;
  }
  
  .code-input-container {
    flex-direction: column;
  }
}

/* 动画效果 */
.register-container {
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
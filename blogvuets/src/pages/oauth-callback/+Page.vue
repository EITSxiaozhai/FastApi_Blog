<template>
  <div class="oauth-container">
    <el-result
      v-if="!error"
      :icon="success ? 'success' : 'info'"
      :title="success ? '授权成功' : '授权处理中...'"
      :sub-title="subTitle"
    >
      <template #extra>
        <el-progress
          v-if="loading"
          :percentage="progress"
          :indeterminate="true"
          status="success"
        />
        <div v-if="success" style="margin-top: 20px;">
          <el-button type="primary" @click="goHome">
            返回首页
          </el-button>
        </div>
      </template>
    </el-result>

    <el-alert
      v-else
      :title="error"
      type="error"
      :closable="false"
      center
    >
      <template #default>
        <p>{{ error }}</p>
        <p>{{ countdown > 0 ? `${countdown}秒后自动跳转到登录页...` : '' }}</p>
      </template>
    </el-alert>
  </div>
</template>

<script setup>
import { onMounted, ref, computed } from 'vue'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const error = ref('')
const success = ref(false)
const progress = ref(0)
const countdown = ref(0)

const subTitle = computed(() => {
  if (success.value) return '授权验证成功，欢迎回来！'
  if (loading.value) return '正在验证授权信息，请稍候...'
  return '准备处理授权信息'
})

const goHome = () => {
  window.location.href = '/'
}

const processOAuth = async (encrypted) => {
  try {
    loading.value = true
    progress.value = 10

    ElMessage.info('开始处理OAuth回调...')
    
    // 模拟进度更新
    const progressTimer = setInterval(() => {
      if (progress.value < 90) {
        progress.value += 10
      }
    }, 200)

    // 解密验证
    progress.value = 30
    const decryptRes = await fetch('https://blogapi.exploit-db.xyz/decrypt', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ payload: encrypted })
    })

    const { valid, data } = await decryptRes.json()
    if (!valid) throw new Error('无效的授权参数')

    progress.value = 60

    // 状态验证
    const statusRes = await fetch(
      `https://blogapi.exploit-db.xyz/check-login?state=${data.state}`
    )
    const { status, token } = await statusRes.json()

    if (status !== 'confirmed') throw new Error('授权流程未完成')

    progress.value = 90

    // 存储Token
    localStorage.setItem('jwt', token)
    
    // 通知父窗口（如果是弹窗）
    if (window.opener) {
      window.opener.postMessage({ type: 'github-auth-success' }, '*')
    }

    progress.value = 100
    clearInterval(progressTimer)
    
    success.value = true
    loading.value = false

    ElMessage.success(`欢迎 ${data.username || '用户'}`)

    // 自动关闭弹窗或跳转
    setTimeout(() => {
      if (window.opener) {
        window.close()
      } else {
        window.location.href = '/'
      }
    }, 2000)

  } catch (err) {
    clearInterval(progressTimer)
    error.value = err.message || '授权处理失败'
    loading.value = false
    
    ElMessage.error(error.value)
    
    // 倒计时跳转到登录页
    countdown.value = 5
    const countdownTimer = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) {
        clearInterval(countdownTimer)
        window.location.href = '/login'
      }
    }, 1000)
  }
}

onMounted(() => {
  console.log('OAuth回调页面已加载')
  
  // 获取URL参数
  const urlParams = new URLSearchParams(window.location.search)
  const payload = urlParams.get('payload')
  
  if (payload) {
    // 延迟一点时间让用户看到加载效果
    setTimeout(() => {
      processOAuth(payload)
    }, 500)
  } else {
    error.value = '缺少必要的授权参数'
  }
})

// 处理页面可见性变化
onMounted(() => {
  const handleVisibilityChange = () => {
    if (document.hidden) {
      console.log('页面被隐藏')
    } else {
      console.log('页面重新可见')
    }
  }
  
  document.addEventListener('visibilitychange', handleVisibilityChange)
  
  // 清理事件监听器
  onBeforeUnmount(() => {
    document.removeEventListener('visibilitychange', handleVisibilityChange)
  })
})
</script>

<style scoped>
.oauth-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 20px;
}

.el-result {
  background: white;
  border-radius: 15px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  padding: 40px;
  max-width: 500px;
  width: 100%;
}

.el-progress {
  width: 100%;
  max-width: 300px;
  margin: 20px auto;
}

.el-alert {
  background: white;
  border-radius: 15px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  padding: 30px;
  max-width: 500px;
  width: 100%;
  border: none;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .oauth-container {
    padding: 10px;
  }
  
  .el-result {
    padding: 20px;
  }
  
  .el-alert {
    padding: 20px;
  }
}
</style> 
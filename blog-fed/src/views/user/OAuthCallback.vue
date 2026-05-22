<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElLoading, ElMessage } from 'element-plus'

const router = useRouter()
const loading = ref(false)
const error = ref('')

const processOAuth = async (encrypted: string) => {
  try {
    loading.value = true

    // 解密验证
    const decryptRes = await fetch('https://blogapi.exploit-db.xyz/decrypt', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ payload: encrypted })
    })

    const { valid, data } = await decryptRes.json()
    if (!valid) throw new Error('无效的授权参数')

    // 状态验证
    const statusRes = await fetch(
      `https://blogapi.exploit-db.xyz/check-login?state=${data.state}`
    )
    const { status, token } = await statusRes.json()

    if (status !== 'confirmed') throw new Error('授权流程未完成')

    // 存储Token并通知父窗口
    localStorage.setItem('jwt', token)
    window.opener?.postMessage({ type: 'github-auth-success' }, '*')

    // 自动关闭逻辑
    setTimeout(() => {
      window.close()
      router.push('/').catch(() => {})
    }, 1500)

    ElMessage.success(`欢迎 ${data.username}`)

  } catch (err) {
    error.value = err.message
    setTimeout(() => router.push('/login'), 3000)
  } finally {
    loading.value = false
  }
}

// 前端修改（正确解析参数）
onMounted(() => {
  const urlParams = new URLSearchParams(window.location.search)
  const payload = urlParams.get('payload')  // 匹配查询参数名

  // 移除hash解析逻辑
  // const hashPayload = window.location.hash.slice(1) // 删除
})
</script>

<template>
  <div class="oauth-container">
    <el-result
      v-if="!error"
      icon="success"
      title="授权处理中..."
      :sub-title="loading ? '正在验证授权信息...' : '即将自动跳转'"
    >
      <template #extra>
        <el-progress
          v-if="loading"
          :percentage="50"
          :indeterminate="true"
          status="success"
        />
      </template>
    </el-result>

    <el-alert
      v-else
      :title="error"
      type="error"
      :closable="false"
      center
    />
  </div>
</template>

<style scoped>
.oauth-container {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.el-progress {
  width: 200px;
}
</style>
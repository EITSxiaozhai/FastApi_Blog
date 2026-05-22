<template>
  <div class="test-page">
    <div class="header">
      <h1>📊 Vike 数据获取测试</h1>
      <p>演示服务器端数据获取和SSR</p>
    </div>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>模拟API数据</span>
          </template>
          <div v-if="loading">
            <el-skeleton :rows="3" animated />
          </div>
          <div v-else>
            <p><strong>用户ID:</strong> {{ data.userId }}</p>
            <p><strong>标题:</strong> {{ data.title }}</p>
            <p><strong>内容:</strong> {{ data.body }}</p>
            <p><strong>获取时间:</strong> {{ data.fetchTime }}</p>
          </div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card>
          <template #header>
            <span>交互测试</span>
          </template>
          <div>
            <p>点击次数: {{ clickCount }}</p>
            <el-button type="primary" @click="handleClick">
              点击测试
            </el-button>
            <br><br>
            <el-button type="success" @click="refreshData">
              重新获取数据
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <div style="margin-top: 20px; text-align: center;">
      <el-button type="info" @click="goBack">
        返回首页
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

// 接收来自服务器端的数据
const props = defineProps({
  data: {
    type: Object,
    default: () => ({})
  }
})

const data = props.data
const loading = ref(false)
const clickCount = ref(0)

const handleClick = () => {
  clickCount.value++
  ElMessage.success(`点击了 ${clickCount.value} 次`)
}

const refreshData = async () => {
  loading.value = true
  ElMessage.info('模拟重新获取数据...')
  
  // 模拟API调用
  setTimeout(() => {
    loading.value = false
    ElMessage.success('数据刷新完成')
  }, 1500)
}

const goBack = () => {
  window.location.href = '/'
}

onMounted(() => {
  console.log('测试页面已挂载，数据:', data)
})
</script>

<style scoped>
.test-page {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  text-align: center;
  margin-bottom: 30px;
}

.header h1 {
  color: #67c23a;
  margin-bottom: 10px;
}
</style> 
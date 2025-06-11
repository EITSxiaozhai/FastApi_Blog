<template>
  <div class="not-found">
    <div class="error-container">
      <div class="error-content">
        <h1>404</h1>
        <h2>页面未找到</h2>
        <p>抱歉，您访问的页面不存在或已被移除。</p>
        
        <div class="actions">
          <el-button type="primary" @click="goHome">
            返回首页
          </el-button>
          <el-button @click="goBack">
            返回上页
          </el-button>
        </div>
      </div>
      
      <div class="error-image">
        <img src="/404.gif" alt="404错误" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'

const goHome = () => {
  window.location.href = '/'
}

const goBack = () => {
  if (window.history.length > 1) {
    window.history.back()
  } else {
    window.location.href = '/'
  }
}

onMounted(() => {
  console.log('404页面已加载')
})
</script>

<style scoped>
.not-found {
  width: 100%;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  overflow: hidden;
}

.error-container {
  display: flex;
  align-items: center;
  gap: 3rem;
  max-width: 1000px;
  padding: 2rem;
}

.error-content {
  flex: 1;
  color: white;
  text-align: center;
}

.error-content h1 {
  font-size: 6rem;
  font-weight: bold;
  margin: 0;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.error-content h2 {
  font-size: 2rem;
  margin: 1rem 0;
  text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
}

.error-content p {
  font-size: 1.1rem;
  margin: 1.5rem 0;
  opacity: 0.9;
}

.actions {
  margin-top: 2rem;
}

.actions .el-button {
  margin: 0 0.5rem;
}

.error-image {
  flex: 1;
  max-width: 400px;
}

.error-image img {
  width: 100%;
  height: auto;
  border-radius: 10px;
  box-shadow: 0 8px 16px rgba(0,0,0,0.2);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .error-container {
    flex-direction: column;
    text-align: center;
  }
  
  .error-content h1 {
    font-size: 4rem;
  }
  
  .error-content h2 {
    font-size: 1.5rem;
  }
  
  .error-image {
    max-width: 300px;
  }
}
</style> 
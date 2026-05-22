<template>
  <div class="about-me-container">
    <div class="profile-section">
      <h1>关于我</h1>
      <div class="profile-content">
        <div class="profile-image">
          <div class="placeholder-img">
            📷 照片区域
          </div>
        </div>
        <div class="profile-text">
          <h2>个人简介</h2>
          <p>
            我是Exp1oit，一名热爱技术的开发者。专注于Web开发、安全研究和技术分享。
            通过这个博客，我希望能够记录自己的学习历程，同时与更多的技术爱好者交流分享。
          </p>
          <p>
            技术栈包括但不限于：Vue.js、Python、FastAPI、数据库设计等。
            始终保持学习的热情，追求代码的优雅与高效。
          </p>
        </div>
      </div>
    </div>

    <div class="resume-section">
      <h2>我的简历</h2>
      <div class="pdf-container">
        <p>简历内容展示区域</p>
      </div>
    </div>

    <div class="contact-section" style="margin-top: 3rem;">
      <h2>联系方式</h2>
      <div class="contact-info">
        <el-card class="contact-card">
          <p><strong>邮箱:</strong> watch.dog@qq.com</p>
          <p><strong>网站:</strong> https://blog.exploit-db.xyz</p>
          <p><strong>技术栈:</strong> Vue.js, Python, FastAPI, MySQL</p>
        </el-card>
      </div>
    </div>

    <div class="vike-demo-info" style="margin-top: 2rem; padding: 1rem; background: #e8f4fd; border-radius: 8px;">
      <h3>🎉 Vike-Vue 迁移测试</h3>
      <p>这是第一个成功迁移到Vike的页面！</p>
      <ul>
        <li>✅ 服务器端渲染工作正常</li>
        <li>✅ Element Plus组件可用</li>
        <li>✅ Vue 3 Composition API正常</li>
        <li>✅ 路由系统工作正常</li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'


const pageTitle = ref('关于我 - Vike版本')

// 页面挂载时的逻辑
onMounted(() => {
  console.log('🎉 关于页面已加载 - Vike版本工作正常！')
  console.log('当前运行环境:', import.meta.env.MODE)
})
</script>

<style scoped>
.about-me-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.profile-section {
  margin-bottom: 3rem;
}

.profile-content {
  display: flex;
  gap: 2rem;
  margin-top: 2rem;
}

.profile-image {
  flex: 0 0 300px;
}

.placeholder-img {
  width: 100%;
  height: 300px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 2rem;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.profile-text {
  flex: 1;
}

.resume-section {
  margin-top: 3rem;
}

.pdf-container {
  margin-top: 1rem;
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 2rem;
  text-align: center;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  background: #fafafa;
}

.contact-section {
  margin-top: 3rem;
}

.contact-card {
  margin-top: 1rem;
}

.contact-info p {
  margin: 0.5rem 0;
}

.vike-demo-info {
  border-left: 4px solid #409eff;
}

.vike-demo-info h3 {
  color: #409eff;
  margin-top: 0;
}

.vike-demo-info ul {
  margin: 1rem 0;
  padding-left: 1.5rem;
}

.vike-demo-info li {
  margin: 0.5rem 0;
  color: #606266;
}

h1 {
  color: #2c3e50;
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

h2 {
  color: #34495e;
  font-size: 1.8rem;
  margin-bottom: 1rem;
}

p {
  color: #666;
  line-height: 1.6;
  margin-bottom: 1rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .profile-content {
    flex-direction: column;
  }
  
  .profile-image {
    flex: none;
  }
  
  .placeholder-img {
    height: 200px;
  }
  
  .about-me-container {
    padding: 1rem;
  }
}
</style> 
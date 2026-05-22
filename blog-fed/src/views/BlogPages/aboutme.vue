<template>
  <div class="about-me-container">
    <div class="profile-section">
      <h1>关于我</h1>
      <div class="profile-content">
        <div class="profile-image">
          <!-- 这里可以放置您的照片 -->
        </div>
        <div class="profile-text">
          <h2>个人简介</h2>
          <p>在这里添加您的个人简介...</p>
        </div>
      </div>
    </div>

    <div class="resume-section">
      <h2>我的简历</h2>
      <div class="pdf-container">
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AboutMe',
  data() {
    return {
      // 可以在这里添加需要的数据
    }
  }
}
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

.profile-image img {
  width: 100%;
  border-radius: 10px;
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
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
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
}
</style>

<template>
  <div class="api-documentation">
    <h1>Bing壁纸API文档</h1>
    
    <section class="api-section">
      <h2>获取每日壁纸</h2>
      <div class="endpoint">
        <code>GET https://blogapi.exploit-db.xyz/api/bing-wallpaper</code>
      </div>
      <h3>返回示例</h3>
      <pre class="response-example">
{
  "url": "https://www.bing.com/th?id=OHR.Example_1920x1080.jpg",
  "title": "示例标题",
  "copyright": "© 示例版权信息",
  "date": "20240403",
  "fullUrl": "https://www.bing.com/th?id=OHR.Example_UHD.jpg"
}</pre>
    </section>

    <section class="api-section">
      <h2>随机获取壁纸</h2>
      <div class="endpoint">
        <code>GET https://blogapi.exploit-db.xyz/api/bing-wallpaper/random=true</code>
      </div>
      <h3>说明</h3>
      <p>随机返回最近7天内的任意一张壁纸</p>
      <h3>返回示例</h3>
      <pre class="response-example">
{
  "url": "https://www.bing.com/th?id=OHR.Example_1920x1080.jpg",
  "title": "示例标题",
  "copyright": "© 示例版权信息",
  "date": "20240403",
  "fullUrl": "https://www.bing.com/th?id=OHR.Example_UHD.jpg"
}</pre>
    </section>

    <section class="api-section">
      <h2>使用示例</h2>
      <div class="code-example">
        <h3>JavaScript</h3>
        <pre>
// 获取今日壁纸
fetch('https://your-domain.com/api/bing-wallpaper')
  .then(response => response.json())
  .then(data => console.log(data));

// 随机获取壁纸
fetch('https://your-domain.com/api/bing-wallpaper/random')
  .then(response => response.json())
  .then(data => console.log(data));</pre>

        <h3>Python</h3>
        <pre>
import requests

# 获取今日壁纸
response = requests.get('https://your-domain.com/api/bing-wallpaper')
data = response.json()
print(data)

# 随机获取壁纸
response = requests.get('https://your-domain.com/api/bing-wallpaper/random')
data = response.json()
print(data)</pre>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
// 这里可以添加一些示例数据或演示功能
</script>

<style scoped>
.api-documentation {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.api-section {
  margin-bottom: 40px;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.endpoint {
  background: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  margin: 10px 0;
}

.response-example,
.code-example pre {
  background: #f5f5f5;
  padding: 15px;
  border-radius: 4px;
  overflow-x: auto;
  font-family: monospace;
}

h1 {
  color: #333;
  margin-bottom: 30px;
}

h2 {
  color: #444;
  margin: 20px 0;
}

h3 {
  color: #555;
  margin: 15px 0;
}

p {
  color: #666;
  line-height: 1.6;
}
</style>

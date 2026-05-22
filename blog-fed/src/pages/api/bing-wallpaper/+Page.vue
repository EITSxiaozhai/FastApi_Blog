<template>
  <div class="api-documentation">
    <div class="header-section">
      <h1>Bing壁纸API文档</h1>
      <p class="description">获取必应每日精美壁纸的API接口文档</p>
    </div>
    
    <section class="api-section">
      <h2>📸 获取每日壁纸</h2>
      <div class="endpoint">
        <span class="method">GET</span>
        <code>https://blogapi-traefik.exploit-db.xyz/api/views/blogs/bing-wallpaper</code>
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
      <h2>🎲 随机获取壁纸</h2>
      <div class="endpoint">
        <span class="method">GET</span>
        <code>https://blogapi-traefik.exploit-db.xyz/api/views/blogs/bing-wallpaper?is_random=true</code>
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
      <h2>💻 使用示例</h2>
      
      <div class="code-tabs">
        <el-tabs v-model="activeTab" class="demo-tabs">
          <el-tab-pane label="JavaScript" name="javascript">
            <pre class="code-example">
// 获取今日壁纸
fetch('https://blogapi-traefik.exploit-db.xyz/api/views/blogs/bing-wallpaper')
  .then(response => response.json())
  .then(data => {
    console.log('今日壁纸:', data);
    document.body.style.backgroundImage = `url(${data.url})`;
  })
  .catch(error => console.error('Error:', error));

// 随机获取壁纸
fetch('https://blogapi-traefik.exploit-db.xyz/api/views/blogs/bing-wallpaper?is_random=true')
  .then(response => response.json())
  .then(data => {
    console.log('随机壁纸:', data);
  });</pre>
          </el-tab-pane>

          <el-tab-pane label="Python" name="python">
            <pre class="code-example">
import requests
import json

# 获取今日壁纸
def get_daily_wallpaper():
    url = 'https://blogapi-traefik.exploit-db.xyz/api/views/blogs/bing-wallpaper'
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        print(f"标题: {data['title']}")
        print(f"日期: {data['date']}")
        print(f"版权: {data['copyright']}")
        return data['url']
    else:
        print("获取失败")
        return None

# 随机获取壁纸
def get_random_wallpaper():
    url = 'https://blogapi-traefik.exploit-db.xyz/api/views/blogs/bing-wallpaper?is_random=true'
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None

# 使用示例
wallpaper = get_daily_wallpaper()
if wallpaper:
    print(f"壁纸URL: {wallpaper}")</pre>
          </el-tab-pane>

          <el-tab-pane label="curl" name="curl">
            <pre class="code-example">
# 获取今日壁纸
curl -X GET "https://blogapi-traefik.exploit-db.xyz/api/views/blogs/bing-wallpaper" \
     -H "Accept: application/json"

# 随机获取壁纸
curl -X GET "https://blogapi-traefik.exploit-db.xyz/api/views/blogs/bing-wallpaper?is_random=true" \
     -H "Accept: application/json"

# 保存壁纸到本地
curl -X GET "https://blogapi-traefik.exploit-db.xyz/api/views/blogs/bing-wallpaper" | \
jq -r '.url' | \
xargs curl -o wallpaper.jpg</pre>
          </el-tab-pane>
        </el-tabs>
      </div>
    </section>

    <section class="api-section">
      <h2>📋 响应字段说明</h2>
      <el-table :data="tableData" style="width: 100%">
        <el-table-column prop="field" label="字段" width="120" />
        <el-table-column prop="type" label="类型" width="100" />
        <el-table-column prop="description" label="描述" />
      </el-table>
    </section>

    <section class="api-section">
      <h2>🚨 注意事项</h2>
      <el-alert
        title="免费使用"
        type="success"
        description="此API完全免费，但请合理使用，避免频繁请求。"
        show-icon>
      </el-alert>
      
      <el-alert
        title="版权信息"
        type="warning"
        description="所有壁纸版权归微软必应所有，仅供个人学习使用。"
        show-icon
        style="margin-top: 15px;">
      </el-alert>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const activeTab = ref('javascript')

const tableData = ref([
  {
    field: 'url',
    type: 'string',
    description: '1920x1080分辨率的壁纸URL'
  },
  {
    field: 'title',
    type: 'string',
    description: '壁纸标题'
  },
  {
    field: 'copyright',
    type: 'string',
    description: '版权信息'
  },
  {
    field: 'date',
    type: 'string',
    description: '壁纸日期，格式：YYYYMMDD'
  },
  {
    field: 'fullUrl',
    type: 'string',
    description: '超高清分辨率的壁纸URL'
  }
])

onMounted(() => {
  console.log('API文档页面已加载')
})
</script>

<style scoped>
.api-documentation {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.header-section {
  text-align: center;
  margin-bottom: 40px;
  padding: 30px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 15px;
  color: white;
}

.header-section h1 {
  font-size: 2.5rem;
  margin-bottom: 10px;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.description {
  font-size: 1.1rem;
  opacity: 0.9;
  margin: 0;
}

.api-section {
  margin-bottom: 40px;
  padding: 25px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border: 1px solid #f0f0f0;
}

.endpoint {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
  margin: 15px 0;
  border-left: 4px solid #409eff;
  display: flex;
  align-items: center;
  gap: 10px;
}

.method {
  background: #67c23a;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-weight: bold;
  font-size: 0.9rem;
}

.endpoint code {
  background: transparent;
  color: #333;
  font-family: 'Consolas', monospace;
  word-break: break-all;
}

.response-example,
.code-example {
  background: #2d3748;
  color: #e2e8f0;
  padding: 20px;
  border-radius: 8px;
  overflow-x: auto;
  font-family: 'Consolas', 'Monaco', monospace;
  line-height: 1.5;
}

.code-tabs {
  margin-top: 20px;
}

.demo-tabs .el-tabs__item {
  font-weight: bold;
}

h1 {
  color: #2c3e50;
  margin-bottom: 20px;
}

.header-section h1 {
  color: white;
}

h2 {
  color: #34495e;
  margin: 25px 0 15px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

h3 {
  color: #5a6c7d;
  margin: 20px 0 10px 0;
}

p {
  color: #666;
  line-height: 1.6;
  margin: 10px 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .api-documentation {
    padding: 10px;
  }
  
  .api-section {
    padding: 15px;
  }
  
  .header-section h1 {
    font-size: 2rem;
  }
  
  .endpoint {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style> 
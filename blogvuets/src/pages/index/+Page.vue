<template>
  <div class="home-page">
    <!-- 背景容器 -->
    <div class="background-container">
      <div class="background-image" :style="backgroundStyle"></div>
      <div class="hero-content">
        <h1 ref="titleElement" class="hero-title"></h1>
        <div class="hero-subtitle">
          <p>探索技术 · 分享知识 · 记录成长</p>
        </div>
      </div>
      
      <div class="scroll-indicator">
        <el-icon class="scroll-arrow">
          <ArrowDown />
        </el-icon>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content">
      <el-container>
        <!-- 博客统计 -->
        <div class="stats-section">
          <el-row :gutter="20">
            <el-col :span="8">
              <el-statistic 
                title="总访问量(PV)" 
                :value="stats.pv"
                suffix="次"
                :precision="0">
                <template #prefix>
                  <el-icon style="vertical-align: -0.125em">
                    <View />
                  </el-icon>
                </template>
              </el-statistic>
            </el-col>
            <el-col :span="8">
              <el-statistic 
                title="独立访客(UV)" 
                :value="stats.uv"
                suffix="人"
                :precision="0">
                <template #prefix>
                  <el-icon style="vertical-align: -0.125em">
                    <User />
                  </el-icon>
                </template>
              </el-statistic>
            </el-col>
            <el-col :span="8">
              <el-statistic 
                title="文章总数" 
                :value="stats.articles"
                suffix="篇"
                :precision="0">
                <template #prefix>
                  <el-icon style="vertical-align: -0.125em">
                    <Document />
                  </el-icon>
                </template>
              </el-statistic>
            </el-col>
          </el-row>
        </div>

        <!-- 搜索栏 -->
        <div class="search-section">
          <el-autocomplete
            v-model="searchQuery"
            :fetch-suggestions="searchSuggestions"
            placeholder="搜索文章..."
            @select="handleSearch"
            style="width: 100%; max-width: 500px;"
            size="large">
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-autocomplete>
        </div>

        <!-- 文章列表 -->
        <div class="articles-section">
          <h2>最新文章</h2>
          
          <div class="articles-grid">
            <el-card 
              v-for="article in articles" 
              :key="article.id"
              class="article-card"
              @click="goToArticle(article.id)">
              
              <template #header>
                <div class="article-header">
                  <span class="article-title">{{ article.title }}</span>
                  <div class="article-meta">
                    <el-tag :type="getTagType(article.category)" size="small">
                      {{ article.category }}
                    </el-tag>
                  </div>
                </div>
              </template>
              
              <div class="article-content">
                <p class="article-excerpt">{{ article.excerpt }}</p>
                
                <div class="article-footer">
                  <div class="article-stats">
                    <span><el-icon><View /></el-icon> {{ article.views }}</span>
                    <span><el-icon><Calendar /></el-icon> {{ formatDate(article.createdAt) }}</span>
                  </div>
                </div>
              </div>
            </el-card>
          </div>

          <!-- 加载更多 -->
          <div class="load-more-section" v-if="hasMore">
            <el-button 
              type="primary" 
              @click="loadMore"
              :loading="loading"
              size="large">
              {{ loading ? '加载中...' : '加载更多' }}
            </el-button>
          </div>
        </div>

        <!-- 网站统计 -->
        <div class="site-info">
          <el-card>
            <div class="site-stats">
              <h3>网站运行状态</h3>
              <p>🕒 运行时间: {{ siteRuntime.days }}天 {{ siteRuntime.hours }}小时 {{ siteRuntime.minutes }}分钟</p>
              <p>📝 使用技术: Vue 3 + Vike + FastAPI + MySQL</p>
              <p>🚀 服务器端渲染已启用</p>
            </div>
          </el-card>
        </div>
      </el-container>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, onBeforeUnmount } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  ArrowDown, View, User, Document, Search, Calendar 
} from '@element-plus/icons-vue'

// 导入API函数
import { fetchBlogList, searchBlogs as apiSearchBlogs } from '@/api/vikeBlogs'

// 接收Vike服务器端数据
const props = defineProps({
  articles: {
    type: Array,
    default: () => []
  },
  stats: {
    type: Object,
    default: () => ({ pv: 0, uv: 0, articles: 0 })
  },
  wallpaper: {
    type: String,
    default: null
  },
  pagination: {
    type: Object,
    default: () => ({ page: 1, pageSize: 9, total: 0, totalPages: 0 })
  },
  error: {
    type: String,
    default: null
  }
})

// 响应式数据
const titleElement = ref()
const searchQuery = ref('')
const loading = ref(false)
const articles = ref([...props.articles])
const hasMore = ref(props.pagination.page < props.pagination.totalPages)
const currentPage = ref(props.pagination.page)

const stats = reactive({
  pv: props.stats.pv,
  uv: props.stats.uv,
  articles: props.stats.articles
})

const siteRuntime = reactive({
  days: 0,
  hours: 0,
  minutes: 0
})

// 背景图片样式
const backgroundStyle = computed(() => ({
  backgroundImage: props.wallpaper 
    ? `url(${props.wallpaper})` 
    : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
}))

// 打字机效果
const typewriter = (element, text, speed = 100) => {
  if (!element) return
  
  let i = 0
  element.textContent = ''
  
  const timer = setInterval(() => {
    if (i < text.length) {
      element.textContent += text.charAt(i)
      i++
    } else {
      clearInterval(timer)
    }
  }, speed)
}

// 搜索建议
const searchSuggestions = async (queryString, callback) => {
  if (!queryString) {
    callback([])
    return
  }
  
  try {
    // 先从本地已加载的文章中搜索
    const localSuggestions = articles.value
      .filter(article => article.title.toLowerCase().includes(queryString.toLowerCase()))
      .map(article => ({
        value: article.title,
        id: article.id
      }))
      .slice(0, 3)
    
    // 如果本地建议不足，调用API搜索
    if (localSuggestions.length < 3) {
      const searchResults = await apiSearchBlogs(queryString)
      if (searchResults) {
        const apiSuggestions = searchResults
          .slice(0, 5 - localSuggestions.length)
          .map(article => ({
            value: article.title,
            id: article.id
          }))
        
        callback([...localSuggestions, ...apiSuggestions])
      } else {
        callback(localSuggestions)
      }
    } else {
      callback(localSuggestions)
    }
  } catch (error) {
    console.error('搜索建议失败:', error)
    callback([])
  }
}

// 处理搜索
const handleSearch = (item) => {
  goToArticle(item.id)
}

// 跳转到文章
const goToArticle = (id) => {
  window.location.href = `/blog/${id}`
}

// 获取标签类型
const getTagType = (category) => {
  const types = ['primary', 'success', 'warning', 'danger', 'info']
  const index = category.length % types.length
  return types[index]
}

// 格式化日期
const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

// 加载更多文章
const loadMore = async () => {
  if (!hasMore.value || loading.value) return
  
  loading.value = true
  
  try {
    const nextPage = currentPage.value + 1
    const result = await fetchBlogList({
      page: nextPage,
      pageSize: props.pagination.pageSize,
      initialLoad: false
    })
    
    if (result && result.data.length > 0) {
      articles.value.push(...result.data)
      currentPage.value = nextPage
      hasMore.value = nextPage < result.pagination.totalPages
      
      ElMessage.success(`加载了 ${result.data.length} 篇文章`)
    } else {
      hasMore.value = false
      ElMessage.info('没有更多文章了')
    }
    
  } catch (error) {
    console.error('加载更多失败:', error)
    ElMessage.error('加载失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 更新网站运行时间
const updateSiteRuntime = () => {
  const startTime = new Date('2023-10-04')
  const now = new Date()
  const diff = now - startTime
  
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
  
  siteRuntime.days = days
  siteRuntime.hours = hours
  siteRuntime.minutes = minutes
}

// 初始化模拟文章数据（仅在API完全失败时使用）
const initMockData = () => {
  console.log('🔍 检查首页数据状态:', { 
    articlesLength: articles.value?.length, 
    propsArticlesLength: props.articles?.length,
    hasError: !!props.error 
  })
  
  // 只有在没有服务器端数据且存在错误时才使用模拟数据
  if ((!articles.value || articles.value.length === 0) && (!props.articles || props.articles.length === 0)) {
    console.warn('⚠️ API数据获取失败，使用fallback模拟数据')
    articles.value = Array.from({ length: 9 }, (_, index) => ({
      id: index + 1,
      title: `[模拟数据] Vike-Vue SSR技术分享 ${index + 1}`,
      excerpt: '⚠️ 这是模拟数据，表示后端API连接失败。请检查FastAPI服务是否正常运行，以及API路径是否正确。',
      category: ['技术', 'Vue', 'SSR', 'Vike'][index % 4],
      views: Math.floor(Math.random() * 1000) + 100,
      createdAt: new Date(Date.now() - index * 24 * 60 * 60 * 1000).toISOString()
    }))
  } else {
    console.log('✅ 使用真实API数据，文章数量:', articles.value?.length)
  }
}

let runtimeTimer = null

onMounted(() => {
  console.log('🎉 首页已加载 - Vike SSR版本!')
  console.log('📊 Props数据详情:', {
    propsArticles: props.articles,
    propsArticlesLength: props.articles?.length,
    articleRefs: articles.value,
    articleRefsLength: articles.value?.length,
    stats: props.stats,
    error: props.error
  })
  
  // 初始化数据
  initMockData()
  
  console.log('📋 数据初始化后:', {
    finalArticles: articles.value,
    finalArticlesLength: articles.value?.length,
    firstArticleTitle: articles.value?.[0]?.title
  })
  
  // 启动打字机效果
  setTimeout(() => {
    typewriter(titleElement.value, 'Exp1oit 的技术博客', 150)
  }, 500)
  
  // 更新运行时间
  updateSiteRuntime()
  runtimeTimer = setInterval(updateSiteRuntime, 60000) // 每分钟更新一次
})

onBeforeUnmount(() => {
  if (runtimeTimer) {
    clearInterval(runtimeTimer)
  }
})
</script>

<style scoped>
.home-page {
  width: 100%;
  min-height: 100vh;
}

.background-container {
  position: relative;
  height: 100vh;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.background-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  z-index: 1;
}

.background-image::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.3);
  z-index: 2;
}

.hero-content {
  position: relative;
  z-index: 3;
  text-align: center;
  color: white;
}

.hero-title {
  font-size: 3.5rem;
  font-weight: 700;
  margin-bottom: 1rem;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
  min-height: 80px;
}

.hero-subtitle {
  font-size: 1.2rem;
  opacity: 0.9;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
}

.scroll-indicator {
  position: absolute;
  bottom: 30px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 3;
  color: white;
  animation: bounce 2s infinite;
}

.scroll-arrow {
  font-size: 2rem;
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-10px);
  }
  60% {
    transform: translateY(-5px);
  }
}

.main-content {
  padding: 60px 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.stats-section {
  margin-bottom: 50px;
  padding: 30px;
  background: white;
  border-radius: 15px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.search-section {
  margin-bottom: 50px;
  text-align: center;
}

.articles-section {
  margin-bottom: 50px;
}

.articles-section h2 {
  color: #2c3e50;
  margin-bottom: 30px;
  font-size: 2rem;
  text-align: center;
}

.articles-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 25px;
  margin-bottom: 40px;
}

.article-card {
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 12px;
  overflow: hidden;
}

.article-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
}

.article-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 15px;
}

.article-title {
  font-weight: bold;
  color: #2c3e50;
  line-height: 1.4;
  flex: 1;
}

.article-content {
  padding: 0;
}

.article-excerpt {
  color: #666;
  line-height: 1.6;
  margin-bottom: 15px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.article-footer {
  border-top: 1px solid #f0f0f0;
  padding-top: 15px;
}

.article-stats {
  display: flex;
  justify-content: space-between;
  color: #999;
  font-size: 14px;
}

.article-stats span {
  display: flex;
  align-items: center;
  gap: 5px;
}

.load-more-section {
  text-align: center;
  margin-top: 40px;
}

.site-info {
  margin-top: 60px;
}

.site-stats h3 {
  color: #2c3e50;
  margin-bottom: 15px;
}

.site-stats p {
  margin: 8px 0;
  color: #666;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .hero-title {
    font-size: 2.5rem;
  }
  
  .articles-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .main-content {
    padding: 40px 15px;
  }
  
  .stats-section .el-col {
    margin-bottom: 20px;
  }
}

@media (max-width: 480px) {
  .hero-title {
    font-size: 2rem;
  }
  
  .articles-grid {
    grid-template-columns: 1fr;
  }
}
</style> 
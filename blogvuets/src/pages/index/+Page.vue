<template>
  <div class="home-page">
    <!-- 背景容器 -->
    <div class="background-container">
      <div class="background-image" :style="backgroundStyle"></div>
      <div class="hero-content">
        <h1 class="hero-title">{{ verse }}</h1>
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

    <!-- 三栏布局主要内容区域 -->
    <div class="main-content">
      <div class="layout-container">
        <!-- 左侧边栏 -->
        <aside class="left-sidebar">
          <!-- 搜索区域 -->
          <el-card class="sidebar-card search-card">
            <template #header>
              <div class="card-header">
                <el-icon><Search /></el-icon>
                <span>文章搜索</span>
              </div>
            </template>
            <el-autocomplete
              v-model="searchQuery"
              :fetch-suggestions="searchSuggestions"
              placeholder="搜索文章..."
              @select="handleSearch"
              style="width: 100%;"
              size="large">
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-autocomplete>
          </el-card>

          <!-- 分类导航 -->
          <el-card class="sidebar-card">
            <template #header>
              <div class="card-header">
                <el-icon><Document /></el-icon>
                <span>文章分类</span>
              </div>
            </template>
            <div class="categories-list">
              <div v-for="category in categories" :key="category.name" 
                   class="category-item" @click="filterByCategory(category.name)">
                <span class="category-name">{{ category.name }}</span>
                <el-badge :value="category.count" class="category-badge" />
              </div>
            </div>
          </el-card>

          <!-- 标签云 -->
          <el-card class="sidebar-card">
            <template #header>
              <div class="card-header">
                <el-icon><Collection /></el-icon>
                <span>热门标签</span>
              </div>
            </template>
            <div class="tags-cloud">
              <el-tag 
                v-for="tag in popularTags" 
                :key="tag.name"
                :type="getTagType(tag.name)"
                class="tag-item"
                @click="filterByTag(tag.name)">
                {{ tag.name }} ({{ tag.count }})
              </el-tag>
            </div>
          </el-card>

          <!-- 最新文章 -->
          <el-card class="sidebar-card">
            <template #header>
              <div class="card-header">
                <el-icon><Clock /></el-icon>
                <span>最新文章</span>
              </div>
            </template>
            <div class="recent-articles">
              <div v-for="article in recentArticles" :key="article.id" 
                   class="recent-item" @click="goToArticle(article.id)">
                <div class="recent-title">{{ article.title }}</div>
                <div class="recent-date">{{ formatDate(article.createdAt) }}</div>
              </div>
            </div>
          </el-card>
        </aside>

        <!-- 中间主内容区域 -->
        <main class="center-content">
          <!-- 文章列表 -->
          <div class="articles-section">
            <div class="section-header">
              <h2>{{ currentFilter === 'all' ? '最新文章' : `${currentFilter} 分类文章` }}</h2>
              <div class="filter-info" v-if="currentFilter !== 'all'">
                <el-tag type="info" closable @close="clearFilter">{{ currentFilter }}</el-tag>
              </div>
            </div>
            
            <div class="articles-grid">
              <el-card 
                v-for="article in filteredArticles" 
                :key="article.id"
                class="article-card"
                @click="goToArticle(article.id)">
                
                <!-- 文章封面图片 -->
                <div class="article-image-container" v-if="article.BlogIntroductionPicture">
                  <img 
                    :src="article.BlogIntroductionPicture" 
                    :alt="article.title"
                    class="article-image"
                    @error="handleImageError"
                  />
                </div>
                
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

            <!-- 分页组件 -->
            <div class="pagination-section" v-if="currentFilter === 'all' && totalPages > 1">
              <el-pagination
                v-model:current-page="currentPage"
                :page-size="pageSize"
                :total="total"
                :page-count="totalPages"
                layout="prev, pager, next, total"
                @current-change="handlePageChange"
              />
            </div>
          </div>
        </main>

        <!-- 右侧边栏 -->
        <aside class="right-sidebar">
          <!-- 博客统计 -->
          <el-card class="sidebar-card">
            <template #header>
              <div class="card-header">
                <el-icon><DataAnalysis /></el-icon>
                <span>网站统计</span>
              </div>
            </template>
            <div class="stats-grid">
              <div class="stat-item">
                <div class="stat-value">{{ stats.pv }}</div>
                <div class="stat-label">总访问量(PV)</div>
              </div>
              <div class="stat-item">
                <div class="stat-value">{{ stats.uv }}</div>
                <div class="stat-label">独立访客(UV)</div>
              </div>
              <div class="stat-item">
                <div class="stat-value">{{ stats.articles }}</div>
                <div class="stat-label">文章总数</div>
              </div>
            </div>
          </el-card>

          <!-- 热门文章 -->
          <el-card class="sidebar-card">
            <template #header>
              <div class="card-header">
                <el-icon><TrendCharts /></el-icon>
                <span>热门文章</span>
              </div>
            </template>
            <div class="popular-articles">
              <div v-for="(article, index) in popularArticles" :key="article.id" 
                   class="popular-item" @click="goToArticle(article.id)">
                <div class="popular-rank">{{ index + 1 }}</div>
                <div class="popular-content">
                  <div class="popular-title">{{ article.title }}</div>
                  <div class="popular-views">{{ article.views }} 次阅读</div>
                </div>
              </div>
            </div>
          </el-card>

          <!-- 网站信息 -->
          <el-card class="sidebar-card">
            <template #header>
              <div class="card-header">
                <el-icon><Monitor /></el-icon>
                <span>运行状态</span>
              </div>
            </template>
            <div class="site-stats">
              <div class="runtime-info">
                <p>🕒 运行时间</p>
                <p class="runtime-value">{{ siteRuntime.days }}天 {{ siteRuntime.hours }}小时 {{ siteRuntime.minutes }}分钟</p>
              </div>
              <div class="tech-stack">
                <p>🛠️ 技术栈</p>
                <div class="tech-tags">
                  <el-tag size="small">Vue 3</el-tag>
                  <el-tag size="small" type="success">Vike SSR</el-tag>
                  <el-tag size="small" type="warning">FastAPI</el-tag>
                  <el-tag size="small" type="danger">MySQL</el-tag>
                </div>
              </div>
            </div>
          </el-card>

          <!-- API服务卡片 -->
          <el-card class="sidebar-card api-card" @click="goToWallpaperAPI">
            <template #header>
              <div class="card-header">
                <el-icon><Picture /></el-icon>
                <span>壁纸API服务</span>
              </div>
            </template>
            <div class="api-info">
              <div class="api-icon">
                <el-icon size="40" color="#409eff"><Picture /></el-icon>
              </div>
              <div class="api-desc">
                <h4>Bing壁纸API</h4>
                <p>获取必应每日精美壁纸，支持随机获取</p>
                <div class="api-features">
                  <el-tag size="small" type="success">免费使用</el-tag>
                  <el-tag size="small" type="warning">每日更新</el-tag>
                  <el-tag size="small" type="info">高清壁纸</el-tag>
                </div>
                <div class="api-link">
                  <el-button type="primary" size="small" @click.stop="goToWallpaperAPI">
                    <el-icon><Link /></el-icon>
                    查看API文档
                  </el-button>
                </div>
              </div>
            </div>
          </el-card>

          <!-- 个人信息卡片 -->
          <el-card class="sidebar-card">
            <template #header>
              <div class="card-header">
                <el-icon><Avatar /></el-icon>
                <span>关于博主</span>
              </div>
            </template>
            <div class="author-info">
              <div class="author-avatar">
                <el-avatar :size="80" src="/avatar.png">Exp1oit</el-avatar>
              </div>
              <div class="author-desc">
                <h4>Exp1oit</h4>
                <p>全栈开发者，热爱技术分享</p>
                <div class="social-links">
                  <el-button link type="primary">
                    <el-icon><Message /></el-icon>
                  </el-button>
                  <el-button link type="success">
                    <el-icon><ChatDotRound /></el-icon>
                  </el-button>
                  <el-button link type="warning">
                    <el-icon><Star /></el-icon>
                  </el-button>
                </div>
              </div>
            </div>
          </el-card>
        </aside>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, onBeforeUnmount, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  ArrowDown, View, User, Document, Search, Calendar, Collection, Clock,
  DataAnalysis, TrendCharts, Monitor, Avatar, Message, ChatDotRound, Star,
  Picture, Link
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
  verse: {
    type: String,
    default: '探索技术 · 分享知识 · 记录成长'
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
const currentPage = ref(1)
const currentFilter = ref('all')
const pageSize = ref(9)
const total = ref(0)
const totalPages = ref(1)

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

// 分类数据
const categories = computed(() => {
  const categoryMap = new Map()
  articles.value.forEach(article => {
    const category = article.category || '未分类'
    categoryMap.set(category, (categoryMap.get(category) || 0) + 1)
  })
  return Array.from(categoryMap.entries()).map(([name, count]) => ({ name, count }))
})

// 热门标签
const popularTags = computed(() => {
  const tagMap = new Map()
  articles.value.forEach(article => {
    if (article.tags && Array.isArray(article.tags)) {
      article.tags.forEach(tag => {
        tagMap.set(tag, (tagMap.get(tag) || 0) + 1)
      })
    }
  })
  return Array.from(tagMap.entries())
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 10)
})

// 最新文章
const recentArticles = computed(() => {
  return [...articles.value]
    .sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
    .slice(0, 5)
})

// 热门文章
const popularArticles = computed(() => {
  return [...articles.value]
    .sort((a, b) => (b.views || 0) - (a.views || 0))
    .slice(0, 8)
})

// 过滤后的文章
const filteredArticles = computed(() => {
  if (currentFilter.value === 'all') {
    return articles.value
  }
  return articles.value.filter(article => article.category === currentFilter.value)
})

// 背景图片样式
const backgroundStyle = computed(() => ({
  backgroundImage: props.wallpaper 
    ? `url(${props.wallpaper})` 
    : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
}))

// 过滤方法
const filterByCategory = (category) => {
  currentFilter.value = category
}

const filterByTag = (tag) => {
  // 按标签过滤的逻辑
  const tagArticles = articles.value.filter(article => 
    article.tags && article.tags.includes(tag)
  )
  if (tagArticles.length > 0) {
    ElMessage.info(`找到 ${tagArticles.length} 篇包含标签 "${tag}" 的文章`)
  }
}

const clearFilter = () => {
  currentFilter.value = 'all'
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

// 跳转到壁纸API页面
const goToWallpaperAPI = () => {
  window.location.href = '/api/bing-wallpaper'
}

// 处理图片加载错误
const handleImageError = (event) => {
  // 设置默认图片或隐藏图片容器
  event.target.style.display = 'none'
  event.target.parentElement.style.display = 'none'
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

// 监听分页数据变化
watch(() => props.pagination, (newPagination) => {
  if (newPagination) {
    currentPage.value = newPagination.page
    pageSize.value = newPagination.pageSize
    total.value = newPagination.total
    totalPages.value = newPagination.totalPages
  }
}, { immediate: true })

// 处理页码变化
const handlePageChange = (page) => {
  if (page === 1) {
    // 第一页不需要查询参数
    window.location.href = '/'
  } else {
    // 其他页面添加page查询参数
    window.location.href = `/?page=${page}`
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
  // 只有在没有服务器端数据且存在错误时才使用模拟数据
  if ((!articles.value || articles.value.length === 0) && (!props.articles || props.articles.length === 0)) {
    console.warn('⚠️ API数据获取失败，使用fallback模拟数据')
    articles.value = Array.from({ length: 9 }, (_, index) => ({
      id: index + 1,
      title: `[模拟数据] Vike-Vue SSR技术分享 ${index + 1}`,
      excerpt: '⚠️ 这是模拟数据，表示后端API连接失败。请检查FastAPI服务是否正常运行，以及API路径是否正确。',
      category: ['技术', 'Vue', 'SSR', 'Vike'][index % 4],
      views: Math.floor(Math.random() * 1000) + 100,
      createdAt: new Date(Date.now() - index * 24 * 60 * 60 * 1000).toISOString(),
      BlogIntroductionPicture: `https://picsum.photos/400/200?random=${index + 1}` // 使用随机图片作为模拟数据
    }))
  }
}

let runtimeTimer = null

onMounted(() => {
  // 初始化数据
  initMockData()
  
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
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 1rem;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
  line-height: 1.4;
  padding: 0 20px;
  text-align: center;
  font-family: "Microsoft YaHei", "微软雅黑", sans-serif;
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

.layout-container {
  display: flex;
  gap: 20px;
}

.left-sidebar {
  flex: 1;
}

.center-content {
  flex: 2;
}

.right-sidebar {
  flex: 1;
}

.sidebar-card {
  background-color: white;
  border-radius: 15px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
  transition: all 0.3s ease;
}

.sidebar-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
}

.search-card {
  margin-bottom: 20px;
}

.categories-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.category-item {
  cursor: pointer;
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 15px;
  transition: all 0.3s ease;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fafafa;
}

.category-item:hover {
  background: #409eff;
  color: white;
  border-color: #409eff;
}

.category-name {
  margin-right: 5px;
}

.category-badge {
  background-color: #f0f0f0;
  border-color: #dcdfe6;
  border-radius: 10px;
  padding: 0 5px;
}

.tags-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.tag-item {
  cursor: pointer;
  transition: all 0.3s ease;
}

.tag-item:hover {
  transform: scale(1.05);
}

.recent-articles {
  margin-top: 10px;
}

.recent-item {
  cursor: pointer;
  padding: 12px;
  border-bottom: 1px solid #f0f0f0;
  transition: all 0.3s ease;
  border-radius: 8px;
  margin-bottom: 5px;
}

.recent-item:hover {
  background: #f8f9fa;
  transform: translateX(5px);
}

.recent-title {
  font-weight: 500;
  color: #2c3e50;
  line-height: 1.4;
  margin-bottom: 5px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.recent-date {
  color: #999;
  font-size: 12px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.filter-info {
  display: flex;
  gap: 10px;
}

.stats-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 15px;
}

.stat-item {
  text-align: center;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 10px;
  border: 1px solid #e9ecef;
}

.stat-value {
  font-size: 1.8rem;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 5px;
}

.stat-label {
  color: #666;
  font-size: 0.9rem;
}

.popular-item {
  cursor: pointer;
  padding: 10px;
  border-bottom: 1px solid #f0f0f0;
  transition: all 0.3s ease;
  border-radius: 8px;
  margin-bottom: 5px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.popular-item:hover {
  background: #f8f9fa;
  transform: translateX(3px);
}

.popular-rank {
  font-weight: bold;
  color: #409eff;
  background: #e3f2fd;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  flex-shrink: 0;
}

.popular-content {
  flex: 1;
}

.popular-title {
  font-weight: 500;
  color: #2c3e50;
  line-height: 1.4;
  margin-bottom: 3px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.popular-views {
  color: #999;
  font-size: 12px;
}

.runtime-value {
  font-weight: bold;
  color: #409eff;
  margin-top: 5px;
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

/* 文章图片样式 */
.article-image-container {
  width: 100%;
  height: 200px;
  overflow: hidden;
  border-radius: 8px 8px 0 0;
  margin-bottom: 15px;
  background: #f5f5f5;
  display: flex;
  align-items: center;
  justify-content: center;
}

.article-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
  background: #f5f5f5;
}

.article-card:hover .article-image {
  transform: scale(1.05);
}

/* 图片加载失败时的样式 */
.article-image-container:empty::before {
  content: '📷';
  font-size: 2rem;
  color: #ccc;
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

.site-stats {
  margin-bottom: 20px;
}

.runtime-info {
  margin-bottom: 10px;
}

.tech-stack {
  margin-bottom: 10px;
}

.tech-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.author-info {
  display: flex;
  align-items: center;
  gap: 20px;
}

.author-avatar {
  flex: 0 0 auto;
}

.author-desc {
  flex: 1;
}

.author-desc h4 {
  margin-bottom: 5px;
}

.author-desc p {
  margin: 0;
}

.social-links {
  margin-top: 10px;
  display: flex;
  gap: 10px;
}

/* API卡片样式 */
.api-card {
  cursor: pointer;
  transition: all 0.3s ease;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.api-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
}

.api-card .card-header {
  color: white;
}

.api-info {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 10px 0;
}

.api-icon {
  flex: 0 0 auto;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 60px;
  height: 60px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
}

.api-desc {
  flex: 1;
}

.api-desc h4 {
  color: white;
  margin-bottom: 8px;
  font-size: 1.1rem;
}

.api-desc p {
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 12px;
  font-size: 0.9rem;
  line-height: 1.4;
}

.api-features {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  margin-bottom: 12px;
}

.api-features .el-tag {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
}

.api-link {
  display: flex;
  justify-content: flex-end;
}

.api-link .el-button {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
}

.api-link .el-button:hover {
  background: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.5);
}

/* 这些样式已经在上面定义过了，移除重复定义 */

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
  
  .layout-container {
    flex-direction: column;
  }
  
  .left-sidebar, .right-sidebar {
    flex: 1;
  }
  
  .article-image-container {
    height: 150px;
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

.pagination-section {
  margin-top: 2rem;
  display: flex;
  justify-content: center;
  padding: 1rem 0;
}
</style> 
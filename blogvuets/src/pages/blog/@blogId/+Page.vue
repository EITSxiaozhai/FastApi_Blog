<template>
  <div class="blog-detail-page">
    <!-- 错误状态 -->
    <div v-if="props.notFound" class="error-container">
      <el-result
        icon="warning"
        title="文章不存在"
        sub-title="抱歉，您访问的文章可能已被删除或不存在">
        <template #extra>
          <el-button type="primary" @click="goHome">返回首页</el-button>
        </template>
      </el-result>
    </div>

    <!-- 加载错误 -->
    <div v-else-if="props.error && !blog" class="error-container">
      <el-result
        icon="error"
        title="加载失败"
        :sub-title="props.error">
        <template #extra>
          <el-button type="primary" @click="$router.go(0)">重新加载</el-button>
          <el-button @click="goHome">返回首页</el-button>
        </template>
      </el-result>
    </div>

    <!-- 正常内容 -->
    <div v-else-if="blog" class="blog-container">
      <!-- 文章头部 -->
      <div class="blog-header">
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item @click="goHome">首页</el-breadcrumb-item>
            <el-breadcrumb-item>{{ blog.category || '博客' }}</el-breadcrumb-item>
            <el-breadcrumb-item>{{ blog.title || '文章详情' }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>

        <div class="blog-meta-header">
          <h1 class="blog-title">{{ blog.title }}</h1>
          
          <div class="blog-meta">
            <div class="meta-item">
              <el-icon><Calendar /></el-icon>
              <span>{{ formatDate(blog.createdAt) }}</span>
            </div>
            <div class="meta-item">
              <el-icon><View /></el-icon>
              <span>{{ blog.views }} 次阅读</span>
            </div>
            <div class="meta-item">
              <el-icon><User /></el-icon>
              <span>{{ blog.author || 'Exp1oit' }}</span>
            </div>
          </div>

          <div class="blog-tags" v-if="blog.tags?.length">
            <el-tag 
              v-for="tag in blog.tags" 
              :key="tag"
              :type="getTagType(tag)"
              size="small">
              {{ tag }}
            </el-tag>
          </div>
        </div>
      </div>

      <!-- 文章内容 -->
      <div class="blog-content">
        <el-card class="content-card">
          <!-- 文章摘要 -->
          <div class="blog-excerpt" v-if="blog.excerpt">
            <el-alert
              :title="blog.excerpt"
              type="info"
              :closable="false"
              show-icon>
            </el-alert>
          </div>

          <!-- 文章正文 -->
          <div class="blog-body" v-html="renderedContent"></div>

          <!-- 文章底部 -->
          <div class="blog-footer">
            <div class="blog-actions">
              <el-button type="primary" @click="likeBlog" :loading="liking">
                <el-icon><StarFilled /></el-icon>
                点赞 ({{ blog.likes || 0 }})
              </el-button>
              
              <el-button @click="shareBlog">
                <el-icon><Share /></el-icon>
                分享
              </el-button>
              
              <el-button @click="scrollToComments">
                <el-icon><ChatDotRound /></el-icon>
                评论 ({{ commentsCount }})
              </el-button>
            </div>

            <div class="blog-copyright">
              <p>📝 原创文章，转载请注明出处</p>
              <p>🔗 本文链接：{{ currentUrl }}</p>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 评论区域 -->
      <div class="comments-section" id="comments">
        <h3>评论区</h3>
        
        <!-- 评论表单 -->
        <el-card class="comment-form-card">
          <div class="comment-form">
            <el-form :model="commentForm" @submit.prevent="submitComment">
              <el-form-item>
                <el-input
                  v-model="commentForm.content"
                  type="textarea"
                  :rows="4"
                  placeholder="写下你的评论..."
                  maxlength="500"
                  show-word-limit>
                </el-input>
              </el-form-item>
              
              <el-form-item>
                <div class="comment-actions">
                  <div class="comment-info">
                    <el-input 
                      v-model="commentForm.name" 
                      placeholder="昵称"
                      style="width: 120px; margin-right: 10px;">
                    </el-input>
                    <el-input 
                      v-model="commentForm.email" 
                      placeholder="邮箱 (可选)"
                      style="width: 150px;">
                    </el-input>
                  </div>
                  
                  <el-button 
                    type="primary" 
                    @click="submitComment"
                    :loading="submittingComment"
                    :disabled="!commentForm.content || !commentForm.name">
                    发表评论
                  </el-button>
                </div>
              </el-form-item>
            </el-form>
          </div>
        </el-card>

        <!-- 评论列表 -->
        <div class="comments-list">
          <el-card 
            v-for="comment in comments" 
            :key="comment.id"
            class="comment-item">
            
            <div class="comment-header">
              <div class="comment-user">
                <el-avatar :size="32">{{ getCommentUserName(comment)?.[0] || '?' }}</el-avatar>
                <div class="user-info">
                  <span class="user-name">{{ getCommentUserName(comment) }}</span>
                  <span class="comment-date">{{ formatDate(comment.createdAt || comment.created_at) }}</span>
                </div>
              </div>
            </div>
            
            <div class="comment-content">
              {{ comment.content }}
            </div>
            
            <div class="comment-actions-bottom">
              <el-button text size="small" @click="replyComment(comment.id)">
                回复
              </el-button>
              <el-button text size="small" @click="likeComment(comment.id)">
                <el-icon><StarFilled /></el-icon>
                {{ comment.likes || 0 }}
              </el-button>
            </div>
          </el-card>

          <!-- 加载更多评论 -->
          <div class="load-more-comments" v-if="hasMoreComments">
            <el-button @click="loadMoreComments" :loading="loadingComments">
              加载更多评论
            </el-button>
          </div>
        </div>
      </div>

      <!-- 相关文章推荐 -->
      <div class="related-articles">
        <h3>相关文章</h3>
        <el-row :gutter="20">
          <el-col :span="8" v-for="article in relatedArticles" :key="article.id">
            <el-card class="related-article-card" @click="goToArticle(article.id)">
              <div class="related-article-title">{{ article.title }}</div>
              <div class="related-article-meta">
                <span>{{ formatDate(article.createdAt) }}</span>
                <span>{{ article.views }} 阅读</span>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch, nextTick } from 'vue'
import { ElMessage, ElNotification } from 'element-plus'
import { 
  Calendar, View, User, StarFilled, Share, ChatDotRound 
} from '@element-plus/icons-vue'
// import { usePageContext } from 'vike-vue/usePageContext'
import { fetchBlogDetail, fetchComments, submitComment as apiSubmitComment, likeBlog as likeBlogApi } from '../../../api/vikeBlogs'
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'
import 'highlight.js/styles/github-dark.css' // GitHub 暗色主题

// 接收Vike服务器端数据
const props = defineProps({
  blog: {
    type: Object,
    default: null
  },
  comments: {
    type: Array,
    default: () => []
  },
  rating: {
    type: Number,
    default: 0
  },
  blogId: {
    type: [String, Number],
    default: null
  },
  notFound: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: null
  }
})

// 确保blogId存在的安全检查
const safeBlogId = computed(() => {
  return props.blogId || (props.blog?.id ? String(props.blog.id) : '1')
})

// 响应式数据
const liking = ref(false)
const submittingComment = ref(false)
const loadingComments = ref(false)
const hasMoreComments = ref(true)
const currentUrl = ref('')

const commentForm = reactive({
  content: '',
  name: '',
  email: ''
})

// 初始化评论数据
const comments = ref([...props.comments])

const relatedArticles = ref([
  {
    id: 2,
    title: 'Vue 3 Composition API 深入解析',
    createdAt: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
    views: 1234
  },
  {
    id: 3,
    title: 'FastAPI 快速入门指南',
    createdAt: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
    views: 890
  },
  {
    id: 4,
    title: 'TypeScript 最佳实践',
    createdAt: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000).toISOString(),
    views: 756
  }
])

// 计算属性
const commentsCount = computed(() => comments.value.length)

const blog = computed(() => {
  // 如果博客不存在，返回null
  if (props.notFound || !props.blog) {
    return null
  }
  return props.blog
})

// Markdown renderer setup
const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
})

// 自定义代码块渲染器使用 highlight.js
md.renderer.rules.fence = function(tokens, idx, options, env, renderer) {
  const token = tokens[idx]
  const info = token.info ? token.info.trim() : ''
  const langName = info.split(/\s+/g)[0]
  
  let highlighted = ''
  let lang = langName
  
  try {
    if (langName && hljs.getLanguage(langName)) {
      // 使用指定语言高亮
      highlighted = hljs.highlight(token.content, { language: langName }).value
      console.log(`🎨 使用 highlight.js 高亮代码块: ${langName}`)
    } else {
      // 自动检测语言
      const result = hljs.highlightAuto(token.content)
      highlighted = result.value
      lang = result.language || 'text'
      console.log(`🔧 自动检测语言: ${lang}`)
    }
  } catch (err) {
    console.warn('⚠️ 代码高亮失败，使用原始内容:', err)
    highlighted = md.utils.escapeHtml(token.content)
  }
  
  return `<pre class="hljs"><code class="hljs language-${lang}">${highlighted}</code></pre>`
}

console.log('✅ highlight.js 代码渲染器已配置')

// 渲染后的内容
const renderedContent = computed(() => {
  if (!blog.value?.content) return ''
  
  try {
    console.log('🔄 开始渲染Markdown内容...')
    console.log('📝 原始内容:', blog.value.content.substring(0, 200) + '...')
    
    // 如果内容已经是HTML格式，直接返回
    if (blog.value.content.includes('<p>') || blog.value.content.includes('<div>')) {
      console.log('✅ 检测到HTML格式，直接返回')
      return blog.value.content
    }
    
    // 预处理Markdown内容 - 为代码块添加语言标识符
    let processedContent = blog.value.content
    
    // 匹配没有语言标识符的代码块
    processedContent = processedContent.replace(/```\n([\s\S]*?)\n```/g, (match, code) => {
      // 根据代码内容推测语言
      let lang = 'text'
      if (code.includes('{') && code.includes('}') && (code.includes('"') || code.includes(':'))) {
        lang = 'json'
      } else if (code.includes('import ') || code.includes('export ') || code.includes('const ') || code.includes('function')) {
        lang = 'javascript'
      } else if (code.includes('<template>') || code.includes('<script>')) {
        lang = 'vue'
      } else if (code.includes('npm ') || code.includes('git ') || code.includes('cd ')) {
        lang = 'bash'
      }
      
      console.log(`🔧 自动为代码块添加语言标识符: ${lang}`)
      return `\`\`\`${lang}\n${code}\n\`\`\``
    })
    
    // 作为Markdown处理
    const rendered = md.render(processedContent)
    console.log('✅ Markdown渲染完成')
    console.log('🎨 渲染后内容预览:', rendered.substring(0, 500) + '...')
    
    // 检查是否包含highlight.js类名
    if (rendered.includes('hljs')) {
      console.log('🌈 检测到 highlight.js 语法高亮')
    } else {
      console.warn('⚠️ 未检测到代码高亮')
    }
    
    return rendered
  } catch (error) {
    console.error('❌ Markdown渲染错误:', error)
    return blog.value.content
  }
})

// 手动添加基础语法高亮的fallback函数
const addBasicSyntaxHighlight = (html: string): string => {
  console.log('🎨 添加手动语法高亮')
  
  return html.replace(/<pre><code>([\s\S]*?)<\/code><\/pre>/g, (match, code) => {
    // 简单的语法高亮处理
    let highlightedCode = code
      // JavaScript关键字
      .replace(/\b(function|const|let|var|import|export|class|if|else|for|while|return)\b/g, '<span style="color: #d73a49; font-weight: bold;">$1</span>')
      // 字符串
      .replace(/"([^"]*)"/g, '<span style="color: #032f62;">"$1"</span>')
      .replace(/'([^']*)'/g, '<span style="color: #032f62;">\'$1\'</span>')
      // 数字
      .replace(/\b(\d+)\b/g, '<span style="color: #005cc5;">$1</span>')
      // 注释
      .replace(/\/\/(.*)/g, '<span style="color: #6a737d; font-style: italic;">//$1</span>')
      // HTML标签
      .replace(/&lt;(\/?[^&gt;]+)&gt;/g, '<span style="color: #22863a;">&lt;$1&gt;</span>')
    
    return `<pre class="manual-highlight"><code>${highlightedCode}</code></pre>`
  })
}

// 方法
const formatDate = (dateString: string | undefined): string => {
  if (!dateString) return '未知时间'
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  })
}

// 安全获取评论用户名
const getCommentUserName = (comment: any): string => {
  // 处理不同的数据结构
  if (comment.name) return comment.name // 前端格式
  if (comment.user?.username) return comment.user.username // 后端格式
  if (comment.username) return comment.username // 直接用户名
  return '匿名用户' // 默认值
}

const getTagType = (tag: string): string => {
  const types = ['primary', 'success', 'warning', 'danger', 'info']
  const index = tag.length % types.length
  return types[index]
}

const goHome = () => {
  window.location.href = '/'
}

const goToArticle = (id: number | string): void => {
  window.location.href = `/blog/${id}`
}

const likeBlog = async () => {
  if (!blog.value) return
  
  liking.value = true
  
  try {
    const result = await likeBlogApi(String(safeBlogId.value))
    if (result) {
      blog.value.likes = result.likes
      ElMessage.success('点赞成功！')
    } else {
      throw new Error('点赞失败')
    }
    
  } catch (error) {
    console.error('点赞失败:', error)
    ElMessage.error('点赞失败，请稍后重试')
  } finally {
    liking.value = false
  }
}

const shareBlog = async () => {
  if (!blog.value) return
  
  if (navigator.share) {
    try {
      await navigator.share({
        title: blog.value.title,
        text: blog.value.excerpt,
        url: window.location.href
      })
      ElMessage.success('分享成功！')
    } catch (error) {
      // 用户取消分享
    }
  } else {
    // 复制链接到剪贴板
    try {
      await navigator.clipboard.writeText(window.location.href)
      ElMessage.success('链接已复制到剪贴板！')
    } catch (error) {
      ElMessage.warning('请手动复制链接分享')
    }
  }
}

const scrollToComments = () => {
  document.getElementById('comments')?.scrollIntoView({ 
    behavior: 'smooth' 
  })
}

const submitComment = async () => {
  if (!commentForm.content || !commentForm.name) {
    ElMessage.warning('请填写昵称和评论内容')
    return
  }

  submittingComment.value = true
  
  try {
    // 获取用户token（如果已登录）
    const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null
    
    const result = await apiSubmitComment(String(safeBlogId.value), commentForm.content, token || undefined)
    
    if (result) {
      // 使用API返回的评论数据
      const newComment = {
        ...result,
        name: commentForm.name, // 使用用户输入的昵称
        email: commentForm.email
      }
      
      comments.value.unshift(newComment)
      
      // 清空表单
      commentForm.content = ''
      commentForm.name = ''
      commentForm.email = ''
      
      ElNotification({
        title: '评论成功',
        message: '您的评论已发表',
        type: 'success'
      })
    } else {
      throw new Error('评论提交失败')
    }
    
  } catch (error) {
    console.error('评论失败:', error)
    ElMessage.error('评论失败，请稍后重试')
  } finally {
    submittingComment.value = false
  }
}

const replyComment = (commentId) => {
  ElMessage.info(`回复功能开发中... (评论ID: ${commentId})`)
}

const likeComment = async (commentId) => {
  const comment = comments.value.find(c => c.id === commentId)
  if (comment) {
    comment.likes = (comment.likes || 0) + 1
    ElMessage.success('点赞成功！')
  }
}

const loadMoreComments = async () => {
  loadingComments.value = true
  
  try {
    // 模拟加载更多评论
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    const moreComments = [
      {
        id: comments.value.length + 1,
        name: '技术爱好者',
        content: 'Vike确实是个不错的选择，比Nuxt轻量很多。',
        createdAt: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
        likes: 2
      }
    ]
    
    comments.value.push(...moreComments)
    hasMoreComments.value = false
    
  } catch (error) {
    ElMessage.error('加载评论失败')
  } finally {
    loadingComments.value = false
  }
}

onMounted(async () => {
  console.log('🚀 博客详情页已加载，文章ID:', safeBlogId.value)
  currentUrl.value = window.location.href
  
  // 模拟增加阅读量
  setTimeout(() => {
    if (blog.value) {
      blog.value.views = (blog.value.views || 0) + 1
    }
  }, 2000)

  // highlight.js 已经在初始化时配置好了
  console.log('🎨 highlight.js 代码高亮已就绪')
  
  // 强制重新渲染一次内容（触发computed）
  nextTick(() => {
    console.log('🔄 强制触发内容重新渲染')
    if (blog.value) {
      // 触发renderedContent重新计算
      const content = renderedContent.value
      console.log('📊 当前渲染内容长度:', content.length)
    }
  })
  
  // 检查DOM中的代码块
  setTimeout(() => {
    const codeBlocks = document.querySelectorAll('.blog-body pre')
    console.log(`🔍 页面中找到 ${codeBlocks.length} 个代码块`)
    
    codeBlocks.forEach((block, index) => {
      const hasShiki = block.classList.contains('shiki') || block.querySelector('.shiki')
      console.log(`📦 代码块 ${index + 1}:`, {
        hasShiki,
        classes: Array.from(block.classList),
        innerHTML: block.innerHTML.substring(0, 100) + '...'
      })
    })
  }, 1000)
})
</script>

<style scoped>
.blog-detail-page {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 20px 0;
}

.blog-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 0 20px;
}

.blog-header {
  margin-bottom: 30px;
}

.breadcrumb {
  margin-bottom: 20px;
}

.breadcrumb .el-breadcrumb-item:first-child {
  cursor: pointer;
  color: #409eff;
}

.blog-meta-header {
  background: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.blog-title {
  font-size: 2.2rem;
  color: #2c3e50;
  margin-bottom: 20px;
  line-height: 1.4;
}

.blog-meta {
  display: flex;
  gap: 20px;
  margin-bottom: 15px;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 5px;
  color: #666;
  font-size: 14px;
}

.blog-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.blog-content {
  margin-bottom: 40px;
}

.content-card {
  border-radius: 12px;
  overflow: hidden;
}

.blog-excerpt {
  margin-bottom: 25px;
}

.blog-body {
  line-height: 1.8;
  color: #333;
  font-size: 16px;
}

.blog-body h2 {
  color: #2c3e50;
  margin: 30px 0 15px 0;
  font-size: 1.5rem;
  border-left: 4px solid #409eff;
  padding-left: 15px;
}

.blog-body h3 {
  color: #34495e;
  margin: 25px 0 12px 0;
  font-size: 1.25rem;
}

.blog-body p {
  margin: 15px 0;
}

.blog-body ul, .blog-body ol {
  margin: 15px 0;
  padding-left: 25px;
}

.blog-body li {
  margin: 8px 0;
}

.blog-body blockquote {
  background: #f8f9fa;
  border-left: 4px solid #409eff;
  margin: 20px 0;
  padding: 15px 20px;
  border-radius: 4px;
}

.blog-body code {
  background: #f1f2f6;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Consolas', 'Monaco', monospace;
  color: #e96900;
}

.blog-body pre {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 15px;
  overflow-x: auto;
  margin: 20px 0;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.5;
}

.blog-body pre code {
  background: transparent;
  padding: 0;
  color: inherit;
  border-radius: 0;
}

/* highlight.js 代码高亮样式 - 保持原生暗色主题，只调整布局 */
.blog-body .hljs {
  border-radius: 8px !important;
  padding: 15px !important;
  overflow-x: auto !important;
  margin: 20px 0 !important;
  font-size: 14px !important;
  line-height: 1.5 !important;
  /* 让 highlight.js 的 github-dark 主题控制颜色 */
}

.blog-body .hljs code {
  background: transparent !important;
  padding: 0 !important;
  border-radius: 0 !important;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace !important;
  margin: 0 !important;
  /* 让 highlight.js 控制颜色 */
}

.blog-footer {
  margin-top: 40px;
  padding-top: 30px;
  border-top: 1px solid #eee;
}

.blog-actions {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.blog-copyright {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
  color: #666;
  font-size: 14px;
}

.blog-copyright p {
  margin: 5px 0;
}

.comments-section {
  margin-bottom: 40px;
}

.comments-section h3 {
  color: #2c3e50;
  margin-bottom: 20px;
  font-size: 1.5rem;
}

.comment-form-card {
  margin-bottom: 30px;
  border-radius: 12px;
}

.comment-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.comment-info {
  display: flex;
  gap: 10px;
}

.comments-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.comment-item {
  border-radius: 12px;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.comment-user {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-info {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-weight: bold;
  color: #2c3e50;
}

.comment-date {
  font-size: 12px;
  color: #999;
}

.comment-content {
  margin: 15px 0;
  line-height: 1.6;
  color: #333;
}

.comment-actions-bottom {
  display: flex;
  gap: 15px;
  align-items: center;
}

.load-more-comments {
  text-align: center;
  margin-top: 20px;
}

.related-articles {
  margin-bottom: 40px;
}

.related-articles h3 {
  color: #2c3e50;
  margin-bottom: 20px;
  font-size: 1.5rem;
}

.related-article-card {
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 12px;
  height: 100%;
}

.related-article-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}

.related-article-title {
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 10px;
  line-height: 1.4;
}

.related-article-meta {
  color: #999;
  font-size: 12px;
  display: flex;
  justify-content: space-between;
}

/* 错误容器样式 */
.error-container {
  min-height: 60vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
}

.error-container .el-result {
  background: white;
  border-radius: 15px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  padding: 40px;
  max-width: 500px;
  width: 100%;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .blog-container {
    padding: 0 15px;
  }
  
  .blog-title {
    font-size: 1.8rem;
  }
  
  .blog-meta {
    flex-direction: column;
    gap: 10px;
  }
  
  .blog-actions {
    flex-direction: column;
    align-items: stretch;
  }
  
  .comment-actions {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }
  
  .comment-info {
    flex-direction: column;
  }
  
  .related-articles .el-col {
    margin-bottom: 15px;
  }
  
  .error-container .el-result {
    padding: 20px;
    margin: 10px;
  }
}
</style> 
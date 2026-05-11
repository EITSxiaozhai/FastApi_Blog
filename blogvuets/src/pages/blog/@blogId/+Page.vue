<template>
  <div class="blog-detail-page">
    <!-- 阅读进度条 -->
    <div class="reading-progress-bar" :style="{ width: readingProgress + '%' }"></div>
    
    <!-- 返回顶部按钮 -->
    <el-backtop 
      :right="20" 
      :bottom="100"
      :visibility-height="400">
      <el-button 
        type="primary" 
        circle
        class="back-to-top-btn">
        <el-icon><ArrowUp /></el-icon>
      </el-button>
    </el-backtop>

    <!-- 移动端目录切换按钮 -->
    <el-button 
      v-if="tocItems.length > 0"
      class="mobile-toc-toggle"
      type="primary"
      circle
      @click="toggleMobileToc">
      <el-icon><List /></el-icon>
    </el-button>

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
    <div v-else-if="blog" class="blog-container" :class="{ 'with-toc': tocItems.length > 0 }">
      <!-- 左侧主内容区域 -->
      <div class="main-content">
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
          <div class="blog-body" v-html="renderedContent" ref="blogBody"></div>

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

              <el-button type="success" @click="goHome">
                <el-icon><HomeFilled /></el-icon>
                返回主页
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
                  placeholder="写下你的评论... *"
                  maxlength="500"
                  show-word-limit
                  required>
                </el-input>
              </el-form-item>
              
              <el-form-item>
                <div class="comment-info">
                  <el-input 
                    v-model="commentForm.name" 
                    placeholder="昵称 *"
                    style="width: 120px; margin-right: 10px;"
                    required>
                  </el-input>
                    <el-input 
                      v-model="commentForm.email" 
                      placeholder="邮箱 *"
                      style="width: 150px;"
                      required>
                    </el-input>
                </div>
                <div class="form-tips">
                  <span style="color: #909399; font-size: 12px;">* 为必填项</span>
                </div>
              </el-form-item>
              
              <el-form-item>
                <div class="recaptcha-container">
                  <div id="recaptcha" ref="recaptchaRef"></div>
                </div>
              </el-form-item>
              
              <el-form-item>
                <div class="comment-actions">
                  <el-button 
                    type="primary" 
                    @click="submitComment"
                    :loading="submittingComment"
                    :disabled="!commentForm.content || !commentForm.name || !commentForm.email || !recaptchaVerified">
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
            :key="(comment as any).id"
            class="comment-item">
            
            <div class="comment-header">
              <div class="comment-user">
                <el-avatar :size="32">{{ getCommentUserName(comment as any)?.[0] || '?' }}</el-avatar>
                <div class="user-info">
                  <span class="user-name">{{ getCommentUserName(comment as any) }}</span>
                  <span class="comment-date">{{ formatDate((comment as any).createdAt || (comment as any).created_at) }}</span>
                </div>
              </div>
            </div>
            
            <div class="comment-content">
              {{ (comment as any).content }}
            </div>
            
            <div class="comment-actions-bottom">
              <el-button text size="small" @click="replyComment((comment as any).id)">
                回复
              </el-button>
              <el-button text size="small" @click="likeComment((comment as any).id)">
                <el-icon><StarFilled /></el-icon>
                {{ (comment as any).likes || 0 }}
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
      </div>

      <!-- 右侧目录分栏 -->
      <el-affix 
        v-if="tocItems.length > 0" 
        ref="tocAffixRef"
        :offset="120"
        class="toc-affix"
        :class="{ 'mobile-visible': mobileTocVisible }"
        @change="onAffixChange">
        <div class="toc-sidebar">
          <div class="toc-container">
            <div class="toc-header">
              <h4>目录</h4>
              <el-button 
                text 
                size="small" 
                @click="toggleToc"
                class="toc-toggle">
                {{ tocVisible ? '收起' : '展开' }}
              </el-button>
            </div>
            <div class="toc-content" v-show="tocVisible">
              <ul class="toc-list">
                <li 
                  v-for="item in tocItems" 
                  :key="item.id"
                  :class="['toc-item', `toc-level-${item.level}`, { active: item.active }]">
                  <a 
                    :href="`#${item.id}`" 
                    @click.prevent="scrollToHeading(item.id)"
                    class="toc-link">
                    {{ item.text }}
                  </a>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </el-affix>


    </div>
  </div>
</template>

<script setup lang="ts">
// 声明全局类型
declare global {
  interface Window {
    grecaptcha: any
  }
}

import { ref, reactive, computed, onMounted, watch, nextTick, onUnmounted } from 'vue'
import { ElMessage, ElNotification } from 'element-plus'
import { 
  Calendar, View, User, StarFilled, Share, ChatDotRound, ArrowUp, HomeFilled, List 
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
const recaptchaVerified = ref(false)
const recaptchaRef = ref<HTMLElement | null>(null)

// 目录项类型定义
interface TocItem {
  id: string
  text: string
  level: number
  active: boolean
}

// 目录相关数据
const tocItems = ref<TocItem[]>([])
const tocVisible = ref(true)
const mobileTocVisible = ref(false)
const blogBody = ref<HTMLElement | null>(null)
const tocAffixRef = ref<any>(null)

const commentForm = reactive({
  content: '',
  name: '',
  email: '',
  recaptcha: ''
})

// 初始化评论数据
const comments = ref([...props.comments])

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
const md = new (MarkdownIt as any)({
  html: true,
  linkify: true,
  typographer: true,
  highlight: function (str: string, lang: string) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return hljs.highlight(str, { language: lang }).value
      } catch (__) {
        console.warn('代码高亮失败:', __)
      }
    }
    return '' // 让MarkdownIt使用默认处理
  }
})

// 渲染后的内容
const defaultTableOpen = md.renderer.rules.table_open || ((tokens: any, idx: number, options: any, env: any, self: any) => {
  return self.renderToken(tokens, idx, options)
})

const defaultTableClose = md.renderer.rules.table_close || ((tokens: any, idx: number, options: any, env: any, self: any) => {
  return self.renderToken(tokens, idx, options)
})

md.renderer.rules.table_open = (tokens: any, idx: number, options: any, env: any, self: any) => {
  return `<div class="markdown-table-wrapper">${defaultTableOpen(tokens, idx, options, env, self)}`
}

md.renderer.rules.table_close = (tokens: any, idx: number, options: any, env: any, self: any) => {
  return `${defaultTableClose(tokens, idx, options, env, self)}</div>`
}

const renderedContent = computed(() => {
  if (!blog.value?.content) return ''
  
  try {
    // 如果内容已经是HTML格式，直接返回
    if (blog.value.content.includes('<p>') || blog.value.content.includes('<div>')) {
      return blog.value.content
    }
    
    // 直接渲染Markdown，不做预处理
    const rendered = md.render(blog.value.content)
    
    return rendered
  } catch (error) {
    console.error('❌ Markdown渲染错误:', error)
    return blog.value.content
  }
})

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
  if (!commentForm.content || !commentForm.name || !commentForm.email) {
    ElMessage.warning('请填写昵称、邮箱和评论内容')
    return
  }

  if (!recaptchaVerified.value) {
    ElMessage.warning('请完成人机验证')
    return
  }

  submittingComment.value = true
  
  try {
    // 获取用户token（如果已登录）
    const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null
    
    const result = await apiSubmitComment(
      String(safeBlogId.value), 
      commentForm.content, 
      commentForm.name,
      commentForm.email,
      token || undefined,
      commentForm.recaptcha
    )
    
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
      commentForm.recaptcha = ''
      
      // 重置reCAPTCHA
      recaptchaVerified.value = false
      if (window.grecaptcha) {
        window.grecaptcha.reset()
      }
      
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

const replyComment = (commentId: any) => {
  ElMessage.info(`回复功能开发中... (评论ID: ${commentId})`)
}

const likeComment = async (commentId: any) => {
  const comment = comments.value.find((c: any) => c.id === commentId) as any
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

// 目录相关方法
const generateToc = () => {
  if (!blogBody.value) return
  
  const headings = blogBody.value.querySelectorAll('h1, h2, h3, h4, h5, h6')
  const toc: TocItem[] = []
  
  headings.forEach((heading: Element, index: number) => {
    const level = parseInt(heading.tagName.charAt(1))
    const text = heading.textContent?.trim() || ''
    const id = `heading-${index}-${Date.now()}`
    
    // 为标题添加ID
    heading.id = id
    
    toc.push({
      id,
      text,
      level,
      active: false
    })
  })
  
  tocItems.value = toc
}

const toggleToc = () => {
  tocVisible.value = !tocVisible.value
}

const toggleMobileToc = () => {
  mobileTocVisible.value = !mobileTocVisible.value
}

// 刷新固钉组件
const refreshAffix = () => {
  if (tocAffixRef.value) {
    // 使用 nextTick 确保 DOM 更新完成
    nextTick(() => {
      // 触发固钉组件重新计算位置
      tocAffixRef.value?.updatePosition?.()
    })
  }
}

// 固钉状态变化处理
const onAffixChange = (fixed: boolean) => {
  console.log('固钉状态变化:', fixed)
}

const scrollToHeading = (headingId: string) => {
  const element = document.getElementById(headingId)
  if (element) {
    element.scrollIntoView({ 
      behavior: 'smooth',
      block: 'start'
    })
  }
}

const updateActiveTocItem = () => {
  if (tocItems.value.length === 0) return
  
  const scrollTop = window.scrollY
  const windowHeight = window.innerHeight
  const center = scrollTop + windowHeight / 2
  
  let activeIndex = -1
  
  tocItems.value.forEach((item: TocItem, index: number) => {
    const element = document.getElementById(item.id)
    if (element) {
      const rect = element.getBoundingClientRect()
      const elementTop = rect.top + scrollTop
      const elementBottom = elementTop + rect.height
      
      if (center >= elementTop && center <= elementBottom) {
        activeIndex = index
      }
    }
  })
  
  // 更新激活状态
  tocItems.value.forEach((item: TocItem, index: number) => {
    item.active = index === activeIndex
  })
}

// 阅读进度
const readingProgress = ref(0)

// 计算阅读进度
const calculateReadingProgress = () => {
  const blogContent = document.querySelector('.blog-body')
  if (!blogContent) return

  const scrollTop = window.scrollY
  const docHeight = document.documentElement.scrollHeight - window.innerHeight
  const progress = (scrollTop / docHeight) * 100
  readingProgress.value = Math.min(100, Math.max(0, progress))
}

// reCAPTCHA 回调函数
const onRecaptchaSuccess = (token: string) => {
  recaptchaVerified.value = true
  commentForm.recaptcha = token
  console.log('reCAPTCHA验证成功:', token)
}

const onRecaptchaExpired = () => {
  recaptchaVerified.value = false
  commentForm.recaptcha = ''
  console.log('reCAPTCHA验证已过期')
}

const onRecaptchaError = () => {
  recaptchaVerified.value = false
  commentForm.recaptcha = ''
  console.log('reCAPTCHA验证出错')
}

// 初始化reCAPTCHA
const initRecaptcha = () => {
  if (typeof window !== 'undefined' && window.grecaptcha && recaptchaRef.value) {
    try {
      window.grecaptcha.render(recaptchaRef.value, {
        sitekey: '6Lfj3kkoAAAAAJzLmNVWXTAzRoHzCobDCs-Odmjq', // 请替换为您的实际site key
        callback: onRecaptchaSuccess,
        'expired-callback': onRecaptchaExpired,
        'error-callback': onRecaptchaError,
        theme: 'light',
        size: 'normal'
      })
    } catch (error) {
      console.error('reCAPTCHA初始化失败:', error)
    }
  }
}

// 监听滚动事件
onMounted(() => {
  window.addEventListener('scroll', calculateReadingProgress)
  window.addEventListener('scroll', updateActiveTocItem)
  window.addEventListener('resize', refreshAffix)
  
  // 添加一个强制激活固钉的滚动监听
  const forceActivateAffix = () => {
    if (tocAffixRef.value && tocItems.value.length > 0) {
      refreshAffix()
    }
  }
  
  window.addEventListener('scroll', forceActivateAffix)
  
  // 初始化reCAPTCHA
  nextTick(() => {
    initRecaptcha()
  })
  
  // 清理函数
  onUnmounted(() => {
    window.removeEventListener('scroll', forceActivateAffix)
  })
})

onUnmounted(() => {
  window.removeEventListener('scroll', calculateReadingProgress)
  window.removeEventListener('scroll', updateActiveTocItem)
  window.removeEventListener('resize', refreshAffix)
})

onMounted(async () => {
  currentUrl.value = window.location.href
  
  // 模拟增加阅读量
  setTimeout(() => {
    if (blog.value) {
      blog.value.views = (blog.value.views || 0) + 1
    }
  }, 2000)
  
  // 延迟刷新固钉组件，确保页面完全加载
  setTimeout(() => {
    refreshAffix()
  }, 100)
  
  // 多次尝试刷新固钉组件
  setTimeout(() => {
    refreshAffix()
  }, 500)
  
  setTimeout(() => {
    refreshAffix()
  }, 1000)
})

// 监听博客内容变化，生成目录
watch(() => renderedContent.value, () => {
  nextTick(() => {
    generateToc()
    // 目录生成后刷新固钉组件
    setTimeout(() => {
      refreshAffix()
    }, 50)
  })
}, { immediate: true })
</script>

<style scoped>
.blog-detail-page {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 20px 0;
  overflow-x: hidden;
  box-sizing: border-box;
}

.blog-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  box-sizing: border-box;
  overflow-x: hidden;
}

/* 当有目录时，扩展容器宽度并采用两栏布局 */
.blog-container.with-toc {
  max-width: 1400px;
  display: grid;
  grid-template-columns: 1fr 280px;
  gap: 30px;
  align-items: start;
  padding: 0 20px;
  box-sizing: border-box;
}

.main-content {
  grid-column: 1;
  max-width: 100%;
  overflow-x: hidden;
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
  position: relative;
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
  word-wrap: break-word;
  overflow-wrap: break-word;
  max-width: 100%;
  box-sizing: border-box;
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

/* 代码块样式 - 防止横向溢出 */
.blog-body pre {
  max-width: 100% !important;
  overflow-x: auto !important;
  word-wrap: break-word !important;
  white-space: pre-wrap !important;
  box-sizing: border-box !important;
}

.blog-body code {
  word-wrap: break-word !important;
  overflow-wrap: break-word !important;
  max-width: 100% !important;
}

.blog-footer {
  margin-top: 40px;
  padding-top: 30px;
  border-top: 1px solid #eee;
}

.blog-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}

.blog-actions .el-button {
  display: flex;
  align-items: center;
  gap: 4px;
}

.blog-actions .el-button .el-icon {
  margin-right: 4px;
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
@media (max-width: 1200px) {
  /* 中等屏幕下调整网格布局 */
  .blog-container.with-toc {
    max-width: 100%;
    display: block;
    grid-template-columns: none;
    gap: 0;
    padding: 0 15px;
  }
  
  .toc-affix {
    position: fixed !important;
    top: 20px;
    right: 20px;
    width: 260px;
    max-width: 260px;
    min-width: 260px;
    z-index: 1000;
  }
  
  .toc-sidebar {
    width: 260px;
    max-width: 260px;
    min-width: 260px;
    max-height: calc(100vh - 40px);
    margin-top: 100px;
  }
}

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
  
  .error-container .el-result {
    padding: 20px;
    margin: 10px;
  }
  
  /* 移动端目录样式 */
  .toc-affix {
    position: fixed !important;
    top: 20px;
    right: 20px;
    width: 280px;
    max-width: 280px;
    min-width: 280px;
    z-index: 1000;
    transform: translateX(100%);
    transition: transform 0.3s ease;
  }
  
  .toc-affix.mobile-visible {
    transform: translateX(0);
  }
  
  .toc-sidebar {
    width: 280px;
    max-width: 280px;
    min-width: 280px;
    max-height: calc(100vh - 40px);
  }
  
  /* 移动端显示目录切换按钮 */
  .mobile-toc-toggle {
    display: flex !important;
  }
  
  /* 移动端移除两栏布局 */
  .blog-container.with-toc {
    max-width: 100%;
    display: block;
    grid-template-columns: none;
    gap: 0;
  }
  
  .toc-content {
    max-height: 40vh;
  }
  
  .toc-link {
    padding: 6px 16px;
    font-size: 13px;
  }
  
  .toc-level-1 .toc-link {
    padding-left: 16px;
  }
  
  .toc-level-2 .toc-link {
    padding-left: 24px;
  }
  
  .toc-level-3 .toc-link {
    padding-left: 32px;
  }
  
  .toc-level-4 .toc-link {
    padding-left: 40px;
  }
  
  .toc-level-5 .toc-link {
    padding-left: 48px;
  }
  
  .toc-level-6 .toc-link {
    padding-left: 56px;
  }
}

/* 阅读进度条样式 */
.reading-progress-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  height: 3px;
  background: linear-gradient(to right, #409EFF, #67C23A);
  z-index: 9999;
  transition: width 0.1s ease;
}

/* 返回顶部按钮样式 */
.back-to-top-btn {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #409EFF, #67C23A);
  border: none;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.back-to-top-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.2);
}

/* 移动端目录切换按钮 */
.mobile-toc-toggle {
  position: fixed;
  top: 20px;
  right: 20px;
  width: 50px;
  height: 50px;
  z-index: 1001;
  display: none;
  background: linear-gradient(135deg, #409EFF, #67C23A);
  border: none;
  box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
}

.mobile-toc-toggle:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px 0 rgba(0, 0, 0, 0.3);
}

/* 目录固钉容器 */
.toc-affix {
  width: 280px;
  max-width: 280px;
  min-width: 280px;
}

/* 目录样式 - 作为独立分栏 */
.toc-sidebar {
  width: 280px;
  max-width: 280px;
  min-width: 280px;
  max-height: calc(100vh - 40px);
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid #e4e7ed;
  overflow: hidden;
  box-sizing: border-box;
  z-index: 100;
}

.toc-container {
  padding: 0;
}

.toc-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: #f8f9fa;
  border-bottom: 1px solid #e4e7ed;
}

.toc-header h4 {
  margin: 0;
  color: #2c3e50;
  font-size: 16px;
  font-weight: 600;
}

.toc-toggle {
  color: #409eff;
  font-size: 12px;
  padding: 4px 8px;
}

.toc-content {
  max-height: 60vh;
  overflow-y: auto;
  padding: 12px 0;
}

.toc-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.toc-item {
  margin: 0;
  padding: 0;
}

.toc-link {
  display: block;
  padding: 8px 20px;
  color: #606266;
  text-decoration: none;
  font-size: 14px;
  line-height: 1.4;
  transition: all 0.3s ease;
  border-left: 3px solid transparent;
  position: relative;
}

.toc-link:hover {
  color: #409eff;
  background: #f0f9ff;
  border-left-color: #409eff;
}

.toc-item.active .toc-link {
  color: #409eff;
  background: #f0f9ff;
  border-left-color: #409eff;
  font-weight: 500;
}

/* 不同级别的缩进 */
.toc-level-1 .toc-link {
  padding-left: 20px;
  font-weight: 600;
}

.toc-level-2 .toc-link {
  padding-left: 30px;
}

.toc-level-3 .toc-link {
  padding-left: 40px;
  font-size: 13px;
}

.toc-level-4 .toc-link {
  padding-left: 50px;
  font-size: 13px;
}

.toc-level-5 .toc-link {
  padding-left: 60px;
  font-size: 12px;
}

.toc-level-6 .toc-link {
  padding-left: 70px;
  font-size: 12px;
}

/* 滚动条样式 */
.toc-content::-webkit-scrollbar {
  width: 4px;
}

.toc-content::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 2px;
}

.toc-content::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 2px;
}

.toc-content::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* reCAPTCHA 样式 */
.recaptcha-container {
  display: flex;
  justify-content: center;
  margin: 10px 0;
}

.comment-info {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.form-tips {
  margin-top: 5px;
  text-align: left;
}
</style>

<!-- 全局样式 - 确保代码块Atom Dark主题能够应用 -->
<style>
/* 防止横向滚动的全局样式 */
* {
  box-sizing: border-box;
}

body {
  overflow-x: hidden;
}

/* 确保所有容器都不会溢出 */
.blog-detail-page,
.blog-container,
.main-content,
.blog-body,
.content-card {
  max-width: 100%;
  overflow-x: hidden;
}
/* 强制应用 Atom Dark 主题到所有代码块 */
pre {
  background-color: #1d1f21 !important;
  border-radius: 8px !important;
  padding: 16px !important;
  overflow-x: auto !important;
  margin: 20px 0 !important;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace !important;
  font-size: 14px !important;
  line-height: 1.6 !important;
  color: #c5c8c6 !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.25) !important;
  border: 1px solid #282a2e !important;
}

pre code {
  background: transparent !important;
  padding: 0 !important;
  border-radius: 0 !important;
  font-family: inherit !important;
  font-size: inherit !important;
  color: inherit !important;
  white-space: pre !important;
  word-wrap: normal !important;
  display: block !important;
}

/* Atom Dark 语法高亮 */
.hljs-keyword,
.hljs-selector-tag,
.hljs-subst,
.hljs-built_in {
  color: #b294bb !important;
  font-weight: normal !important;
}

.hljs-title,
.hljs-section,
.hljs-selector-id,
.hljs-function .hljs-title {
  color: #81a2be !important;
  font-weight: normal !important;
}

.hljs-string,
.hljs-doctag,
.hljs-regexp {
  color: #b5bd68 !important;
}

.hljs-number,
.hljs-literal {
  color: #de935f !important;
}

.hljs-comment,
.hljs-quote {
  color: #969896 !important;
  font-style: italic !important;
}

.hljs-variable,
.hljs-template-variable,
.hljs-attr {
  color: #f0c674 !important;
}

.hljs-type,
.hljs-class .hljs-title {
  color: #f0c674 !important;
}

.hljs-tag,
.hljs-name,
.hljs-attribute {
  color: #cc6666 !important;
}

.hljs-link {
  color: #81a2be !important;
  text-decoration: underline !important;
}

.hljs-symbol,
.hljs-bullet {
  color: #8abeb7 !important;
}

.hljs-builtin-name {
  color: #8abeb7 !important;
}

.hljs-meta {
  color: #969896 !important;
}

.hljs-params {
  color: #c5c8c6 !important;
}

  /* 文章内容图片适配容器，避免溢出 */
  .blog-body img {
    max-width: 100% !important;
    height: auto !important;
    display: block !important;
    margin: 10px auto !important;
  }

/* 行内代码 */
.blog-body .markdown-table-wrapper {
  width: 100%;
  max-width: 100%;
  margin: 24px 0;
  overflow-x: auto;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  background: #fff;
}

.blog-body table {
  width: 100%;
  min-width: 640px;
  border-collapse: collapse;
  border-spacing: 0;
  margin: 0;
  color: #303133;
  font-size: 15px;
  line-height: 1.6;
}

.blog-body > table {
  display: block;
  max-width: 100%;
  min-width: 100%;
  overflow-x: auto;
  margin: 24px 0;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
}

.blog-body th,
.blog-body td {
  padding: 10px 14px;
  border: 1px solid #e4e7ed;
  text-align: left;
  vertical-align: top;
  white-space: nowrap;
}

.blog-body th {
  background: #f5f7fa;
  color: #1f2d3d;
  font-weight: 600;
}

.blog-body tr:nth-child(even) td {
  background: #fafafa;
}

code:not(pre code) {
  background-color: rgba(29, 31, 33, 0.8) !important;
  color: #c5c8c6 !important;
  padding: 0.2em 0.4em !important;
  border-radius: 3px !important;
  font-size: 85% !important;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace !important;
  border: 1px solid rgba(55, 59, 65, 0.5) !important;
}
</style>

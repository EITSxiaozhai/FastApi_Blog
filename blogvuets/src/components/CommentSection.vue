<template>
  <div class="comment-section">
    <div class="comment-header">
      <h3>评论区</h3>
      <div class="comment-actions-header">
        <el-button 
          text 
          size="small" 
          @click="loadCommentsFromDB"
          :loading="loading"
          :disabled="loading">
          <el-icon><Refresh /></el-icon>
          刷新评论
        </el-button>
        <el-button 
          text 
          size="small" 
          @click="debugComments"
          type="warning">
          <el-icon><StarFilled /></el-icon>
          调试
        </el-button>
      </div>
    </div>
    
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
    <div class="comments-list" v-loading="loading">
      <!-- 评论为空时的提示 -->
      <div v-if="!loading && comments.length === 0" class="empty-comments">
        <el-empty description="暂无评论，快来抢沙发吧！" />
      </div>
      
      <!-- 评论列表 -->
      <el-card 
        v-for="comment in comments" 
        :key="(comment as CommentType).id"
        class="comment-item">
        
        <div class="comment-header">
          <div class="comment-user">
            <el-avatar :size="32">{{ getCommentUserName(comment as CommentType)?.[0] || '?' }}</el-avatar>
            <div class="user-info">
              <span class="user-name">{{ getCommentUserName(comment as CommentType) }}</span>
              <span class="comment-date">{{ formatDate((comment as CommentType).createdAt || (comment as CommentType).created_at) }}</span>
            </div>
          </div>
        </div>
        
        <div class="comment-content">
          {{ (comment as CommentType).content }}
        </div>
        
        <div class="comment-actions-bottom">
          <el-button text size="small" @click="replyComment((comment as CommentType).id)">
            回复
          </el-button>
          <el-button text size="small" @click="likeComment((comment as CommentType).id)">
            <el-icon><StarFilled /></el-icon>
            {{ (comment as CommentType).likes || 0 }}
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
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { ElMessage, ElNotification } from 'element-plus'
import { StarFilled, Refresh } from '@element-plus/icons-vue'
import { fetchComments, submitComment as apiSubmitComment, likeComment as likeCommentApi } from '../api/vikeBlogs'
import { debugCommentData, generateCommentDebugReport } from '../utils/commentDebug'

// Props
const props = defineProps({
  blogId: {
    type: [String, Number],
    required: true
  },
  initialComments: {
    type: Array,
    default: () => []
  }
})

// Emits
const emit = defineEmits(['comment-submitted'])

// 响应式数据
const submittingComment = ref(false)
const loadingComments = ref(false)
const hasMoreComments = ref(true)
const comments = ref([...props.initialComments])
const loading = ref(false)

const commentForm = reactive({
  content: '',
  name: '',
  email: ''
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

// 评论类型定义
interface CommentType {
  id: number
  name?: string
  username?: string
  user?: {
    username: string
  }
  content: string
  likes?: number
  createdAt?: string
  created_at?: string
}

// 安全获取评论用户名
const getCommentUserName = (comment: CommentType): string => {
  // 处理不同的数据结构
  if (comment.name) return comment.name // 前端格式
  if (comment.user?.username) return comment.user.username // 后端格式
  if (comment.username) return comment.username // 直接用户名
  return '匿名用户' // 默认值
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
    
    const result = await apiSubmitComment(
      String(props.blogId), 
      commentForm.content, 
      commentForm.name,
      commentForm.email,
      token || undefined
    )
    
    if (result) {
      // 使用API返回的评论数据
      const newComment = {
        ...result,
        name: commentForm.name, // 使用用户输入的昵称
        email: commentForm.email,
        createdAt: result.createdAt || new Date().toISOString()
      }
      
      comments.value.unshift(newComment)
      
      // 清空表单
      commentForm.content = ''
      commentForm.name = ''
      commentForm.email = ''
      
      // 触发父组件事件
      emit('comment-submitted', newComment)
      
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
  try {
    const result = await likeCommentApi(String(commentId))
    if (result) {
      const comment = comments.value.find((c: any) => c.id === commentId) as any
      if (comment) {
        comment.likes = result.likes
        ElMessage.success('点赞成功！')
      }
    } else {
      throw new Error('点赞失败')
    }
  } catch (error) {
    console.error('点赞失败:', error)
    ElMessage.error('点赞失败，请稍后重试')
  }
}

// 从数据库加载评论
const loadCommentsFromDB = async () => {
  if (loading.value) return
  
  loading.value = true
  
  try {
    console.log('🔄 正在从数据库加载评论，博客ID:', props.blogId)
    const result = await fetchComments(String(props.blogId))
    
    if (result && Array.isArray(result)) {
      console.log('✅ 成功加载评论:', result.length, '条')
      
      // 处理评论数据，确保格式正确
      const processedComments = result.map((comment: any) => ({
        id: comment.id,
        name: comment.user?.username || comment.name || '匿名用户',
        content: comment.content,
        likes: comment.likes || 0,
        createdAt: comment.createdAt || comment.createTime || new Date().toISOString(),
        user: comment.user || { username: comment.name || '匿名用户' }
      }))
      
      comments.value = processedComments
      console.log('📝 处理后的评论数据:', processedComments)
    } else {
      console.warn('⚠️ 评论数据为空或格式错误')
      comments.value = []
    }
  } catch (error) {
    console.error('❌ 加载评论失败:', error)
    ElMessage.error('加载评论失败，请稍后重试')
  } finally {
    loading.value = false
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

// 调试评论功能
const debugComments = async () => {
  try {
    console.log('🔍 开始调试评论功能...')
    const debugInfo = await debugCommentData(String(props.blogId), fetchComments)
    const report = generateCommentDebugReport(debugInfo)
    
    console.log(report)
    
    // 显示调试结果
    ElMessage({
      message: `调试完成：找到 ${debugInfo.commentsCount} 条评论，${debugInfo.errors.length} 个错误`,
      type: debugInfo.errors.length > 0 ? 'warning' : 'success',
      duration: 5000
    })
    
  } catch (error) {
    console.error('❌ 调试失败:', error)
    ElMessage.error('调试失败，请检查控制台')
  }
}

// 组件挂载时加载评论
import { onMounted } from 'vue'
onMounted(() => {
  // 如果初始评论为空，尝试从数据库加载
  if (comments.value.length === 0) {
    loadCommentsFromDB()
  }
})
</script>

<style scoped>
.comment-section {
  margin-bottom: 40px;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.comment-header h3 {
  color: #2c3e50;
  margin: 0;
  font-size: 1.5rem;
}

.comment-actions-header {
  display: flex;
  gap: 10px;
}

.empty-comments {
  text-align: center;
  padding: 40px 20px;
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

/* 响应式设计 */
@media (max-width: 768px) {
  .comment-actions {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }
  
  .comment-info {
    flex-direction: column;
  }
}
</style>

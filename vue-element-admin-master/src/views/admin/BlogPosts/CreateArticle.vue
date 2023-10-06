<template>
  <el-container>
    <el-main>
      <div>
        <template v-if="!editMode">
          <h3>创建文章</h3>
          <el-input v-model="post.title" placeholder="请输入标题" />
          <markdown-editor v-model="post.content" style="height: 1500px" />
          <el-button type="primary" @click="createPost">保存</el-button>
        </template>
        <template v-else>
          <h3>编辑文章</h3>
          <el-input v-model="post.title" placeholder="请输入标题" />
          <markdown-editor v-model="post.content" style="height: 1500px" />
          <el-button type="success" @click="savePost">保存</el-button>
          <el-button type="warning" @click="cancelEdit">取消</el-button>
        </template>
      </div>
    </el-main>
  </el-container>
</template>

<script>
import { CreateContent } from '@/api/admin/BlogPosts/BlogPosts'
import MarkdownEditor from '@/components/MarkdownEditor'

export default {
  components: {
    // eslint-disable-next-line vue/no-unused-components
    MarkdownEditor
  },
  data() {
    return {
      post: {
        title: '',
        content: ''
      },
      editMode: false
    }
  },
  methods: {
    async createPost() {
      try {
        // 发送创建文章请求到后端
        const response = await CreateContent(this.post)
        if (response.data.code === 20000) {
          // 创建成功，可以处理成功的逻辑，例如跳转到文章详情页面
          this.$router.push({ name: 'ArticleDetail', params: { blog_id: response.data.blog_id }})
        } else {
          // 创建失败，处理失败逻辑
          this.$message.error('创建文章失败')
        }
      } catch (error) {
        console.error('API error:', error)
      }
    },
    async savePost() {
      // 更新文章的逻辑，可以与之前的编辑逻辑一致
      // ...
    },
    cancelEdit() {
      // 取消编辑，可以清空表单或者跳转到其他页面
      // ...
    },
    enterEditMode() {
      this.editMode = true
    }
  }
}
</script>

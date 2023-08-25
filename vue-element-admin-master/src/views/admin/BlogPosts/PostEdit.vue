<!-- PostEdit.vue -->
<template>
  <div>
    <h1>Edit Post: {{ post.title }}</h1>
    <!-- 编辑表单或其他内容 -->
  </div>
</template>

<script>
import { getBlogDetail } from '@/api/admin/BlogPosts/BlogPosts' // 假设有一个获取详情的 API

export default {
  data() {
    return {
      post: {}
    }
  },
  created() {
    // 根据路由参数中的id，加载对应的文章详情
    this.loadPostDetail(this.$route.params.id)
  },
  methods: {
    async loadPostDetail(id) {
      try {
        const response = await getBlogDetail(id) // 使用 API 获取详情数据
        this.post = response.data
      } catch (error) {
        console.error('API error:', error)
      }
    }
  }
}
</script>

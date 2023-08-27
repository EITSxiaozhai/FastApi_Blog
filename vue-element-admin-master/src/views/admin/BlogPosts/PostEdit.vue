<template>
  <el-container>
    <el-main>
      <div>
        <template v-if="post.BlogId">
          <el-input
            v-model="post.title"
            type="textarea"
            autosize
            placeholder="请输入内容"
          />
          <el-row :gutter="10" style="margin-top: 20px">
            <el-col :xs="8" :sm="6" :md="4" :lg="3" :xl="1">
              <div class="grid-content bg-purple" />
            </el-col>
            <el-col :xs="4" :sm="6" :md="8" :lg="9" :xl="11">
              <div class="grid-content bg-purple-light">作者: {{ post.author }}</div>
            </el-col>
            <el-col :xs="4" :sm="6" :md="8" :lg="9" :xl="11">
              <div class="grid-content bg-purple">创建时间
                <el-date-picker
                  v-model="value1"
                  type="datetime"
                  placeholder="选择日期时间"
                  style="margin-bottom: 20px"
                />
              </div>
            </el-col>
            <el-col :xs="8" :sm="6" :md="4" :lg="3" :xl="1">
              <div class="grid-content bg-purple-light" />
            </el-col>
          </el-row>
          <markdown-editor v-model="post.content" style="height: 1000px" />
          <el-container style="margin-top: 20px;margin-bottom: 20px"><el-avatar shape="square" :size="350" :fit="fit" :src="post.BlogIntroductionPicture" /></el-container>
        </template>
        <template v-else>
          Loading...
        </template>
        <template v-if="editMode">
          <el-button type="success" @click="savePost">Save</el-button>
          <el-button type="warning" @click="cancelEdit">Cancel</el-button>
        </template>
        <template v-else>
          <el-button type="primary" @click="enterEditMode">Edit</el-button>
        </template>
      </div>
    </el-main>
  </el-container>
</template>

<script>
import { BlogDetails, BlogDetailsedit } from '@/api/admin/BlogPosts/BlogPosts'
import MarkdownEditor from '@/components/MarkdownEditor'

export default {
  components: {
    // eslint-disable-next-line vue/no-unused-components
    MarkdownEditor
  },
  data() {
    return {
      post: {},
      editMode: false,
      value1: '',
      title: ''
    }
  },
  created() {
    this.loadPostDetail(this.$route.query.blog_id)
  },
  methods: {
    async loadPostDetail(blog_id) {
      try {
        const response = await BlogDetails(blog_id)
        this.post = response.data[0]
        // 将 created_at 转换为 JavaScript Date 对象并设置为 value1
        this.value1 = new Date(this.post.created_at)
      } catch (error) {
        console.error('API error:', error)
      }
    },
    async savePost() {
      // Prepare the data to be sent to the API
      const postData = {
        blog_id: this.post.BlogId,
        title: this.post.title,
        content: this.post.content
        // ... include other fields you want to send
      }

      try {
        // Send the data to the API using Axios or any other HTTP library
        const response = await BlogDetailsedit(this.post.BlogId, postData)
        // Handle the response, update state or perform any other actions
        console.log('API response:', response.data)

        // Reset the post object to its original state and exit edit mode
        this.loadPostDetail(this.$route.query.blog_id)
        this.editMode = false
      } catch (error) {
        console.error('API error:', error)
        // Handle error cases if needed
      }
    },
    enterEditMode() {
      this.editMode = true
    },
    cancelEdit() {
      // Reset the post object to its original state
      this.loadPostDetail(this.$route.query.blog_id)
      this.editMode = false
    }
  }
}
</script>

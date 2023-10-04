<template>
  <el-container>
    <el-main>
      <div>
        <template v-if="post.BlogId">
          <h3>标题</h3>
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
            <el-col :xs="8" :sm="6" :md="4" :lg="3" :xl="1">
              <div class="grid-content bg-purple-light" />
            </el-col>
          </el-row>
          <markdown-editor v-model="post.content" style="height: 1500px" />
          <div><h1>文章首页图片</h1>
            <!--            <el-upload-->
            <!--              class="upload-demo"-->
            <!--              drag-->
            <!--              :action="''"-->
            <!--              multiple-->
            <!--              :on-success="handleSuccess"-->
            <!--              :on-error="handleError"-->
            <!--              :before-upload="beforeUpload"-->
            <!--            >-->
            <!--              <i class="el-icon-upload" />-->
            <!--              <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>-->
            <!--              <div slot="tip" class="el-upload__tip">只能上传jpg/png文件，且不超过500kb</div>-->
            <!--            </el-upload>-->
          </div>
          <div>
            <el-upload
              :before-upload="beforeUpload"
              action="#"
              list-type="picture-card"
              :auto-upload="true"
            >
              <i slot="default" class="el-icon-plus" />
              <div slot="file" slot-scope="{file}">
                <img
                  class="el-upload-list__item-thumbnail"
                  :src="file.url"
                >
                <span class="el-upload-list__item-actions">
                  <span
                    class="el-upload-list__item-preview"
                    @click="handlePictureCardPreview(file)"
                  >
                    <i class="el-icon-zoom-in" />
                  </span>
                  <span
                    v-if="!disabled"
                    class="el-upload-list__item-delete"
                    @click="handleDownload(file.url)"
                  >
                    <i class="el-icon-download" />
                  </span>
                  <span
                    v-if="!disabled"
                    class="el-upload-list__item-delete"
                    @click="handleRemove(file)"
                  >
                    <i class="el-icon-delete" />
                  </span>
                </span>
              </div>
            </el-upload>
            <el-dialog :visible.sync="dialogVisible">
              <img width="100%" :src="dialogImageUrl" alt="">
            </el-dialog>
            <div slot="tip" class="el-upload__tip">只能上传jpg/png文件，且不超过500kb</div>
          </div>
          <!--          <el-container style="margin-top: 20px;margin-bottom: 20px">-->
          <!--            <el-avatar shape="square" :size="350" :fit="fit" :src="post.BlogIntroductionPicture" />-->
          <!--          </el-container>-->
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
import { BlogDetails, BlogDetailsedit, Updatehomepageimage } from '@/api/admin/BlogPosts/BlogPosts'
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
      title: '',
      dialogImageUrl: '',
      dialogVisible: false,
      disabled: false
    }
  },
  created() {
    this.loadPostDetail(this.$route.query.blog_id)
  },
  methods: {
    beforeUpload(file) {
      const blogId = this.post.BlogId
      // 创建 FormData 对象
      const formData = new FormData()
      formData.append('file', file)
      formData.append('blog_id', blogId)
      Updatehomepageimage(blogId, formData)
        .then((response) => {
          // 处理后端响应
          file.url = response.data.msg
          this.dialogImageUrl = file.url
          // 根据后端响应执行其他操作
          this.$message({
            message: '博客首页图片上传成功',
            type: 'success'
          })
        })
        .catch((error) => {
          // 处理请求错误
          console.error('API error:', error)
          this.$message({
            message: '博客首页图片上传失败',
            type: 'warning'
          })
        })
      return true
    },
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
    },
    handleRemove(file) {
      console.log(file)
    },
    handlePictureCardPreview(file) {
      this.dialogImageUrl = file.url
      this.dialogVisible = true
    },
    handleDownload(file) {
      console.log(file)
    }
  }
}
</script>

<template>
  <el-container>
    <el-main>
      <div>
        <template v-if="post.BlogId">
          <h3>标题</h3>
          <el-input
            v-model="post.title"
            autosize
            placeholder="请输入标题"
            type="textarea"
          />
          <el-select
            v-model="value"
            allow-create
            default-first-option
            filterable
            multiple
            placeholder="请选择文章标签"
          >
            <el-option
              v-for="item in options"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
          <el-row :gutter="10" style="margin-top: 20px">
            <el-col :lg="3" :md="4" :sm="6" :xl="1" :xs="8">
              <div class="grid-content bg-purple" />
            </el-col>
            <el-col :lg="3" :md="4" :sm="6" :xl="1" :xs="8">
              <div class="grid-content bg-purple-light" />
            </el-col>
          </el-row>
          <markdown-editor v-model="post.content" style="height: 85vh" />
          <div><h1>文章首页图片</h1>
          </div>
          <div>
            <el-upload
              :auto-upload="true"
              :before-upload="beforeUpload"
              :file-list="fileList"
              action="#"
              list-type="picture-card"
            >
              <i slot="default" class="el-icon-plus" />
              <div slot="file" slot-scope="{file}">
                <img
                  :src="file.url"
                  class="el-upload-list__item-thumbnail"
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
              <img :src="dialogImageUrl" alt="" width="100%">
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
import { BlogDetails, BlogDetailsedit, Updatehomepageimage, BlogTagget } from '@/api/admin/BlogPosts/BlogPosts'
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
        content: '',
        BlogIntroductionPicture: '',
        author: '',
        tags: ''
      },
      editMode: false,
      value1: '',
      title: '',
      dialogImageUrl: '',
      dialogVisible: false,
      disabled: false,
      fileList: [],
      options: [
        {
          value: 'HTML',
          label: 'HTML'
        }, {
          value: 'CSS',
          label: 'CSS'
        }, {
          value: 'JavaScript',
          label: 'JavaScript'
        }],
      value: []
    }
  },
  created() {
    this.fetchArticleCategories()
    this.loadPostDetail(this.$route.query.blog_id)
  },
  methods: {
    async fetchArticleCategories() {
      try {
        // 向API发送请求以获取文章分类
        const response = await BlogTagget()
        this.options = response.data.map(item => ({
          value: item.Article_Type,
          label: item.Article_Type
        }))
      } catch (error) {
        console.error('获取文章分类时出错：', error)
      }
    },
    beforeUpload(file) {
      const blogId = this.post.BlogId
      const formData = new FormData()
      formData.append('file', file)
      formData.append('blog_id', blogId)

      Updatehomepageimage(blogId, formData)
        .then((response) => {
          // 处理后端响应
          file.url = response.data.msg
          this.dialogImageUrl = file.url

          // 添加上传的文件到 fileList 数组中
          this.fileList.push(file)

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
        console.log(this.post)
        // 加载文章首页图片并设置到 fileList 数组中
        this.loadHomepageImage(blog_id)
      } catch (error) {
        console.error('API error:', error)
      }
    },
    async loadHomepageImage(blog_id) {
      try {
        // 在此处调用您的 API 来加载文章首页图片的URL，假设该 API 是 loadHomepageImage
        const response = this.post.BlogIntroductionPicture
        const imgUrl = response
        // 创建一个文件对象并设置URL
        const file = {
          url: imgUrl,
          name: '图片名称.jpg', // 设置图片名称
          status: 'success', // 设置图片状态为成功
          uid: 1 // 设置唯一ID
        }

        // 将文件对象添加到 fileList 数组中
        this.fileList.push(file)
      } catch (error) {
        console.error('API error:', error)
      }
    },
    async savePost() {
      // Prepare the data to be sent to the API
      // const postData = {
      //   blog_id: this.post.BlogId,
      //   title: this.post.title,
      //   content: this.post.content,
      //   author: 'test',
      //   tags = ''
      //   // ... include other fields you want to send
      // }
      this.post.tags = this.value
      try {
        // Send the data to the API using Axios or any other HTTP library
        const response = await BlogDetailsedit(this.post.BlogId, this.post)
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

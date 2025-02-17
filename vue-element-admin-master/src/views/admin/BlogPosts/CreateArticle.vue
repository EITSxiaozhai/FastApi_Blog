<template>
  <el-container>
    <el-main>
      <el-card>
        <div>
          <template v-if="!editMode">
            <h3>创建文章</h3>
            <h1>
              <el-input v-model="post.title" placeholder="请输入标题" />
            </h1>
            <h3>添加相关的标签</h3>
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
            <h3>是否发布</h3>
            <el-select v-model="post.publishStatus" allow-create default-first-option filterable placeholder="是否发布？">
              <el-option v-for="item in publishOptions" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
            <div style="padding-top: 20px" />
            <markdown-editor v-model="post.content" style="height: 85vh" />
            <div style="padding-top: 20px">
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
            <el-button style="margin-top: 20px" type="primary" @click="createPost">保存</el-button>
          </template>
          <template v-else>
            <h3>编辑文章</h3>
            <el-input v-model="post.title" placeholder="请输入标题" />
            <markdown-editor v-model="post.content" style="height: 75vh" />
            <el-button type="success" @click="savePost">保存</el-button>
            <el-button type="warning" @click="cancelEdit">取消</el-button>
          </template>
        </div>
      </el-card>
    </el-main>
  </el-container>
</template>

<script>
import { CreateContent, Updatehomepageimage, BlogTagget } from '@/api/admin/BlogPosts/BlogPosts'
import MarkdownEditor from '@/components/MarkdownEditor'
import Cookies from 'js-cookie'

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
        publishStatus: ''
      },
      dialogImageUrl: '',
      dialogVisible: false,
      disabled: false,
      editMode: false,
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
      value: [],
      // 发布状态选择器的选项与选中值
      publishOptions: [
        { value: 'draft', label: '草稿' },
        { value: 'publish', label: '发布' }
      ],
      publishStatus: []
    }
  },
  created() {
    this.fetchArticleCategories()
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
    updateAuthor() {
      this.post.author = Cookies.get('username')
    },
    beforeUpload(file) {
      // if (!this.post.title || !this.post.content) { // 检查标题和内容是否为空
      //   this.$message.error('请完成标题和内容后再上传图片')
      //   return false // 阻止上传
      // }
      const blogId = this.$route.query.blog_id
      const formData = new FormData()
      formData.append('file', file)
      formData.append('blog_id', blogId)
      Updatehomepageimage(blogId, formData)
        .then((response) => {
          // 处理后端响应
          file.url = response.data.msg
          this.dialogImageUrl = file.url
          console.log(file.url)
          // 添加上传的文件到 fileList 数组中
          this.fileList.push(file)
          this.post.BlogIntroductionPicture = file.url
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
    async createPost() {
      // 检查标题和内容是否为空
      if (!this.post.title || !this.post.content || !this.post.publishStatus) {
        this.$message.error('标题和内容不能为空,且发布状态必须选择')
        return
      }
      this.post.tags = this.value
      try {
        // 发送创建文章请求到后端
        const response = await CreateContent(this.post)
        if (response.data.code === 20000) {
          // 创建成功，可以处理成功的逻辑，例如跳转到文章详情页面
          this.$router.push({ name: 'ArticleDetail', params: { blog_id: response.data.blog_id }})
          this.$message.success('创建文章成功')
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

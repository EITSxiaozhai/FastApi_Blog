<template>
  <el-container>
    <el-main>
      <el-card>
        <div slot="header" class="clearfix">
          <span>{{ editMode ? '编辑文章' : '创建文章' }}</span>
        </div>
        <el-form ref="postForm" :model="post" :rules="rules" label-width="100px">
          <el-form-item label="标题" prop="title">
            <el-input v-model="post.title" placeholder="请输入标题" />
          </el-form-item>

          <el-form-item label="标签" prop="tags">
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
          </el-form-item>

          <el-form-item label="发布状态" prop="PublishStatus">
            <el-select v-model="post.PublishStatus" placeholder="请选择发布状态">
              <el-option v-for="item in publishOptions" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
          </el-form-item>

          <el-form-item label="内容" prop="content">
            <markdown-editor v-model="post.content" style="height: 60vh" />
          </el-form-item>

          <el-form-item label="封面图片" prop="BlogIntroductionPicture">
            <el-upload
              :auto-upload="true"
              :before-upload="beforeUpload"
              :file-list="fileList"
              action="#"
              list-type="picture-card"
            >
              <i slot="default" class="el-icon-plus" />
              <div slot="file" slot-scope="{file}">
                <img :src="file.url" class="el-upload-list__item-thumbnail">
                <span class="el-upload-list__item-actions">
                  <span class="el-upload-list__item-preview" @click="handlePictureCardPreview(file)">
                    <i class="el-icon-zoom-in" />
                  </span>
                  <span class="el-upload-list__item-delete" @click="handleRemove(file)">
                    <i class="el-icon-delete" />
                  </span>
                </span>
              </div>
            </el-upload>
            <div slot="tip" class="el-upload__tip">只能上传jpg/png文件，且不超过500kb</div>
          </el-form-item>

          <el-form-item>
            <el-button type="primary" :loading="loading || uploadLoading" @click="createPost">保存</el-button>
            <el-button @click="$router.push('/admin/blog')">取消</el-button>
          </el-form-item>
        </el-form>

        <el-dialog :visible.sync="dialogVisible" append-to-body>
          <img :src="dialogImageUrl" alt="" width="100%">
        </el-dialog>
      </el-card>
    </el-main>
  </el-container>
</template>

<script>
import { CreateContent, Updatehomepageimage, BlogTagget, getAdminId } from '@/api/admin/BlogPosts/BlogPosts'
import MarkdownEditor from '@/components/MarkdownEditor'
import Cookies from 'js-cookie'

export default {
  name: 'CreateArticle',
  components: {
    MarkdownEditor
  },
  data() {
    return {
      loading: false,
      uploadLoading: false,
      post: {
        title: '',
        content: '',
        BlogIntroductionPicture: '',
        author: '',
        PublishStatus: '',
        NumberViews: 0,
        NumberLikes: 0,
        admin_id: null
      },
      rules: {
        title: [
          { required: true, message: '请输入文章标题', trigger: 'blur' },
          { min: 1, max: 100, message: '长度在 1 到 100 个字符', trigger: 'blur' }
        ],
        content: [
          { required: true, message: '请输入文章内容', trigger: 'blur' },
          { min: 1, message: '内容不能为空', trigger: 'blur' }
        ],
        PublishStatus: [
          { required: true, message: '请选择发布状态', trigger: 'change' }
        ],
        BlogIntroductionPicture: [
          { required: true, message: '请上传文章封面图片', trigger: 'change' }
        ]
      },
      dialogImageUrl: '',
      dialogVisible: false,
      fileList: [],
      options: [],
      value: [],
      publishOptions: [
        { value: 'False', label: '草稿' },
        { value: 'True', label: '发布' }
      ],
      editMode: false
    }
  },
  created() {
    this.fetchArticleCategories()
  },
  methods: {
    async fetchArticleCategories() {
      try {
        const response = await BlogTagget()
        this.options = response.data.map(item => ({
          value: item.Article_Type,
          label: item.Article_Type
        }))
      } catch (error) {
        console.error('获取文章分类失败:', error)
        this.$message.error('获取文章分类失败')
      }
    },
    updateAuthor() {
      const username = Cookies.get('username')
      if (!username) {
        this.$message.error('未登录或登录已过期')
        this.$router.push('/login')
        return false
      }
      this.post.author = username
      return true
    },
    beforeUpload(file) {
      this.uploadLoading = true
      const blogId = this.$route.query.blog_id
      const formData = new FormData()
      formData.append('file', file)
      formData.append('blog_id', blogId)

      Updatehomepageimage(blogId, formData)
        .then(response => {
          file.url = response.data.msg
          this.dialogImageUrl = file.url
          this.fileList.push(file)
          this.post.BlogIntroductionPicture = file.url
          this.$message.success('封面图片上传成功')
        })
        .catch(error => {
          console.error('上传失败:', error)
          this.$message.error('封面图片上传失败')
        })
        .finally(() => {
          this.uploadLoading = false
        })

      return true
    },
    async createPost() {
      try {
        if (!this.$refs.postForm) {
          this.$message.error('表单初始化失败')
          return
        }

        const valid = await this.$refs.postForm.validate()
        if (!valid) {
          return
        }

        if (!this.updateAuthor()) {
          return
        }

        this.loading = true
        const username = Cookies.get('username')
        const adminResponse = await getAdminId(username)

        if (!adminResponse || adminResponse.code !== 20000 || !adminResponse.data?.admin_id) {
          throw new Error('获取管理员信息失败')
        }

        const postData = {
          title: this.post.title,
          content: this.post.content,
          BlogIntroductionPicture: this.post.BlogIntroductionPicture,
          author: this.post.author,
          PublishStatus: this.post.PublishStatus === 'True',
          NumberViews: 0,
          NumberLikes: 0,
          admin_id: adminResponse.data.admin_id,
          tags: this.value
        }

        const response = await CreateContent(postData)
        if (response.code === 20000) {
          this.$message.success('创建文章成功')
          this.$router.push('/admin/blogpost/blogpost')
        } else {
          throw new Error(response.message || '创建文章失败')
        }
      } catch (error) {
        console.error('创建文章失败:', error)
        this.$message.error(error.message || '创建文章失败')
      } finally {
        this.loading = false
      }
    },
    handlePictureCardPreview(file) {
      this.dialogImageUrl = file.url
      this.dialogVisible = true
    },
    handleRemove(file) {
      const index = this.fileList.indexOf(file)
      if (index !== -1) {
        this.fileList.splice(index, 1)
        this.post.BlogIntroductionPicture = ''
      }
    }
  }
}
</script>

<style scoped>
.el-upload__tip {
  color: #909399;
  font-size: 12px;
  margin-top: 5px;
}
</style>

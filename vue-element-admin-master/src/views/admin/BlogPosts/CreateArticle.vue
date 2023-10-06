<template>
  <el-container>
    <el-main>
      <div>
        <template v-if="!editMode">
          <h3>创建文章</h3>
          <h1>
            <el-input v-model="post.title" placeholder="请输入标题" />
          </h1>

          <div style="padding-top: 20px" />
          <markdown-editor v-model="post.content" style="height: 1500px" />
          <div style="padding-top: 20px">
            <el-upload
              :before-upload="beforeUpload"
              action="#"
              list-type="picture-card"
              :auto-upload="true"
              :file-list="fileList"
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
          <el-button type="primary" style="margin-top: 20px" @click="createPost">保存</el-button>
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
import { CreateContent, Updatehomepageimage } from '@/api/admin/BlogPosts/BlogPosts'
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
    beforeUpload(file) {
      if (!this.post.title || !this.post.content) { // 检查标题和内容是否为空
        this.$message.error('请完成标题和内容后再上传图片')
        return false // 阻止上传
      }
      const formData = new FormData()
      formData.append('file', file)
      Updatehomepageimage(formData)
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
    async createPost() {
      // 检查标题和内容是否为空
      if (!this.post.title || !this.post.content) {
        this.$message.error('标题和内容不能为空')
        return
      }
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

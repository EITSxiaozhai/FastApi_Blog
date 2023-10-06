<template>
  <el-container>
    <el-header style="margin-top: 20px">
      <el-row class="demo-autocomplete">
        <el-col :span="6">
          <div class="sub-title">激活即列出输入建议</div>
          <el-autocomplete
            v-model="state2"
            class="inline-input"
            :fetch-suggestions="querySearch"
            placeholder="请输入想要搜索的文章"
            :trigger-on-focus="false"
            @select="handleSelect"
          />
        </el-col>
        <el-col :span="6">
          <el-button type="primary" @click="createItem">增加文章</el-button>
        </el-col>
      </el-row>
    </el-header>
    <el-main>
      <el-card class="box-card">
        <div>
          <el-table :data="adminData" style="width: 100%">
            <el-table-column prop="BlogId" label="文章id" />
            <el-table-column prop="title" label="标题" />
            <el-table-column prop="author" label="作者" />
            <el-table-column prop="created_at" label="创建时间" />
            <el-table-column label="操作">
              <template slot-scope="scope">
                <el-button type="text" @click="editItem(scope.row)">编辑</el-button>
                <el-button type="text" @click="deleteItem(scope.row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-card>
      <div class="child-page-container">
        <router-view />
      </div>
    </el-main>
  </el-container>

</template>

<script>
import { Postlist, DeletePost, Updatehomepageimage } from '@/api/admin/BlogPosts/BlogPosts'
import { MessageBox } from 'element-ui'
import PostEdit from '@/views/admin/BlogPosts/PostEdit.vue'
export default {
  components: {
    // eslint-disable-next-line vue/no-unused-components
    PostEdit
  },
  data() {
    return {
      adminData: []
    }
  },
  created() {
    this.fetchAdminData()
  },
  methods: {

    editItem(item) {
      // 导航到编辑页面，传递文章ID作为参数
      this.$router.push({ path: `/Blogid`, query: { blog_id: item.BlogId }})
    },
    async fetchAdminData() {
      try {
        const response = await Postlist()
        this.adminData = response.data
      } catch (error) {
        console.error('API error:', error)
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
    createItem() {
    // 使用路由名称导航到增加文章页面
      this.$router.push({ name: 'CreateArticle' })
    },
    async deleteItem(item) {
      try {
        const confirmResult = await MessageBox.confirm('确认删除此项吗？', '提示', {
          type: 'warning'
        })

        if (confirmResult === 'confirm') {
          const response = await DeletePost(item.BlogId)
          if (response.data.success) {
            this.fetchAdminData()
          }
        }
      } catch (error) {
        console.error('Delete error:', error)
      }
    }
  }
}
</script>

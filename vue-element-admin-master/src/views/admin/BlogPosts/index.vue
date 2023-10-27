<template>
  <el-container>
    <el-header style="margin-top: 20px">
      <el-row class="demo-autocomplete">
        <el-col :span="6">
          <el-autocomplete
            v-model="state"
            :fetch-suggestions="querySearchAsync"
            placeholder="请输入想要搜索的文章"
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
            <el-table-column prop="xxx" label="阅读量" />
            <el-table-column prop="xxx" label="评分值">
              <template>
                <!-- 在这里自定义列内容 -->
                <el-rate v-model="testrate" disabled>测试</el-rate>
              </template>
            </el-table-column>
            <el-table-column label="操作">
              <template slot-scope="scope">
                <el-button type="text" @click="editItem(scope.row)">编辑</el-button>
                <el-button type="text" @click="deleteItem(scope.row)">删除</el-button>
                <el-button size="small">评论</el-button>
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
      adminData: [],
      state: '',
      timeout: null,
      testrate: 2
    }
  },
  created() {
    this.fetchAdminData()
  },
  methods: {
    querySearchAsync(queryString, cb) {
      const articles = this.adminData // 使用你的文章数据数组 adminData
      const results = queryString
        ? articles.filter(this.createArticleFilter(queryString)).map((article) => ({
          value: article.title, // 将文章标题作为显示文本
          data: article // 保留原始文章数据
        }))
        : []
      console.log('Search results:', results) // 添加这行代码进行调试
      clearTimeout(this.timeout)
      this.timeout = setTimeout(() => {
        cb(results)
      }, 1) // 这里可以根据需要调整延迟时间
    },
    createArticleFilter(queryString) {
      return (article) => {
        // 确保文章标题存在，并且进行模糊匹配
        return article.title && article.title.toLowerCase().indexOf(queryString.toLowerCase()) === 0
      }
    },
    handleSelect(item) {
      // 用户选择了搜索结果后的处理逻辑
      // 可以根据选中的文章执行相关操作
      console.log(item)
      // 获取选中文章的BlogId
      const blogId = item.data.BlogId
      // 导航到对应的文章博客页面，并传递正确的blog_id参数
      this.$router.push({ path: `/Blogid`, query: { blog_id: blogId }})
    },
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
      const blogId = this.$route.query.blog_id
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
    async createItem() {
      try {
        // 获取所有文章列表
        const response = await Postlist()
        const posts = response.data
        // 找到最大的文章id
        let maxId = 0
        for (const post of posts) {
          if (post.BlogId > maxId) {
            maxId = post.BlogId
          }
        }

        // 将最大文章id加1作为新文章的id
        const newId = maxId + 1

        // 构建路由链接，将新文章的id作为参数传递到创建文章页面
        this.$router.push({ name: 'CreateArticle', query: { blog_id: newId }})
      } catch (error) {
        console.error('Create error:', error)
      }
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

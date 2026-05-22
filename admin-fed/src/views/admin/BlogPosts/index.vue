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
        <el-col :span="6">
          <el-button type="primary" @click="Crawlerrequestsent">文章爬虫提交</el-button>
        </el-col>
        <el-col :span="6">
          <el-button type="primary" @click="tokenforcedrefresh">token强制刷新</el-button>
        </el-col>
      </el-row>
    </el-header>
    <el-main>
      <el-card class="box-card">
        <div>
          <el-table v-loading="listLoading" :data="adminData" :row-key="row => row.BlogId" :empty-text="'暂无数据'" style="width: 100%">
            <el-table-column label="文章id" prop="BlogId" />
            <el-table-column label="标题" prop="title" />
            <el-table-column label="作者" prop="author" />
            <el-table-column label="创建时间" prop="created_at" :formatter="formatDate" />
            <el-table-column label="阅读量" prop="NumberViews" />
            <el-table-column label="点赞" prop="NumberLikes" />
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
import { Postlist, DeletePost } from '@/api/admin/BlogPosts/BlogPosts'
import { Crawlersubmitbutton } from '@/api/admin/CrawlerSubmission'
import { MessageBox } from 'element-ui'
import PostEdit from '@/views/admin/BlogPosts/PostEdit.vue'
import store from '@/store'

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
      listLoading: false
    }
  },
  created() {
    this.fetchAdminData()
  },
  methods: {
    querySearchAsync(queryString, cb) {
      const articles = this.adminData
      const results = queryString
        ? articles
          .filter(this.createArticleFilter(queryString))
          .map(article => ({ value: article.title, data: article }))
        : []
      clearTimeout(this.timeout)
      this.timeout = setTimeout(() => {
        cb(results)
      }, 200)
    },
    createArticleFilter(queryString) {
      return (article) => {
        return article.title && article.title.toLowerCase().includes(queryString.toLowerCase())
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
        this.listLoading = true
        const response = await Postlist()
        this.adminData = Array.isArray(response.data) ? response.data : []
      } catch (error) {
        console.error('API error:', error)
        this.$message.error('获取文章列表失败')
      } finally {
        this.listLoading = false
      }
    },
    async tokenforcedrefresh() {
      try {
        await store.dispatch('user/handleCheckRefreshToken')
      } catch (error) {
        console.error('Create error:', error)
      }
    },
    async createItem() {
      try {
        const posts = Array.isArray(this.adminData) ? this.adminData : []
        const ids = posts
          .map(p => Number(p.BlogId))
          .filter(id => Number.isFinite(id))
        const maxId = ids.length ? Math.max(...ids) : 0
        const newId = maxId + 1

        // 构建路由链接，将新文章的id作为参数传递到创建文章页面
        this.$router.push({ name: 'CreateArticle', query: { blog_id: newId }})
      } catch (error) {
        console.error('Create error:', error)
      }
    },
    async Crawlerrequestsent() {
      try {
        // 调用后端接口
        const response = await Crawlersubmitbutton()
        // 处理成功响应
        console.log('请求成功:', response)
        this.$message.success('爬虫提交成功')
        // 在这里可以根据后端返回的数据进行相应的处理
      } catch (error) {
        // 处理请求失败
        console.error('请求失败:', error)
        this.$message.error('爬虫提交失败')
        // 在这里可以根据错误信息进行相应的处理
      }
    },
    async deleteItem(item) {
      console.log(item.BlogId)
      try {
        const confirmResult = await MessageBox.confirm('确认删除此项吗？', '提示', {
          type: 'warning'
        })
        if (confirmResult === 'confirm') {
          const response = await DeletePost(item.BlogId)
          console.log('DeletePost 响应:', response)
          this.$message({
            message: '删除成功',
            type: 'success'
          })
          this.fetchAdminData()
        }
      } catch (error) {
        console.error('Delete error:', error)
        this.$message({
          message: '删除失败，请重试',
          type: 'error'
        })
      }
    },
    formatDate(row, column, cellValue) {
      const value = cellValue || row[column.property]
      if (!value) return ''
      const date = new Date(value)
      if (Number.isNaN(date.getTime())) return String(value)
      const y = date.getFullYear()
      const m = `${date.getMonth() + 1}`.padStart(2, '0')
      const d = `${date.getDate()}`.padStart(2, '0')
      const hh = `${date.getHours()}`.padStart(2, '0')
      const mm = `${date.getMinutes()}`.padStart(2, '0')
      return `${y}-${m}-${d} ${hh}:${mm}`
    }
  }
}
</script>

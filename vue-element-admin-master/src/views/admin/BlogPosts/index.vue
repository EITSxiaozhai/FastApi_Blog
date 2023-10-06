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
import { Postlist, DeletePost } from '@/api/admin/BlogPosts/BlogPosts'
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
        this.$router.push({ name: 'CreateArticle', query: { id: newId }})
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

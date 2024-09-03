<template>
  <div style="margin-top: 20px;margin-left: 20px;margin-right: 20px">
    <el-card>
      <el-button @click="resetDateFilter">清除日期过滤器</el-button>
      <el-button @click="clearFilter">清除所有过滤器</el-button>
      <el-table
        ref="filterTable"
        :data="tableData"
        style="width: 100%"
      >
        <el-table-column
          prop="TagName"
          label="标签名"
        />
        <el-table-column
          prop="Date"
          label="创建时间"
        />
        <el-table-column
          prop="Blog_id"
          label="关联ID"
        />
        <el-table-column
          prop="Blog_title"
          label="关联标题"
        />
        <el-table-column
          prop="OtherOperation"
          label="其他操作"
          width="auto"
        >
          <template v-slot="">
            <el-button type="primary">修改标签</el-button>
            <el-button type="danger">删除标签</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script>
import { BlogTagList } from '@/api/admin/BlogPosts/BlogPosts'

export default {
  data() {
    return {
      tableData: [] // 初始状态为空，等API调用后填充
    }
  },
  async created() {
    await this.GetTageinfo() // 组件创建时获取数据
  },
  methods: {
    async GetTageinfo() {
      try {
        // 向API发送请求以获取文章分类
        const response = await BlogTagList()
        // 将响应数据转换为数组格式
        this.tableData = Object.values(response.data).map(item => ({
          TagName: item.TagName,
          Date: item.Date,
          Blog_id: item.Blog_id,
          Blog_title: item.Blog_title
        }))
      } catch (error) {
        console.error('获取文章分类时出错：', error)
      }
    },
    resetDateFilter() {
      this.$refs.filterTable.clearFilter('date')
    },
    clearFilter() {
      this.$refs.filterTable.clearFilter()
    }
  }
}
</script>

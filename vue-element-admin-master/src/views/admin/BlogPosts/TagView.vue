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
          label="关联博客ID"
          prop="Blog_id"
        />
        <el-table-column
          label="关联标题"
          prop="Blog_title"
        />
        <el-table-column
          column-key="date"
          label="创建时间"
          prop="Date"
          sortable
        />
        <el-table-column
          :filter-method="filterTag"
          :filters="tagFilters"
          label="标签名"
          prop="Tags"
        >
          <template v-slot="scope">
            <!-- 循环展示所有的标签 -->
            <el-tag
              v-for="(tag, index) in scope.row.Tags"
              :key="index"
              style="margin-right: 4px"
            >
              {{ tag }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          label="其他操作"
          prop="OtherOperation"
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
  computed: {
    // 动态生成 filters
    tagFilters() {
      // 获取所有标签并去重
      const allTags = this.tableData.flatMap(item => item.Tags)
      return [...new Set(allTags)].map(tag => ({ text: tag, value: tag }))
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
          Blog_id: item.Blog_id,
          Blog_title: item.Blog_title,
          Date: item.Date,
          Tags: item.Tags // 将 Tags 数组保存在这里
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
    },
    // 筛选标签
    filterTag(value, row) {
      return row.Tags.includes(value)
    }
  }
}
</script>

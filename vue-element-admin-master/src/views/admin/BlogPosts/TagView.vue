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
          :filter-method="filterTag"
          :filters="tagFilters"
          prop="TagName"
          label="标签名"
        >
          <template v-slot="scope">
            <!-- 使用 el-tag 包裹标签名 -->
            <el-tag>{{ scope.row.TagName }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column

          prop="Date"
          sortable
          column-key="date"
          label="创建时间"
        />
        <el-table-column
          prop="Blog_id"
          label="关联博客ID"
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
  computed: {
    // 动态生成 filters
    tagFilters() {
      const tags = this.tableData.map(item => item.TagName)
      // 去重并生成 filter 对象数组
      return [...new Set(tags)].map(tag => ({ text: tag, value: tag }))
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
    },
    formatter(row, column) {
      return row.address
    },
    filterTag(value, row) {
      return row.TagName === value
    },
    filterHandler(value, row, column) {
      const property = column['property']
      return row[property] === value
    }
  }
}
</script>

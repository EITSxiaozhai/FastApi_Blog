<template>
  <div>
    <h1>测试标题</h1>
    <ul>
      <!-- 使用v-for指令遍历adminData数组，并渲染列表 -->
      <li v-for="user in adminData" :key="user.UserId">
        {{ user.username }} - {{ user.UserEmail }}
      </li>
    </ul>
  </div>
</template>

<script>
import { adminlist } from '@/api/admin/user.js'

export default {
  data() {
    return {
      adminData: [] // 初始化一个空数组，用于存储adminlist接口的数据
    }
  },
  created() {
    // 在组件创建时调用adminlist接口
    this.fetchAdminList()
  },
  methods: {
    async fetchAdminList() {
      try {
        const response = await adminlist() // 调用adminlist接口
        this.adminData = response.data // 将接口返回的数据存储在adminData中
      } catch (error) {
        console.error('API error:', error)
      }
    }
  }
}
</script>

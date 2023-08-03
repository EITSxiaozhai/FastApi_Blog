<template>
  <el-container>
    <el-header />
    <el-main>
      <div>
        <ul>
          <!-- 使用v-for指令遍历adminData数组，并渲染列表 -->
          <el-table :data="adminData" border style="width: 100%">
            <el-table-column fixed prop="username" label="用户名" width="240">
              <!-- 绑定点击事件，点击用户名时打开修改信息的对话框 -->
              <template slot-scope="scope">
                <span @click="openEditDialog(scope.row)">{{ scope.row.username }}</span>
              </template>
            </el-table-column>
            <el-table-column fixed prop="UserEmail" label="用户邮箱" width="240" />
            <el-table-column prop="Typeofuser.value" label="用户权限" width="auto" />
            <el-table-column prop="UserUuid" label="用户唯一ID" width="auto" />
            <el-table-column prop="province" label="禁用状态" width="120">
              <el-button type="success" icon="el-icon-check" circle />
            </el-table-column>
          </el-table>
        </ul>
      </div>
    </el-main>

    <!-- 添加修改信息的对话框 -->
    <el-dialog :visible.sync="editDialogVisible" title="修改用户信息" @close="handleDialogClose">
      <!-- 在对话框中添加表单用于修改用户信息 -->
      <el-form ref="editForm" :model="editFormData" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="editFormData.username" />
        </el-form-item>
        <el-form-item label="用户邮箱" prop="UserEmail">
          <el-input v-model="editFormData.UserEmail" />
        </el-form-item>
        <el-select v-model="adminData.Typeofuser" placeholder="请选择">
          <el-option
            v-for="item in adminData.Typeofuser"
            :key="item.value"
            :label="item.code"
            :value="item.value"
          />
        </el-select>
        <!-- 其他需要修改的字段 -->
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button @click="editDialogVisible = false">取 消</el-button>
        <el-button type="primary" @click="saveEdit">保 存</el-button>
      </span>
    </el-dialog>

  </el-container>
</template>

<script>
import { adminlist, updateUser } from '@/api/admin/user.js'

export default {
  data() {
    return {
      adminData: [], // 初始化一个空数组，用于存储adminlist接口的数据
      editDialogVisible: false, // 添加控制对话框显示与隐藏的变量
      editFormData: {} // 添加一个对象用于存储修改信息的表单数据
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
    },
    // 点击用户名时打开修改信息的对话框，并初始化表单数据
    openEditDialog(row) {
      this.editFormData = { ...row } // 使用对象拷贝复制用户数据，防止直接修改原始数据
      this.editDialogVisible = true
    },
    // 点击保存按钮处理修改信息的逻辑
    async saveEdit() {
      try {
        // 调用后端接口将修改后的信息保存到数据库中
        await updateUser(this.editFormData)
        // 更新页面上的用户列表
        await this.fetchAdminList()
        // 关闭对话框
        this.editDialogVisible = false
      } catch (error) {
        console.error('API error:', error)
        // 处理错误，例如显示错误提示等
      }
    },
    // 对话框关闭时的处理
    handleDialogClose() {
      // 可以在这里重置表单数据等
      // 关闭对话框
      this.editDialogVisible = false
    }
    // 其他方法...
  }
}
</script>

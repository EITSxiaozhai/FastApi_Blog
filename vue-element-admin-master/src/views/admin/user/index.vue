<template>
  <el-container>
    <el-header />
    <el-main style="margin-top: -50px;">
      <el-button type="primary" @click="openAddDialog">添加用户</el-button>
      <el-button type="success">成功按钮</el-button>

      <el-card style="margin-top: 20px">
        <div>
          <ul>
            <!-- 使用v-for指令遍历adminData数组，并渲染列表 -->
            <el-table :data="adminData" border style="width: 100%">
              <el-table-column fixed label="用户名" prop="username" width="150">
                <!-- 绑定点击事件，点击用户名时打开修改信息的对话框 -->
                <template slot-scope="scope">
                  <span @click="openEditDialog(scope.row)">{{ scope.row.username }}</span>
                </template>
              </el-table-column>
              <el-table-column fixed label="用户邮箱" prop="UserEmail" width="240" />
              <el-table-column label="用户权限" prop="privilegeName.code" width="100" />
              <el-table-column label="用户唯一ID" prop="UserUuid" width="300" />
              <el-table-column label="禁用状态" prop="province" width="120">
                <el-button circle icon="el-icon-check" type="success" />
              </el-table-column>
              <el-table-column label="其他操作" prop="province" width="auto">
                <el-button icon="el-icon-edit" type="primary">编辑用户</el-button>
                <el-button icon="el-icon-delete" type="primary">删除用户</el-button>
                <el-button icon="el-icon-search" type="primary">重置密码</el-button>
              </el-table-column>
            </el-table>
          </ul>
        </div>
        <el-button-group style="">
          <el-button icon="el-icon-arrow-left" type="primary">上一页</el-button>
          <el-button type="primary">下一页<i class="el-icon-arrow-right el-icon--right" /></el-button>
        </el-button-group>
      </el-card>
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
        <el-form-item label="用户权限" prop="Typeofuser">
          <el-select v-model="editFormData.userprivilegesData" placeholder="请选择">
            <el-option
              v-for="(privilege, key) in userprivilegesData"
              :key="key"
              :label="privilege.value"
              :value="key"
            />
          </el-select>
        </el-form-item>

        <!-- 其他需要修改的字段 -->
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button @click="editDialogVisible = false">取 消</el-button>
        <el-button type="primary" @click="saveEdit">保 存</el-button>
      </span>
    </el-dialog>
    <!-- 添加新用户的对话框 -->
    <el-dialog :visible.sync="addDialogVisible" title="添加新用户">
      <el-form ref="addForm" :model="addFormData" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="addFormData.username" />
        </el-form-item>
        <el-form-item label="用户密码" prop="Userpassword">
          <el-input v-model="addFormData.userpassword" />
        </el-form-item>
        <el-form-item label="用户邮箱" prop="UserEmail">
          <el-input v-model="addFormData.UserEmail" />
        </el-form-item>
        <el-form-item label="用户权限" prop="Typeofuser">
          <el-select v-model="addFormData.userprivilegesData" placeholder="请选择">
            <el-option
              v-for="(privilege, key) in userprivilegesData"
              :key="key"
              :label="privilege.value"
              :value="key"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="用户性别" prop="Typeofusergender">
          <el-select v-model="addFormData.gender" placeholder="请选择">
            <el-option
              v-for="(privilege, key) in userprivilegesData"
              :key="key"
              :label="privilege.value"
              :value="key"
            />
          </el-select>
        </el-form-item>
        <!-- 其他需要添加的字段 -->
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button @click="addDialogVisible = false">取 消</el-button>
        <el-button type="primary" @click="saveAdd">保 存</el-button>
      </span>
    </el-dialog>

  </el-container>
</template>

<script>
import { adminlist, updateUser, userprivileges, adminadd } from '@/api/admin/user.js'

export default {
  data() {
    return {
      adminData: [], // 初始化一个空数组，用于存储adminlist接口的数据
      typeofuserData: [],
      editDialogVisible: false, // 添加控制对话框显示与隐藏的变量
      addDialogVisible: false, // 添加新用户对话框的显示与隐藏变量
      editFormData: {}, // 添加一个对象用于存储修改信息的表单数据
      addFormData: {}, // 添加一个对象用于存储新用户信息的表单数据
      userprivilegesData: [],
      gender: []
    }
  },
  created() {
    // 在组件创建时调用adminlist接口
    this.fetchAdminList()
    this.fetchTypeofuserData()
    this.fetchuserprivileges()
  },
  methods: {
    async fetchuserprivileges() {
      try {
        const response = await userprivileges()
        this.userprivilegesData = response.data
      } catch (error) {
        console.error('API error:', error)
      }
    },
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
    openAddDialog() {
      this.addFormData = {} // 重置表单数据
      this.addDialogVisible = true // 打开添加用户对话框
    },
    async fetchTypeofuserData() {
      try {
        const response = await adminlist() // Call the API to get Typeofuser data
        this.typeofuserData = response.data // Store the API response in typeofuserData
      } catch (error) {
        console.error('API error:', error)
      }
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
    async saveAdd() {
      try {
        const payload = { ...this.addFormData }
        // 调用后端接口将新用户信息保存到数据库中
        console.log(this.userprivilegesData)
        payload.userPrivileges = Number(payload.userPrivileges)
        await adminadd(payload)
        // 更新页面上的用户列表
        await this.fetchAdminList()
        // 关闭对话框
        this.addDialogVisible = false
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

<script setup>
import { ref } from 'vue';
import axios from 'axios';
import backApi from "@/Api/backApi";

const loginForm = ref({
  username: '',
  password: '',
});

const login = async () => {
  try {
    console.log(loginForm)
    const response = await backApi.post('/generaluser/login', {
      username: loginForm.value.username,
      password: loginForm.value.password,
    });
    // 根据后端返回的数据处理登录成功或失败的情况
    if (response.data.success) {
      // 登录成功，可以进行页面跳转或其他操作
      console.log('登录成功:', response.data.message);
    } else {
      // 登录失败，处理错误消息
      console.error('登录失败:', response.data.message);
    }
  } catch (error) {
    console.error('登录失败:', error);
  }
};
</script>

<template>
  <el-form  :model="loginForm" label-width="80px" class="login-form">
    <el-form-item label="用户名" prop="username">
      <el-input  @input="loginForm.username = $event" v-model="loginForm.username" placeholder="请输入用户名"></el-input>
    </el-form-item>
    <el-form-item label="密码" prop="password">
      <el-input @input="loginForm.password = $event" type="password" v-model="loginForm.password" placeholder="请输入密码"></el-input>
    </el-form-item>
    <el-form-item>
      <el-button type="primary" @click="login">登录</el-button>
    </el-form-item>
  </el-form>
</template>

<style scoped>
.login-form {
  max-width: 400px;
  margin: 0 auto;
  padding: 20px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
</style>

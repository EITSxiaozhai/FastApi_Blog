<script setup>
import { ref, onMounted, onBeforeMount,nextTick,onActivated } from 'vue';
import backApi from "@/Api/backApi";
import { useRouter } from 'vue-router'; // 导入useRouter函数
import { ElNotification } from 'element-plus';
import vueRecaptcha from 'vue3-recaptcha2';

const v2Sitekey = '6Lfj3kkoAAAAAJzLmNVWXTAzRoHzCobDCs-Odmjq';

// 回傳一組 token，並把 token 傳給後端驗證
const recaptchaVerified = (res) => {
  console.log(res);
      ElNotification({
        title: 'Warning',
        message: '您还没有登录哦，点击卡片跳转到登录页面',
        type: 'warning',
      })
};

const recaptchaExpired = () => {
  // 過期後執行動作
};

const recaptchaFailed = () => {
  // 失敗執行動作
};


const loginForm = ref({
  username: '',
  password: '',
});

let router; // 声明路由器变量

onBeforeMount(() => {
  router = useRouter(); // 在组件挂载之前获取路由器实例
});



const token = ref(''); // 创建一个ref变量来存储令牌

onMounted(() => {
  // 在组件加载后从localStorage中加载令牌
  const storedToken = localStorage.getItem("token");
  if (storedToken) {
    token.value = storedToken;
  }
});



const login = async () => {
  try {
    console.log(loginForm);
    console.log(token)
    const response = await backApi.post('/generaluser/login', {
      username: loginForm.value.username,
      password: loginForm.value.password,
    });

    if (response.data.success) {
      const newToken = response.data.token;
      localStorage.setItem("token", newToken);
      token.value = newToken;


      router.push('/blog'); // 使用router进行页面重定向
      ElNotification({
    title: 'Success',
    message: '登录成功',
    type: 'success',
  })
    } else {
        ElNotification({
    title: 'Warning',
    message: '登录失败',
    type: 'warning',
  })
      console.error('登录失败:', response.data.message);
    }
  } catch (error) {
      ElNotification({
    title: 'Warning',
    message: '登录失败',
    type: 'warning',
  })
    console.error('登录失败:', error);
  }
};
</script>

<template>
  <el-form :model="loginForm" label-width="80px" class="login-form">
    <el-form-item label="用户名" prop="username">
      <el-input @input="loginForm.username = $event" v-model="loginForm.username" placeholder="请输入用户名"></el-input>
    </el-form-item>
    <el-form-item label="密码" prop="password">
      <el-input @input="loginForm.password = $event" type="password" v-model="loginForm.password"
                placeholder="请输入密码"></el-input>
    </el-form-item>

    <el-form-item>
  <vueRecaptcha
    :sitekey="v2Sitekey"
    @verified="recaptchaVerified"
    @expired="recaptchaExpired"
    @failed="recaptchaFailed"
  ></vueRecaptcha>
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

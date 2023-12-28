<script setup>
import { ref, onMounted, onBeforeMount,nextTick,onActivated } from 'vue';
import backApi from "@/Api/backApi";
import { useRouter } from 'vue-router'; // 导入useRouter函数
import { ElNotification } from 'element-plus';
import vueRecaptcha from 'vue3-recaptcha2';
import { useStore } from 'vuex';
import VueJwtDecode from 'vue-jwt-decode';


const v2Sitekey = '6Lfj3kkoAAAAAJzLmNVWXTAzRoHzCobDCs-Odmjq';

// 回傳一組 token，並把 token 傳給後端驗證
const isLoginButtonDisabled = ref(true);

const recaptchaVerified = (response) => {

  isLoginButtonDisabled.value = false; // 用户通过验证，按钮变为有效
};

const recaptchaExpired = () => {
  isLoginButtonDisabled.value = true; // 验证过期，按钮变为无效
};

const recaptchaFailed = () => {
  isLoginButtonDisabled.value = true; // 验证失败，按钮变为无效
};

const LoginUserForm = ref({
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


const store = useStore();

const login = async () => {
  try {


    const response = await backApi.post('/generaluser/login', {
      username: LoginUserForm.value.username,
      password: LoginUserForm.value.password,
    });

    if (response.data.success) {
      const newToken = response.data.token;
      localStorage.setItem("token", newToken);

      token.value = newToken;

      const decodedToken = VueJwtDecode.decode(newToken);
      const username = decodedToken.username;
  // 调用 Vuex mutation 设置 token 和用户名
      store.commit('setTokenAndUsername', { token: newToken, username });
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
  <el-container>
      <el-aside  style="height: 100vh;width: 70%;background-size: cover;;background-image: url('https://api.vvhan.com/api/view');" >测试</el-aside>
    <el-main style= 'padding-top: 20%'>
       <el-form  :model="LoginUserForm" label-width="80px" class="login-form">
    <el-form-item label="用户名" prop="username">
      <el-input  v-model="LoginUserForm.username" placeholder="请输入用户名"></el-input>
    </el-form-item>
    <el-form-item label="密码" prop="password">
      <el-input type="password" v-model="LoginUserForm.password"
                placeholder="请输入密码"></el-input>
    </el-form-item>

    <el-form-item>
      <div>
  <vueRecaptcha
  :sitekey="v2Sitekey"
  size="normal"
  theme="light"
  hl="zh-CN"
  @verify="recaptchaVerified"
  @expire="recaptchaExpired"
  @fail="recaptchaFailed"
  >
</vueRecaptcha>
      </div>
    </el-form-item>
    <el-form-item>
      <el-button type="primary" @click="login" :disabled="isLoginButtonDisabled">登录</el-button>
      <el-button  type="primary" ><router-link  style="text-decoration: none" to="/reg">注册</router-link></el-button>
    </el-form-item>
  </el-form>
    </el-main>
  </el-container>

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

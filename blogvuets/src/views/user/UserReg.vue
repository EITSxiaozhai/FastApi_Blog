<script setup>
import { ref, reactive } from 'vue';
import vueRecaptcha from 'vue3-recaptcha2';
import { ElNotification } from 'element-plus';
import backApi from "@/Api/backApi";

const v2Sitekey = '6Lfj3kkoAAAAAJzLmNVWXTAzRoHzCobDCs-Odmjq';

// 回傳一組 token，並把 token 傳給後端驗證
const recaptchaVerified = (res) => {
  console.log(res);
};

const recaptchaExpired = () => {
  // 過期後執行動作
};

const recaptchaFailed = () => {
  // 失敗執行動作
};

const registerForm = ref({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  verificationCode: '',
});

const verificationCodeDisabled = ref(false);
const verificationCodeButtonText = ref('获取验证码');

const getVerificationCode = () => {
  // 在这里执行获取验证码的逻辑
  // 可以向后端发送请求获取验证码
  // 示例代码中仅模拟获取验证码并计时60秒
  verificationCodeDisabled.value = true;
  verificationCodeButtonText.value = '60s 后重新获取';
  let seconds = 60;
  const timer = setInterval(() => {
    seconds--;
    if (seconds <= 0) {
      clearInterval(timer);
      verificationCodeDisabled.value = false;
      verificationCodeButtonText.value = '获取验证码';
    } else {
      verificationCodeButtonText.value = `${seconds}s 后重新获取`;
    }
  }, 1000);
};

const register = async () => {
  try {
    console.log(registerForm);

    const response = await backApi.post('/generaluser/reguser', {
      username: registerForm.value.username,
      password: registerForm.value.password,
      email: registerForm.value.email,
      // 其他注册需要的字段
    });

    if (response.data.success) {
      // 注册成功的处理
      console.log('注册成功:', response.data.message);
      ElNotification({
        title: 'Success',
        message: '注册成功',
        type: 'success',
      });

      // 在注册成功后，您可能还需要执行其他操作，例如跳转到登录页面
      // router.push('/login');
    } else {
      // 注册失败的处理
      console.error('注册失败:', response.data.message);
      ElNotification({
        title: 'Warning',
        message: '注册失败',
        type: 'warning',
      });
    }
  } catch (error) {
    console.error('注册失败:', error);
    ElNotification({
      title: 'Warning',
      message: '注册失败',
      type: 'warning',
    });
  }
};

// 调用注册函数
register();
</script>

<template>
  <el-form
    :model="registerForm"
    label-width="80px"
    class="register-form"
    ref="registerForm"
    @submit.prevent="register"

  >
    <el-form-item label="用户名" prop="username">
      <el-input  @input='registerForm.username($event)' v-model="registerForm.username" placeholder="请输入用户名"></el-input>
    </el-form-item>
    <el-form-item label="邮箱" prop="email">
      <el-input @input='registerForm.username($event)' v-model="registerForm.email" placeholder="请输入邮箱"></el-input>
    </el-form-item>
    <el-form-item label="密码" prop="password">
      <el-input
        type="password"
        v-model="registerForm.password"
        placeholder="请输入密码"
        @input='registerForm.username($event)'
      ></el-input>
    </el-form-item>
    <el-form-item label="确认密码" prop="confirmPassword">
      <el-input
        type="password"
        @input='registerForm.username($event)'
        v-model="registerForm.confirmPassword"
        placeholder="请确认密码"
      ></el-input>
    </el-form-item>
    <el-form-item label="验证码" prop="verificationCode">
      <el-input
          @input='registerForm.username($event)'
        v-model="registerForm.verificationCode"
        placeholder="请输入验证码"
      ></el-input>
      <el-button
        class="get-verification-code"
        @click="getVerificationCode"
        :disabled="verificationCodeDisabled"
      >
        {{ verificationCodeButtonText }}
      </el-button>
    </el-form-item>
    <el-form-item>
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
    </el-form-item>
    <el-form-item>
      <el-button type="primary" native-type="submit">注册</el-button>
      <el-button  type="primary" ><router-link  style="text-decoration: none" to="/login">登录</router-link></el-button>
    </el-form-item>
  </el-form>
</template>



<style scoped>
.register-form {
  max-width: 400px;
  margin: 0 auto;
  padding: 20px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.get-verification-code[disabled] {
  background-color: #ccc;
  cursor: not-allowed;
}
</style>

<script setup>
import { ref, reactive } from 'vue';
import vueRecaptcha from 'vue3-recaptcha2';
import { ElNotification } from 'element-plus';
import backApi from "@/Api/backApi";

const v2Sitekey = '6Lfj3kkoAAAAAJzLmNVWXTAzRoHzCobDCs-Odmjq';


const googleRecaptchaVerified = ref(false);

// 回傳一組 token，並把 token 傳給後端驗證
const recaptchaVerified = (res) => {
  // 设置 googleRecaptchaVerified 为 true
  RegisterUserForm.value.googlerecaptcha = res
  googleRecaptchaVerified.value = true;

};

const recaptchaExpired = () => {
  // 過期後執行動作
};

const recaptchaFailed = () => {
  // 失敗執行動作
};

const RegisterUserForm = ref({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  verificationCode: '',
  googlerecaptcha:'',
  EmailverificationCod:'',

});


const validatePassword = (rule, value, callback) => {

  if (value === undefined) {
    callback(new Error('密码不能为空'));
  } else if (value === '') {
    callback(new Error('请输入密码'));
  } else if (value.length < 8) {
    callback(new Error('密码长度不能小于 8 位'));
  } else {
    callback();
  }
};

const validateConfirmPassword = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请再次输入密码'));
  } else if (value !== RegisterUserForm.value.password) {
    callback(new Error('两次输入密码不一致'));
  } else {
    callback();
  }
};

const validateUsername = (rule, value, callback) => {


  //匹配不包含空格和中文字符的用户名
  const reg = /^[^\s\u4e00-\u9fa5]+$/;
  if (!reg.test(value)) {
    callback(new Error('用户名不能包含空格和中文字符'));
  } else {
    callback();
  }
};

const validateEmail = (rule, value, callback) => {
  const reg = /^[a-zA-Z0-9_-]*@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$/;
  if (!reg.test(value)) {
    callback(new Error('请输入正确的邮箱地址'));
  } else {
    callback();
  }
};


const verificationCodeDisabled = ref(false);
const verificationCodeButtonText = ref('获取验证码');

const getVerificationCode = async () => {
  // 检查邮箱是否为空
  if (!RegisterUserForm.value.email) {
    // 如果邮箱为空，不发送请求
    console.log("Email is empty. Request not sent.");
    return;
  }

  const response = await backApi.post('/generaluser/emailcod', {
    email: RegisterUserForm.value.email,
  });

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
    // Check if Google reCAPTCHA is verified
    if (googleRecaptchaVerified.value) {
      // Perform registration logic
      const response = await backApi.post('/generaluser/reguser', {
        username: RegisterUserForm.value.username,
        password: RegisterUserForm.value.password,
        confirmpassword: RegisterUserForm.value.confirmPassword,
        email: RegisterUserForm.value.email,
        googlerecaptcha : RegisterUserForm.value.googlerecaptcha,
        EmailverificationCod: RegisterUserForm.value.EmailverificationCod,

        // Other registration fields
      });

      // Check the registration response
      if (response.data.Success === 'True') {
        // Registration successful

        ElNotification({
          title: 'Success',
          message: 'Registration successful',
          type: 'success',
        });

        // After successful registration, you may want to perform other actions, such as redirecting to the login page
        this.router.push('/login');
      } else {
        // Registration failed
        console.error('Registration failed:', response.data.message);
        ElNotification({
          title: 'Warning',
          message: 'Registration failed',
          type: 'warning',
        });
      }
    } else {
      // If Google reCAPTCHA is not verified, show a warning to the user
      ElNotification({
        title: 'Warning',
        message: 'Please complete Google reCAPTCHA verification',
        type: 'warning',
      });
    }
  } catch (error) {
    // Handle registration error
    console.error('Registration failed:', error);

  }
};
</script>

<template>
  <el-container style="height: 100%;width: 100%;background-size: cover;background-image: url('https://api.vvhan.com/api/view');" >

  <el-main  >
    <h1  style="padding-left:40%" >注册页面</h1>
    <el-form
    v-model="RegisterUserForm"
    label-width="80px"
    class="register-form"
    ref="registerForm"
    @submit.prevent="register"

  >
<el-form-item label="用户名" prop="username" :rules="[{ validator: validateUsername, trigger: 'blur' }]">
    <el-input  v-model="RegisterUserForm.username" placeholder="请输入用户名"></el-input>
  </el-form-item>

  <el-form-item label="密码" prop="password" :rules="[{ validator: validatePassword, trigger: 'blur' }]">
    <el-input
      type="password"
      v-model="RegisterUserForm.password"
      placeholder="请输入密码"
      :show-password="true"
    ></el-input>
  </el-form-item>

  <el-form-item label="确认密码" prop="confirmPassword" :rules="[{ validator: validateConfirmPassword, trigger: 'blur' }]">
    <el-input
      type="password"
      v-model="RegisterUserForm.confirmPassword"
      placeholder="请确认密码"
      :show-password="true"
    ></el-input>
  </el-form-item>

  <el-form-item label="邮箱" prop="email" :rules="[{ validator: validateEmail, trigger: 'blur' }]">
    <el-input  v-model="RegisterUserForm.email" placeholder="请输入邮箱"></el-input>
  </el-form-item>

    <el-form-item label="验证码" prop="verificationCode">
      <el-input
        v-model="RegisterUserForm.EmailverificationCod"
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
  <el-form-item>
    <vueRecaptcha
      :sitekey="v2Sitekey"
      size="normal"
      theme="light"
      hl="zh-CN"
      v-model="RegisterUserForm.googlerecaptcha"
      @verify="recaptchaVerified"
      @expire="recaptchaExpired"
      @fail="recaptchaFailed"
    ></vueRecaptcha>
  </el-form-item>
    </el-form-item>
    <el-form-item>
      <el-button type="primary" native-type="submit">注册</el-button>
      <el-button  type="primary" ><router-link  style="text-decoration: none" to="/login">登录</router-link></el-button>
    </el-form-item>
  </el-form>
  </el-main>

    </el-container>
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

#app .el-main form{
 background-color:#faf9f9;
  opacity: 0.9;

}

</style>

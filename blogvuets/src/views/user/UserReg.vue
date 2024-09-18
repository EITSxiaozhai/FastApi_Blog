<script lang="ts" setup>
import {ref, reactive, watch, onBeforeMount, nextTick, onMounted, defineProps} from 'vue';
import vueRecaptcha from 'vue3-recaptcha2';
import {ElNotification, ElUpload, ElMessage} from 'element-plus';
import {Plus} from '@element-plus/icons-vue'
import type {UploadProps} from 'element-plus'
import {useRouter} from 'vue-router';
import type {FormInstance} from 'element-plus'
import _ from 'lodash';
import { UploadUserAvatar,RegUser,CheckUserName,SentMailCod } from '@//Api/User/userapi'


const v2Sitekey = '6Lfj3kkoAAAAAJzLmNVWXTAzRoHzCobDCs-Odmjq';

const imageUrl = ref('')
let router;

onBeforeMount(() => {
  router = useRouter(); // 在组件挂载之前获取路由器实例
});

//此处创建了一个Google验证码的prors.否则报错
const props = defineProps({
  hl: {
    type: String,
    required: false
  },
})

onMounted(() => {
  //此处重写Google前端js的地址。使用国内地址就可以正常加载这个Google验证
  const recaptchaUrl = `https://recaptcha.net/recaptcha/api.js?onload=recaptchaReady&render=explicit&hl=${props.hl}&_=${+new Date()}`
  const scriptTag = document.createElement("script");
  scriptTag.id = "recaptcha-script";
  scriptTag.setAttribute("src", recaptchaUrl);
  document.head.appendChild(scriptTag);
});

const handleAvatarSuccess: UploadProps['onSuccess'] = (
    response,
    uploadFile
) => {
  imageUrl.value = URL.createObjectURL(uploadFile.raw!)
}

const beforeAvatarUpload: UploadProps['beforeUpload'] = (rawFile) => {
  if (rawFile.type !== 'image/jpeg') {
    ElMessage.error('Avatar picture must be JPG format!')
    return false
  } else if (rawFile.size / 1024 / 1024 > 2) {
    ElMessage.error('Avatar picture size can not exceed 2MB!')
    return false
  }
  return true
}


const googleRecaptchaVerified = ref(false);

// 回傳一組 token，並把 token 傳給後端驗證
const recaptchaVerified = (res: any) => {
  // 设置 googleRecaptchaVerified 为 true
  RegisterUserForm.googlerecaptcha = res
  googleRecaptchaVerified.value = true;

};

const recaptchaExpired = () => {
  // 過期後執行動作
};

const recaptchaFailed = () => {
  // 失敗執行動作
};

const registerFormRef = ref(null);
const RegisterUserForm = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  verificationCode: '',
  googlerecaptcha: '',
  EmailverificationCod: '',
  UserAvatar: '',
});


const verificationCodeDisabled = ref(false);
const verificationCodeButtonText = ref('获取验证码');

const getVerificationCode = async () => {
  // 检查邮箱是否为空
  if (!RegisterUserForm.email) {
    // 如果邮箱为空，不发送请求

    return;
  }

  const response = await SentMailCod({
    email: RegisterUserForm.email,
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


const ruleFormRef = ref<FormInstance>()

const debouncedCheckUsername = _.debounce(async (username, callback) => {
  try {
    const response = await CheckUserName( {username: username});
    if (response.data.exists) {
      callback(new Error('用户名已存在'));
    } else {
      callback();
    }
  } catch (error) {
    console.error('Error checking username:', error);
    callback(new Error('验证用户名时发生错误'));
  }
}, 500);  // 500毫秒的防抖延迟

const validateUsername = (rule: any, value: any, callback: any) => {
  const reg = /^[^\s\u4e00-\u9fa5]+$/;

  if (!reg.test(value)) {
    callback(new Error('用户名不能包含空格和中文字符'));
  } else {
    // 使用防抖函数触发用户名检查
    debouncedCheckUsername(value, callback);
  }
};

const validatePass = (rule: any, value: any, callback: any) => {
  if (value === '') {
    callback(new Error('Please input the password'))
  } else {
    if (RegisterUserForm.confirmPassword !== '') {
      if (!ruleFormRef.value) return
      ruleFormRef.value.validateField('checkPass', () => null)
    }
    callback() // 添加这一行
  }
}

const validatePass2 = (rule: any, value: any, callback: any) => {
  nextTick(() => {
    const passwordValue = RegisterUserForm.password;
    const password2Value = value
    if (value === '') {
      callback(new Error('请再次输入密码'));
    } else if (passwordValue === '') {
      callback(new Error('请先输入密码'));
    } else if (password2Value !== passwordValue) {
      callback(new Error('两次输入不一致'));
    } else {
      callback();
    }
  });
};

const validateEmail = (rule: any, value: any, callback: any) => {
  const reg = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/;
  if (!reg.test(value)) {
    callback(new Error('请输入正确的邮箱地址'));
  } else {
    callback();
  }
};

const rules = reactive({
  username: [
    {required: true, min: 6, max: 18, validator: validateUsername, trigger: 'change'}
  ],
  password: [
    {required: true, type: 'password', message: "请填写你的密码", validator: validatePass, trigger: 'change'}
  ],
  confirmPassword: [
    {required: true, type: 'password', message: "确认密码和你输入的密码不同", validator: validatePass2, trigger: 'change'}
  ],
  verificationCode: [{required: true, message: '请输入正确邮箱验证码', trigger: 'blur', min: 6, max: 6}],
  email: [{
    required: true,
    type: 'email',
    message: '请输入正确的邮箱地址',
    validator: validateEmail,
    trigger: 'change'
  }],
});


const register = async () => {
  try {
    // Check if Google reCAPTCHA is verified
    if (googleRecaptchaVerified.value) {
      // Perform registration logic
      const response = await RegUser({
        username: RegisterUserForm.username,
        password: RegisterUserForm.password,
        confirmpassword: RegisterUserForm.confirmPassword,
        email: RegisterUserForm.email,
        googlerecaptcha: RegisterUserForm.googlerecaptcha,
        EmailverificationCod: RegisterUserForm.EmailverificationCod,
        UserAvatar: RegisterUserForm.UserAvatar
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
        router.push('/login');
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
const uploadAvatarRef = ref(null);

const ossUpload = async (param: any) => {
  if (ElUpload.props.ref === 'uploadavatar') {
    // ElUpload.methods.clearFiles.call(ElUpload);
  }
  const formData = new FormData();
  formData.append('file', param.file);
  await UploadUserAvatar(formData);
};

// :ref="RegisterUserForm"
</script>

<template>
  <el-container
      style="height: 100%;width: 100%;background-size: cover;background-image: url('https://api.vvhan.com/api/view');">

    <el-main>
      <h1 style="padding-left:40%">注册页面</h1>
      <el-form
          :model="RegisterUserForm"
          label-width="80px"
          class="register-form"
          :rules="rules"
          @submit.prevent="register"
          ref="registerFormRef"
      >
        <el-form-item label="用户名" prop="username" :rules="rules.username">
          <el-input v-model.trim="RegisterUserForm.username" placeholder="请输入用户名"></el-input>
        </el-form-item>

        <el-form-item label="密码" prop="password" :rules="rules.password">
          <el-input
              type="password"
              v-model.trim="RegisterUserForm.password"
              placeholder="请输入密码"
              :show-password="true"
          ></el-input>
        </el-form-item>

        <el-form-item label="确认密码" prop="confirmPassword" :rules="rules.confirmPassword">
          <el-input
              type="password"
              v-model.trim="RegisterUserForm.confirmPassword"
              placeholder="请确认密码"
              :show-password="true"
          ></el-input>
        </el-form-item>

        <el-form-item label="邮箱" prop="email" :rules="rules.email">
          <el-input v-model.trim="RegisterUserForm.email" placeholder="请输入邮箱"></el-input>
        </el-form-item>

        <el-form-item label="验证码" prop="verificationCode">
          <el-input
              v-model.trim="RegisterUserForm.EmailverificationCod"
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
        <el-form-item label="你的头像">
          <el-upload
              class="avatar-uploader"
              action=#
              v-model="RegisterUserForm.UserAvatar"
              ref="uploadavatar"
              :show-file-list="false"
              :http-request="ossUpload"
              :on-success="handleAvatarSuccess"
              :before-upload="beforeAvatarUpload"
          >
            <img v-if="imageUrl" :src="imageUrl" class="avatar"/>
            <el-icon v-else class="avatar-uploader-icon">
              <Plus/>
            </el-icon>
          </el-upload>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" native-type="submit">注册</el-button>
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

#app .el-main form {
  background-color: #faf9f9;
  opacity: 0.9;

}

.avatar-uploader .avatar {
  width: 178px;
  height: 178px;
  display: block;
}
</style>

<style>
.avatar-uploader .el-upload {
  border: 1px dashed var(--el-border-color);
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: var(--el-transition-duration-fast);
}

.avatar-uploader .el-upload:hover {
  border-color: var(--el-color-primary);
}

.el-icon.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 178px;
  height: 178px;
  text-align: center;
}

</style>

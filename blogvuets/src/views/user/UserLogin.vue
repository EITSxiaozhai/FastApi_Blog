<script setup>
import {ref, onMounted, onBeforeMount, nextTick, onActivated, defineProps , onBeforeUnmount} from 'vue';
import {useRouter} from 'vue-router'; // 导入useRouter函数
import {ElNotification} from 'element-plus';
import vueRecaptcha from 'vue3-recaptcha2';
import {useStore} from 'vuex';
import VueJwtDecode from 'vue-jwt-decode';
import {UserLogin, CheckLogin,GetQrcode} from '@/api/User/userapi';
import '@/assets/css/UserLogin.css';

const v2Sitekey = '6Lfj3kkoAAAAAJzLmNVWXTAzRoHzCobDCs-Odmjq';

// 回傳一組 token，並把 token 傳給後端驗證
const isLoginButtonDisabled = ref(true);

const recaptchaVerified = (response) => {
  LoginUserForm.value.googlerecaptcha = response
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
  googlerecaptcha: '',
});

let router; // 声明路由器变量

onBeforeMount(() => {
  router = useRouter(); // 在组件挂载之前获取路由器实例
});


const token = ref(''); // 创建一个ref变量来存储令牌

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
// 在组件加载后从localStorage中加载令牌
  const storedToken = localStorage.getItem("token");
  if (storedToken) {
    token.value = storedToken;
  }

});


// // 动态设置 recaptchaUrl
// const setRecaptchaUrl = async () => {
//   const vueRecaptchaModule = await import('vue3-recaptcha2');
//   const { vueRecaptcha } = vueRecaptchaModule.default;
//
//   // 修改 recaptchaUrl 属性
//   const urlx = `https://recaptcha.net/recaptcha/api.js?onload=recaptchaReady&render=explicit&hl=zh-CN&_=${+new Date()}`
//   vueRecaptcha.props.recaptchaUrl.default = urlx;
// };


const store = useStore();

const login = async () => {
  try {

    const response = await UserLogin({

      username: LoginUserForm.value.username,
      password: LoginUserForm.value.password,
      googlerecaptcha: LoginUserForm.value.googlerecaptcha

    });

    if (response.data.success) {
      const newToken = response.data.token;
      localStorage.setItem("token", newToken);

      token.value = newToken;

      const decodedToken = VueJwtDecode.decode(newToken);
      const username = decodedToken.username;
      // 调用 Vuex mutation 设置 token 和用户名
      store.commit('setTokenAndUsername', {token: newToken, username});
      // 更新 Vuex store 中的用户名
      store.commit('setUsername', username);
      if (store.getters.getLastVisitedRoute) {
        const routepage = store.getters.getLastVisitedRoute
        router.push(`/blog/${routepage}`);
      } else {
        router.push(`/`);
      }
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



// 新增二维码相关状态
const qrCodeImage = ref('');
const githubLoginState = ref('');
const isPolling = ref(false);
let pollInterval = null;

// 获取GitHub登录二维码
// 二维码获取与轮询逻辑
const fetchGithubQRCode = async () => {
  try {
    // 重置状态
    qrCodeImage.value = '';
    githubLoginState.value = '';
    isPolling.value = false;
    if (pollInterval) clearInterval(pollInterval);

    // 发起新请求
    const response = await GetQrcode();
    qrCodeImage.value = response.data.qrCodeUrl;
    githubLoginState.value = response.data.state;
    startPolling();
  } catch (error) {
    ElNotification({
      title: '错误',
      message: '获取二维码失败，3秒后重试',
      type: 'error'
    });
    setTimeout(fetchGithubQRCode, 3000);
  }
};

// 轮询检查登录状态
const startPolling = () => {
  isPolling.value = true;
  pollInterval = setInterval(async () => {
    try {

    const response = await CheckLogin({ state: githubLoginState.value });

      if (response.data.status === 'confirmed') {
        clearInterval(pollInterval);
        isPolling.value = false;

        // 处理登录成功逻辑
        localStorage.setItem('token', response.data.token);
        store.commit('setTokenAndUsername', {
          token: response.data.token,
          username: response.data.username
        });

        ElNotification({
          title: '成功',
          message: 'GitHub登录成功',
          type: 'success'
        });

        router.push('/');
      } else if (response.data.status === 'expired') {
        clearInterval(pollInterval);
        isPolling.value = false;
        ElNotification({
          title: '过期',
          message: '二维码已过期，请刷新页面',
          type: 'warning'
        });
        await fetchGithubQRCode(); // 重新获取二维码
      }
    } catch (error) {
      clearInterval(pollInterval);
      isPolling.value = false;
    }
  }, 2000);
};

onMounted(() => {
  fetchGithubQRCode();
});

onBeforeUnmount(() => {
  if (pollInterval) {
    clearInterval(pollInterval);
  }
});
</script>

<template>
  <el-container
      style="height: 100%;width: 100%;background-size: cover;background-image: url('https://api.vvhan.com/api/view');">
    <el-main>

      <el-form :model="LoginUserForm" class="login-form" label-width="80px">
              <div class="qrcode-section">
        <div class="qrcode-container">
          <img
            v-if="qrCodeImage"
            :src="qrCodeImage"
            alt="GitHub扫码登录"
            class="qrcode-image"
          />
          <div v-else class="qrcode-loading">
            <el-icon class="is-loading"><Loading /></el-icon>
            生成二维码中...
          </div>
          <div v-if="isPolling" class="qrcode-status">
            <el-icon class="is-loading"><Loading /></el-icon>
            等待扫码...
          </div>
        </div>
        <div class="qrcode-tips">
          <p>使用 GitHub 扫码登录</p>
          <p>首次扫码将自动创建账号</p>
        </div>
      </div>
        <el-form-item label="用户名" prop="username">
          <el-input v-model="LoginUserForm.username" placeholder="请输入用户名"></el-input>
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="LoginUserForm.password" placeholder="请输入密码"
                    type="password"></el-input>
        </el-form-item>

        <el-form-item>
          <div>
            <vueRecaptcha
                :sitekey="v2Sitekey"
                hl="zh-CN"
                size="normal"
                theme="light"
                @expire="recaptchaExpired"
                @fail="recaptchaFailed"
                @verify="recaptchaVerified"
            >
            </vueRecaptcha>
          </div>
        </el-form-item>
        <el-form-item>
          <el-button :disabled="isLoginButtonDisabled" type="primary" @click="login">登录</el-button>
          <el-button type="primary">
            <router-link style="text-decoration: none" to="/reg">注册</router-link>
          </el-button>
        </el-form-item>
      </el-form>


    </el-main>

  </el-container>

</template>
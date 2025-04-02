<template>
  <div class="login-container">
    <el-form
      ref="loginForm"
      :model="loginForm"
      :rules="loginRules"
      autocomplete="on"
      class="login-form"
      label-position="left"
    >

      <div class="title-container">
        <h3 class="title">Login Form</h3>
      </div>

      <el-form-item prop="username">
        <span class="svg-container">
          <svg-icon icon-class="user" />
        </span>
        <el-input
          ref="username"
          v-model="loginForm.username"
          autocomplete="on"
          name="username"
          placeholder="Username"
          tabindex="1"
          type="text"
        />
      </el-form-item>

      <el-tooltip v-model="capsTooltip" content="Caps lock is On" manual placement="right">
        <el-form-item prop="password">
          <span class="svg-container">
            <svg-icon icon-class="password" />
          </span>
          <el-input
            :key="passwordType"
            ref="password"
            v-model="loginForm.password"
            :type="passwordType"
            autocomplete="on"
            name="password"
            placeholder="Password"
            tabindex="2"
            @blur="capsTooltip = false"
            @keyup.native="checkCapslock"
            @keyup.enter.native="handleLogin"
          />
          <span class="show-pwd" @click="showPwd">
            <svg-icon :icon-class="passwordType === 'password' ? 'eye' : 'eye-open'" />
          </span>
        </el-form-item>
      </el-tooltip>

      <el-form-item v-model="loginForm.googlerecaptcha" prop="googlerecaptcha">
        <div id="grecaptcha" />
      </el-form-item>

      <el-button
        :loading="loading"
        style="width:100%;margin-bottom:30px;"
        type="primary"
        @click.native.prevent="handleLogin"
      >Login
      </el-button>

      <div style="position:relative">

        <div class="tips">
          <span>
            <el-button class="thirdparty-button" type="primary" @click="showDialog=true">
              Or connect with
            </el-button>
          </span>
        </div>
      </div>
    </el-form>

    <el-dialog :visible.sync="showDialog" title="Or connect with">
      Can not be simulated on local, so please combine you own business simulation! ! !
      <br>
      <br>
      <br>
      <social-sign />
    </el-dialog>
  </div>
</template>

<script>
import Cookies from 'js-cookie'
import { validUsername } from '@/utils/validate'
import SocialSign from './components/SocialSignin'

export default {
  name: 'Login',
  components: {
    SocialSign
  },
  data() {
    const validateUsername = (rule, value, callback) => {
      if (!validUsername(value)) {
        callback()
      } else {
        callback()
      }
    }
    const validatePassword = (rule, value, callback) => {
      if (value.length < 6) {
        callback(new Error('Passwords do not meet security requirements'))
      } else {
        callback()
      }
    }
    const validategooglerecaptcha = (rule, value, callback) => {
      if (!value) {
        callback(new Error('Please complete the AI detection.'))
      } else {
        callback()
      }
    }
    return {
      loginForm: {
        username: '',
        password: '',
        googlerecaptcha: ''
      },
      loginRules: {
        username: [{ required: true, trigger: 'blur', validator: validateUsername }],
        password: [{ required: true, trigger: 'blur', validator: validatePassword }],
        googlerecaptcha: [{ required: true, validator: validategooglerecaptcha }]
      },
      passwordType: 'password',
      capsTooltip: false,
      loading: false,
      showDialog: false,
      redirect: undefined,
      otherQuery: {},
      googlerecaptcha: null,
      sitekey: '6LfRyR8oAAAAAEQ34CTwyS7B1m7dhnsVWLtR8TUB'
    }
  },
  watch: {
    $route: {
      handler: function(route) {
        const query = route.query
        if (query) {
          this.redirect = query.redirect
          this.otherQuery = this.getOtherQuery(query)
        }
      },
      immediate: true
    }
  },
  created() {
    // window.addEventListener('storage', this.afterQRScan)
  },
  mounted() {
    if (this.loginForm.username === '') {
      this.$refs.username.focus()
    } else if (this.loginForm.password === '') {
      this.$refs.password.focus()
    } else if (this.loginForm.googlerecaptcha === '') {
      this.$refs.googlerecaptcha.focus()
    }
    this.loaded()
  },
  destroyed() {
    // window.removeEventListener('storage', this.afterQRScan)
  },
  methods: {
    submit: function(token) {
      console.log('Submit button clicked') // 添加此行以确认按钮是否点击
      if (this.loginForm.googlerecaptcha) {
        console.log('googlerecaptcha is not empty') // 添加此行以确认 password2 是否不为空
        console.log(this.loginForm.googlerecaptcha)
      } else {
        console.error('googlerecaptcha is empty')
      }
    },
    loaded() {
      setTimeout(() => {
        // 在回调函数中调用 submit 方法，同时设置 password2
        window.grecaptcha.render('grecaptcha', {
          sitekey: this.sitekey,
          callback: (token) => {
            this.loginForm.googlerecaptcha = token
            this.submit(token) // 在回调函数中调用 submit 方法
          }
        })
      }, 200)
    },
    checkCapslock(e) {
      const { key } = e
      this.capsTooltip = key && key.length === 1 && (key >= 'A' && key <= 'Z')
    },
    showPwd() {
      if (this.passwordType === 'password') {
        this.passwordType = ''
      } else {
        this.passwordType = 'password'
      }
      this.$nextTick(() => {
        this.$refs.password.focus()
      })
    },
    handleLogin() {
      this.$refs.loginForm.validate(valid => {
        console.log(this.loginForm)
        if (valid) {
          this.loading = true
          Cookies.set('username', this.loginForm.username)
          this.$store.dispatch('user/login', this.loginForm)
            .then(() => {
              this.$router.push({ path: this.redirect || '/', query: this.otherQuery })
              this.loading = false
            })
            .catch((error) => {
              this.loading = false
              if (error.response && error.response.status === 401) {
                this.$message({
                  message: '登录失败：用户名或密码错误',
                  type: 'error',
                  duration: 3000
                })
                // 重置表单
                this.loginForm.username = ''
                this.loginForm.password = ''
                this.loginForm.googlerecaptcha = ''
                // 重置AI验证
                window.grecaptcha.reset()
                // 清空表单验证
                this.$refs.loginForm.clearValidate()
                // 聚焦到用户名输入框
                this.$nextTick(() => {
                  this.$refs.username.focus()
                })
              } else {
                this.$message({
                  message: error.message || '登录失败，请稍后重试',
                  type: 'error',
                  duration: 3000
                })
              }
            })
        } else {
          console.log('error submit!!')
          return false
        }
      })
    },

    getOtherQuery(query) {
      return Object.keys(query).reduce((acc, cur) => {
        if (cur !== 'redirect') {
          acc[cur] = query[cur]
        }
        return acc
      }, {})
    }
    // afterQRScan() {
    //   if (e.key === 'x-admin-oauth-code') {
    //     const code = getQueryObject(e.newValue)
    //     const codeMap = {
    //       wechat: 'code',
    //       tencent: 'code'
    //     }
    //     const type = codeMap[this.auth_type]
    //     const codeName = code[type]
    //     if (codeName) {
    //       this.$store.dispatch('LoginByThirdparty', codeName).then(() => {
    //         this.$router.push({ path: this.redirect || '/' })
    //       })
    //     } else {
    //       alert('第三方登录失败')
    //     }
    //   }
    // }
  }
}
</script>

<style lang="scss">
/* 修复input 背景不协调 和光标变色 */
/* Detail see https://github.com/PanJiaChen/vue-element-admin/pull/927 */

$bg: #283443;
$light_gray: #fff;
$cursor: #fff;

@supports (-webkit-mask: none) and (not (cater-color: $cursor)) {
  .login-container .el-input input {
    color: $cursor;
  }
}

/* reset element-ui css */
.login-container {
  .el-input {
    display: inline-block;
    height: 47px;
    width: 85%;

    input {
      background: transparent;
      border: 0px;
      -webkit-appearance: none;
      border-radius: 0px;
      padding: 12px 5px 12px 15px;
      color: $light_gray;
      height: 47px;
      caret-color: $cursor;

      &:-webkit-autofill {
        box-shadow: 0 0 0px 1000px $bg inset !important;
        -webkit-text-fill-color: $cursor !important;
      }
    }
  }

  .el-form-item {
    border: 1px solid rgba(255, 255, 255, 0.1);
    background: rgba(0, 0, 0, 0.1);
    border-radius: 5px;
    color: #454545;
  }
}
</style>

<style lang="scss" scoped>
$bg: #2d3a4b;
$dark_gray: #889aa4;
$light_gray: #eee;

.login-container {
  min-height: 100%;
  width: 100%;
  background-color: $bg;
  overflow: hidden;

  .login-form {
    position: relative;
    width: 520px;
    max-width: 100%;
    padding: 160px 35px 0;
    margin: 0 auto;
    overflow: hidden;
  }

  .tips {
    font-size: 14px;
    color: #fff;
    margin-bottom: 10px;

    span {
      &:first-of-type {
        margin-right: 16px;
      }
    }
  }

  .svg-container {
    padding: 6px 5px 6px 15px;
    color: $dark_gray;
    vertical-align: middle;
    width: 30px;
    display: inline-block;
  }

  .title-container {
    position: relative;

    .title {
      font-size: 26px;
      color: $light_gray;
      margin: 0px auto 40px auto;
      text-align: center;
      font-weight: bold;
    }
  }

  .show-pwd {
    position: absolute;
    right: 10px;
    top: 7px;
    font-size: 16px;
    color: $dark_gray;
    cursor: pointer;
    user-select: none;
  }

  .thirdparty-button {
    position: absolute;
    right: 0;
    bottom: 6px;
  }

  @media only screen and (max-width: 470px) {
    .thirdparty-button {
      display: none;
    }
  }
}
</style>

<script setup>
import {ref} from 'vue';
// import {useHead} from '@unhead/vue';
import { useMeta } from 'vue-meta';

const description = ref('Exp1oit的博客,分享Linux服务器搭建运维,学习Python技术,vue3,利用Fastapi,Django,mysql的技术搭建个人网站,分享Devops教程,记录一下自己的学习成果,欢迎来到我的博客首页,搜索你感兴趣的？')
const keywords = ref('Linux,Python,Vue,运维,云服务,Seo,K8s,Devops,运维开发,FastApi,Blog,Django')


// 使用 `useMeta` 设置 meta 信息
const { meta } = useMeta({
  description: description.value,
  keywords: keywords.value
});

</script>

<template>

  <div id="app">
    <router-view/>
<!--    <div v-for="item of 500" :key="item" class="snowflake"></div>-->
  </div>
</template>


<style lang="scss">

#app, body {
  font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen-Sans, Ubuntu, Cantarell, Helvetica Neue, sans-serif;
  height: 100%; /* 使#app占满全屏高度 */
  padding: 0;
  margin: 0;
  width: 100%;
}
</style>
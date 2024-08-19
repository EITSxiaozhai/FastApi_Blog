<script setup>
import {ref} from 'vue';
import {useHead} from '@unhead/vue';

const myPage = ref({description: 'Exp1oit的博客。分享Linux服务器搭建运维,学习Python技术,vue3,利用Fastapi,Django,mysql的技术搭建个人网站。记录一下自己的学习成果'})
const title = ref('title')
const metakeywords = ref('Linux,Python,Vue,运维,云服务,Seo,计算机教学,计算机基础')


useHead({
  meta: [{name: 'description', content: () => myPage.value.description},
    {name: 'keywords', content: () => metakeywords}],
})
</script>

<template>
  <head>
    <meta name="keywords" content="">
  </head>
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
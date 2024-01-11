<script setup>
import { ref } from 'vue';
import { useHead } from '@unhead/vue';

const myPage = ref({ description: 'Exp1oit的博客。分享Linux服务器搭建运维,学习Python技术,vue3,利用Fastapi,Django,mysql的技术搭建个人网站。记录一下自己的学习成果'})
const title = ref('title')
const metakeywords = ref( 'Linux,Python,Vue,运维,云服务,Seo,计算机教学,计算机基础')


useHead({
  meta: [{ name: 'description', content: () => myPage.value.description },
    { name: 'keywords',content: () => metakeywords}],
})
</script>

<template>
  <head>
    <meta name="keywords" content="">
  </head>
  <div id="app">
    <router-view/>
  </div>
</template>


<style>
html, body {
  height: 100%;
  width: 100%;
  margin: 0;
  padding: 0;
  background: rgb(233, 233, 235);
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB',
  'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
}

#app {
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB',
  'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
  height: 100%; /* 使#app占满全屏高度 */
}
</style>
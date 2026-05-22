<script setup>
import {ref} from 'vue';
import {useHead} from '@unhead/vue';

const myPage = ref({description: 'Exp1oit的博客，专注于Linux服务器运维、Python编程、Vue 3开发、FastAPI、Django、MySQL、DevOps等技术的应用。通过详细教程和个人经验分享，帮助开发者掌握云服务、DevOps流程、网站搭建和计算机技术的最佳实践'})
const title = ref('title')
const metakeywords = ref('Linux服务器运维, Python开发, Vue 3, FastAPI, Django, MySQL, DevOps, 网站搭建, 云服务, 运维教程, CI/CD, 容器化, 自动化部署, 技术博客, SEO优化')


useHead({
  meta: [{name: 'description', content: () => myPage.value.description},
    {name: 'keywords', content: () => metakeywords}],
})
</script>

<template>
  <head>
    <meta content="" name="keywords">
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
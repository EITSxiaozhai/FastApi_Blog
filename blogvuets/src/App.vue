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
    <div v-for="item of 500" :key="item" class="snowflake"></div>
  </div>
</template>


<style lang="scss">
.snowflake {
  --size: 5vw;
  width: var(--size);
  height: var(--size);
  background: url("../static/img/xuehua.png") no-repeat;
  background-size: 100% 100%;
  position: fixed;
  top: -5vh;
  z-index: -1;
}

@keyframes snowfall {
  100% {
    transform: translate3d(var(--end), 100vh, 0);
  }
}

@for $i from 0 through 500 {
  .snowflake:nth-child(#{$i}) {
    //每个雪花的大小
    --size: #{random(10) * 0.1}vw;
    //雪花移动目标点 -70后是负数 这样雪花会向左下方飘落
    --end: #{random(20) - 70}vw;
    left: #{random(150)}vw;
    animation: snowfall #{5 + random(8)}s linear infinite;
    animation-delay: -#{random(10)}s;
  }
}



html, body {
  height: 100%;
  width: 100%;
  margin: 0;
  padding: 0;
  background: rgb(233, 233, 235);
  font-family:-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen-Sans, Ubuntu, Cantarell, Helvetica Neue, sans-serif;
}

#app {
font-family:-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen-Sans, Ubuntu, Cantarell, Helvetica Neue, sans-serif;
  height: 100%; /* 使#app占满全屏高度 */
}
</style>
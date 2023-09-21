<script setup>
</script>

<template>
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
<script setup>
import {RouterLink, RouterView} from 'vue-router'
import HelloWorld from './components/HelloWorld.vue'
</script>

<template>
  <header>
    <el-menu
        :default-active="activeIndex"
        class="el-menu-demo"
        mode="horizontal"
        :ellipsis="false"
        @select="handleSelect"
    >
      <el-menu-item index="0">LOGO</el-menu-item>
      <div class="flex-grow"/>
      <el-menu-item index="1">Exp1oit Blog</el-menu-item>
      <el-sub-menu index="2">
        <template #title>Workspace</template>
        <el-menu-item index="2-1">
          <p>
            <RouterLink to="/">主页</RouterLink>
          </p>
        </el-menu-item>
        <el-menu-item index="2-2">
          <p>
            <RouterLink to="/about">个人介绍</RouterLink>
          </p>
        </el-menu-item>
        <el-sub-menu index="2-4">
          <template #title>item four</template>
          <el-menu-item index="2-4-1">
            <RouterLink to="/">Home</RouterLink>
          </el-menu-item>
          <el-menu-item index="/about">个人介绍</el-menu-item>
        </el-sub-menu>
      </el-sub-menu>
    </el-menu>
  </header>
  <div class="wrapper">
  </div>
  <RouterView/>
</template>

<style>
header {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  z-index: 9999;
  background-color: #ffffff; /* 可根据需要设置背景颜色 */
}
</style>

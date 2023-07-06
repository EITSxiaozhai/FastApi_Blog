<script setup>
import {RouterLink, RouterView} from 'vue-router'
import HelloWorld from './components/HelloWorld.vue'
</script>

<template>
  <el-container>
    <el-header>
      <el-menu
          :default-active="activeIndex"
          class="el-menu-demo"
          mode="horizontal"
          @select="handleSelect"
      >
        <el-menu-item index="1">Exp1oit Blog</el-menu-item>
        <el-sub-menu index="2">
          <template #title>导航</template>
          <el-menu-item index="2-1">个人介绍</el-menu-item>
          <el-menu-item index="2-2">GIT主页</el-menu-item>
          <el-menu-item index="2-3">个人NAS</el-menu-item>
          <el-sub-menu index="2-4">
            <template #title>子菜单项目</template>
            <el-menu-item index="2-4-1">item one</el-menu-item>
            <el-menu-item index="2-4-2">item two</el-menu-item>
            <el-menu-item index="2-4-3">item three</el-menu-item>
          </el-sub-menu>
        </el-sub-menu>
        <el-menu-item index="3" disabled>Info</el-menu-item>
        <el-menu-item index="4">Orders</el-menu-item>
      </el-menu>
    </el-header>
  </el-container>

  <el-container id="left-my" style="padding-top: 1px;">
    <el-aside id="left-my-card">
      <el-row>
        <el-card style="background-color:#79bbff;">
          <img
              src="https://shadow.elemecdn.com/app/element/hamburger.9cf7b091-55e9-11e9-a976-7f4d0b07eef6.png"
              class="image"
          />
          <div style="padding: 14px">
            <span>Exp1oit</span>
            <p>一个混运维想转开发的小菜鸡</p>
          </div>
        </el-card>
      </el-row>
    </el-aside>

    <el-container>
      <el-main id="maincare" style="margin-left: 10%">
        <div class="about">
          <div class="common-layout">
            <el-container>
              <el-main>
                <div v-for="blog in data" :key="blog.BlogId">
                  <el-card class="box-card" style="margin-top: 10px">
                    <h1>{{ blog.title }}</h1>
                    <div class="box-card">
                      <img :src="blog.BlogIntroductionPicture" alt="" style="">
                    </div>
                    <span>{{ blog.content }}</span>
                    <p>作者: {{ blog.author }}</p>
                  </el-card>
                </div>
              </el-main>
            </el-container>
          </div>
        </div>
      </el-main>
      <el-space direction="vertical" style="padding-right: 10%">
        <el-card v-for="i in 2" :key="i" class="box-card" style="width: 250px">
          <template #header>
            <div class="card-header">
              <span>最多阅读文章</span>
            </div>
          </template>
        </el-card>
      </el-space>

    </el-container>
  </el-container>
</template>


<script>
import axios from 'axios';
import VueParticles from 'vue-particles';


export default {
  data() {
    return {
      data: [],
    };
  },
  created() {
    this.getData();
  },
  methods: {
    getData() {
      axios.get('http://127.0.0.1:8000/blog/BlogIndex')
          .then(response => {
            this.data = response.data;
          })
          .catch(error => {
            console.error(error);
          });
    },
  },
  components: {
    VueParticles,
  },
};
</script>

<style>
#left-my-card {
  transform: translatex(20px) translatey(13px);
}

</style>

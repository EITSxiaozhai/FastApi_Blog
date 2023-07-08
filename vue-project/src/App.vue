<script setup>
import {RouterLink, RouterView} from 'vue-router'
import HelloWorld from './components/HelloWorld.vue'
</script>

<template>

  <el-container id="top-mains">
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
      </el-menu>
    </el-header>
  </el-container>

  <el-container id="left-my">
    <el-aside id="left-my-card" style="padding-top: 5%">
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

    <el-container style="margin-top: 1%;height: 10%">
      <el-main id="maincare" style="margin-left: 10%">
        <div class="about">
          <div class="common-layout">
            <el-container>
              <el-main>
                <div v-for="blog in data" :key="blog.BlogId">
                  <el-card class="box-card" style="margin-top: 10px">
                    <h1 style="font-size: 30px;">{{ blog.title }}</h1>
                    <h1>{{ blog.content }}</h1>
                    <el-container id="blog-img-container">
                      <img id="blog-img" :src="blog.BlogIntroductionPicture" alt="">
                    </el-container>
                    <h1>作者: {{ blog.author }}</h1>
                  </el-card>
                </div>
              </el-main>
            </el-container>
          </div>
        </div>

      </el-main>

      <el-container>
        <el-card>
          <el-space direction="vertical" style="padding-right: 10%">
            <el-card v-for="i in 2" :key="i" class="box-card" style="width: 250px">
              <template #header>
                <div class="card-header">
                  <span>最多阅读文章</span>
                </div>
              </template>
            </el-card>

          </el-space>
          <el-divider />
          <el-carousel iindicator-position="none">
            <el-carousel-item v-for="blog in data">
              <h3 text="2xl" justify="center">{{ item }}</h3>
              <img id="blog-img" :src="blog.BlogIntroductionPicture" alt="">
            </el-carousel-item>
          </el-carousel>

        </el-card>
      </el-container>
    </el-container>
  </el-container>

  <el-footer>
    <el-row style="display: flex; align-items: center;">
      <el-col :span="6">
        <el-statistic title="共计访问人数" :value="268500"/>
      </el-col>
    </el-row>
  </el-footer>

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

#left-my .el-container .el-container > .el-card {
  height: 92%;
  transform: translatex(25px) translatey(50px);
}


.about div img {
  display: inline-block;
  height: 275px;
}

#top-mains {
  position: fixed;
  height: 6rem;
  width: 100%;
  right: 0;
  top: 0;
  z-index: 999;
}

#left-my-card {
  transform: translatex(83px) translatey(67px);
  height: 397px;
  width: 281px;
  position: relative;
  left: -1px;
  padding-top: 0px !important;
  top: -1px;
}


#left-my .el-space--vertical {
  position: relative;
  top: 7%;
  transform: translatex(0px) translatey(0px);
}


#app footer {
  border-color: #9ad9df;
  border-style: solid;
  border-width: 1px;
  box-shadow: 0px 0px 26px 0px #aeb5f3;
  border-top-left-radius: 0px;
  border-top-right-radius: 50px;
  border-bottom-left-radius: 50px;
  border-bottom-right-radius: 0px;
}



#top-mains .el-header ul{
 background-color:#c6e2ff;
   border-top-left-radius:20px;
 border-top-right-radius:20px;
 border-bottom-left-radius:20px;
 border-bottom-right-radius:20px;
  box-shadow:-2px 0px 19px 1px #d1edc4;
  margin-top: 10px;
}


</style>





<script setup>
import {RouterLink, RouterView} from 'vue-router'
import HelloWorld from './components/HelloWorld.vue'
import { particles } from '../public/JS/backjs'
</script>

<template>

  <el-container id="top-mains">
    <el-header>
      <el-menu
          class="el-menu-demo"
          mode="horizontal"
      >
        <h1 style="padding-left: 20px;font-size: 20px">
          Exp1oit Blog</h1>

          <el-sub-menu index="2-4" id="login">
            <template #title>登录</template>
            <el-menu-item index="2-4-1">
              <a href="" style="text-decoration:none">注册</a>
            </el-menu-item>
          </el-sub-menu>

      </el-menu>
    </el-header>
  </el-container>

  <el-container id="left-my">
    <el-aside id="left-my-card" style="padding-top: 5%">
      <el-row>
        <el-card>
          <img
              src="https://shadow.elemecdn.com/app/element/hamburger.9cf7b091-55e9-11e9-a976-7f4d0b07eef6.png"
              class="image"
          />
          <div style="padding: 14px">
            <h1>Exp1oit</h1>
            <h1>一个混运维想转开发的小菜鸡</h1>
          </div>
          <el-divider/>
          <h1>本站技术栈</h1>
          <el-timeline>
            <el-timeline-item>
              Fastapi
            </el-timeline-item>
            <el-timeline-item>
              Celery
            </el-timeline-item>
            <el-timeline-item>
              Vue3
            </el-timeline-item>
          </el-timeline>
          <el-divider/>
        </el-card>
      </el-row>
    </el-aside>

    <el-container style="margin-top: 1%;height: 10%">
      <el-main id="maincare">
        <div class="about">
          <div class="common-layout">
            <el-container>
              <el-main>
                <div v-for="blog in data" :key="blog.BlogId">
                  <el-card shadow="hover" id="main-boxcard" class="box-card" style="margin-top: 10px">
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
          <el-space direction="vertical" style="margin-right: 10%">
            <el-card v-for="i in 2" :key="i" class="box-card" style="width: auto">
              <template #header>
                <div class="card-header">
                  <span>最多阅读文章</span>
                </div>
              </template>
            </el-card>

          </el-space>
          <el-divider/>
          <el-carousel iindicator-position="none">
            <el-carousel-item v-for="blog in data">
              <h3 text="2xl" justify="center"></h3>
              <img id="blog-img" :src="blog.BlogIntroductionPicture" alt="">
            </el-carousel-item>
          </el-carousel>
        </el-card>
      </el-container>
    </el-container>
  </el-container>
  <div id = "footer">
      <el-footer
      style="box-shadow:0 0 26px 0 #767697;background-image: linear-gradient(-225deg, #E3FDF5 0%, #FFE6FA 100%);">
    <el-row>
      <el-col :span="6">
        <el-statistic title="共计访问人数" :value="268500"/>
      </el-col>
    </el-row>

  </el-footer>
  </div>



  <div>
    <el-backtop :right="100" :bottom="100"/>
  </div>


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

#login {
  margin-left: auto;
}


#left-my-card {
  margin-left: 50px;
}


#left-my .el-space--vertical {
  position: relative;
  top: 7%;
  transform: translatex(0px) translatey(0px);
}






body {
  //background-image: linear-gradient(to right, #74ebd5 0%, #9face6 100%);
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB',
  'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
}


#left-my .el-container .el-container > .el-card {
  width: 364px;
}

#main-boxcard {
  border-radius: 30px; /* 设置圆角半径 */
}


.el-header {
  padding-left: 0;
  padding-right: 0;
}

.el-menu-demo {
  width: 100%;
}

#footer {
  padding-left: 0;
  padding-right: 0;
}

</style>





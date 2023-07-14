<script setup>
import { useRouter } from 'vue-router';
import { reactive, ref } from 'vue';
import axios from 'axios';
import { loadFull } from 'tsparticles';

const particlesInit = async (engine) => {
  await loadFull(engine);
};

const particlesLoaded = async (container) => {
  console.log("Particles container loaded", container);
};

const router = useRouter();
const data = reactive({
  data: []
});

const loading = ref(false);
const loadedCards = ref(4); // 初始加载的卡片数量

function getData() {
  axios.get('http://127.0.0.1:8000/blog/BlogIndex')
    .then(response => {
      data.data = response.data;
      console.log(data.data);
    })
    .catch(error => {
      console.error(error);
    });
}

getData();

const jumpFn = (id) => {
  console.log(id);
  router.push(`/blog/${id}`);
};

const loadMoreCards = () => {
  loading.value = true;
  setTimeout(() => {
    loadedCards.value += 3; // 每次加载3张卡片
    loading.value = false;
  }, 1000); // 模拟异步加载延迟
};
</script>

<template>

   <!--  背景开始-->
  <div id="app" style="opacity: 0.7;">
    <vue-particles
        id="tsparticles"
        :particlesInit="particlesInit"
        :particlesLoaded="particlesLoaded"
        url="http://foo.bar/particles.json"
    />

    <vue-particles
        id="tsparticles"
        :particlesInit="particlesInit"
        :particlesLoaded="particlesLoaded"
        :options="{
                    background: {
                        color: {
                            value: '#95d475'
                        }
                    },
                    fpsLimit: 120,
                    interactivity: {
                        events: {
                            onClick: {
                                enable: true,
                                mode: 'push'
                            },
                            onHover: {
                                enable: true,
                                mode: 'repulse'
                            },
                            resize: true
                        },
                        modes: {
                            bubble: {
                                distance: 400,
                                duration: 2,
                                opacity: 0.8,
                                size: 40
                            },
                            push: {
                                quantity: 4
                            },
                            repulse: {
                                distance: 200,
                                duration: 0.4
                            }
                        }
                    },
                    particles: {
                        color: {
                            value: '#ffffff'
                        },
                        links: {
                            color: '#ffffff',
                            distance: 150,
                            enable: true,
                            opacity: 0.5,
                            width: 1
                        },
                        collisions: {
                            enable: true
                        },
                        move: {
                            direction: 'none',
                            enable: true,
                            outMode: 'bounce',
                            random: false,
                            speed: 2,
                            straight: false
                        },
                        number: {
                            density: {
                                enable: true,
                                area: 800
                            },
                            value: 80
                        },
                        opacity: {
                            value: 0.5
                        },
                        shape: {
                            type: 'circle'
                        },
                        size: {
                            random: true,
                            value: 5
                        }
                    },
                    detectRetina: true
                }"
    />
  </div>

  <div class="index">
      <!--网站导航栏-->
  <el-container id="top-mains">
    <el-header>
      <el-menu
          class="el-menu-demo"
          mode="horizontal"
      >
        <h1 style="padding-left: 20px;font-size: 20px">
          Exp1oit Blog</h1>
        <div id="Search_input" class="search-container">
          <el-input
              v-model="input1"
              class="w-50 m-2"
              size="large"
              placeholder="搜索你感兴趣的文章"
              :prefix-icon="Search"

          />
        </div>

        <el-sub-menu index="2-4" id="login">
          <template #title>登录</template>
          <el-menu-item index="2-4-1">
            <a href="" style="text-decoration:none">注册</a>
          </el-menu-item>
        </el-sub-menu>

      </el-menu>
    </el-header>
  </el-container>
  <!--网站导航栏-->
  <!--个人介绍卡片-->
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
    <!--个人介绍卡片-->

    <!--    文章介绍卡片-->
    <el-container style="margin-top: 1%;height: 10%;z-index:9;">
      <el-main id="maincare">
        <div class="about">
          <div class="common-layout">
            <el-container>
              <el-main>
                <div v-for="(blog, index) in data.data.slice(0, loadedCards)" :key="blog.BlogId">
<!--                  <router-link :to="`/blog/${blog.BlogId}`">-->
                  <el-card v-loading="loading" shadow="hover" id="main-boxcard" class="box-card" style="margin-top: 10px;" @click="jumpFn(blog.BlogId)">
                    <div><h1 style="font-size: 25px;height: 20%" >{{ blog.title }} </h1>
                                          <el-container id="blog-img-container">
<!--                      <img id="blog-img" :src="blog.BlogIntroductionPicture" alt="">-->
                    </el-container>
                    </div>
                    <h1>{{ blog.content }} </h1>
                    <el-divider />
                    {{ blog.author}} {{ blog.created_at }}
                                <!-- 卡片内容 -->
                  </el-card>
<!--                  </router-link>-->
                </div>
              </el-main>
              <div><el-backtop :right="100" :bottom="100"/></div>
            </el-container>
          </div>
        </div>
    <div class="bt_container">
      <el-button type="primary" @click="loadMoreCards" v-if="!loading">查看更多</el-button>
      <el-button type="primary" disabled v-else>
        <i class="el-icon-loading"></i> 加载中...
      </el-button>
    </div>
      </el-main>
      <!--    文章介绍卡片-->

      <!--      右侧介绍卡片-->
      <el-container style="display: flex;
  flex-direction: column; height: 90%;">
        <el-card>
          <el-space direction="vertical" style="margin-right: 10%;width: 100%;">
            <el-card v-for="i in 2" :key="i" class="box-card">
              <template #header>
                <div class="card-header">
                  <span>最多阅读文章</span>
                </div>
              </template>
              <div v-for="o in 4" :key="o" class="text item">{{ '这个文章的测试标题为hahahahha ' + o }}</div>
            </el-card>
          </el-space>

          <el-divider/>

          <el-carousel iindicator-position="none">
            <el-carousel-item v-for="blog in data.data">
              <h3 text="2xl" justify="center"></h3>
              <img id="blog-img" :src="blog.BlogIntroductionPicture" alt="">
            </el-carousel-item>
          </el-carousel>
        </el-card>

          <el-card style="margin-top: 20px">
            文章分类
          </el-card>

        <el-card style="margin-top: 20px">
            资源链接
          </el-card>

        <el-card style="margin-top: 20px">
            文章标签
          </el-card>

        <el-card style="margin-top: 20px">
            网站统计
          </el-card>

      </el-container>

    </el-container>
  </el-container>
  <!--      右侧介绍卡片-->

  <!--  页面脚底卡片-->
  <div id="footer">
    <el-footer
        style="box-shadow:0 0 26px 0 #767697;background-image: linear-gradient(-225deg, #E3FDF5 0%, #FFE6FA 100%);">
      <el-row class="search-container">
        <el-col :span="6">
          <el-statistic title="共计访问人数" :value="268500"/>
        </el-col>
      </el-row>
    </el-footer>
  </div>
  <!--  页面脚底卡片-->
  </div>



</template>

<style>

.bt_container{
  display: flex;
  justify-content: center;
  align-items: center;
}

#left-my .el-container .el-container > .el-card {
  height: 92%;
  transform: translatex(25px) translatey(50px);
}

.about div img {
  display: inline-block;
  height: 275px;
}

#top-mains {
  opacity: 0.8;
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
//background-image: linear-gradient(to right, #74ebd5 0%, #9face6 100%); font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB',
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
  opacity: 0.8;
  position: relative;
  padding-left: 0;
  padding-right: 0;
}

#app {
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: -999; /* 设置一个较低的层叠顺序，以确保它在其他内容的下方 */
}

.search-container {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-left: 40px;
}

.el-card .el-card__body a {
  color: black;
  text-decoration: none;
}

#app div .index #left-my .el-container #maincare .about .common-layout .el-container .el-main{
 width: 100vh !important;
}

</style>
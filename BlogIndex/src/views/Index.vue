<script setup>
import {useRouter} from 'vue-router';
import {reactive, ref} from 'vue';
import axios from 'axios';
import {loadFull} from 'tsparticles';
import backApi from '../Api/backApi.js';
import 'element-plus/theme-chalk/display.css'

import { particles } from '@/components/particles/particles.js'
import { loadSlim } from "tsparticles-slim";

const particlesInit = async (engine) => {
  await loadFull(engine);
};

const particlesLoaded = async (container) => {
  console.log("Particles container loaded", container);
};

const input1 = ref('');

const router = useRouter();
const data = reactive({
  data: []
});

const loading = ref(false);
const loadedCards = ref(4); // 初始加载的卡片数量

function getData() {
  backApi.get('/blog/BlogIndex')
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
    loadedCards.value += 2; // 每次加载3张卡片
    loading.value = false;
  }, 1000); // 模拟异步加载延迟
};


</script>

<template>
    <div id="app">
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
                            value: '#73767a'
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
                        move: {
                            direction: 'none',
                            enable: true,
                            outMode: 'bounce',
                            random: false,
                            speed: 1,
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


  <el-container id="left-my" style="margin-top: 3%;">
      <el-header id="top-mains">
        <el-menu
            class="el-menu-demo"
            mode="horizontal">
          <h1 style="padding-left: 20px;font-size: 20px">
            Exp1oit Blog</h1>
          <div>
            <el-input
                v-model="input1"
                class="w-50 m-2"
                size="large"
                placeholder="Please Input"
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
      <!--个人介绍卡片-->
      <!--    文章介绍卡片-->


        <el-row :gutter="10" style="display: flex; justify-content: center;">
          <el-col style="margin-left: 20px" xs="10" :sm="10" :md="15" :lg="4" :xl="3" class="hidden-lg-and-down" >
            <el-card>
                  <img
                      src="https://shadow.elemecdn.com/app/element/hamburger.9cf7b091-55e9-11e9-a976-7f4d0b07eef6.png"
                      class="image"
                  />
                  <div style="padding: 14px">
                    <h1>Exp1oit</h1>
                    <h1></h1>
                  </div>
                  <el-divider/>
                  <h1>联系我</h1>
                  <el-container id="svg-icon">
                    <svg xmlns="http://www.w3.org/2000/svg" width="30" height="30" fill="currentColor"
                         class="bi bi-github" viewBox="0 0 16 16">
                      <path
                          d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.012 8.012 0 0 0 16 8c0-4.42-3.58-8-8-8z"/>
                    </svg>
                    <svg xmlns="http://www.w3.org/2000/svg" width="30" height="30" fill="currentColor"
                         class="bi bi-envelope" viewBox="0 0 16 16">
                      <path
                          d="M0 4a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V4Zm2-1a1 1 0 0 0-1 1v.217l7 4.2 7-4.2V4a1 1 0 0 0-1-1H2Zm13 2.383-4.708 2.825L15 11.105V5.383Zm-.034 6.876-5.64-3.471L8 9.583l-1.326-.795-5.64 3.47A1 1 0 0 0 2 13h12a1 1 0 0 0 .966-.741ZM1 11.105l4.708-2.897L1 5.383v5.722Z"/>
                    </svg>
                    <svg xmlns="http://www.w3.org/2000/svg" width="30" height="30" fill="currentColor"
                         class="bi bi-wechat" viewBox="0 0 16 16">
                      <path
                          d="M11.176 14.429c-2.665 0-4.826-1.8-4.826-4.018 0-2.22 2.159-4.02 4.824-4.02S16 8.191 16 10.411c0 1.21-.65 2.301-1.666 3.036a.324.324 0 0 0-.12.366l.218.81a.616.616 0 0 1 .029.117.166.166 0 0 1-.162.162.177.177 0 0 1-.092-.03l-1.057-.61a.519.519 0 0 0-.256-.074.509.509 0 0 0-.142.021 5.668 5.668 0 0 1-1.576.22ZM9.064 9.542a.647.647 0 1 0 .557-1 .645.645 0 0 0-.646.647.615.615 0 0 0 .09.353Zm3.232.001a.646.646 0 1 0 .546-1 .645.645 0 0 0-.644.644.627.627 0 0 0 .098.356Z"/>
                      <path
                          d="M0 6.826c0 1.455.781 2.765 2.001 3.656a.385.385 0 0 1 .143.439l-.161.6-.1.373a.499.499 0 0 0-.032.14.192.192 0 0 0 .193.193c.039 0 .077-.01.111-.029l1.268-.733a.622.622 0 0 1 .308-.088c.058 0 .116.009.171.025a6.83 6.83 0 0 0 1.625.26 4.45 4.45 0 0 1-.177-1.251c0-2.936 2.785-5.02 5.824-5.02.05 0 .1 0 .15.002C10.587 3.429 8.392 2 5.796 2 2.596 2 0 4.16 0 6.826Zm4.632-1.555a.77.77 0 1 1-1.54 0 .77.77 0 0 1 1.54 0Zm3.875 0a.77.77 0 1 1-1.54 0 .77.77 0 0 1 1.54 0Z"/>
                    </svg>
                  </el-container>

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
            </el-col>




          <el-col  :xs="24" :sm="24" :md="24" :lg="20" :xl="17">
          <el-main id="maincare">
              <div class="about">
                  <el-container v-for="(blog, index) in data.data.slice(0, loadedCards)" :key="blog.BlogId">
                    <el-main>
                      <!--                  <router-link :to="`/blog/${blog.BlogId}`">-->
                      <el-card v-loading="loading" shadow="hover" id="main-boxcard" class="box-card"
                               @click="jumpFn(blog.BlogId)">
                        <el-container>
                          <el-row :gutter="10">
                          <el-aside>
                            <img :src="blog.BlogIntroductionPicture" alt="图像描述" id="blog-image">
                          </el-aside>
                          <el-main>
                              <h1 style="font-size: 25px;height: 20%">{{ blog.title }}</h1>
                              <el-container>
                                {{ blog.author }} {{ blog.created_at }}
                              </el-container>
                          </el-main>
                          </el-row>
                        </el-container>
                        <!-- 卡片内容 -->
                      </el-card>
                      <!--                  </router-link>-->
                    </el-main>
                    <div>
                      <el-backtop :right="100" :bottom="100"/>
                    </div>
                  </el-container>
              </div>
              <div class="bt_container" style="display: flex; justify-content: center;">
                <el-button type="primary" @click="loadMoreCards" v-if="!loading">查看更多</el-button>
                <el-button type="primary" disabled v-else>
                  <i class="el-icon-loading"></i> 加载中...
                </el-button>
              </div>
          </el-main>
            </el-col>


          <el-col :xs="24" :sm="24" :md="24" :lg="4" :xl="3">
            <el-card>
                <el-space direction="vertical">
                    <template #header>
                      <div class="card-header">
                        <span>最多阅读文章</span>
                      </div>
                    </template>
                    <div v-for="o in 4" :key="o" class="text item">{{ '这个文章的测试标题为hahahahha ' + o }}</div>
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
                      </el-col>
        </el-row>



      <!--    文章介绍卡片-->
      <el-footer
          style="box-shadow:0 0 26px 0 #767697;background-image: linear-gradient(-225deg, #E3FDF5 0%, #FFE6FA 100%); margin-top: 20px">
        <el-row class="search-container">
          <el-col :span="6">
            <el-statistic title="共计访问人数" :value="268500"/>
          </el-col>
        </el-row>
      </el-footer>
    </el-container>

</template>

<style>




#main-boxcard {
  border-top-left-radius: 0px;
  border-top-right-radius: 50px;
  border-bottom-left-radius: 50px;
  border-bottom-right-radius: 0px;
}

.about div img {
  height: 200px;
  margin-left: 50px;
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

.el-header {
  padding-left: 0;
  padding-right: 0;
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


#blog-image{
 display:inline-block;
 width:232px;
}

#svg-icon svg {
  margin-left: 30px;
}

</style>

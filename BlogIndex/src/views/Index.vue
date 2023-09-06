<script setup xmlns="http://www.w3.org/1999/html">
import {useRouter} from 'vue-router';
import {reactive, ref, onMounted, onBeforeUnmount} from 'vue';

import {loadFull} from 'tsparticles';
import backApi from '../Api/backApi.js';
import 'element-plus/theme-chalk/display.css'

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

const pageSize = 4;
let currentPage = 1;
const loadedCards = ref(pageSize);

const loadData = async (page) => {
  try {

    const response = await backApi.get(`/blog/BlogIndex?initialLoad=false&page=${page}&pageSize=${pageSize}`);
    if (response.data.length > 0) {
      data.data.push(...response.data);
      loading.value = true
    }
  } catch (error) {
    console.error(error);
  }
};

onMounted(() => {
  loadData(currentPage.value);
});


const loadMoreCards = () => {
  currentPage++;
  loadedCards.value = pageSize * currentPage;
  loadData(currentPage);
};


getData();

const jumpFn = (id) => {
  console.log(id);
  router.push(`/blog/${id}`);
};


const showFloatingWindow = ref(false);


const toggleFloatingWindow = () => {
  showFloatingWindow.value = !showFloatingWindow.value;
};

const closeFloatingWindow = () => {
  showFloatingWindow.value = false;
};

const handleGlobalClick = (event) => {
  if (!event.target.closest('.floating-window')) {
    closeFloatingWindow();
  }
};

onMounted(() => {
  document.addEventListener('click', handleGlobalClick);
});

</script>

<template>
  <div id="app">
    <div class="particles-container" style="z-index: -1;">
      <vue-particles
          id="tsparticles"
          :particlesInit="particlesInit"
          :particlesLoaded="particlesLoaded"


      />
      <vue-particles
          id="tsparticles"
          :particlesInit="particlesInit"
          :particlesLoaded="particlesLoaded"
          :options="{
                    background: {
                        color: {
                            value: '#C0C4CC'
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
  </div>


  <el-container id="left-my" style="margin-top: 3%;">
    <el-header id="top-mains">
      <el-menu
          class="el-menu-demo"
          mode="horizontal">
        <h1 style="padding-left: 20px;font-size: 20px">
          <router-link to="/blog/" style="text-decoration: none;">Exp1oit Blog</router-link>
        </h1>
        <div class="search-container">
          <el-button
              v-model="input1"
              class="w-50 m-2"
              size="large"
              placeholder="请输入"
              :prefix-icon="Search"
              @click.stop="toggleFloatingWindow"
          >搜索你感兴趣的文章
          </el-button>
          <!-- 浮动窗口 -->
<transition  name="el-fade-in-linear">
      <div v-show=showFloatingWindow class="floating-window"  :class="{ show: showFloatingWindow }" @mouseleave="closeFloatingWindow">
        <el-input v-model="input1" placeholder="请输入" clearable />
        <el-button @click="searchArticles">搜索</el-button>
      </div>
</transition>
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
      <el-col style="margin-left: 20px" xs="10" :sm="10" :md="15" :lg="4" :xl="3" class="hidden-lg-and-down">
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
          <h1>本站技术以及框架</h1>
          <el-timeline>
            <el-timeline-item>
              Fastapi
            </el-timeline-item>
            <el-timeline-item>
              Celery
            </el-timeline-item>
            <el-timeline-item>
              Vue3+Vue2
            </el-timeline-item>
            <el-timeline-item>
              vue-element-admin
            </el-timeline-item>
          </el-timeline>
          <el-divider/>
        </el-card>
      </el-col>


      <el-col :xs="24" :sm="24" :md="24" :lg="20" :xl="17">
        <el-main id="maincare">
          <div class="about">
            <el-container v-for="(blog, index) in data.data.slice(0, loadedCards)" :key="blog.BlogId">
              <el-main>
                <!--                  <router-link :to="`/blog/${blog.BlogId}`">-->

                <transition  name="el-fade-in-linear">
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
                  </transition>
                <!--                  </router-link>-->
              </el-main>
              <div>
                <el-backtop :right="100" :bottom="100"/>
              </div>
            </el-container>
          </div>
          <div class="bt_container" style="display: flex; justify-content: center;">
            <el-button
                type="primary"
                @click="loadMoreCards"
                v-if="data.data.length % pageSize === 0 && !loading">
              查看更多
            </el-button>
            <p v-else>没有更多文章可以查看了</p>
          </div>
        </el-main>
      </el-col>


      <el-col :xs="24" :sm="24" :md="24" :lg="4" :xl="3" id="left2" >
        <div style="position: sticky; top: 80px;">
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
          </div>
      </el-col>

    </el-row>


    <!--    文章介绍卡片-->
    <el-footer>
      <div id="footer">
        <el-row class="footer-content">
          <el-col :span="6">
            <h3>关于本站</h3>
            <p>欢迎来到我的博客，这里分享了各种有趣的技术和知识。</p>
          </el-col>
          <el-col :span="6">
            <h3>联系我们</h3>
            <p>Email: example@example.com</p>
            <p>社交媒体: <a href="#">Twitter</a>, <a href="#">Facebook</a></p>
          </el-col>
          <el-col :span="6">
            <h3>文章分类</h3>
            <ul>
              <li><a href="#">技术教程</a></li>
              <li><a href="#">编程技巧</a></li>
              <li><a href="#">设计与创意</a></li>
            </ul>
          </el-col>
          <el-col :span="6">
            <h3>友情链接</h3>
            <ul>
              <li><a href="#">友情链接1</a></li>
              <li><a href="#">友情链接2</a></li>
              <li><a href="#">友情链接3</a></li>
            </ul>
          </el-col>
        </el-row>
        <el-row class="footer-bottom">
          <el-col :span="12">
            <p>&copy; 2023 My Blog. All Rights Reserved.</p>
          </el-col>
          <el-col :span="12">
            <p>建站时间: 2022年1月</p>
          </el-col>
        </el-row>
      </div>
    </el-footer>
  </el-container>

</template>

<style>

.app{
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB',
  'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
}

.el-footer {
  padding-top: 100px;
  display: flex;
  height: 4vh;
  width: 100%;
  align-items: center;
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



.el-header {
  padding-left: 0;
  padding-right: 0;
}



.el-card .el-card__body a {
  color: black;
  text-decoration: none;
}


#blog-image {
  display: inline-block;
  width: 232px;
}

#svg-icon svg {
  margin-left: 30px;
}


#footer {
  position: absolute;
  left: 0;
  right: 0;
  box-shadow: 0 0 26px 0 #767697;
  background-image: linear-gradient(-225deg, #E3FDF5 0%, #FFE6FA 100%);
  margin-top: 20px;
  width: 100%; /* 将底部栏宽度设置为100% */
  z-index: 1; /* 设置一个适当的 z-index 值 */

}

.footer-content {
  max-width: 100%; /* 将内容区域的最大宽度设置为100% */
  margin: 0 auto;
  padding: 0 20px; /* 添加左右内边距，使内容区域不至于过于靠边 */
}

.footer-content h3 {
  font-size: 18px;
  margin-bottom: 10px;
}

.footer-content p, .footer-content ul {
  font-size: 14px;
  line-height: 1.6;
}

.footer-content a {
  color: #333;
  text-decoration: none;
}

.footer-bottom {
  max-width: 100%; /* 将内容区域的最大宽度设置为100% */
  text-align: center;
  font-size: 12px;
  color: #95d475;
  border-top: 3px solid #79bbff;
  padding-top: 20px;
}


.particles-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}


.floating-window {
  position: fixed;
  top: 50%;
  left: 50%;
  width: 20%;
  height: 20%;
  transform: translate(-50%, -50%);
  background-color: white;
  border: 1px solid #ccc;
  padding: 10px;
  display: none;
  z-index: 9999;
}

.floating-window.show {
  display: block; /* 当 "showFloatingWindow" 为 true 时显示 */
}
</style>

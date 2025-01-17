<script setup>
import {useRouter} from 'vue-router';
import {reactive, ref, onMounted, onBeforeUnmount, watch, onUnmounted, computed} from 'vue';
import TypeIt from 'typeit'
import 'element-plus/theme-chalk/display.css'
import {useStore} from "vuex";
import 'animate.css';
import WOW from "wow.js";
import { GoogleUVPV,fetchBlogIndex } from "@/api/Blog/blogapig"

//自动布局修改适配手机端平板端屏幕
const useXlLayout = () => {
  const xlLayout = ref(window.innerWidth <= 1200);

  const checkLayout = () => {
    xlLayout.value = window.innerWidth <= 1200;
  };

  onMounted(() => {
    window.addEventListener('resize', checkLayout);
  });

  onBeforeUnmount(() => {
    window.removeEventListener('resize', checkLayout);
  });

  return {
    xlLayout,
  };
};

const {xlLayout} = useXlLayout();


const input1 = ref('');
const text = ref(null)
const router = useRouter();
// 定义 ref 变量存储 UV 和 PV 数据
const totalUV = ref(0);
const totalPV = ref(0);
const data = reactive({
  data: []
});


// 创建函数来获取 UV 和 PV 数据
const fetchUvPvData = async () => {
  try {
    const response = await GoogleUVPV({});
    if (response.data.code === 20000) {
      totalUV.value = response.data.data['UV'];
      totalPV.value = response.data.data['PV'];
    }
  } catch (error) {
    console.error('Error fetching UV/PV data:', error);
  }
};

const pageSize = 4;
let currentPage = 1;
const loadedCards = ref(pageSize);

const loadData = async (page = 0) => {
  try {
    // 调用 fetchBlogIndex 函数并传入参数
    const response = await fetchBlogIndex({ page, pageSize });

    if (response.data.length > 0) {
      response.data.forEach(blog => {
        // 判断博客是否已加载，根据 BlogID 判断
        const isBlogLoaded = data.data.some(loadedBlog => loadedBlog.BlogId === blog.BlogId);

        if (!isBlogLoaded) {
          // 如果博客未加载，则将其推入数据数组
          data.data.push(blog);
          // 可选：如果你想要跟踪已加载的 BlogID，可以将其添加到集合中
          // loadedBlogIds.value.add(blog.BlogId);
        }
      });
    }
  } catch (error) {
    console.error(error);
  }
};

onMounted(() => {
  const wow = new WOW({
    boxClass: 'wow',
    animateClass: 'animated',
    offset: 0,
    mobile: true,
    live: true,
    scrollContainer: null,
    resetAnimation: true,
    callback: function (box) {
      if (box.classList.contains('slideInLeft')) {
        box.style.opacity = '1'; // 设置透明度为1，淡入
      }
    },
  })
  wow.init();
  loadData(currentPage.value);
});


const loadMoreCards = () => {
  currentPage++;
  loadedCards.value = pageSize * currentPage;
  loadData(currentPage);
};




const showFloatingWindow = ref(false);


const toggleFloatingWindow = () => {
  showFloatingWindow.value = !showFloatingWindow.value;
};


const VerseGetting = async () => {
  try {
    const response = await fetch('https://v1.jinrishici.com/rensheng/shiguang');
    const data = await response.json();

    return data.content
  } catch (error) {
    console.error('Error fetching data:', error);
  }
};


onMounted(async () => {
  await fetchUvPvData();
  const content = await VerseGetting();
  new (TypeIt)(text.value, {
    strings: [content],
    cursorChar: "<span class='cursorChar'>|<span>",//用于光标的字符。HTML也可以
    speed: 100,
    lifeLike: true,// 使打字速度不规则
    cursor: true,//在字符串末尾显示闪烁的光标
    breakLines: false,// 控制是将多个字符串打印在彼此之上，还是删除这些字符串并相互替换
    loop: false,//是否循环
  }).go()
})

const scrollY = ref(0);
const headerBackgroundColor = ref('rgba(0, 0, 0, 0)'); // 初始化背景透明度为0
const isHeaderHidden = ref(false);
const scrollDirection = ref('down'); // 初始化滚动方向为向下

onMounted(() => {
  window.addEventListener('scroll', handleScroll);
});

onBeforeUnmount(() => {
  window.removeEventListener('scroll', handleScroll);
});

function handleScroll() {
  const newScrollY = window.scrollY;

  // 根据滚动方向控制标题栏显示和隐藏
  if (newScrollY > scrollY.value) {
    // 向下滚动
    scrollDirection.value = 'down';
  } else {
    // 向上滚动
    scrollDirection.value = 'up';
  }

  scrollY.value = newScrollY;
}

// 监听滚动方向的变化
watch(scrollDirection, (newDirection, oldDirection) => {
  if (newDirection === 'up') {
    // 向上滚动时显示标题栏
    isHeaderHidden.value = false;

  } else {
    // 向下滚动时隐藏标题栏
    isHeaderHidden.value = true;
  }
});
const siteCreationTime = ref({value: new Date('2023-10-04')});
const timeElapsed = ref({
  years: 0,
  months: 0,
  days: 0,
  hours: 0,
  minutes: 0,
  seconds: 0,
});

const updateSiteCreationTime = () => {
  const startTime = siteCreationTime.value.value;
  const currentTime = new Date();
  let timeDiff = currentTime - startTime;

  // 计算时间差的各个时间单位
  const millisecondsPerSecond = 1000;
  const millisecondsPerMinute = 60 * millisecondsPerSecond;
  const millisecondsPerHour = 60 * millisecondsPerMinute;
  const millisecondsPerDay = 24 * millisecondsPerHour;
  const millisecondsPerMonth = 30 * millisecondsPerDay;
  const millisecondsPerYear = 365 * millisecondsPerDay;

  timeElapsed.value.years = Math.floor(timeDiff / millisecondsPerYear);
  timeDiff -= timeElapsed.value.years * millisecondsPerYear;

  timeElapsed.value.months = Math.floor(timeDiff / millisecondsPerMonth);
  timeDiff -= timeElapsed.value.months * millisecondsPerMonth;

  timeElapsed.value.days = Math.floor(timeDiff / millisecondsPerDay);
  timeDiff -= timeElapsed.value.days * millisecondsPerDay;

  timeElapsed.value.hours = Math.floor(timeDiff / millisecondsPerHour);
  timeDiff -= timeElapsed.value.hours * millisecondsPerHour;

  timeElapsed.value.minutes = Math.floor(timeDiff / millisecondsPerMinute);
  timeDiff -= timeElapsed.value.minutes * millisecondsPerMinute;

  timeElapsed.value.seconds = Math.floor(timeDiff / millisecondsPerSecond);
};

// 使用setInterval每秒更新建站时间
let timerId;
onMounted(() => {
  updateSiteCreationTime();

  timerId = setInterval(updateSiteCreationTime, 1000);
});

onUnmounted(() => {
  clearInterval(timerId); // 组件销毁时清除定时器
});

const store = useStore();
const usernames = computed(() => store.getters.getUsername);
const tokens = computed(() => store.getters.getToken);
const isLoggedIn = computed(() => !!usernames.value);

// 跳转到注册页面
const redirectToRegister = () => {
  // 在这里编写跳转逻辑
  router.push('/register');
};

// 跳转到用户个人资料页面
const redirectToUserProfile = () => {
  // 在这里编写跳转逻辑
  router.push('/user-profile');
};

const sendEmail = () => {
  // 替换以下邮箱地址为你的目标邮箱
  const emailAddress = 'watch.dog@qq.com';
  // 使用window.location.href来触发mailto链接
  window.location.href = `mailto:${emailAddress}`;
};

</script>

<template>

  <div class="background-container" :style="{ transform: `translateY(-${scrollY}px)` }" style="z-index: 3">
    <div class="background-image"></div>
    <h1 style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);" ref="text" class="msg"></h1>
  </div>


  <el-container id="left-my" style="margin-top: 3%;">

    <el-header id="top-mains" :class="{ 'hidden': isHeaderHidden }"
               :style="{ 'background-color': headerBackgroundColor }" style="padding-right: 0;padding-left: 0">
      <transition name="fade">
        <el-menu
            class="el-menu-demo"
            mode="horizontal">

          <el-menu-item index="1">
            <h1>
              <router-link to="/" style="text-decoration: none;">Exp1oit Blog</router-link>
            </h1>
          </el-menu-item>



            <el-autocomplete style="margin-right: auto"
                v-model="state"
                :fetch-suggestions="querySearchAsync"
                placeholder="搜索你感兴趣的"
                @select="handleSelect"
            />

          <el-menu-item index="3" >
            <router-link to="/about-me" style="text-decoration: none;">关于我</router-link>
          </el-menu-item>


          <el-sub-menu index="4">
            <template #title>
              {{ isLoggedIn ? `你好：${usernames}` : '你还未登录' }}
            </template>
            <router-link style="text-decoration:none" to="/user-profile">
              <el-menu-item v-if="isLoggedIn" index="2-4-2">
                个人资料
              </el-menu-item>
            </router-link>
            <router-link style="text-decoration:none" to="/reg">
              <el-menu-item index="2-4-1">
                注册
              </el-menu-item>
            </router-link>
            <router-link style="text-decoration:none" to="/login">
              <el-menu-item index="2-4-1">登录
              </el-menu-item>
            </router-link>
          </el-sub-menu>

        </el-menu>
      </transition>
    </el-header>

    <!--个人介绍卡片-->
    <!--    文章介绍卡片-->

    <el-row :gutter="10" style=" justify-content: center; max-width: 100% ">
      <el-col xs="24" :sm="24" :md="6" :lg="4" :xl="3" class="hidden-lg-and-down;">
        <el-card class="wow animate__bounce bounceInLeft box-card" data-wow-duration="2s">
          <div style="padding: 14px">
            <h1>Exp1oit</h1>
            <h1></h1>
          </div>
          <el-divider/>
          <h4>联系我</h4>
          <el-container id="svg-icon">
            <a href="https://github.com/Eitsxiaozhai" target="_blank" rel="noopener noreferrer">
              <svg xmlns="http://www.w3.org/2000/svg" width="30" height="30" fill="currentColor"
                   class="bi bi-github" viewBox="0 0 16 16">
                <path
                    d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.012 8.012 0 0 0 16 8c0-4.42-3.58-8-8-8z"/>
              </svg>
            </a>
            <svg @click="sendEmail" xmlns="http://www.w3.org/2000/svg" width="30" height="30" fill="currentColor"
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
          <h4>本站技术以及框架</h4>
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
          </el-timeline>
          <el-divider/>
        </el-card>

        <el-card style="margin-top: 20px; position: sticky; top: 62px;">
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
            <el-carousel-item v-for="blog in data.data" :key="blog.BlogId">
              <h3 text="2xl" justify="center"></h3>
              <img id="blog-img" :src="blog.BlogIntroductionPicture" alt="">
            </el-carousel-item>
          </el-carousel>
        </el-card>
      </el-col>

      <transition name="el-fade-in-fast">

        <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="10" class="maincaretest">
          <div class="content-container">

            <el-main id="maincare">
              <div class="about">

                <el-container v-for="(blog) in data.data" :key="blog.BlogId">
                  <el-main>
                    <keep-alive>
                      <transition name="el-fade-in-linear">
                        <router-link target="_blank" style="text-decoration: none" :to="`/blog/${blog.BlogId}`">
                          <!-- 使用条件判断选择布局 -->
                          <template v-if="xlLayout ">
                            <el-card class="wow animate__bounce bounceInDown box-card" data-wow-duration="2s"
                                     shadow="hover" id="main-boxcard"
                                     style="display: flex; flex-direction: column; height: 99%;">
                              <img :src="blog.BlogIntroductionPicture" alt="图像描述" id="blog-image"
                                   style="flex: 1 0 auto;">

                              <div style="flex: 0 0 auto; padding: 10px;">
                                <h1 style="font-size: 25px;">{{ blog.title }}</h1>
                                <p>作者:{{ blog.author }}</p>
                                <p>发布日期:{{ blog.created_at }}</p>

                              </div>
                              <el-tag v-for="(tag, index) in blog.tag"
                                      :key="index" type="primary"> {{ tag }}
                              </el-tag>
                            </el-card>

                          </template>
                          <template v-else>
                            <!-- 使用你的布局 -->
                            <el-card shadow="hover" id="main-boxcard" class="wow animate__bounce bounceInDown box-card"
                                     data-wow-duration="2s">
                              <el-container>
                                <img :src="blog.BlogIntroductionPicture" alt="图像描述" id="blog-image">
                                <el-main>
                                  <h1 style="font-size: 25px;">{{ blog.title }}</h1>
                                  <p>作者:{{ blog.author }}</p>
                                  <p>发布日期:{{ blog.created_at }}</p>
                                </el-main>
                              </el-container>
                              <el-tag v-for="(tag, index) in blog.tag"
                                      :key="index" type="primary"> {{ tag }}
                              </el-tag>
                            </el-card>
                          </template>
                        </router-link>
                      </transition>
                    </keep-alive>
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
          </div>
        </el-col>

      </transition>


      <el-col :xs="24" :sm="24" :md="6" :lg="5" :xl="3" id="left2">
        <div style="position: sticky; top: 62px;">

          <el-card class="wow animate__bounce animate__rollIn box-card" data-wow-duration="2s" style="margin-top: 20px">
            文章分类

          </el-card>

          <el-card class="wow animate__bounce animate__rollIn box-card" data-wow-duration="2s" style="margin-top: 20px">
            资源链接
          </el-card>

          <el-card class="wow animate__bounce animate__rollIn box-card" data-wow-duration="2s" style="margin-top: 20px">
            文章标签
            <div class="flex gap-5">
              <el-tag type="primary">Tag 1</el-tag>
              <el-tag type="success">Tag 2</el-tag>
              <el-tag type="info">Tag 3</el-tag>
              <el-tag type="warning">Tag 4</el-tag>
              <el-tag type="danger">Tag 5</el-tag>
            </div>
          </el-card>

          <el-card class="wow animate__bounce animate__rollIn box-card" data-wow-duration="2s" style="margin-top: 20px">

            <el-row>
              <el-col :span="12">
                <el-statistic title="独立访客数" :value="totalUV"/>
              </el-col>
              <el-col :span="12">
                <el-statistic title="页面浏览量" :value="totalPV"/>
              </el-col>
            </el-row>
          </el-card>
        </div>
      </el-col>
      <!--    文章介绍卡片-->
    </el-row>

    <el-footer style="margin-top: 10%;">
      <div id="footer">
        <el-row class="footer-content">
          <el-col :span="6">
            <h4>联系我</h4>
            <p>Email: watch.dog@qq.com</p>
          </el-col>
        </el-row>
        <el-row class="footer-bottom">
          <el-col :span="12">
            <p>&copy; 2023 My Blog. All Rights Reserved.</p>
          </el-col>
          <el-col :span="12">
            <p>
              建站时间:
              {{ timeElapsed.years }}年
              {{ timeElapsed.months }}月
              {{ timeElapsed.days }}天
              {{ timeElapsed.hours }}小时
              {{ timeElapsed.minutes }}分钟
              {{ timeElapsed.seconds }}秒
            </p>
          </el-col>
        </el-row>
      </div>
    </el-footer>

  </el-container>

</template>


<style>

#app .background-container h1 {
  font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen-Sans, Ubuntu, Cantarell, Helvetica Neue, sans-serif;
  color: #eeeeee;
  font-weight: 300;
}

/* 脚注内容的样式 */
.footer-content {
  max-width: 1200px; /* 设置最大宽度，根据需要调整 */
  margin: 0 auto; /* 居中对齐 */
}

.footer-content h3 {
  font-size: 24px; /* 设置标题字体大小 */
}

.footer-content p {
  font-size: 16px; /* 设置段落字体大小 */
  margin: 5px 0; /* 减小段落上下边距 */
}

/* 链接的样式 */
.footer-content a {
  color: #fff; /* 设置链接颜色 */
  text-decoration: underline; /* 添加下划线 */
  margin-right: 10px; /* 设置链接右侧间距 */
}

/* 脚注底部样式 */
.footer-bottom {
  max-width: 1200px; /* 设置最大宽度，根据需要调整 */
  margin: 10px auto 0; /* 减小上外边距 */
  font-size: 14px; /* 设置字体大小 */
  text-align: center; /* 文本居中对齐 */
}

/* 版权信息样式 */
.footer-bottom p {
  margin: 5px 0; /* 设置段落上下边距 */
}

/* 建站时间样式 */
.footer-bottom p:last-child {
  margin-top: 10px; /* 设置最后一个段落的上外边距 */
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
  z-index: 999;
}





.el-header {
  padding-left: 0;
  padding-right: 0;
}


.el-card .el-card__body a {
  color: black;
  text-decoration: none;
}

body {
  background: rgb(233, 233, 235);
}

#blog-image {
  display: inline-block;
  width: 232px;
}

#svg-icon svg {
  margin-left: 30px;
}


#footer {
  background: #79bbff;
  font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen-Sans, Ubuntu, Cantarell, Helvetica Neue, sans-serif;
  color: #fff; /* 设置文本颜色 */
  padding: 10px 0; /* 减小上下边距 */
  position: absolute;
  left: 0;
  right: 0;
  box-shadow: #a0cfff 0px 0px 150px;
}


.floating-window {
  position: fixed;
  top: 50%;
  left: 50%;
  width: 20%;
  height: 20%;
  transform: translate(-50%, -50%);
  background-color: rgba(255, 255, 255, 0.84);
  border: 1px solid rgba(204, 204, 204, 0.35);
  padding: 10px;
  display: none;
  z-index: 9999;
}

.floating-window.show {
  display: block; /* 当 "showFloatingWindow" 为 true 时显示 */
}


.background-container {
  position: relative;
  margin-left: 0;
  margin-right: 0;
  width: 100%;
  height: 100vh; /* 设置容器高度为视口高度 */
  overflow: hidden; /* 隐藏溢出的内容 */
  z-index: -9999;
}

.background-image {
  /* 背景图片样式，替换为您的背景图片样式 */
  background-image: url("https://api.vvhan.com/api/bing?rand=sj");
  background-size: cover;
  width: 100%;
  height: 100%;
  transition: transform 10s ease; /* 添加过渡效果 */
}

.hidden {
  display: none;
}

.el-menu--horizontal > .el-menu-item:nth-child(1) {
  margin-right: auto;
}
</style>

<style src="wow.js/css/libs/animate.css"></style>
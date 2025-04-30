<script setup>
import {useRouter} from 'vue-router';
import {reactive, ref, onMounted, onBeforeUnmount, watch, onUnmounted, computed, watchEffect} from 'vue';
import TypeIt from 'typeit'
import 'element-plus/theme-chalk/display.css'
import {useStore} from "vuex";
import 'animate.css';
import WOW from "wow.js";
import '@/assets/css/IndexPage.css';
import {GoogleUVPV, fetchBlogIndex, searchBlogs, getBingWallpaper} from "@/api/Blog/blogapig"
import {debounce} from "lodash";
import {Moon, Sunny, ArrowDownBold, User, Calendar} from "@element-plus/icons-vue";

// 响应式状态
const isDark = ref(false)

// 初始化时检查本地存储和系统偏好
const initializeTheme = () => {
  const savedTheme = localStorage.getItem('element-plus-theme');

  // 优先使用手动保存的主题
  if (savedTheme) {
    isDark.value = savedTheme === 'dark';
  } else {
    // 自动根据时间设置 (18:00-6:00 为深色模式)
    const currentHour = new Date().getHours();
    isDark.value = currentHour >= 18 || currentHour < 6;
  }

  toggleDarkMode(isDark.value);
};


// 切换暗黑模式
const toggleDarkMode = (dark) => {
  const html = document.documentElement
  dark ? html.classList.add('dark') : html.classList.remove('dark')
  localStorage.setItem('element-plus-theme', dark ? 'dark' : 'light')
}

onMounted(() => {
  initializeTheme();

  // 每小时检查一次时间变化
  const timeCheckTimer = setInterval(initializeTheme, 60 * 60 * 1000);

  // 添加 visibilitychange 监听
  const handleVisibilityChange = () => {
    if (!document.hidden) initializeTheme();
  };

  document.addEventListener('visibilitychange', handleVisibilityChange);

  onBeforeUnmount(() => {
    clearInterval(timeCheckTimer);
    document.removeEventListener('visibilitychange', handleVisibilityChange);
  });
});


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
  data: [],
  loadedIds: new Set() // 用于跟踪已加载的博客ID
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

// 动态页面大小设置
const getPageSize = () => {
  const width = window.innerWidth;
  if (width > 1200) {
    return 12; // 大屏幕显示12个
  } else if (width > 768) {
    return 8;  // 中等屏幕显示8个
  } else {
    return 4;  // 小屏幕显示4个
  }
};

const pageSize = ref(getPageSize());
let currentPage = 1;
const loadedCards = ref(pageSize.value);
const loading = ref(false);
const error = ref(null);

const loadData = async (page = 0) => {
  loading.value = true;
  error.value = null;
  try {
    const response = await fetchBlogIndex({page, pageSize: pageSize.value});
    if (response.data && response.data.length > 0) {
      // 过滤掉已加载的博客
      const newBlogs = response.data.filter(blog => !data.loadedIds.has(blog.BlogId));
      
      // 将新博客添加到数据和已加载ID集合中
      newBlogs.forEach(blog => {
        data.data.push(blog);
        data.loadedIds.add(blog.BlogId);
      });

      // 如果没有新数据，说明已经加载完所有数据
      if (newBlogs.length === 0) {
        loadedCards.value = data.data.length;
      }
    }
  } catch (err) {
    error.value = '加载数据失败，请稍后重试';
    console.error(err);
  } finally {
    loading.value = false;
  }
};

const loadMoreCards = () => {
  // 只有当还有更多数据可加载时才增加页码
  if (data.data.length >= loadedCards.value) {
    currentPage++;
    loadedCards.value = pageSize.value * currentPage;
    loadData(currentPage);
  }
};

// 重置数据
const resetData = () => {
  data.data = [];
  data.loadedIds.clear();
  currentPage = 1;
  loadedCards.value = pageSize.value;
};

// 监听窗口大小变化，动态调整页面大小
const handleResize = () => {
  const newPageSize = getPageSize();
  if (newPageSize !== pageSize.value) {
    pageSize.value = newPageSize;
    // 如果当前加载的数量小于新的页面大小，则加载更多
    if (loadedCards.value < pageSize.value) {
      loadMoreCards();
    }
  }
};

onMounted(() => {
  // 初始化 WOW 动画
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
        box.style.opacity = '1';
      }
    },
  });
  wow.init();

  // 重置数据并加载
  resetData();
  loadData(currentPage);
  
  // 添加窗口大小变化监听
  window.addEventListener('resize', handleResize);
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize);
});

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


const sendEmail = () => {
  // 替换以下邮箱地址为你的目标邮箱
  const emailAddress = 'watch.dog@qq.com';
  // 使用window.location.href来触发mailto链接
  window.location.href = `mailto:${emailAddress}`;
};

const state = ref(''); // 用于绑定输入框的值
// 提供搜索建议的函数
const querySearchAsync = async (queryString, cb) => {
  if (queryString.trim() === '') {
    cb([]); // 如果输入为空，返回空数组
    return;
  }

  try {
    const response = await searchBlogs(queryString); // 调用后端 API
    const suggestions = response.data || []; // 调整根据实际响应格式
    cb(suggestions.map(blog => ({
      value: blog.title, // 回显的值
      id: blog.BlogId,       // 可以附加其他数据
    })));
  } catch (error) {
    console.error('获取建议失败:', error);
    cb([]); // 出现错误时返回空数组
  }
};

// 创建防抖函数，设置延迟时间为 300 毫秒
debounce(querySearchAsync, 300);

// 处理用户选择
const handleSelect = (item) => {
  window.location.href = `https://blog.exploit-db.xyz/blog/${item.id}`; // 跳转到该 URL
};

// 添加壁纸相关的响应式变量
const backgroundImage = ref('');

// 获取Bing壁纸
const fetchBingWallpaper = async () => {
  try {
    const response = await getBingWallpaper(true); // 随机获取一张壁纸
    if (response.data.code === 20000) {
      backgroundImage.value = response.data.data.url;
      // 预加载图片
      const img = new Image();
      img.src = response.data.data.url;
      img.onload = () => {
        // 图片加载完成后更新背景
        document.querySelector('.background-image').style.backgroundImage = `url(${response.data.data.url})`;
      };
    }
  } catch (error) {
    console.error('获取壁纸失败:', error);
  }
};

// 在组件挂载时获取壁纸
onMounted(() => {
  fetchBingWallpaper();
  // 每6小时更新一次壁纸
  const wallpaperTimer = setInterval(fetchBingWallpaper, 6 * 60 * 60 * 1000);
  
  // 组件卸载时清除定时器
  onUnmounted(() => {
    clearInterval(wallpaperTimer);
  });
});

// 标签类型轮换
const getTagType = (index) => {
  const types = ['primary', 'success', 'warning', 'danger', 'info']
  return types[index % types.length]
}

// 瀑布流布局相关
const blogGrid = ref(null);
const columns = ref(3); // 默认3列

// 计算列数
const calculateColumns = () => {
  const width = window.innerWidth;
  if (width > 1200) {
    columns.value = 3;
  } else if (width > 768) {
    columns.value = 2;
  } else {
    columns.value = 1;
  }
};

// 监听窗口大小变化
onMounted(() => {
  calculateColumns();
  window.addEventListener('resize', calculateColumns);
  
  // 在组件卸载时移除事件监听
  onBeforeUnmount(() => {
    window.removeEventListener('resize', calculateColumns);
  });
});

// 将博客数据分组到不同列
const columnBlogs = computed(() => {
  const cols = Array.from({ length: columns.value }, () => []);
  data.data.forEach((blog, index) => {
    const columnIndex = index % columns.value;
    cols[columnIndex].push(blog);
  });
  return cols;
});
</script>

<template>
  <div class="theme-transition">
  <div :style="{ transform: `translateY(-${scrollY}px)` }" class="background-container" style="z-index: 3">
    <h1 ref="text" class="msg" style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);"></h1>
    <div class="background-image"></div>
    <h1>
      <el-icon
          class="arrow-down animate-arrow"
          style="position: absolute; top: 80%; left: 50%; transform: translate(-50%, -50%); font-size: 4rem; color: white"
      >
        <ArrowDownBold/>
      </el-icon>
    </h1>
  </div>


  <el-container id="left-my" style="margin-top: 3%;">

    <el-header id="top-mains" :class="{ 'hidden': isHeaderHidden }"

               :style="{ 'background-color': headerBackgroundColor }" style="padding-right: 0;padding-left: 0">
      <transition name="fade">
        <el-menu
            class="el-menu-demo"
            mode="horizontal">


          <h1 style="display: flex; justify-content: center; align-items: center; margin: 0;">
            <router-link style="text-decoration: none;" to="/">Exp1oit Blog</router-link>
          </h1>


          <!-- Autocomplete Centered -->
          <el-autocomplete v-model="state"
                           :fetch-suggestions="querySearchAsync"
                           placeholder="搜索你感兴趣的"
                           style="margin-right: auto;margin-left: auto;margin-top: auto;margin-bottom: auto;"
                           @select="handleSelect"
          />

          <el-switch
              v-model="isDark"
              inline-prompt
              :active-icon="Moon"
              :inactive-icon="Sunny"
              @change="toggleDarkMode"
          />

          <el-menu-item index="3">
            <router-link style="text-decoration: none;" to="/about-me">关于我</router-link>
          </el-menu-item>

          <el-sub-menu index="5">
            <template #title>共享API接口</template>
            <el-menu-item index="5-1">
              <router-link style="text-decoration: none;" to="/api/bing-wallpaper">API壁纸</router-link>
            </el-menu-item>
          </el-sub-menu>

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
      <el-col :lg="4" :md="6" :sm="24" :xl="3" class="hidden-lg-and-down;" xs="24">
        <el-card class="wow animate__bounce bounceInLeft box-card" data-wow-duration="2s">
          <div style="padding: 14px">
            <h1>Exp1oit</h1>
            <h1></h1>
          </div>
          <el-divider/>
          <h4>联系我</h4>
          <el-container id="svg-icon">
            <a href="https://github.com/Eitsxiaozhai" rel="noopener noreferrer" target="_blank">
              <svg class="bi bi-github" fill="currentColor" height="30" viewBox="0 0 16 16"
                   width="30" xmlns="http://www.w3.org/2000/svg">
                <path
                    d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.012 8.012 0 0 0 16 8c0-4.42-3.58-8-8-8z"/>
              </svg>
            </a>
            <svg class="bi bi-envelope" fill="currentColor" height="30" viewBox="0 0 16 16" width="30"
                 xmlns="http://www.w3.org/2000/svg" @click="sendEmail">
              <path
                  d="M0 4a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V4Zm2-1a1 1 0 0 0-1 1v.217l7 4.2 7-4.2V4a1 1 0 0 0-1-1H2Zm13 2.383-4.708 2.825L15 11.105V5.383Zm-.034 6.876-5.64-3.471L8 9.583l-1.326-.795-5.64 3.47A1 1 0 0 0 2 13h12a1 1 0 0 0 .966-.741ZM1 11.105l4.708-2.897L1 5.383v5.722Z"/>
            </svg>
            <svg class="bi bi-wechat" fill="currentColor" height="30" viewBox="0 0 16 16"
                 width="30" xmlns="http://www.w3.org/2000/svg">
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
              <h3 justify="center" text="2xl"></h3>
              <img id="blog-img" :src="blog.BlogIntroductionPicture" alt="">
            </el-carousel-item>
          </el-carousel>
        </el-card>
      </el-col>

      <transition name="el-fade-in-fast">

        <el-col :lg="12" :md="12" :sm="24" :xl="10" :xs="24" class="maincaretest">
          <div class="content-container">
            <el-main id="maincare">
              <div class="masonry-grid" ref="blogGrid">
                <div 
                  v-for="(column, columnIndex) in columnBlogs" 
                  :key="columnIndex" 
                  class="masonry-column"
                >
                  <div 
                    v-for="blog in column" 
                    :key="blog.BlogId" 
                    class="masonry-item"
                  >
                    <router-link :to="`/blog/${blog.BlogId}`" style="text-decoration: none" target="_blank">
                      <el-card 
                        class="blog-card wow animate__bounce bounceInDown" 
                        data-wow-duration="2s" 
                        shadow="hover"
                      >
                        <div class="blog-card-content">
                          <div class="blog-image-container">
                            <img 
                              class="blog-image" 
                              :src="blog.BlogIntroductionPicture" 
                              alt="图像描述"
                            >
                          </div>
                          <div class="blog-info">
                            <h2 class="blog-title">{{ blog.title }}</h2>
                            <div class="blog-meta">
                              <span class="author">
                                <el-icon><User /></el-icon>
                                {{ blog.author }}
                              </span>
                              <span class="date">
                                <el-icon><Calendar /></el-icon>
                                {{ blog.created_at }}
                              </span>
                            </div>
                            <div class="blog-tags">
                              <el-tag 
                                v-for="(tag, index) in blog.tag"
                                :key="index" 
                                :type="getTagType(index)"
                                class="tag-item"
                              >
                                {{ tag }}
                              </el-tag>
                            </div>
                          </div>
                        </div>
                      </el-card>
                    </router-link>
                  </div>
                </div>
              </div>
              <div class="bt_container" style="display: flex; justify-content: center;">
                <el-button
                  v-if="data.data.length >= loadedCards.value && !loading && data.data.length > 0"
                  type="primary"
                  @click="loadMoreCards"
                >
                  加载更多
                </el-button>
                <el-button
                  v-else-if="loading"
                  type="primary"
                  :loading="true"
                >
                  加载中...
                </el-button>
                <p v-else-if="data.data.length === 0">暂无文章</p>
                <p v-else>没有更多文章了</p>
              </div>
            </el-main>
          </div>
        </el-col>

      </transition>


      <el-col id="left2" :lg="5" :md="6" :sm="24" :xl="3" :xs="24">
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
                <el-statistic :value="totalUV" title="独立访客数"/>
              </el-col>
              <el-col :span="12">
                <el-statistic :value="totalPV" title="页面浏览量"/>
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
  </div>
</template>


<style src="wow.js/css/libs/animate.css"></style>
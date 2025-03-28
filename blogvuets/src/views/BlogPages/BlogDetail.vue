<script setup>
import {ref, nextTick, onMounted, onBeforeUnmount, computed, watch, watchEffect, reactive} from 'vue';
import {RouterLink, useRoute, useRouter} from 'vue-router';
import {useStore} from 'vuex';
import {useHead} from '@unhead/vue';
import MarkdownIt from 'markdown-it';
import {plantuml} from "@mdit/plugin-plantuml";
import hljs from 'highlight.js';
import 'highlight.js/styles/atom-one-dark.css';
import {ChatDotRound, ChatLineRound, ChatRound, Sunny, Moon} from '@element-plus/icons-vue';
import {ElMessage, ElNotification} from "element-plus";
import {UToast, createObjectURL} from 'undraw-ui';
import Fingerprint2 from "fingerprintjs2";
import emoji from '@/assets/emoji';
import '@/assets/css/BlogDetail.css';
import {
  postBlogRatings,
  postUserBlogId,
  postCommentList,
  postCommentSave,
  getAverageRatingRequest
} from '@/api/Blog/blogapig';

// 响应式状态
const isDark = ref(false);
const route = useRoute();
const router = useRouter();
const store = useStore();
const value = ref();
const isLoading = ref(true);
const currentStep = ref(0);
const currentAnchor = ref('');
const elTreeRef = ref(null);
const tableOfContents = ref([]);
const readingProgress = ref(0);
const stepMarginTop = ref();
const fingerprint = ref(null);
const commentx = ref();
const myPage = ref({description: ''});

// 常量定义
const icons = [ChatRound, ChatLineRound, ChatDotRound];
let totalCharacters = 0;
let temp_id = 100;

// 响应式数据
const data = reactive({
  blogData: null
});

// 计算属性
const usernames = computed(() => store.getters.getUsername);
const tokens = computed(() => store.getters.getToken);
const isLoggedIn = computed(() => !!usernames.value);

// 配置对象
const treeProps = {
  data: tableOfContents.value,
  props: {
    children: 'children',
    label: 'label',
    isLeaf: (data, node) => !data.children || !data.children.length,
  },
  highlightCurrent: true,
  'default-expand-all': true,
};

const config = reactive({
  user: {
    id: 1,
    username: usernames.value,
    avatar: 'https://static.juzicon.com/avatars/avatar-200602130320-HMR2.jpeg?x-oss-process=image/resize,w_100',
    likeIds: [1, 2, 3]
  },
  emoji: emoji,
  comments: [],
  total: 10
});

// Markdown 渲染器实例
const md = new MarkdownIt({
  langPrefix: 'language-',
  html: true,
  linkify: true,
  typographer: true,
  highlight: function (str, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return hljs.highlight(str, {language: lang}).value;
      } catch (__) {
        console.warn('代码高亮失败:', __);
      }
    }
    return '';
  }
}).use(plantuml);

// 工具函数
const stringToHex = str => [...str].map(char => char.charCodeAt(0).toString(16)).join('');

// 主题相关函数
const initializeTheme = () => {
  const savedTheme = localStorage.getItem('element-plus-theme');
  if (savedTheme) {
    isDark.value = savedTheme === 'dark';
  } else {
    const currentHour = new Date().getHours();
    isDark.value = currentHour >= 18 || currentHour < 6;
  }
  toggleDarkMode(isDark.value);
};

const toggleDarkMode = (dark) => {
  const html = document.documentElement;
  dark ? html.classList.add('dark') : html.classList.remove('dark');
  localStorage.setItem('element-plus-theme', dark ? 'dark' : 'light');
};

// Markdown 处理函数
const convertMarkdown = (markdownText) => {
  md.renderer.rules.text = function (tokens, idx) {
    let content = tokens[idx].content;
    content = content.replace(/&gt;/g, '>');
    return content;
  };

  let renderedContent = md.render(markdownText);
  const toc = [];
  
  renderedContent = renderedContent.replace(/<h([1-6])[^>]*>(.*?)<\/h\1>/gmi, (match, level, title) => {
    const anchor = `#anchor-${toc.length}`;
    toc.push({level: parseInt(level), title, anchor});
    return `<h${level} id="anchor-${toc.length - 1}">${title}</h${level}>`;
  });

  renderedContent = renderedContent.replace(/<a(.*?)href="(.*?)"(.*?)>(.*?)<\/a>/g, 
    '<a$1href="$2"$3 style="color: blue; text-decoration: underline;">$4</a>');
  
  renderedContent = renderedContent.replace(/<img(.*?)src="(.*?)"(.*?)>/g, 
    '<img$1src="$2"$3 class="markdown-image" style="display: block; margin: 0 auto;">');

  renderedContent = renderedContent.replace(/\$\$uml\s*(.*?)\$\$/gs, (match, umlCode) => {
    const hexUml = stringToHex(umlCode);
    const plantUmlUrl = `https://www.plantuml.com/plantuml/png/~h${hexUml}`;
    return `<img src="${plantUmlUrl}" alt="PlantUML 图表" style="display: block; margin: 0 auto;">`;
  });

  const codeBlocks = renderedContent.match(/<pre><code class="lang-(.*?)">([\s\S]*?)<\/code><\/pre>/gm);
  if (codeBlocks) {
    codeBlocks.forEach(codeBlock => {
      const langMatch = codeBlock.match(/<code class="lang-(.*?)">/);
      const lang = langMatch ? langMatch[1] : null;
      const codeMatch = codeBlock.match(/<code class="lang-.*?">([\s\S]*?)<\/code>/);
      const code = codeMatch ? codeMatch[1] : null;
      if (lang && code) {
        const highlightedCode = hljs.highlight(lang, code).value;
        renderedContent = renderedContent.replace(
          codeBlock,
          `<pre><code class="lang-${lang}">${highlightedCode}</code></pre>`
        );
      }
    });
  }

  tableOfContents.value = buildTreeStructure(toc);
  return renderedContent;
};

// 目录生成相关函数
const generateTableOfContents = (markdownContent) => {
  const toc = [];
  const headers = markdownContent.match(/<h([1-6])[^>]*>(.*?)<\/h\1>/gmi);

  if (headers) {
    headers.forEach((header, index) => {
      const levelMatch = header.match(/<h([1-6])[^>]*>/);
      const titleMatch = header.match(/<h[1-6][^>]*>(.*?)<\/h[1-6]>/i);

      if (levelMatch && titleMatch) {
        const level = parseInt(levelMatch[1]);
        const title = titleMatch[1] || "Unknown Title";
        const anchor = `#anchor-${index}`;
        toc.push({level, title, anchor});
        markdownContent = markdownContent.replace(header, `<h${level} id="anchor-${index}">${title}</h${level}>`);
      }
    });
  }
  tableOfContents.value = buildTreeStructure(toc);
};

const buildTreeStructure = (toc) => {
  const root = [];
  const stack = [{level: 0, children: root}];

  toc.forEach(item => {
    const node = {label: item.title, anchor: item.anchor, children: []};

    while (stack.length > 0 && stack[stack.length - 1].level >= item.level) {
      stack.pop();
    }

    if (stack.length > 0) {
      stack[stack.length - 1].children.push(node);
    }

    stack.push({level: item.level, children: node.children});
  });

  return root;
};

// UI 交互函数
const addCopyButtons = () => {
  nextTick(() => {
    document.querySelectorAll('pre').forEach(pre => {
      if (pre.querySelector('.copy-button')) return;

      const button = document.createElement('button');
      button.className = 'copy-button';
      button.textContent = '复制';

      button.onclick = async () => {
        try {
          const code = pre.querySelector('code').textContent;
          await navigator.clipboard.writeText(code);
          ElNotification({
            title: '成功',
            message: '代码已复制到剪贴板',
            type: 'success',
            duration: 2000
          });
        } catch (err) {
          ElNotification({
            title: '错误',
            message: '无法复制代码',
            type: 'error',
            duration: 2000
          });
        }
      };

      pre.appendChild(button);
    });
  });
};

const scrollToCurrentNode = () => {
  nextTick(() => {
    const tree = elTreeRef.value;
    if (tree) {
      const currentNode = tree.getCurrentNode();
      const nodeEl = tree.$el.querySelector('.is-current');

      if (nodeEl && currentNode) {
        nodeEl.scrollIntoView({
          behavior: 'smooth',
          block: 'center'
        });
      }
    }
  });
};

const handleScroll = () => {
  const headings = document.querySelectorAll('h1[id], h2[id], h3[id], h4[id], h5[id], h6[id]');
  let closestHeading = null;

  headings.forEach(heading => {
    const bounding = heading.getBoundingClientRect();
    if (bounding.top >= 0 && bounding.top <= window.innerHeight / 2) {
      closestHeading = heading;
    }
  });

  if (closestHeading && closestHeading.id !== currentAnchor.value) {
    currentAnchor.value = `#${closestHeading.id}`;
    scrollToCurrentNode();
  }
};

const handleNodeClick = (data) => {
  const targetElement = document.querySelector(data.anchor);

  if (targetElement) {
    targetElement.scrollIntoView({
      behavior: 'smooth',
      block: 'center',
      inline: 'nearest'
    });

    targetElement.classList.add('selected');
    setTimeout(() => {
      targetElement.classList.remove('selected');
    }, 2000);
  }
};

// 数据获取和更新函数
const getData = async () => {
  const blogId = route.params.blogId;
  try {
    const response = await postUserBlogId(blogId);

    if (!response?.data) {
      throw new Error('接口返回数据格式异常');
    }

    data.blogData = response.data;
    isLoading.value = false;
    document.title = data.blogData.title || '默认标题';

    const content = data.blogData.content ? String(data.blogData.content) : '';
    const htmlContent = convertMarkdown(content);

    generateTableOfContents(htmlContent);
    myPage.value.description = content;

    nextTick(() => {
      document.querySelectorAll('pre code').forEach((block) => {
        hljs.highlightElement(block);
      });
      addCopyButtons();
      commentx.value = document.querySelector('#commentx')?.offsetHeight || 0;
      window.addEventListener('scroll', updateReadingProgress);
      updateReadingProgress();
    });

  } catch (error) {
    console.error('数据加载失败:', error);
    ElNotification.error('内容加载失败，请刷新重试');
  }
};

const updateReadingProgress = () => {
  if (!data.blogData?.content) return;

  const scrollTop = document.documentElement.scrollTop;
  const windowHeight = document.documentElement.clientHeight;
  const documentHeight = document.documentElement.scrollHeight;
  const commentHeight = commentx.value?.offsetHeight || 0;

  const scrollableHeight = documentHeight - commentHeight - windowHeight;

  if (scrollableHeight <= 0) {
    readingProgress.value = 100;
    return;
  }

  const scrolled = Math.min(scrollTop / scrollableHeight, 1);
  readingProgress.value = Math.floor(scrolled * 100);
};

// API 调用函数
const vote = async () => {
  const blogId = route.params.blogId;
  const device_id = fingerprint.value;
  const ratingValue = value.value;

  if (typeof ratingValue !== 'number' || !Number.isInteger(ratingValue) || ratingValue < 1 || ratingValue > 5) {
    console.error("Invalid rating value:", ratingValue);
    return;
  }

  try {
    const queryParams = new URLSearchParams({
      rating: ratingValue.toString(),
      device_id: device_id.toString(),
    });

    const response = await postBlogRatings(blogId, queryParams);
    const oldContent = data.data[0].content;
    data.data = response.data;

    if (oldContent !== data.data[0].content) {
      generateTableOfContents(data.data.content);
    }
  } catch (error) {
    console.error("Error in vote function:", error);
  }
};

const getAverageRating = async () => {
  const blogId = route.params.blogId;
  try {
    const response = await getAverageRatingRequest(blogId);
    averageRating.value = response.data;
  } catch (error) {
    console.error(error);
  }
};

const LoadComments = async () => {
  const blogId = route.params.blogId;
  try {
    const CommentList = await postCommentList(blogId);
    config.comments = CommentList.data;
    nextTick(() => {
      commentx.value = commentx.value.offsetHeight;
    });
  } catch (error) {
    console.error(error);
  }
};

const UpComments = async (str) => {
  const blogId = route.params.blogId;
  const token = localStorage.getItem("token");
  try {
    const UpComment = await postCommentSave(blogId, str, token);
    if (UpComment.data.code === 40002) {
      UToast({message: 'Token无效，请尝试重新登录', type: 'info'});
      localStorage.removeItem("token");
      localStorage.removeItem("vuex");
      return;
    } else if (UpComment.data.code === 40003) {
      console.error('无效的 Token');
      UToast({message: 'Token无效，请尝试重新登录', type: 'info'});
      localStorage.removeItem("token");
      localStorage.removeItem("vuex");
      return;
    }
  } catch (error) {
    console.error(error);
  }
};

// 事件处理函数
const submitRating = async () => {
  try {
    await vote();
  } catch (error) {
    console.error(error);
  }
};

const submit = async ({content, parentId, files, finish, reply}) => {
  const jsonData = {
    content: content,
    parentId: parentId,
    files: files,
  };

  const token = localStorage.getItem("token");
  const blogId = route.params.blogId;
  await UpComments(jsonData);

  if (!token) {
    ElNotification({
      title: 'Warning',
      message: '您还没有登录哦，点击卡片跳转到登录页面',
      type: 'warning',
      onClick: () => {
        router.push('/login');
      },
    });
    UToast({message: '未登录状态,评论将不会保存', type: 'info'});
    return;
  }

  let contentImg = files.map(e => createObjectURL(e)).join('||');

  const comment = {
    id: String((temp_id += 1)),
    parentId: parentId,
    uid: config.user.id,
    address: '来自江苏',
    content: content,
    likes: 0,
    createTime: '1分钟前',
    contentImg: contentImg,
    user: {
      username: config.user.username,
      avatar: config.user.avatar,
      level: 6,
      homeLink: `/${(temp_id += 1)}`
    },
    reply: null
  };

  setTimeout(() => {
    finish(comment);
    UToast({message: '评论成功!', type: 'info'});
  }, 200);
};

const like = (id, finish) => {
  setTimeout(() => {
    finish();
  }, 200);
};

// 生命周期钩子
onMounted(() => {
  initializeTheme();
  const timeCheckTimer = setInterval(initializeTheme, 60 * 60 * 1000);
  const handleVisibilityChange = () => {
    if (!document.hidden) initializeTheme();
  };
  document.addEventListener('visibilitychange', handleVisibilityChange);

  store.commit('setLastVisitedRoute', route.params.blogId);
  getAverageRating();
  LoadComments();

  const options = {
    excludes: {
      userAgent: true,
      language: true,
      colorDepth: true
    }
  };

  window.addEventListener('scroll', handleScroll);
  Fingerprint2.get(options, function (components) {
    const fingerprintId = Fingerprint2.x64hash128(components.map(function (pair) {
      return pair.value;
    }).join(), 31);
    fingerprint.value = fingerprintId;
  });

  onBeforeUnmount(() => {
    clearInterval(timeCheckTimer);
    document.removeEventListener('visibilitychange', handleVisibilityChange);
  });
});

onBeforeUnmount(() => {
  window.removeEventListener('scroll', handleScroll);
  window.removeEventListener('scroll', updateReadingProgress);
});

// 初始化
getData().then(() => {
  if (data.blogData?.content) {
    totalCharacters = data.blogData.content.length;
    window.addEventListener('scroll', updateReadingProgress);
  } else {
    console.warn('内容数据异常，无法计算阅读进度');
    totalCharacters = 0;
  }
});

// 页面元数据
useHead({
  meta: [{name: 'description', content: () => myPage.value.description}]
});
</script>

<template>
  <el-container class="theme-transition">
    <el-header id="top-mains" :class="{'hidden': scrollDirection === 'down'}">
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
      <el-progress :percentage="Math.max(0, Math.min(100, readingProgress))" :show-text="false"/>
    </el-header>

    <el-card
        v-if="!isLoading"
        style="margin: 3% auto; width: 99%; box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);"
    >
      <div class="text-item">
        <h1 class="title">{{ data.blogData.title }}</h1>
            <el-divider>
    </el-divider>
        <div class="info">
          <span class="author">作者: {{ data.blogData.author }}</span>
          <span class="date">发布时间：{{ data.blogData.created_at }}</span>
        </div>
      </div>
    </el-card>

    <el-card v-else>
      <!-- 骨架屏 -->
      <el-skeleton :rows="5" animated/>
    </el-card>

    <el-container class="affix-container">
      <el-aside>
        <el-affix :offset="270" target=".affix-container">
          <el-card>
              <el-tree
                  v-if="!isLoading"
                  ref="elTreeRef"
                  :current-node-key="currentAnchor"
                  :data="tableOfContents"
                  :default-expand-all="treeProps['default-expand-all']"
                  :highlight-current="treeProps.highlightCurrent"
                  :props="treeProps"
                  node-key="anchor"
                  @node-click="handleNodeClick"
              />
              <el-skeleton v-else :rows="5" animated/>
          </el-card>

          <el-card style="margin-top: 1%">
            <h4>对你有帮助吗？</h4>
            <el-rate
                v-model="value"
                :colors="['#409eff', '#67c23a', '#FF9900']"
                :icons="icons"
                :void-icon="ChatRound"
                @change="submitRating"
            />
            <el-switch
                v-model="isDark"
                inline-prompt
                :active-icon="Moon"
                :inactive-icon="Sunny"
                @change="toggleDarkMode"
            />
          </el-card>
        </el-affix>
      </el-aside>

      <el-main>
        <el-card v-if="!isLoading" style="padding-bottom: 10%">
          <div class="blog-content">
            <div v-html="convertMarkdown(data.blogData.content)"/>
          </div>
        </el-card>

        <el-card v-else>
          <el-skeleton :rows="10" animated/>
        </el-card>

      <div id="commentx" ref="commentx">
        <el-card style="margin-top: 1%">
          <u-comment :config="config" @like="like" @submit="submit" />
        </el-card>
      </div>
      </el-main>
      <el-backtop/>
    </el-container>
  </el-container>
</template>



<script setup>
import {ref, nextTick, onMounted, onBeforeUnmount, computed} from 'vue';
import {RouterLink,} from 'vue-router'
import {useRoute} from "vue-router";
import MarkdownIt from 'markdown-it';
import {plantuml} from "@mdit/plugin-plantuml";
import hljs from 'highlight.js';
import 'highlight.js/styles/atom-one-dark-reasonable.css';
import {useRouter} from "vue-router";
import {reactive} from "vue";
import '@/assets/css/BlogDetail.css';
import {
  postBlogRatings,
  postUserBlogId,
  postCommentList,
  postCommentSave,
  getAverageRatingRequest
} from '@/api/Blog/blogapig';

import {ChatDotRound, ChatLineRound, ChatRound} from '@element-plus/icons-vue'
import Fingerprint2 from "fingerprintjs2";
import {useStore} from 'vuex';
import emoji from '@/assets/emoji';
import {UToast, createObjectURL} from 'undraw-ui';
import {ElNotification} from "element-plus";
import {useHead} from '@unhead/vue';

// 常用变量操作
const route = useRoute()
const value = ref()
const icons = [ChatRound, ChatLineRound, ChatDotRound]
const isLoading = ref(true); // 初始时，骨架屏可见
const currentStep = ref(0); // 创建响应式变量用于跟踪当前标题索引
// 创建Markdown渲染器实例
const currentAnchor = ref(''); // 当前高亮的锚点
const elTreeRef = ref(null); // el-tree 的引用
const md = new MarkdownIt({
  langPrefix: 'language-',
  html: true,
  linkify: true,
  typographer: true
}).use(plantuml);
const tableOfContents = ref([]);
const router = useRouter()
const data = reactive({
  data: []
})

const treeProps = {
  data: tableOfContents.value,
  props: {
    children: 'children',
    label: 'label',
    isLeaf: (data, node) => !data.children || !data.children.length,
  },
  highlightCurrent: true, // 高亮当前节点
  'default-expand-all': true,
};


// 滚动 el-tree 组件，使当前节点保持在视图中间
const scrollToCurrentNode = () => {
  nextTick(() => {
    const tree = elTreeRef.value;
    if (tree) {
      const currentNode = tree.getCurrentNode(); // 获取当前高亮节点
      const nodeEl = tree.$el.querySelector('.is-current'); // 获取高亮节点的 DOM 元素

      if (nodeEl && currentNode) {
        nodeEl.scrollIntoView({
          behavior: 'smooth',
          block: 'center'
        });
      }
    }
  });
};

// 页面滚动监听函数
const handleScroll = () => {
  const headings = document.querySelectorAll('h1[id], h2[id], h3[id], h4[id], h5[id], h6[id]');
  let closestHeading = null;

  // 遍历所有标题，找到最接近视口顶部的标题
  headings.forEach(heading => {
    const bounding = heading.getBoundingClientRect();
    if (bounding.top >= 0 && bounding.top <= window.innerHeight / 2) {
      closestHeading = heading;
    }
  });

  // 如果找到了新的当前标题，则更新currentAnchor
  if (closestHeading && closestHeading.id !== currentAnchor.value) {
    currentAnchor.value = `#${closestHeading.id}`;
    scrollToCurrentNode(); // 滚动到当前节点
  }
};

//计算UML hex编码
const stringToHex = str => [...str].map(char => char.charCodeAt(0).toString(16)).join('');


// 转换markdown操作代码高亮和目录生成
const convertMarkdown = (markdownText) => {

  // 使用 'replace' 方法修改转义行为
  md.renderer.rules.text = function (tokens, idx) {
    let content = tokens[idx].content;
    // 恢复 '>' 字符
    content = content.replace(/&gt;/g, '>');
    return content;
  };

  // 生成 HTML 内容
  let renderedContent = md.render(markdownText);

  // 解析目录并添加锚点
  const toc = [];
  renderedContent = renderedContent.replace(/<h([1-6])[^>]*>(.*?)<\/h\1>/gmi, (match, level, title, offset) => {
    const anchor = `#anchor-${toc.length}`;
    toc.push({level: parseInt(level), title, anchor});
    return `<h${level} id="anchor-${toc.length - 1}">${title}</h${level}>`;
  });

  // 高亮代码
  renderedContent = renderedContent.replace(/<a(.*?)href="(.*?)"(.*?)>(.*?)<\/a>/g, '<a$1href="$2"$3 style="color: blue; text-decoration: underline;">$4</a>');
  const codeBlocks = renderedContent.match(/<pre><code class="lang-(.*?)">([\s\S]*?)<\/code><\/pre>/gm);
  renderedContent = renderedContent.replace(/<img(.*?)src="(.*?)"(.*?)>/g, '<img$1src="$2"$3 class="markdown-image" style="display: block;  margin: 0 auto;">');

// 正则表达式匹配 PlantUML 代码块
  renderedContent = renderedContent.replace(/\$\$uml\s*(.*?)\$\$/gs, (match, umlCode) => {
    // 对 UML 代码进行 Hex 编码
    const hexUml = stringToHex(umlCode);

    // 创建 PlantUML 图表 URL
    const plantUmlUrl = `https://www.plantuml.com/plantuml/png/~h${hexUml}`;

    // 返回图像标签
    return `<img src="${plantUmlUrl}" alt="PlantUML 图表" style="display: block; margin: 0 auto;">`;
  });

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
  // 更新目录
  tableOfContents.value = buildTreeStructure(toc);
  return renderedContent;
};


// 生成目录
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

// 将扁平结构转换为树形结构
const buildTreeStructure = (toc) => {
  const root = [];
  const stack = [{level: 0, children: root}];  // 初始层级为 0 的根节点

  toc.forEach(item => {
    const node = {label: item.title, anchor: item.anchor, children: []};

    // 如果当前项的层级小于等于堆栈顶层的层级，弹出堆栈
    while (stack.length > 0 && stack[stack.length - 1].level >= item.level) {
      stack.pop();
    }

    // 将当前节点添加到堆栈顶层的 children 中
    if (stack.length > 0) {
      stack[stack.length - 1].children.push(node);
    }

    // 将当前项压入堆栈
    stack.push({level: item.level, children: node.children});
  });

  return root;
};


// 处理树节点点击
const handleNodeClick = (data) => {
  const targetElement = document.querySelector(data.anchor);

  if (targetElement) {
    // 滚动到目标元素
    targetElement.scrollIntoView({
      behavior: 'smooth',
      block: 'center',
      inline: 'nearest'
    });

    // 给目标元素添加选中样式
    targetElement.classList.add('selected');

    // 在一定时间后移除选中样式
    setTimeout(() => {
      targetElement.classList.remove('selected');
    }, 2000); // 2秒后恢复原来的颜色
  }
};


// 博客内容获取操作
const getData = async () => {
  const blogId = route.params.blogId;
  try {
    const response = await postUserBlogId(blogId);
    data.data = response.data;
    isLoading.value = false;
    document.title = data.data[0].title;
    myPage.value.description = data.data[0].content;

    // Ensure content is converted to HTML if it's Markdown
    const htmlContent = convertMarkdown(response.data[0].content);

    // Trigger table of contents generation
    generateTableOfContents(htmlContent);

    setTimeout(() => {
      hljs.highlightAll();
    }, 0);
  } catch (error) {
    console.error('Error fetching blog data:', error);
  }
};
// 页面元数据变量
const myPage = ref({description: ''})
// 操作页面元数据
useHead({
  meta: [{name: 'description', content: () => myPage.value.description}]
  // computed (not recommended)
})


// 阅读进度变量
const readingProgress = ref(0);
let totalCharacters = 0;

// 获取阅读进度操作
const updateReadingProgress = () => {
  const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
  const windowHeight = window.innerHeight;
  const documentHeight = document.documentElement.scrollHeight - commentx.value;
  const scrollableDistance = documentHeight - windowHeight;
  const scrollPercentage = (scrollTop / scrollableDistance) * 100;


  // 根据阅读进度计算当前标题索引
  const totalSteps = tableOfContents.value.length;
  const calculatedStep = Math.floor((scrollPercentage / 100) * totalSteps);

  // 更新currentStep
  currentStep.value = calculatedStep;
  stepMarginTop.value = -calculatedStep * 15;
  readingProgress.value = scrollPercentage;
};


// 在 data.data 中的字符数，用于计算阅读进度
const stepMarginTop = ref(); // 创建响应式变量来存储步骤条的 margin-top 值


// 获取数据并计算阅读进度
getData().then(() => {
  // 获取文章内容的总字符数，确保 data.data[0] 有值
  totalCharacters = data.data[0].content.length;
  // 监听滚动事件，更新阅读进度
  window.addEventListener('scroll', updateReadingProgress)
});


onBeforeUnmount(() => {
  // 移除滚动事件监听
  window.removeEventListener('scroll', handleScroll);
  window.removeEventListener('scroll', updateReadingProgress);
});

// 设备id变量
const fingerprint = ref(null);

// 挂载时操作
onMounted(async () => {
  const commentx = ref(null)

  // 使用Fingerprint2生成浏览器指纹
  const options = {
    excludes: {
      userAgent: true, // 排除用户代理信息
      language: true,  // 排除语言设置
      colorDepth: true // 排除颜色深度
      // 更多排除选项可根据需求添加
    }
  };
  window.addEventListener('scroll', handleScroll);
  Fingerprint2.get(options, function (components) {
    const fingerprintId = Fingerprint2.x64hash128(components.map(function (pair) {
      return pair.value;
    }).join(), 31);  // 生成指纹ID
    fingerprint.value = fingerprintId;
    // 可以将 fingerprintId 发送到服务器或进行其他操作
  });
});


// 投票方法操作
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
    const oldContent = data.data[0].content; // 保存投票前的内容
    data.data = response.data;

    // 判断是否需要重新生成目录
    if (oldContent !== data.data[0].content) {
      generateTableOfContents(data.data.content);
    }
  } catch (error) {
    console.error("Error in vote function:", error);
  }
};


// 平均分变量
const averageRating = ref(0); // 创建一个 ref 来存储平均评分


// 获取平均评分数据并设置到 averageRating
const getAverageRating = async () => {
  const blogId = route.params.blogId;
  try {
    const response = await getAverageRatingRequest(blogId);
    averageRating.value = response.data; // 设置平均评分数据到 ref
  } catch (error) {
    console.error(error);
  }
};

//加载评论操作
const LoadComments = async () => {
  const blogId = route.params.blogId;
  try {
    const CommentList = await postCommentList(blogId);
    config.comments = CommentList.data;
    //获取到评论后下个Tick才会读取评论区高度
    nextTick(() => {
      commentx.value = commentx.value.offsetHeight;
    })
  } catch (error) {
    console.error(error);
  }
};

//提交评论操作
const UpComments = async (str) => {
  const blogId = route.params.blogId;
  const token = localStorage.getItem("token"); // 从本地存储获取 token
  try {
    const UpComment = await postCommentSave(blogId, str, token);
    if (UpComment.data.code === 40002) {
      // Token 已过期
      UToast({message: 'Token无效，请尝试重新登录', type: 'info'})
      localStorage.removeItem("token"); // 删除本地存储中的过期 Token
      localStorage.removeItem("vuex")
      return; // 提前结束函数执行
    } else if (UpComment.data.code === 40003) {
      // 无效的 Token
      console.error('无效的 Token');
      UToast({message: 'Token无效，请尝试重新登录', type: 'info'})
      localStorage.removeItem("token"); // 删除本地存储中的过期 Token
      localStorage.removeItem("vuex")
      return; // 提前结束函数执行
    } else {
      // 其他错误状态码的处理
      return;
    }
  } catch (error) {
    console.error(error);
  }
};

const commentx = ref()

onMounted(() => {
  store.commit('setLastVisitedRoute', route.params.blogId);
  getAverageRating();
  LoadComments();
});


const submitRating = async () => {

  try {
    // 调用 vote 函数提交评分
    await vote();
  } catch (error) {
    console.error(error);
  }
};

const store = useStore();
const usernames = computed(() => store.getters.getUsername);
const tokens = computed(() => store.getters.getToken);

const config = reactive({
  user: {
    id: 1,
    username: usernames.value,
    avatar: 'https://static.juzicon.com/avatars/avatar-200602130320-HMR2.jpeg?x-oss-process=image/resize,w_100',
    // 评论id数组 建议:存储方式用户uid和评论id组成关系,根据用户uid来获取对应点赞评论id,然后加入到数组中返回
    likeIds: [1, 2, 3]
  },
  emoji: emoji,
  comments: [],
  total: 10
})

let temp_id = 100
// 提交评论事件
const submit = async ({content, parentId, files, finish, reply}) => {
  let str = '提交评论:' + content + ';\t父id: ' + parentId + ';\t图片:' + files + ';\t被回复评论:'

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
        // 用户点击通知时执行的操作
        router.push('/login'); // 跳转到登录页面
      },
    })
    UToast({message: '未登录状态,评论将不会保存', type: 'info'})
    // 如果没有 token，阻止评论的提交并提示用户去登录
    return;
  }
  /**
   * 上传文件后端返回图片访问地址，格式以'||'为分割; 如:  '/static/img/program.gif||/static/img/normal.webp'
   */
  let contentImg = files.map(e => createObjectURL(e)).join('||')


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
  }
  setTimeout(() => {
    finish(comment)
    UToast({message: '评论成功!', type: 'info'})
  }, 200)
}
// 点赞按钮事件 将评论id返回后端判断是否点赞，然后在处理点赞状态
const like = (id, finish) => {
  setTimeout(() => {
    finish()
  }, 200)
}

config.comments = []
const isLoggedIn = computed(() => !!usernames.value);


</script>

<template>
  <el-container>
    <el-header id="top-mains" :class="{ 'hidden': scrollDirection === 'down' }">
      <el-menu
          class="el-menu-demo"
          mode="horizontal">

        <el-menu-item index="1">
          <h1>
            <router-link style="text-decoration: none;" to="/">Exp1oit Blog</router-link>
          </h1>
        </el-menu-item>


        <el-autocomplete v-model="state"
                         :fetch-suggestions="querySearchAsync"
                         placeholder="搜索你感兴趣的"
                         style="margin-right: auto"
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
  </el-container>
  <div>
    <el-card
        v-if="!isLoading"
        style="margin: 3% auto; width: 99%; box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);"
    >
      <div v-for="(item, index) in data.data" :key="index" class="text-item">
        <h1 class="title">{{ item.title }}</h1>
        <div class="info">
          <span class="author">作者: {{ item.author }}</span>
          <span class="rating">
          总体评分:
          <el-rate v-model="averageRating" allow-half disabled style="margin-left: 10px;"/>
        </span>
          <span class="date">发布时间：{{ item.created_at }}</span>
        </div>
      </div>
    </el-card>

    <el-card v-else>
      <!-- 骨架屏 -->
      <el-skeleton :rows="5" animated/>
    </el-card>
  </div>

  <el-row>
    <el-container class="affix-container">
      <el-col :lg="6" :md="4" :sm="0" :xl="5" :xs="0">
        <el-aside>
          <el-affix :offset="270" target=".affix-container">
            <el-card style="height: 30vh">
              <div>
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
              </div>
            </el-card>

            <el-card style="margin-top: 1%">
              <h4>喜欢该文章吗？</h4>
              <el-rate
                  v-model="value"
                  :colors="['#409eff', '#67c23a', '#FF9900']"
                  :icons="icons"
                  :void-icon="ChatRound"
                  @change="submitRating"
              />
            </el-card>
          </el-affix>
        </el-aside>
      </el-col>

      <el-col :lg="18" :md="24" :sm="24" :xl="17" :xs="24">

        <el-main>
          <el-card v-if="!isLoading" style="margin-top: 20px;padding-bottom: 10%">
            <div v-for="(item, index) in data.data" :key="index" class="text item">
              <div>
                <div v-html="convertMarkdown(item.content)"></div>
              </div>
            </div>
          </el-card>

          <el-card v-else>
            <el-skeleton :rows="10" animated/>
          </el-card>

          <div ref="commentx">
            <el-card style="margin-top: 1%">
              <u-comment :config="config" @like="like" @submit="submit">
              </u-comment>
            </el-card>
          </div>
        </el-main>
      </el-col>
      <el-backtop/>
    </el-container>
  </el-row>
</template>



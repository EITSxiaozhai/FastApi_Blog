<script setup>
import {ref, onBeforeMount, onMounted, onBeforeUnmount, onUnmounted,computed} from 'vue';
import {RouterLink, RouterView} from 'vue-router'
import {useRoute} from "vue-router";
import MarkdownIt from 'markdown-it';
import hljs from 'highlight.js';
import 'highlight.js/styles/default.css'; // Import the style you prefer
const route = useRoute()
import {useRouter} from "vue-router";
import {reactive} from "vue";
import backApi from '../Api/backApi.ts';
import {Discount} from "@element-plus/icons-vue";
import {ChatDotRound, ChatLineRound, ChatRound} from '@element-plus/icons-vue'
import Fingerprint2 from "fingerprintjs2";
import { useStore } from 'vuex';

import emoji from '@/assets/emoji'
import {UToast, createObjectURL} from 'undraw-ui';
import {ElNotification} from "element-plus";

const value = ref()
const icons = [ChatRound, ChatLineRound, ChatDotRound]

const isLoading = ref(true); // 初始时，骨架屏可见


const router = useRouter()
const data = reactive({
  data: []
})


const currentStep = ref(0); // 创建响应式变量用于跟踪当前标题索引


// 创建Markdown渲染器实例
const md = new MarkdownIt();

const tableOfContents = ref([]);

const convertMarkdown = (markdownText) => {
  let renderedContent = md.render(markdownText);

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

  // 解析目录
  const toc = [];
  const headers = renderedContent.match(/<h(.*?)>(.*?)<\/h\1>/gm);
  if (headers) {
    headers.forEach(header => {
      const levelMatch = header.match(/<h(\d)>/);
      const level = levelMatch ? parseInt(levelMatch[1]) : 0;
      const titleMatch = header.match(/<h\d>(.*?)<\/h\d>/);
      const title = titleMatch ? titleMatch[1] : '';

      if (level > 0 && title) {
        const anchor = `#anchor-${toc.length}`;
        toc.push({level, title, anchor});
        renderedContent = renderedContent.replace(header, `<h${level} id="anchor-${toc.length}">${title}</h${level}>`);
      }
    });
  }
  tableOfContents.value = toc;
  return renderedContent;
};


const getData = async () => {
  const blogId = route.params.blogId;
  try {
    const response = await backApi.post(`/user/Blogid?blog_id=${blogId}`);
    data.data = response.data;
    isLoading.value = false;
    // 手动触发代码高亮
    setTimeout(() => {
      hljs.highlightAll();
    }, 0);

    // 触发目录生成逻辑
    generateTableOfContents(response.data.content);
  } catch (error) {
    console.error(error);
  }
};

const generateTableOfContents = (markdownContent) => {
  if (typeof markdownContent !== 'string' || markdownContent.trim() === '') {
    // 如果 markdownContent 为空或不是字符串，直接返回
    return;
  }

  const toc = [];
  const headers = markdownContent.match(/<h([1-6])>(.*?)<\/h\1>/gm);
  if (headers) {
    headers.forEach((header, index) => {
      const levelMatch = header.match(/<h([1-6])>/);
      const level = levelMatch ? parseInt(levelMatch[1]) : 0;
      const titleMatch = header.match(/<h[1-6]>(.*?)<\/h[1-6]>/);
      const title = titleMatch ? titleMatch[1] : '';

      if (level > 0 && title) {
        const anchor = `#anchor-${index}`;
        toc.push({level, title, anchor});
        markdownContent = markdownContent.replace(header, `<h${level} id="anchor-${index}">${title}</h${level}>`);
      }
    });
  }

  tableOfContents.value = toc;
};


getData()


const readingProgress = ref(0);
let totalCharacters = 0;

const updateReadingProgress = () => {
  const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
  const windowHeight = window.innerHeight;
  const documentHeight = document.documentElement.scrollHeight;
  const scrollableDistance = documentHeight - windowHeight;
  const scrollPercentage = (scrollTop / scrollableDistance) * 100;


    // 根据阅读进度计算当前标题索引
  const totalSteps = tableOfContents.value.length;
  const calculatedStep = Math.floor((scrollPercentage / 100) * totalSteps);

  // 更新currentStep
  currentStep.value = calculatedStep;
  stepMarginTop.value = -calculatedStep * 25;
  readingProgress.value = scrollPercentage;
};


// 在 data.data 中的字符数，用于计算阅读进度
const stepMarginTop = ref(); // 创建响应式变量来存储步骤条的 margin-top 值



// 获取数据并计算阅读进度
getData().then(() => {
  // 获取文章内容的总字符数，确保 data.data[0] 有值
  totalCharacters = data.data[0].content.length;

  // 监听滚动事件，更新阅读进度
  window.addEventListener('scroll', updateReadingProgress);

});



onBeforeUnmount(() => {
  // 移除滚动事件监听
  window.removeEventListener('scroll', updateReadingProgress);
});

const fingerprint = ref(null);

onMounted(() => {
  // 使用Fingerprint2生成浏览器指纹
  const options = {
    excludes: {
      userAgent: true, // 排除用户代理信息
      language: true,  // 排除语言设置
      colorDepth: true // 排除颜色深度
      // 更多排除选项可根据需求添加
    }
  };

  Fingerprint2.get(options, function (components) {
    const fingerprintId = Fingerprint2.x64hash128(components.map(function (pair) {
      return pair.value;
    }).join(), 31);  // 生成指纹ID

    fingerprint.value = fingerprintId;

    // 可以将 fingerprintId 发送到服务器或进行其他操作
  });
});

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

    const response = await backApi.post(`/blogs/${blogId}/ratings/?${queryParams.toString()}`);
    data.data = response.data;
    generateTableOfContents(response.data.content);
  } catch (error) {
    console.error("Error in vote function:", error);
  }
};


const averageRating = ref(0); // 创建一个 ref 来存储平均评分

// 获取平均评分数据并设置到 averageRating
const getAverageRating = async () => {
  const blogId = route.params.blogId;
  try {
    const response = await backApi.get(`/blogs/${blogId}/average-rating/`);
    averageRating.value = response.data; // 设置平均评分数据到 ref
  } catch (error) {
    console.error(error);
  }
};

const LoadComments = async () => {
  const blogId = route.params.blogId;
  try {
    const CommentList = await backApi.post(`/generaluser/${ blogId }/commentlist`);
    config.comments = CommentList.data;
    console.log(config.comments)
  } catch (error) {
    console.error(error);
  }
};


const UpComments = async (str) => {
    const blogId = route.params.blogId;
    const token = localStorage.getItem("token"); // 从本地存储获取 token
    try {
        if (!token) {
            router.push('/login'); // 跳转到登录页面
            return; // 提前结束函数执行
        }
        const UpComment = await backApi.post(`/generaluser/${blogId}/commentsave`, {
            content: str,
        }, {
            headers: {
                'Authorization': `Bearer ${token}`, // 在 headers 中包含 token
            },
        });
        if (UpComment.data.code === 40002) {
            // Token 已过期
            console.error('Token 已过期');
            localStorage.removeItem("token"); // 删除本地存储中的过期 Token
            return; // 提前结束函数执行
        } else if (UpComment.data.code === 40003) {
            // 无效的 Token
            console.error('无效的 Token');
            localStorage.removeItem("token"); // 删除本地存储中的过期 Token
            return; // 提前结束函数执行
        } else {
            // 其他错误状态码的处理
            return;
        }
    } catch (error) {
        console.error(error);
    }
};

onMounted(() => {
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

  console.log(jsonData)
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

config.comments = [

]




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

</script>

<template>
  <el-container>

    <el-aside style="width: 13%;">
      <el-card style="height: 40%; position: fixed; width: 13%;margin-top: 10%">
        <el-steps
          direction="vertical"
          :active="currentStep"
          v-if="!isLoading"
          :style="{ 'margin-top': stepMarginTop + 'px' }"
        >
          <el-step v-for="(item, index) in tableOfContents" :key="index" :title="item.title"></el-step>
        </el-steps>
        <el-skeleton :rows="5" animated v-else />
      </el-card>
            <el-card style="position: fixed; width: 13%;margin-top: 30%">
                <h4>喜欢该文章吗？</h4>
          <el-rate
            v-model="value"
            :icons="icons"
            :void-icon="ChatRound"
            :colors="['#409eff', '#67c23a', '#FF9900']"
            @change="submitRating"
          />
        </el-card>
    </el-aside>


    <el-container>
      <el-header :class="{ 'hidden': scrollDirection === 'down' }" id="top-mains">
        <el-menu class="el-menu-demo" mode="horizontal">
          <h1 style="padding-left: 20px;font-size: 20px">
            <router-link to="/blog" style="text-decoration: none;">Exp1oit Blog</router-link>
          </h1>
  <el-sub-menu index="2-4" id="login">
    <template #title>
      {{ isLoggedIn ? `你好：${usernames}` : '登录' }}
    </template>
    <el-menu-item v-if="isLoggedIn" index="2-4-2">
      <a href="#" style="text-decoration:none" @click.prevent="redirectToUserProfile">个人资料</a>
    </el-menu-item>
    <el-menu-item index="2-4-1">
      <a href="" style="text-decoration:none" @click.prevent="redirectToRegister">注册</a>
    </el-menu-item>
  </el-sub-menu>
        </el-menu>
        <el-progress :percentage="readingProgress" :show-text="false"/>
      </el-header>
      <el-main >
        <el-card style="margin-top: 5%; display: flex; justify-content: center;" v-if="!isLoading" pa>
          <div v-for="(item, index) in data.data" :key="index" class="text item">
            <div>
              <div style="display: flex; flex-direction: column; align-items: center;">
                <h1 style="font-size: 200%" class="el-title">{{ item.title }}</h1>
              </div>
              <div style="display: flex; justify-content: center; align-items: center;">
                <h3 style="padding-right: 50px">作者:{{ item.author }}</h3>
                <h3>总体评分:</h3>
                <el-rate style="padding-right: 50px" v-model="averageRating" allow-half disabled/>
                <h3 style="padding-right: 50px">发布时间：{{ item.created_at }}</h3>
              </div>
            </div>
          </div>

        </el-card>
        <el-card v-else>
          <!-- 骨架屏 -->
          <el-skeleton :rows="5" animated/>
        </el-card>
        <el-card style="margin-top: 20px;padding-bottom: 10%" v-if="!isLoading">
          <div v-for="(item, index) in data.data" :key="index" class="text item">
            <div class="card-header">
              <div v-html="convertMarkdown(item.content)"></div>
            </div>
          </div>
        </el-card>
        <el-skeleton :rows="5" animated v-else/>
        <el-card  style="margin-top: 1%" >
                  <u-comment :config="config" @submit="submit" @like="like">
        </u-comment>
          </el-card>
      </el-main>

    </el-container>
    <el-backtop :right="100" :bottom="100" />
  </el-container>



</template>


<style>

.common-layout div .el-aside {
  top: 60px;
  position: sticky;
}


#top-mains {
  opacity: 0.8;
  position: fixed;
  padding-left: 0;
  padding-right: 0;
  width: 100%;
  height: 60px;
  right: 0;
  top: 0;
  z-index: 2;
}

#app .el-backtop{
 background-color: rgb(210, 109, 109);
}

</style>


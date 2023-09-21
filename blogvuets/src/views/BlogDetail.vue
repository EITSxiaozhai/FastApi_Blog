<script setup>
import {ref, onBeforeMount, onMounted, onBeforeUnmount, onUnmounted} from 'vue';
import {RouterLink, RouterView} from 'vue-router'
import {useRoute} from "vue-router";
import MarkdownIt from 'markdown-it';
import hljs from 'highlight.js';
import 'highlight.js/styles/default.css'; // Import the style you prefer
const route = useRoute()
import {useRouter} from "vue-router";
import {reactive} from "vue";
import backApi from '../Api/backApi.js';
import {Discount} from "@element-plus/icons-vue";
import {ChatDotRound, ChatLineRound, ChatRound} from '@element-plus/icons-vue'
import Fingerprint2 from "fingerprintjs2";

import emoji from '@/assets/emoji'
import { UToast, createObjectURL } from 'undraw-ui';

const value = ref()
const icons = [ChatRound, ChatLineRound, ChatDotRound]

const isLoading = ref(true); // 初始时，骨架屏可见





const router = useRouter()
const data = reactive({
  data: []
})


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

  readingProgress.value = scrollPercentage;
};

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
  console.log("vote function is called");
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

onMounted(() => {
  getAverageRating();
});

const submitRating = async () => {
  console.log("submitRating function is called"); // 添加这行日志
  try {
    // 调用 vote 函数提交评分
    await vote();
  } catch (error) {
    console.error(error);
  }
};

const config = reactive({
  user: {
    id: 1,
    username: 'jack',
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
const submit = ({ content, parentId, files, finish, reply }) => {
    let str = '提交评论:' + content + ';\t父id: ' + parentId + ';\t图片:' + files + ';\t被回复评论:'
  console.log(str, reply)

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
    UToast({ message: '评论成功!', type: 'info' })
  }, 200)
}
// 点赞按钮事件 将评论id返回后端判断是否点赞，然后在处理点赞状态
const like = (id, finish) => {
  console.log('点赞: ' + id)
  setTimeout(() => {
    finish()
  }, 200)
}

config.comments = [
  {
    id: '1',
    parentId: null,
    uid: '1',
    address: '来自上海',
    content:
      '缘生缘灭，缘起缘落，我在看别人的故事，别人何尝不是在看我的故事?别人在演绎人生，我又何尝不是在这场戏里?谁的眼神沧桑了谁?我的眼神，只是沧桑了自己[喝酒]',
    likes: 2,
    contentImg: 'https://gitee.com/undraw/undraw-ui/raw/master/public/docs/normal.webp',
    createTime: '1分钟前',
    user: {
      username: '落🤍尘',
      avatar: 'https://static.juzicon.com/avatars/avatar-200602130320-HMR2.jpeg?x-oss-process=image/resize,w_100',
      level: 6,
      homeLink: '/1'
    }
  }
]

</script>

<template>
  <div class="common-layout">
    <el-container>
      <el-header :class="{ 'hidden': scrollDirection === 'down' }" id="top-mains">
        <el-menu class="el-menu-demo" mode="horizontal">
          <h1 style="padding-left: 20px;font-size: 20px">
            <router-link to="/" style="text-decoration: none;">Exp1oit Blog</router-link>
          </h1>
          <el-sub-menu index="2-4" id="login">
            <template #title>登录</template>
            <el-menu-item index="2-4-1">
              <a href="" style="text-decoration:none">注册</a>
            </el-menu-item>
          </el-sub-menu>
        </el-menu>
        <el-progress :percentage="readingProgress" :show-text="false"/>
      </el-header>

      <el-card style="margin-top: 3%; display: flex; justify-content: center;" v-if="!isLoading">
        <div>
          <div style="display: flex; flex-direction: column; align-items: center;">
            <h1 style="font-size: 250%" class="el-title">欢迎来到我们的文章介绍页面</h1>
          </div>
          <div style="display: flex; justify-content: center; align-items: center;">
            <h3 style="padding-right: 50px">作者:</h3>
            <h3>总体评分:</h3>
            <el-rate style="padding-right: 50px" v-model="averageRating" allow-half disabled/>
            <h3 style="padding-right: 50px">发布时间：</h3>
          </div>
        </div>
      </el-card>
      <el-card v-else>
        <!-- 骨架屏 -->
        <el-skeleton :rows="5" animated/>
      </el-card>

      <el-container>
        <el-aside style="margin-top: 20px;position: sticky; ">
          <el-card>
            <div class="table-of-contents" v-if="!isLoading">
              <h2>目录</h2>
              <ul>
                <li v-for="(item, index) in tableOfContents" :key="index">
                  <a :href="item.anchor">{{ item.title }}</a>
                </li>
              </ul>
            </div>
            <el-skeleton :rows="5" animated v-else/>
            <el-card style="margin-top: 20px">
              <h4>喜欢该文章吗？</h4>
              <el-rate
                v-model="value"
                :icons="icons"
                :void-icon="ChatRound"
                :colors="['#409eff', '#67c23a', '#FF9900']"
                @change="submitRating"
              />
            </el-card>
          </el-card>
        </el-aside>

        <el-main>
          <el-card v-if="!isLoading">
            <div v-for="(item, index) in data.data" :key="index" class="text item">

                <div class="card-header">
                  <div v-html="convertMarkdown(item.content)"></div>
                </div>
            </div>

          </el-card>
          <el-skeleton :rows="5" animated v-else/>
        </el-main>
      </el-container>
        <u-comment :config="config" @submit="submit" @like="like">
    <!-- <template>导航栏卡槽</template> -->
    <!-- <template #info>用户信息卡槽</template> -->
    <!-- <template #card>用户信息卡片卡槽</template> -->
    <!-- <template #opearte>操作栏卡槽</template> -->
  </u-comment>
    </el-container>
  </div>
</template>



<style>

.common-layout div .el-aside {
  top: 60px;
  position: sticky;
}


#top-mains {
  opacity: 0.8;
  position: fixed;
  width: 100%;
  height: 60px;
  right: 0;
  top: 0;
  z-index: 2;
}

.table-of-contents {
  padding: 20px;
  background-color: #f2f2f2;
  border-radius: 4px;
}

.table-of-contents h2 {
  font-size: 18px;
  margin-bottom: 10px;
}

.table-of-contents ul {
  list-style: none;
  padding: 0;
}

.table-of-contents li {
  margin-bottom: 5px;
}


</style>


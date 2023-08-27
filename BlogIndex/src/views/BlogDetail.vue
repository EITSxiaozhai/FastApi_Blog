<script setup>
import { ref, onBeforeMount, onMounted, onBeforeUnmount, onUnmounted} from 'vue';
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


import {loadFull} from "tsparticles";

const particlesInit = async (engine) => {
  await loadFull(engine);
};

const particlesLoaded = async (container) => {
  console.log("Particles container loaded", container);
};


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
        toc.push({ level, title, anchor });
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
        toc.push({ level, title, anchor });
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
</script>

<template>

  <div class="common-layout">
    <el-container>
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
                <el-progress :percentage="readingProgress"  :show-text="false"/>
        </el-header>

      <el-container>
        <el-aside style="padding-top: 60px">
          <el-card>
            <div class="table-of-contents">
              <h2>目录</h2>
              <ul>
                <li v-for="(item, index) in tableOfContents" :key="index">
                  <a :href="item.anchor">{{ item.title }}</a>

                </li>
              </ul>
            </div>
          </el-card>
          </el-aside>

        <el-main style="margin-top: 40px">
          <div v-for="(item, index) in data.data" :key="index" class="text item">
            <el-card class="box-card">
              <template #header>
                <div class="card-header">
                  <h1><span>{{ item.title }}</span></h1>
                  <h1>作者:{{ item.author }}</h1>
                  <el-divider />
                  <div v-html="convertMarkdown(item.content)"></div>
                </div>
              </template>
            </el-card>
          </div>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>


<style>
#top-mains {
  opacity: 0.8;
  position: fixed;
  width: 100%;
  height:60px;
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


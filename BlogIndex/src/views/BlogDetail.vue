<script setup>
import {RouterLink, RouterView} from 'vue-router'
import {useRoute} from "vue-router";
import MarkdownIt from 'markdown-it';
const route = useRoute()
import axios from "axios";
import {useRouter} from "vue-router";
import {reactive} from "vue";
import backApi from '../Api/backApi.js';
import {Discount} from "@element-plus/icons-vue";

const router = useRouter()
const data = reactive({
  data: []
})



// 创建Markdown渲染器实例
const md = new MarkdownIt();

function convertMarkdown(markdownText) {
  return md.render(markdownText);
}


function getData() {
  const blogId = router.currentRoute.value.params.blogId;
  backApi.post(`/user/Blogid?blog_id=${blogId}`)
      .then(response => {
        data.data = response.data;
        console.log(data.data)
      })
      .catch(error => {
        console.error(error);
      });
}

getData()


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
      </el-header>

      <el-container>
        <el-aside>
          <el-card>
            测试侧栏
          </el-card>
        </el-aside>
        <el-container>
          <el-main>
            <div v-for="(item, index) in data.data" :key="index" class="text item">
              <el-card class="box-card">
                <template #header>
                  <div class="card-header">
                    <span>{{ item.title }}</span>
                    <el-button class="button" text>{{ item.author }}</el-button>
<div v-html="convertMarkdown(item.content)"></div>
                  </div>
                </template>
              </el-card>
            </div>
          </el-main>
        </el-container>
      </el-container>
    </el-container>
    <el-footer
        style="box-shadow:0 0 26px 0 #767697;background-image: linear-gradient(-225deg, #E3FDF5 0%, #FFE6FA 100%); margin-top: 20px">
      <el-row class="search-container">
        <el-col :span="6">
          <el-statistic title="共计访问人数" :value="268500"/>
        </el-col>
      </el-row>
    </el-footer>
  </div>
</template>


<style>

#top-mains {
  opacity: 0.8;
  position: fixed;
  height: 6rem;
  width: 100%;
  right: 0;
  top: 0;
  z-index: 999;
}


body {
  background-image: url('https://w.wallhaven.cc/full/zy/wallhaven-zyxvqy.jpg');
  background-size: cover;
  background-repeat: no-repeat;
  background-position: center;
//background-image: linear-gradient(to right, #74ebd5 0%, #9face6 100%); font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
}


</style>


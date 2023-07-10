<script setup>
import {RouterLink, RouterView} from 'vue-router'
import {useRoute} from "vue-router";
const  route = useRoute()
import axios from "axios";
import {useRouter} from "vue-router";
import {reactive} from "vue";

const  router = useRouter()
const data = reactive({
  data:[]
})
       function getData() {
const blogId = router.currentRoute.value.params.blogId;
  axios.post(`http://127.0.0.1:8000/blog/Blogid?blog_id=${blogId}`)
          .then(response => {
            data.data= response.data;
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
  <el-container id="top-mains">
    <el-header>
      <el-menu
          class="el-menu-demo"
          mode="horizontal"
      >
        <h1 style="padding-left: 20px;font-size: 20px">
          Exp1oit Blog</h1>
        <div id="Search_input" class="search-container">
          <el-input
              v-model="input1"
              class="w-50 m-2"
              size="large"
              placeholder="搜索你感兴趣的文章"
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
  </el-container>

<el-container style="margin-top: 50px">
  <el-main>

  <el-card class="box-card">
    <template #header>
      <div class="card-header">
        <span>Card name</span>
        <el-button class="button" text>Operation button</el-button>
      </div>
    </template>
    <div v-for="o in 100" :key="o" class="text item">{{ 'List item ' + o }}</div>
  </el-card>

  </el-main>
      <el-footer id="footer"
        style="box-shadow:0 0 26px 0 #767697;background-image: linear-gradient(-225deg, #E3FDF5 0%, #FFE6FA 100%);">
      <el-row class="search-container">
        <el-col :span="6">
          <el-statistic title="共计访问人数" :value="268500"/>
        </el-col>
      </el-row>
    </el-footer>
</el-container>

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


#footer {
  opacity: 0.8;
  position: relative;
  padding-left: 0;
  padding-right: 0;
}

</style>


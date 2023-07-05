<template>
      <el-aside>
        <el-card class="box-card">
          <div class="card-content">
            <img src="https://aliyuncdn.antdv.com/vue.png" alt="">
            个人介绍
          </div>
        </el-card>
      </el-aside>

  <div class="about">
    <div class="common-layout">
    <el-container>
      <el-main>
        <div v-for="blog in data" :key="blog.BlogId">
          <el-card class="box-card" style="margin-top: 10px">
      <h1>{{ blog.title }}</h1>
            <div class="box-card">
              <img :src="blog.BlogIntroductionPicture" alt="" style="">
            </div>
      <span>{{ blog.content }}</span>
      <p>作者: {{ blog.author }}</p>
          </el-card>
    </div>
      </el-main>
    </el-container>
  </div>
  </div>
</template>


<script>
import axios from 'axios';

export default {
  data() {
    return {
      data: [],
    };
  },
  created() {
    this.getData();
  },
  methods: {
    getData() {
      axios.get('http://127.0.0.1:8000/blog/BlogIndex')
          .then(response => {
            this.data = response.data;
          })
          .catch(error => {
            console.error(error);
          });
    },
  },
};
</script>


<style>

#app .about .common-layout .el-container .el-main div .box-card .el-card__body .box-card img{
 height:100% !important;
 width:100% !important;
}

#app{
 position:relative;
 top:78px;
}

</style>

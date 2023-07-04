<template>
  <div class="about" style="height: 9px">
    <div v-for="blog in data" :key="blog.BlogId">
      <el-divider/>
      <h2>{{ blog.title }}</h2>
      <span>{{ blog.content }}</span>
      <p>作者: {{ blog.author }}</p>
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
@media (min-width: 1024px) {
  .about {
    min-height: 100vh;
    display: flex;
    align-items: center;
  }
}
</style>

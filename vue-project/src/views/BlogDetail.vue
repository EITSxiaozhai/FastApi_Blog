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
      <div>
    <div v-for="blog in data.data" :key="blog.BlogId">
      <h1>{{ blog.title }}</h1>
      <p>{{ blog.content }}</p>
    </div>
  </div>
</template>

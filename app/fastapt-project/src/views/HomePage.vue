<template>
  <div id="home">
      <div>
    <h1>所有博客状态</h1>
    <ul>
      <li v-for="item in apiData" :key="item.id">
        <h1> {{ item[1]["title"] }} </h1>
      </li>
      <li v-for="item in apiData" :key="item.id">
      <h1>  {{ item[0]["title"] }} </h1>
      </li>
      <li v-for="item in apiData" :key="item.id">
       <h1> {{ item[2]["title"] }} </h1>
      </li>
    </ul>
  </div>
  </div>
</template>

<script>
import axios from 'axios'
// import HelloWorld from './components/HelloWorld.vue'
export default {
  data() {
    return {
      apiData: []
    }
  },
  async created() {
    try {
      const response = await axios.get('http://127.0.0.1:8000/blog/BlogIndex')
      this.apiData = response.data
    } catch (error) {
      console.log(error)
    }
  }
}
</script>



<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>

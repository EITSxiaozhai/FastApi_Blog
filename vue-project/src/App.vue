<template>
  <lay-layout className="example">
    <lay-header>{{ boo }}</lay-header>
    <lay-body>
      <lay-layout>
        <lay-side>{{ str }}</lay-side>
        <lay-body>
          {{ b}}
          <lay-button @click="handle"> 点击按钮</lay-button>
        </lay-body>
      </lay-layout>
    </lay-body>
    <lay-footer>{{ a }}</lay-footer>
  </lay-layout>
</template>

<script>
import {ref} from 'vue';

export default {
  setup() {
    let a = ref(1);
    let b = ref(2);
    let str = ref("abc");
    let boo = ref(true);
    const handle = () => {
      console.log("handle2")
      a.value++;
      b.value++;
      str.value += '--';
      boo.value = !boo.value;
    }
    return {
      a,
      b,
      handle,
      str,
      boo,
    }
  }
}
</script>
<style>



.example .layui-footer,
.example .layui-header {
  line-height: 60px;
  text-align: center;
  background: #87ca9a;
  color: white;
}

.example .layui-side {
  display: flex;
  height: 100%;
  background: #77c38c;
  align-items: center;
  justify-content: center;
  color: white;
}




.example .layui-body {
  display: flex;
  background: #b6effb;
  height: 100%;
  align-items: center;
  justify-content: center;
  color: black;
}
</style>
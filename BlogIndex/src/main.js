import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import Particles from "vue3-particles"
import * as ElementPlusIconsVue from '@element-plus/icons-vue'


const app = createApp(App)

for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}
app.use(Particles)
app.use(router)

app.mount('#app')
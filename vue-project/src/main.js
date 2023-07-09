import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import Particles from "vue3-particles";

createApp(App).use(Particles);



const app = createApp(App).use(Particles)

app.use(router)


app.mount('#app')
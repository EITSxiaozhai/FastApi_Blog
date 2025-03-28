import {createApp} from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import UndrawUi from 'undraw-ui'
import 'undraw-ui/dist/style.css'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import {createHead} from '@unhead/vue'
import "animate.css"
import 'animate.css/animate.compat.css'
import 'element-plus/theme-chalk/display.css'
import 'element-plus/theme-chalk/dark/css-vars.css'
import './assets/css/css-vars.css'

const head = createHead()
createApp(App).use(store).use(router).use(UndrawUi).use(ElementPlus).use(head).mount('#app')

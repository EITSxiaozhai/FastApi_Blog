import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import UndrawUi from 'undraw-ui'
import 'undraw-ui/dist/style.css'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'


// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
createApp(App).use(store).use(router).use(UndrawUi).use(ElementPlus).mount('#app')

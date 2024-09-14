import {createApp} from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import UndrawUi from 'undraw-ui'
import 'undraw-ui/dist/style.css'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import {createHead} from '@unhead/vue'
import { createMetaManager } from 'vue-meta'
import "animate.css"
import 'animate.css/animate.compat.css'
import 'element-plus/theme-chalk/display.css'


const head = createHead()
createApp(App).use(store).use(router).use(createMetaManager(false, {
    meta: { tag: 'meta', nameless: true }
})).use(UndrawUi).use(ElementPlus).use(head).mount('#app')

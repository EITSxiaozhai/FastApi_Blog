import {fileURLToPath, URL} from 'node:url'
import {defineConfig} from 'vite'
import vue from '@vitejs/plugin-vue'
import vike from 'vike/plugin'
import vercel from 'vite-plugin-vercel'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import {ElementPlusResolver} from 'unplugin-vue-components/resolvers'

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [
        vue(),
        vike(),
        vercel(),
        AutoImport({
            resolvers: [ElementPlusResolver()],
        }),
        Components({
            resolvers: [ElementPlusResolver()],
        }),
    ],
    resolve: {
        alias: {
            '@': fileURLToPath(new URL('./src', import.meta.url))
        }
    },
    server: {
        host: '0.0.0.0'
    },
    ssr: {
        noExternal: ['axios', 'vue-router', 'vuex', 'element-plus', /^@element-plus/]
    },
    define: {
        'process.env.NODE_ENV': JSON.stringify(process.env.NODE_ENV || 'production'),
        'global': 'globalThis'
    }
})
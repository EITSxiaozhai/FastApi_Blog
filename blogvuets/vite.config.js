import {fileURLToPath, URL} from 'node:url'

import {defineConfig} from 'vite'
import vue from '@vitejs/plugin-vue'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import {ElementPlusResolver} from 'unplugin-vue-components/resolvers'
import dotenv from 'dotenv';
// https://vitejs.dev/config/
dotenv.config();

export default defineConfig({
    mode: process.env.NODE_ENV,
    plugins: [
        vue(),
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
    build: {
    // 将.env.production中的变量注入到构建中
    envDir: process.cwd(),
    },
    optimizeDeps: {
    exclude: ['@unhead/vue'],
  },
})
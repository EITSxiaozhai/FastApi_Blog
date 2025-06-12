import {fileURLToPath, URL} from 'node:url'
import {defineConfig} from 'vite'
import vue from '@vitejs/plugin-vue'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import {ElementPlusResolver} from 'unplugin-vue-components/resolvers'
import dotenv from 'dotenv'
import { resolve } from 'path'

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
        ssr: true,
        envDir: process.cwd(),
        rollupOptions: {
            input: {
                main: './src/main.js',
                server: './src/entry-server.js',
                client: './src/entry-client.js'
            },
            output: {
                format: 'esm'
            }
        }
    },
    optimizeDeps: {
        exclude: ['@unhead/vue'],
    },
})
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
                main: resolve(__dirname, 'index.html'),
                server: resolve(__dirname, 'src/entry-server.js'),
                client: resolve(__dirname, 'src/entry-client.js')
            },
            output: {
                entryFileNames: 'assets/[name].js',
                chunkFileNames: 'assets/[name].js',
                assetFileNames: 'assets/[name].[ext]',
                format: 'es'
            }
        },
        commonjsOptions: {
            include: [/axios/, /vue-router/, /vuex/, /node_modules/]
        },
        sourcemap: false,
        minify: 'terser'
    },
    optimizeDeps: {
        exclude: ['@unhead/vue'],
        include: ['axios', 'vue-router', 'vuex']
    },
    ssr: {
        noExternal: ['axios', 'vue-router', 'vuex', 'element-plus', /^@element-plus/],
        external: []
    },
    define: {
        'process.env.NODE_ENV': JSON.stringify(process.env.NODE_ENV || 'production'),
        'global': 'globalThis'
    }
})
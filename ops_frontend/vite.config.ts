import {defineConfig} from 'vite';
import vue from '@vitejs/plugin-vue';
import VueSetupExtend from 'vite-plugin-vue-setup-extend';
import AutoImport from 'unplugin-auto-import/vite';
import Components from 'unplugin-vue-components/vite';
import {ElementPlusResolver} from 'unplugin-vue-components/resolvers';
import WindiCSS from 'vite-plugin-windicss';
import Icons from 'unplugin-icons/vite';
import IconsResolver from 'unplugin-icons/resolver'
import path from "path";

export default defineConfig({
    base: './',
    resolve: {
        alias: {
            // 设置别名
            '@': path.resolve(__dirname, './src')
        },
    },
    plugins: [
        vue(),
        VueSetupExtend(),
        AutoImport({
            resolvers: [ElementPlusResolver()]
        }),
        Components({
            resolvers: [
                ElementPlusResolver(),
                IconsResolver()
            ]
        }),
        Icons({
            autoInstall: true }),
        WindiCSS()
    ],
    optimizeDeps: {
        include: ['schart.js']
    },
    server: {
        host: "0.0.0.0"
    },
    envDir: "env"
});

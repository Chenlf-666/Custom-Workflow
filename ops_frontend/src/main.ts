import {createApp} from 'vue';
import ElementPlus from 'element-plus';
import 'element-plus/dist/index.css';
import * as ElementPlusIconsVue from '@element-plus/icons-vue';
import 'element-plus/theme-chalk/dark/css-vars.css'
import zhCn from 'element-plus/es/locale/lang/zh-cn';
import App from './App.vue';
import router from './router';
import 'element-plus/dist/index.css';
import '@/assets/css/icon.css';
import store from '@/store';
import 'virtual:windi.css';
import 'virtual:windi-devtools';
// import 'default-passive-events';
// import '@/utils/browserPatch'

import {permissionDirective} from './directives/permission'

const app = createApp(App)

// 注册elementplus图标
for (const [name, component] of Object.entries(ElementPlusIconsVue)) {
    app.component(name, component);
}

app.use(ElementPlus, {
    locale: zhCn,
});

app.use(store);
app.use(router);

// 自定义权限指令
app.directive('permission', permissionDirective)


app.mount('#app')
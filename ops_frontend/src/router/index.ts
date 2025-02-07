import {createRouter, createWebHashHistory, RouteRecordRaw} from "vue-router";
import Index from "@/views/index.vue";
import axios from "@/axios";
import jwt_decode, {JwtPayload} from "jwt-decode";
import {toast} from "../utils";

const createRoute = (path: string, name: string, title: string, chunkName: string) => ({
    path,
    name,
    meta: { title },
    component: () => import(/* webpackChunkName: chunkName */ `@/views/${path}.vue`)
});

const routes: RouteRecordRaw[] = [
    {
        path: '/',
        redirect: '/dashboard'
    },
    {
        path: "/",
        name: "Index",
        component: Index,
        children: [
            createRoute("dashboard", "dashboard", "系统首页", "dashboard"),
            createRoute("permission", "permission", "权限管理", "permission"),
            createRoute("profile", "profile", "个人中心", "user"),
            createRoute("users", "用户管理", "用户管理", ""),
            createRoute("log", "日志管理", "日志管理", ""),
            createRoute("customWorkflows", "工作流管理", "工作流管理", ""),
            // createRoute("cusWorkflowDetail", "工作流详情", "工作流详情", ""),
            createRoute("worksheet", "工单管理", "工单管理", ""),
            ...Array.from({ length: 8 }, (_, i) => createRoute(`worksheet_${i + 1}`, `worksheet_${i + 1}`, `worksheet_${i + 1}`, "worksheet")),
            {
                path: '/customWorkflows/detail',
                name: '工作流详情',
                meta: {
                    title: '工作流详情'
                },
                component: () => import('@/views/cusWorkflowDetail.vue')
            },

        ]
    },
    {
        path: "/login",
        name: "Login",
        meta: {
            title: '登录'
        },
        component: () => import( /* webpackChunkName: "login" */ "@/views/login.vue")
    },
    {
        path: '/403',
        name: '403',
        meta: {
            title: '没有权限'
        },
        component: () => import(/* webpackChunkName: "403" */ '@/views/403.vue')
    },
    {
        path: '/:catchAll(.*)',
        name: '404',
        meta: {
            title: '页面不存在'
        },
        component: () => import(/* webpackChunkName: "404" */ '@/views/404.vue')
    }
];


const router = createRouter({
    history: createWebHashHistory(),
    routes
});

// 路由守卫[导航守卫]
router.beforeEach(async (to, from) => {
    let refresh_token = localStorage.getItem("refresh");
    // const expire = Number(localStorage.getItem("expire"));
    // const now = new Date().getTime();

    //每次页面操作，用refresh token刷新token
    if(refresh_token){
        await axios.post(`/auth/refresh`, {
        "refresh": refresh_token, // token: token,
        }).then(res => {
            localStorage.setItem('token', res.data.access);
            const decoded = jwt_decode<JwtPayload>(res.data.access || '') || null;
            localStorage.setItem("expire", ((decoded.exp || 0) * 1000).toString());
        }).catch(error => {
            refresh_token = "";
            localStorage.clear();
            return '/login';
        })
    }

    //没有登录跳转到登录页面 or Token过期后要求重新登录
    if ((!refresh_token && to.path != '/login')) {
        localStorage.setItem('intendedPath', to.fullPath);
        return '/login';
    }

    //防止重复登录
    if (refresh_token && to.path == '/login') {
        return '/';
    }

    // If the user just logged in, redirect them to the intended path
    const intendedPath = localStorage.getItem('intendedPath');
    if (intendedPath && refresh_token) {
        localStorage.removeItem('intendedPath');
        return intendedPath;
    }

});

export default router;

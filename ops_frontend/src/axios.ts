import axios from "axios";
import {toast} from '@/utils/';
import router from "@/router";

interface configObj {
    baseURL: string,
    downloadURL: string,
    webSocketURL: string
}
let configure: configObj = {
    baseURL: '',
    downloadURL: '',
    webSocketURL: ''
};
export const config = (() => {
    const currentUrl = window.location.href;
    const url = new URL(currentUrl);
    const hostname = `${url.hostname}`;
    const protocol = `${url.protocol}`;
    if (hostname === 'localhost') {
        configure.baseURL = import.meta.env.VITE_URL_BASE
        configure.downloadURL = import.meta.env.VITE_URL_DOWNLOAD_LOG
        configure.webSocketURL = import.meta.env.VITE_URL_LOG
        return configure;
    } else {
        configure.baseURL = protocol + "//" + hostname + "/v1/api/"
        configure.downloadURL = protocol + "//" + hostname + "/download/log/"
        configure.webSocketURL = "wss://" + hostname + "/v1/api/ws/log/"
        return configure;
    }
})();


const service = axios.create({
    baseURL: "http://127.0.0.1:8000",
});

service.defaults.timeout = 10000;

// 添加请求拦截器
service.interceptors.request.use(function (config) {
    // 在发送请求之前做些什么
    let token = localStorage.token;
    if (token) {
        // @ts-ignore
        config.headers.Authorization = 'Bearer ' + token;
    }
    return config;
}, function (error) {
    // 对请求错误做些什么
    return Promise.reject(error);
});

// 添加响应拦截器
service.interceptors.response.use(function (response) {
    // 对响应数据做点什么
    return response;
}, function (error) {
    // 对响应错误做点什么
    if (error.response.status === 401) {
        // 如果出现403， 清除本地token缓存，强制重新登录
        localStorage.clear();
        toast("认证过期，请重新登录！", 'error');
        router.replace({
            path: '/login'
        })
        return Promise.reject(error);
    }
    if (error.response.status >= 500) {
        // 如果出现403， 清除本地token缓存，强制重新登录
        toast("服务器内部错误！", 'error');
        return Promise.reject(error);
    }
    if (error.response.status === 404) {
        // 如果出现403， 清除本地token缓存，强制重新登录
        toast(`Code: 404 <br> Error msg: Not Found!"`, 'error', true)
        return Promise.reject(error);
    }
    toast(`Code: ${error.response.status} <br> Error: ${error.response.data.message}`, 'error', true)
    return Promise.reject(error);
});

export default service
import axios from 'axios';

const baseURL = process.env.VUE_APP_API_URL; // 使用环境变量设置的 API 地址

const ajax = axios.create({
    baseURL: baseURL
});

export default ajax;
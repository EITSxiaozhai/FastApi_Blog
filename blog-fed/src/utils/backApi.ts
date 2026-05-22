import axios from 'axios';
import router from '@/router'; // 确认路由实例导入正确


const apis = {
  production: 'https://blogapi-traefik.exploit-db.xyz/api/',
  development: 'http://127.0.0.1:8000/api/',
  test: 'http://192.168.0.150:49200/api/'
};

const baseURL = process.env.NODE_ENV === 'production' ? apis.production : apis.development;

const backApi = axios.create({
  baseURL: baseURL
});

// 添加响应拦截器
backApi.interceptors.response.use(
  response => {
    return response;
  },
  error => {
    if (error.response) {
      const status = error.response.status;
      if (status === 404 || status === 500) {
        // 路由到错误页面
        router.push({
          name: 'errorPage',
          query: {
            statusCode: status,
            message: error.response.data.detail || 'An unexpected error occurred' // 可带上后端返回的错误信息
          }
        });
      }
    } else {
      // 处理网络错误或请求未发出去的情况
      console.error('Network/Request Error:', error.message);
    }
    return Promise.reject(error);
  }
);

export default backApi;
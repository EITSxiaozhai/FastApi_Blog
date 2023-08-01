import axios from 'axios';

const apis = {
  production: 'http://192.168.0.150:49200/api', // 线上 (生成环境)
  development: 'http://127.0.0.1:8000/api/', // 本地 (开发环境)
  test: 'http://192.168.0.150:49200/api/' // (测试环境)
};

const baseURL = process.env.NODE_ENV === 'production' ? apis.production : apis.development;

const ajax = axios.create({
  baseURL: baseURL
});

export default ajax;
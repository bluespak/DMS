// 파일 최상단에 import
import axios from 'axios';

// Axios 인스턴스 생성
const api = axios.create({
  baseURL: process.env.REACT_APP_API_BASE_URL || '/api',
  timeout: 10000,
  withCredentials: true,
});

// API 요청 인터셉터 (로그 전송 로직 제거)
api.interceptors.request.use(
  config => {
    const requestInfo = {
      method: config.method,
      url: config.url,
      data: config.data,
      headers: config.headers,
    };
    console.log('📤 API 요청:', requestInfo.method, requestInfo.url);
    return config;
  },
  error => Promise.reject(error)
);

// 응답 인터셉터 (응답 후에 실행)
api.interceptors.response.use(
  (response) => {
    const responseInfo = {
      status: response.status,
      statusText: response.statusText,
      url: response.config.url,
      method: response.config.method?.toUpperCase(),
      dataSize: response.data ? JSON.stringify(response.data).length : 0
    };

    console.log('📥 API 응답:', responseInfo.status, responseInfo.url);
     
    return response;
  },
  (error) => {
    const errorInfo = {
      status: error.response?.status,
      statusText: error.response?.statusText,
      url: error.config?.url,
      method: error.config?.method?.toUpperCase(),
      message: error.message
    };

    console.error('❌ 응답 에러:', errorInfo.status, errorInfo.message);
    
    return Promise.reject(error);
  }
);

// 요청 시간 측정을 위한 미들웨어
api.interceptors.request.use(
  (config) => {
    config.metadata = { startTime: new Date().getTime() };
    return config;
  }
);

api.interceptors.response.use(
  (response) => {
    response.config.metadata.endTime = new Date().getTime();
    return response;
  },
  (error) => {
    if (error.config) {
      error.config.metadata = error.config.metadata || {};
      error.config.metadata.endTime = new Date().getTime();
    }
    return Promise.reject(error);
  }
);


export default api;
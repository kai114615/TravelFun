import axios from 'axios';

// 創建 axios 實例
const request = axios.create({
  baseURL: 'http://localhost:8000', // Django 後端 API 地址
  timeout: 15000, // 請求超時時間
  headers: {
    'Content-Type': 'application/json',
  },
});

// 請求攔截器
request.interceptors.request.use(
  (config) => {
    // 從 localStorage 獲取 token
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 響應攔截器
request.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    if (error.response) {
      if (error.response.status === 401) {
        // Token 過期，嘗試使用 refresh token
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          try {
            const response = await axios.post('http://localhost:8000/api/token/refresh/', {
              refresh: refreshToken
            });

            if (response.data.access) {
              localStorage.setItem('access_token', response.data.access);
              // 重試原始請求
              error.config.headers.Authorization = `Bearer ${response.data.access}`;
              return request(error.config);
            }
          } catch (refreshError) {
            // refresh token 也過期，清除所有 token
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            window.location.href = '/login';
          }
        }
      }
    }
    return Promise.reject(error);
  }
);

export { request };

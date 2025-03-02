import axios from 'axios';
import router from '@/router';

// 創建 axios 實例
const api = axios.create({
  baseURL: 'http://127.0.0.1:8000', // 使用 IP 而不是 localhost
  timeout: 10000, // 增加超時時間
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  withCredentials: false // 修改為 false，因為我們使用 JWT
});

// 請求攔截器
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      // 確保 headers 存在
      config.headers = config.headers || {};
      // 使用 Bearer scheme
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// 響應攔截器
api.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    // 如果是 401 錯誤（未授權）且不是重試請求
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // 嘗試使用 refresh token 獲取新的 access token
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post('http://127.0.0.1:8000/api/token/refresh/', {
            refresh: refreshToken
          }, {
            headers: {
              'Content-Type': 'application/json',
              'Accept': 'application/json'
            }
          });

          if (response.data.access) {
            localStorage.setItem('access_token', response.data.access);
            // 更新原始請求的 Authorization header
            originalRequest.headers.Authorization = `Bearer ${response.data.access}`;
            // 重試原始請求
            return api(originalRequest);
          }
        }
      } catch (refreshError) {
        console.error('Token refresh failed:', refreshError);
        // 清除所有認證信息
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        // 重定向到登入頁面，並保存當前路徑
        router.push({
          path: '/login',
          query: { redirect: router.currentRoute.value.fullPath }
        });
      }
    }

    // 處理其他錯誤
    if (error.response) {
      switch (error.response.status) {
        case 403:
          console.error('權限不足:', error.response.data);
          break;
        case 404:
          console.error('資源不存在:', error.response.data);
          break;
        case 500:
          console.error('伺服器錯誤:', error.response.data);
          break;
        default:
          console.error('請求錯誤:', error.response.data);
      }
    } else if (error.request) {
      console.error('無法連接到伺服器，請檢查網絡連接');
    } else {
      console.error('請求配置錯誤:', error.message);
    }

    return Promise.reject(error);
  }
);

export default api;

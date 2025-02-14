import axios from 'axios';

// API 基礎配置
const API_BASE_URL = 'http://127.0.0.1:8000';

// 創建 axios 實例
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  // 允許跨域請求攜帶憑證
  withCredentials: true,
});

// 請求攔截器
api.interceptors.request.use(
  (config) => {
    // 打印完整的請求配置
    console.log('發送請求:', {
      url: config.url,
      method: config.method,
      headers: config.headers,
      data: JSON.stringify(config.data, null, 2), // 格式化輸出
      baseURL: config.baseURL,
      withCredentials: config.withCredentials,
    });

    const token = localStorage.getItem('access_token');
    if (token)
      config.headers.Authorization = `Bearer ${token}`;

    return config;
  },
  (error) => {
    console.error('請求攔截器錯誤:', error);
    return Promise.reject(error);
  },
);

// 響應攔截器
api.interceptors.response.use(
  (response) => {
    // 打印完整的響應數據
    console.log('收到響應:', {
      status: response.status,
      statusText: response.statusText,
      headers: response.headers,
      data: JSON.stringify(response.data, null, 2), // 格式化輸出
      config: {
        url: response.config.url,
        method: response.config.method,
        data: response.config.data,
      },
    });
    return response;
  },
  async (error) => {
    // 打印詳細的錯誤信息
    console.error('響應錯誤:', {
      message: error.message,
      response: {
        data: error.response?.data,
        status: error.response?.status,
        statusText: error.response?.statusText,
        headers: error.response?.headers,
      },
      request: {
        url: error.config?.url,
        method: error.config?.method,
        data: error.config?.data,
        headers: error.config?.headers,
      },
    });

    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      console.log('嘗試刷新 token...');

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post(
                    `${API_BASE_URL}/api/token/refresh/`,
                    { refresh: refreshToken },
                    { withCredentials: true },
        );

        const { access } = response.data;
        localStorage.setItem('access_token', access);
        console.log('token 刷新成功');

        originalRequest.headers.Authorization = `Bearer ${access}`;
        return api(originalRequest);
      }
      catch (refreshError) {
        console.error('token 刷新失敗:', refreshError);
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  },
);

// API 端點
export const AUTH_API = {
  register: (data) => {
    console.log('調用註冊 API，發送數據:', JSON.stringify(data, null, 2));
    return api.post('/api/user/register/', data);
  },
  login: (data) => {
    console.log('調用登入 API，發送數據:', JSON.stringify(data, null, 2));
    return api.post('/api/user/signin/', data);
  },
  logout: () => api.post('/api/user/logout/'),
  checkAuth: () => api.get('/api/user/check-auth/'),
};

export const USER_API = {
  getProfile: () => api.get('/api/user/profile/'),
  updateProfile: (data) => {
    console.log('調用更新資料 API，發送數據:', JSON.stringify(data, null, 2));
    return api.put('/api/user/profile/', data);
  },
};

export default api;

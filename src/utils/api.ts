import type { AxiosResponse } from 'axios';
import axios from 'axios';
import type { Product } from '@/types';
import { Toast } from '@/utils/global';

interface Data {
  data: Product
}

const { VITE_URL, VITE_PATH } = import.meta.env;

// 根據環境變數設定 baseURL
const BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
const API_PATH = import.meta.env.VITE_PATH || 'api/v1'; // 添加默認值

// 檢查服務器狀態
async function checkServerStatus() {
  try {
    const response = await fetch(`${BASE_URL}/api/health-check/`, {
      method: 'GET',
      mode: 'cors',
      credentials: 'include',
      headers: {
        Accept: 'application/json',
      },
    });

    if (!response.ok) {
      console.error('Health check failed with status:', response.status);
      const text = await response.text();
      console.error('Response text:', text);
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data.status === 'ok';
  }
  catch (error: any) {
    console.error('Health check failed:', error);
    errorMsg(
      '服務器檢查失敗',
      `無法連接到後端服務器 (${BASE_URL})，請檢查：\n`
      + '1. Django 服務器是否已啟動 (python manage.py runserver)\n'
      + '2. 服務器地址是否正確\n'
      + '3. CORS 設定是否正確\n'
      + '4. Django 是否已安裝必要的套件 (corsheaders, rest_framework)\n'
      + `5. 錯誤信息: ${error.message}`,
    );
    return false;
  }
}

// 創建 axios 實例
const request = axios.create({
  baseURL: BASE_URL,
  timeout: 10000,
  withCredentials: true, // 允許跨域請求攜帶憑證
  headers: {
    'Content-Type': 'application/json',
    'X-Requested-With': 'XMLHttpRequest',
  },
});

export function successMsg(title: string, text?: string) {
  return Toast.fire({
    icon: 'success',
    title,
    text,
  });
}

export function errorMsg(title: string, text?: string) {
  return Toast.fire({
    icon: 'error',
    title,
    text,
  });
}

// 請求攔截器
request.interceptors.request.use(
  async (config) => {
    try {
      // 只在非健康檢查請求時檢查服務器狀態
      if (!config.url?.includes('health-check')) {
        const isServerOnline = await checkServerStatus();
        if (!isServerOnline)
          throw new Error('後端服務器未啟動或無法訪問');
      }

      // 從 localStorage 獲取 token
      const token = localStorage.getItem('access_token');
      console.log('請求攔截器中的 token:', token);

      if (token)
        config.headers.Authorization = `Bearer ${token}`;

      // 從 cookie 中獲取 CSRF token
      const csrfToken = document.cookie.replace(
        /(?:(?:^|.*;\s*)csrftoken\s*=\s*([^;]*).*$)|^.*$/,
        '$1',
      );

      if (csrfToken)
        config.headers['X-CSRFToken'] = csrfToken;

      // 添加時間戳防止緩存
      if (config.method === 'get')
        config.params = { ...config.params, _t: Date.now() };

      return config;
    }
    catch (error: any) {
      errorMsg('請求配置錯誤', error.message);
      return Promise.reject(error);
    }
  },
  (error) => {
    errorMsg('請求配置錯誤', error.message);
    return Promise.reject(error);
  },
);

// 響應攔截器
request.interceptors.response.use(
  (res: AxiosResponse) => {
    // JWT token 處理
    if (res.data?.access)
      localStorage.setItem('access_token', res.data.access);

    if (res.data?.refresh)
      localStorage.setItem('refresh_token', res.data.refresh);

    return res;
  },
  async (error) => {
    if (error.response?.status === 401) {
      // 清除無效的 token
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      errorMsg('登入已過期', '請重新登入');
    }
    return Promise.reject(error);
  },
);

const api = {
  user: {
    signin: '/api/token/',
    register: '/api/user/register/',
    logout: '/api/user/logout/',
    checkSigin: '/api/user/check-auth/',
    refreshToken: '/api/token/refresh/',
    product: `/api/${API_PATH}/product`,
    cart: `/api/${API_PATH}/cart`,
    coupon: `/api/${API_PATH}/coupon`,
    order: `/api/${API_PATH}/order`,
    pay: `/api/${API_PATH}/pay`,
  },
  admin: {
    product: `/api/${API_PATH}/admin/product`,
    upload: `/api/${API_PATH}/admin/upload`,
    order: `/api/${API_PATH}/admin/order`,
    coupon: `/api/${API_PATH}/admin/coupon`,
  },
  forum: {
    posts: '/api/forum/',
    like: (postId: number) => `/api/forum/${postId}/like/`,
    comment: (postId: number) => `/api/forum/${postId}/add_comment/`,
    categories: '/api/forum/categories/',
    moderators: '/api/forum/moderators/',
  },
};

// API USER
async function apiUserRegister(data: FormData) {
  try {
    // 先檢查服務器狀態
    const isServerOnline = await checkServerStatus();
    if (!isServerOnline) {
      errorMsg(
        '連接失敗',
        '後端服務器未啟動或無法訪問，請檢查：\n'
        + '1. Django 服務器是否已啟動 (python manage.py runserver)\n'
        + '2. 端口 8000 是否被占用\n'
        + '3. 防火牆設置是否正確\n'
        + '4. Django settings.py 中的 CORS 設定是否正確\n'
        + '5. Django 是否已安裝 django-cors-headers',
      );
      throw new Error('後端服務器未啟動或無法訪問');
    }

    // 檢查 FormData 內容
    console.log('準備發送的註冊數據:');
    for (const [key, value] of data.entries()) {
      if (value instanceof File) {
        console.log(`${key}:`, {
          name: value.name,
          type: value.type,
          size: value.size,
        });
      }
      else {
        console.log(`${key}:`, value);
      }
    }

    const response = await request.post(api.user.register, data, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    console.log('註冊響應:', response.data);

    if (response.data?.success)
      successMsg('註冊成功', '歡迎加入！');

    return response;
  }
  catch (error: any) {
    console.error('Registration error:', error);
    if (error.response) {
      // 服務器回應了錯誤
      errorMsg(
        '註冊失敗',
        error.response.data?.message || '註冊失敗，請稍後重試',
      );
    }
    else if (error.request) {
      // 請求發出但沒有收到回應
      errorMsg(
        '連接失敗',
        '無法連接到後端服務器，請檢查：\n'
        + '1. 後端服務器是否啟動 (http://127.0.0.1:8000)\n'
        + '2. CORS 設定是否正確\n'
        + '3. 網路連接是否正常\n'
        + '4. 瀏覽器控制台是否有其他錯誤',
      );
    }
    else {
      // 請求配置出錯
      errorMsg('請求錯誤', error.message);
    }
    throw error;
  }
}
async function apiUserSignin(data: any) {
  try {
    console.log('開始登入...');

    const response = await request.post(api.user.signin, data, {
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    });

    console.log('登入響應:', response.data);

    if (response.data?.access) {
      // 保存 token 到 localStorage
      localStorage.setItem('access_token', response.data.access);
      if (response.data.refresh)
        localStorage.setItem('refresh_token', response.data.refresh);

      // 登入成功後顯示成功消息
      successMsg('登入成功', '歡迎回來！');
    }
    return response;
  }
  catch (error: any) {
    console.error('登入錯誤:', error);
    // 清除可能存在的無效 token
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');

    if (error.response)
      errorMsg('登入失敗', error.response.data?.detail || '帳號或密碼錯誤');
    else if (error.request)
      errorMsg('連接失敗', '無法連接到後端服務器');
    else
      errorMsg('請求錯誤', error.message);

    throw error;
  }
}
const apiUserLogout = () => request.post(api.user.logout);
async function apiUserCheckSignin() {
  try {
    const token = localStorage.getItem('access_token');
    if (!token)
      return { data: { success: false, isAuthenticated: false } };

    const response = await request.get(api.user.checkSigin);
    return response;
  }
  catch (error: any) {
    console.error('Check signin error:', error);
    if (error.response?.status === 401 || error.response?.status === 403) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      return { data: { success: false, isAuthenticated: false } };
    }
    throw error;
  }
}
const apiUserGetAllProducts = () => request.get(`${api.user.product}s/all`);
function apiUserGetProducts(category: string = '') {
  if (category)
    return request.get(`${api.user.product}s?category=${category}`);

  return request.get(`${api.user.product}s`);
}
const apiUSerGetProduct = (id: string) => request.get(`${api.user.product}/${id}`);
const apiUserGetCarts = () => request.get(api.user.cart);
const apiUserPostCart = (data: any) => request.post(api.user.cart, data);
const apiUserDelCart = (id: string) => request.delete(`${api.user.cart}/${id}`);
const apiUserDelCarts = () => request.delete(`${api.user.cart}/s`);
const apiUserPostCoupon = (data: any) => request.post(api.user.coupon, data);
const apiUserGetOrder = (id: string) => request.get(`${api.user.order}/${id}`);
const apiUserPostOrder = (data: any) => request.post(api.user.order, data);
const apiUserPostPay = (id: string) => request.post(`${api.user.pay}/${id}`);

// API Admin
const apiAdminGetProducts = (page: number) => request.get(`${api.admin.product}s?page=${page}`);
const apiAdminGetAllProducts = () => request.get(`${api.admin.product}s/all`);
const apiAdminPostProduct = (data: Data) => request.post(api.admin.product, data);
const apiAdminPutProduct = (id: string, data: Data) => request.put(`${api.admin.product}/${id}`, data);
const apiAdminDelProduct = (id: string) => request.delete(`${api.admin.product}/${id}`);
function apiAdminUploadImage(formData: FormData) {
  return request.post(api.admin.upload, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
}
const apiAdminGetOrders = () => request.get(`${api.admin.order}s`);
const apiAdminPutOrder = (id: string, data: any) => request.put(`${api.admin.order}/${id}`, data);
const apiAdminDelOrder = (id: string) => request.delete(`${api.admin.order}/${id}`);
const apiAdminDelOrders = () => request.delete(`${api.admin.order}s/all`);
const apiAdminGetCoupons = () => request.get(`${api.admin.coupon}s`);
const apiAdminPostCoupon = (data: any) => request.post(`${api.admin.coupon}`, data);
const apiAdminPutCoupon = (id: string, data: any) => request.put(`${api.admin.coupon}/${id}`, data);
const apiAdminDelCoupon = (id: string) => request.delete(`${api.admin.coupon}/${id}`);

// Forum API functions
export const apiForumGetPosts = () => request.get(api.forum.posts);
export const apiForumGetPost = (id: number) => request.get(`${api.forum.posts}${id}/`);
export async function apiForumToggleLike(postId: number) {
  try {
    const response = await request.post(`${api.forum.like(postId)}`);
    return response;
  }
  catch (error: any) {
    console.error('按讚失敗:', error);
    throw error;
  }
}

export async function apiForumAddComment(postId: number, content: string) {
  try {
    const response = await request.post(api.forum.comment(postId), { content });
    if (response.data.status === 'success')
      successMsg('評論發表成功');

    return response;
  }
  catch (error: any) {
    console.error('發表評論失敗:', error);
    if (error.response?.status === 401)
      errorMsg('請先登入', '需要登入才能發表評論');
    else
      errorMsg('發表失敗', error.response?.data?.message || '請稍後再試');

    throw error;
  }
}

export const apiForumGetComments = (postId: number) => request.get(`${api.forum.posts}${postId}/comments/`);

export async function apiForumDeleteComment(commentId: number) {
  try {
    const response = await request.delete(`${api.forum.posts}comments/${commentId}/`);
    if (response.data.status === 'success')
      successMsg('評論已刪除');

    return response;
  }
  catch (error: any) {
    console.error('刪除評論失敗:', error);
    errorMsg('刪除失敗', error.response?.data?.message || '請稍後再試');
    throw error;
  }
}

export const apiForumGetCategories = () => request.get(api.forum.categories);
export const apiForumGetModerators = () => request.get(api.forum.moderators);

export {
  api,
  apiAdminGetAllProducts,
  apiAdminGetProducts,
  apiAdminPostProduct,
  apiAdminPutProduct,
  apiAdminDelProduct,
  apiAdminUploadImage,
  apiAdminGetOrders,
  apiAdminPutOrder,
  apiAdminDelOrder,
  apiAdminDelOrders,
  apiAdminGetCoupons,
  apiAdminPostCoupon,
  apiAdminPutCoupon,
  apiAdminDelCoupon,
  apiUserSignin,
  apiUserLogout,
  apiUserCheckSignin,
  apiUserGetAllProducts,
  apiUserGetCarts,
  apiUSerGetProduct,
  apiUserGetProducts,
  apiUserPostCart,
  apiUserDelCart,
  apiUserDelCarts,
  apiUserPostCoupon,
  apiUserGetOrder,
  apiUserPostOrder,
  apiUserPostPay,
  apiUserRegister,
};

import { defineStore } from 'pinia';
import { ref } from 'vue';
import { apiUserSignin, apiUserLogout, apiUserCheckSignin } from '../utils/api';
import { useRouter } from 'vue-router';
import { successMsg } from '@/utils/api';

export interface UserInfo {
  id: number;
  username: string;
  email: string;
  full_name: string;
  avatar?: string;
  last_login?: string;
  updated_at?: string;
}

export const useUserStore = defineStore('user', () => {
  const router = useRouter();
  const userInfo = ref<UserInfo | null>(null);
  const loginStatus = ref(false);
  const isLoading = ref(false);

  // 登入功能
  const signin = async (data: { username: string; password: string; rememberMe?: boolean }) => {
    isLoading.value = true;

    try {
      const res = await apiUserSignin({
        username: data.username,
        password: data.password,
      });

      const { data: { success, token, user } } = res;

      if (success) {
        // 設置 cookie 過期時間
        const expires = data.rememberMe
          ? new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toUTCString()
          : '';

        document.cookie = `token=${token};path=/;expires=${expires}`;
        if (res.data.refresh) {
          document.cookie = `refresh_token=${res.data.refresh};path=/;expires=${expires}`;
        }

        loginStatus.value = true;
        userInfo.value = user;

        // 如果選擇記住我，保存用戶資料
        if (data.rememberMe) {
          localStorage.setItem('userInfo', JSON.stringify(user));
        }

        // 登入成功後不在這裡處理導向，由調用方處理
      }
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    } finally {
      isLoading.value = false;
    }
  };

  // 檢查登入狀態
  const checkLoginStatus = async () => {
    try {
      // 先檢查 cookie 中是否有 token
      const token = document.cookie.replace(/(?:(?:^|.*;\s*)token\s*=\s*([^;]*).*$)|^.*$/, '$1');
      
      if (!token) {
        loginStatus.value = false;
        userInfo.value = null;
        localStorage.removeItem('userInfo');
        return false;
      }

      const res = await apiUserCheckSignin();
      const { data: { success, isAuthenticated, user } } = res;

      if (success && isAuthenticated) {
        loginStatus.value = true;
        userInfo.value = user;
        return true;
      } else {
        loginStatus.value = false;
        userInfo.value = null;
        localStorage.removeItem('userInfo');
        // 清除無效的 token
        document.cookie = 'token=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/';
        document.cookie = 'refresh_token=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/';
        return false;
      }
    } catch (error) {
      console.error('Check login status failed:', error);
      loginStatus.value = false;
      userInfo.value = null;
      localStorage.removeItem('userInfo');
      return false;
    }
  };

  // 登出功能
  const logout = async () => {
    try {
      // 無論 API 呼叫是否成功，都清除本地資料
      userInfo.value = null;
      loginStatus.value = false;
      localStorage.removeItem('userInfo');
      
      // 清除所有相關的 cookies
      document.cookie = 'token=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/';
      document.cookie = 'refresh_token=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/';
      document.cookie = 'sessionid=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/';

      // 嘗試呼叫後端登出 API，但不等待回應
      apiUserLogout().catch(() => {
        console.log('Backend logout API call failed, but local logout successful');
      });

      // 顯示登出成功訊息
      successMsg('已成功登出');

      // 跳轉到登入頁面
      router.push('/login');
      
      return true;
    } catch (error) {
      console.log('Local logout process completed');
      return true;  // 即使有錯誤也返回成功
    }
  };

  return {
    userInfo,
    loginStatus,
    isLoading,
    signin,
    logout,
    checkLoginStatus,
  };
});

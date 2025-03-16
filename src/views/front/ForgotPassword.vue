<template>
  <div class="min-h-screen bg-gradient-to-b from-gray-50 to-white flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full bg-white rounded-xl shadow-lg p-8">
      <!-- 標題區域 -->
      <div class="text-center mb-6">
        <h2 class="text-3xl font-bold text-gray-900 mb-2">忘記密碼</h2>
        <p class="text-gray-600">{{ stepMessages[currentStep] }}</p>
      </div>

      <!-- 步驟指示器 -->
      <div class="step-indicator mb-8">
        <div class="step-line"></div>
        <div class="step-items">
          <div v-for="(label, index) in ['輸入郵箱', '驗證身份', '重設密碼']" 
              :key="index" 
              class="step-item"
              :class="{'active': currentStep >= index, 'completed': currentStep > index}">
            <div class="step-number">{{ index + 1 }}</div>
            <div class="step-label">{{ label }}</div>
          </div>
        </div>
      </div>

      <!-- 第一步：輸入郵箱 -->
      <div v-if="currentStep === 0" class="space-y-6">
        <div class="form-group">
          <label class="block text-sm font-medium text-gray-700 mb-1">電子郵箱</label>
          <input 
            type="email" 
            v-model="formData.email" 
            placeholder="請輸入您的註冊郵箱" 
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
          />
          <div v-if="errors.email" class="mt-1 text-sm text-red-600">{{ errors.email }}</div>
        </div>
        <button 
          @click="sendResetEmail" 
          class="w-full py-3 bg-primary text-white rounded-lg hover:bg-primary-dark transition-colors font-medium text-base"
          :disabled="loading"
        >
          {{ loading ? '發送中...' : '發送驗證碼' }}
        </button>
      </div>

      <!-- 第二步：輸入驗證碼 -->
      <div v-else-if="currentStep === 1" class="space-y-6">
        <div class="p-4 bg-blue-50 border-l-4 border-primary rounded-md mb-4">
          <p class="text-sm text-gray-700">驗證碼已發送至 <strong class="text-gray-900">{{ formData.email }}</strong></p>
          <p class="text-xs text-gray-500">請檢查您的收件箱及垃圾郵件資料夾</p>
        </div>
        
        <div class="form-group">
          <label class="block text-sm font-medium text-gray-700 mb-1">驗證碼</label>
          <input 
            type="text" 
            v-model="formData.code" 
            placeholder="請輸入6位數驗證碼" 
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
            maxlength="6"
          />
          <div v-if="errors.code" class="mt-1 text-sm text-red-600">{{ errors.code }}</div>
        </div>
        
        <div class="flex justify-end mb-4">
          <button 
            @click="resendCode"
            class="text-primary hover:text-primary-dark text-sm"
            :disabled="countdown > 0"
            :class="{'opacity-50 cursor-not-allowed': countdown > 0}"
          >
            {{ countdown > 0 ? `重新發送 (${countdown}s)` : '重新發送驗證碼' }}
          </button>
        </div>
        
        <button 
          @click="verifyCode" 
          class="w-full py-3 bg-primary text-white rounded-lg hover:bg-primary-dark transition-colors font-medium text-base mb-3"
          :disabled="loading"
        >
          {{ loading ? '驗證中...' : '驗證' }}
        </button>
        
        <button 
          @click="goBack" 
          class="w-full py-3 bg-transparent border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium text-base"
        >
          返回上一步
        </button>
      </div>

      <!-- 第三步：設置新密碼 -->
      <div v-else-if="currentStep === 2" class="space-y-6">
        <div class="form-group">
          <label class="block text-sm font-medium text-gray-700 mb-1">新密碼</label>
          <input 
            type="password" 
            v-model="formData.password" 
            placeholder="請輸入新密碼" 
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
          />
          <p class="mt-1 text-xs text-gray-500">密碼長度至少8個字符，建議包含字母、數字和特殊符號</p>
          <div v-if="errors.password" class="mt-1 text-sm text-red-600">{{ errors.password }}</div>
        </div>
        
        <div class="form-group">
          <label class="block text-sm font-medium text-gray-700 mb-1">確認密碼</label>
          <input 
            type="password" 
            v-model="formData.confirmPassword" 
            placeholder="請再次輸入新密碼" 
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
          />
          <div v-if="errors.confirmPassword" class="mt-1 text-sm text-red-600">{{ errors.confirmPassword }}</div>
        </div>
        
        <button 
          @click="resetPassword" 
          class="w-full py-3 bg-primary text-white rounded-lg hover:bg-primary-dark transition-colors font-medium text-base mb-3"
          :disabled="loading"
        >
          {{ loading ? '處理中...' : '重設密碼' }}
        </button>
        
        <button 
          @click="goBack" 
          class="w-full py-3 bg-transparent border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium text-base"
        >
          返回上一步
        </button>
      </div>

      <!-- 第四步：完成 -->
      <div v-else-if="currentStep === 3" class="text-center py-6">
        <div class="success-icon mx-auto mb-4">✓</div>
        <h2 class="text-2xl font-bold text-gray-900 mb-2">密碼重設成功</h2>
        <p class="text-gray-600 mb-6">您可以使用新密碼登入您的帳號</p>
        <button 
          @click="goToLogin" 
          class="w-full py-3 bg-primary text-white rounded-lg hover:bg-primary-dark transition-colors font-medium text-base"
        >
          前往登入
        </button>
      </div>

      <!-- 底部連結 -->
      <div v-if="currentStep < 3" class="text-center mt-6 text-gray-600">
        <router-link to="/login" class="text-primary hover:text-primary-dark font-medium">返回登入</router-link>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent, ref, reactive, computed, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';

export default defineComponent({
  name: 'ForgotPasswordView',
  setup() {
    console.log('忘記密碼頁面已加載');
    const router = useRouter();
    const API_BASE_URL = 'http://127.0.0.1:8000';
    
    // 基本設置
    const currentStep = ref(0);
    const loading = ref(false);
    const resetToken = ref('');
    const countdown = ref(0);
    let countdownTimer = null;
    
    // 表單數據
    const formData = reactive({
      email: '',
      code: '',
      password: '',
      confirmPassword: ''
    });
    
    // 錯誤訊息
    const errors = reactive({
      email: '',
      code: '',
      password: '',
      confirmPassword: ''
    });
    
    // 步驟提示訊息
    const stepMessages = computed(() => ({
      0: '我們將發送驗證碼到您的郵箱',
      1: '請輸入收到的6位數驗證碼',
      2: '請設置您的新密碼',
      3: '您已成功重設密碼'
    }));
    
    // 發送重設郵件
    const sendResetEmail = async () => {
      errors.email = '';
      
      // 驗證郵箱
      if (!formData.email) {
        errors.email = '請輸入電子郵箱';
        return;
      }
      
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
        errors.email = '請輸入有效的電子郵箱';
        return;
      }
      
      loading.value = true;
      
      try {
        console.log('開始發送密碼重置請求...');
        const formDataObj = new FormData();
        formDataObj.append('email', formData.email);
        
        console.log(`正在發送密碼重置請求到 ${API_BASE_URL}/password-reset/api/request/`);
        
        // 修改 axios 請求配置
        const response = await axios.post(
          `${API_BASE_URL}/password-reset/api/request/`,
          formDataObj,
          { 
            headers: { 
              'Accept': 'application/json',
              'X-Requested-With': 'XMLHttpRequest'
            },
            withCredentials: false // 跨域請求時不發送 credentials
          }
        );
        
        console.log('API 響應:', response.data);
        
        if (response.data.success) {
          resetToken.value = response.data.token;
          currentStep.value = 1;
          startCountdown();
        } else {
          errors.email = response.data.error || '發送失敗，請稍後再試';
        }
      } catch (error) {
        console.error('發送錯誤詳情:', error);
        if (error.response) {
          console.error('伺服器回應:', error.response.status, error.response.data);
          errors.email = `請求失敗 (${error.response.status}): ${error.response.data.error || '伺服器錯誤'}`;
        } else if (error.request) {
          console.error('請求未收到回應:', error.request);
          errors.email = '無法連接到伺服器，請檢查網絡連接';
        } else {
          console.error('請求設置錯誤:', error.message);
          errors.email = '發送失敗，請稍後再試';
        }
      } finally {
        loading.value = false;
      }
    };
    
    // 開始倒數計時
    const startCountdown = () => {
      countdown.value = 60;
      if (countdownTimer) clearInterval(countdownTimer);
      
      countdownTimer = setInterval(() => {
        if (countdown.value > 0) {
          countdown.value--;
        } else {
          if (countdownTimer) clearInterval(countdownTimer);
        }
      }, 1000);
    };
    
    // 重新發送驗證碼
    const resendCode = async () => {
      if (countdown.value > 0) return;
      await sendResetEmail();
    };
    
    // 驗證驗證碼
    const verifyCode = async () => {
      errors.code = '';
      
      if (!formData.code) {
        errors.code = '請輸入驗證碼';
        return;
      }
      
      if (formData.code.length !== 6 || !/^\d+$/.test(formData.code)) {
        errors.code = '請輸入6位數字驗證碼';
        return;
      }
      
      loading.value = true;
      
      try {
        console.log('開始驗證驗證碼...');
        const formDataObj = new FormData();
        formDataObj.append('token', resetToken.value);
        formDataObj.append('code', formData.code);
        
        const response = await axios.post(
          `${API_BASE_URL}/password-reset/api/verify/`,
          formDataObj,
          { 
            headers: { 
              'Accept': 'application/json',
              'X-Requested-With': 'XMLHttpRequest'
            },
            withCredentials: false
          }
        );
        
        console.log('驗證碼驗證響應:', response.data);
        
        if (response.data.success) {
          currentStep.value = 2;
        } else {
          errors.code = response.data.error || '驗證碼不正確，請重新輸入';
        }
      } catch (error) {
        console.error('驗證錯誤詳情:', error);
        if (error.response) {
          console.error('伺服器回應:', error.response.status, error.response.data);
          errors.code = `驗證失敗 (${error.response.status}): ${error.response.data.error || '伺服器錯誤'}`;
        } else if (error.request) {
          console.error('請求未收到回應:', error.request);
          errors.code = '無法連接到伺服器，請檢查網絡連接';
        } else {
          console.error('請求設置錯誤:', error.message);
          errors.code = '驗證失敗，請稍後再試';
        }
      } finally {
        loading.value = false;
      }
    };
    
    // 重設密碼
    const resetPassword = async () => {
      errors.password = '';
      errors.confirmPassword = '';
      
      if (!formData.password) {
        errors.password = '請輸入新密碼';
        return;
      }
      
      if (formData.password.length < 8) {
        errors.password = '密碼長度至少為8個字符';
        return;
      }
      
      if (!formData.confirmPassword) {
        errors.confirmPassword = '請再次輸入新密碼';
        return;
      }
      
      if (formData.password !== formData.confirmPassword) {
        errors.confirmPassword = '兩次輸入的密碼不一致';
        return;
      }
      
      loading.value = true;
      
      try {
        console.log('開始重設密碼...');
        const formDataObj = new FormData();
        formDataObj.append('token', resetToken.value);
        formDataObj.append('password', formData.password);
        
        const response = await axios.post(
          `${API_BASE_URL}/password-reset/api/reset/`,
          formDataObj,
          { 
            headers: { 
              'Accept': 'application/json',
              'X-Requested-With': 'XMLHttpRequest'
            },
            withCredentials: false
          }
        );
        
        console.log('密碼重設響應:', response.data);
        
        if (response.data.success) {
          currentStep.value = 3;
          
          // 自動跳轉倒數計時
          setTimeout(() => {
            goToLogin();
          }, 5000);
        } else {
          errors.password = response.data.error || '重設密碼失敗，請稍後再試';
        }
      } catch (error) {
        console.error('重設密碼錯誤詳情:', error);
        if (error.response) {
          console.error('伺服器回應:', error.response.status, error.response.data);
          errors.password = `重設失敗 (${error.response.status}): ${error.response.data.error || '伺服器錯誤'}`;
        } else if (error.request) {
          console.error('請求未收到回應:', error.request);
          errors.password = '無法連接到伺服器，請檢查網絡連接';
        } else {
          console.error('請求設置錯誤:', error.message);
          errors.password = '重設密碼失敗，請稍後再試';
        }
      } finally {
        loading.value = false;
      }
    };
    
    // 返回上一步
    const goBack = () => {
      currentStep.value--;
    };
    
    // 前往登入頁面
    const goToLogin = () => {
      router.push('/login');
    };
    
    // 添加跳轉定時器變數
    let redirectTimer = null;
    
    // 生命週期鉤子
    onMounted(() => {
      console.log('忘記密碼頁面已掛載');
      
      // 強制設置文檔標題，並延遲執行確保它不被其他代碼覆蓋
      document.title = '忘記密碼 - Travel Fun';
      setTimeout(() => {
        document.title = '忘記密碼 - Travel Fun';
      }, 100);
      
      // 重置所有狀態，確保頁面初始化
      currentStep.value = 0;
      loading.value = false;
      resetToken.value = '';
      countdown.value = 0;
      if (countdownTimer) {
        clearInterval(countdownTimer);
        countdownTimer = null;
      }
      
      // 清空表單數據
      formData.email = '';
      formData.code = '';
      formData.password = '';
      formData.confirmPassword = '';
      
      // 清空錯誤訊息
      errors.email = '';
      errors.code = '';
      errors.password = '';
      errors.confirmPassword = '';
      
      console.log('忘記密碼頁面狀態已重置');
    });
    
    onUnmounted(() => {
      if (countdownTimer) {
        clearInterval(countdownTimer);
        countdownTimer = null;
      }
      
      // 清除跳轉定時器
      if (redirectTimer) {
        clearTimeout(redirectTimer);
        redirectTimer = null;
      }
    });
    
    return {
      currentStep,
      loading,
      formData,
      errors,
      stepMessages,
      countdown,
      sendResetEmail,
      resendCode,
      verifyCode,
      resetPassword,
      goBack,
      goToLogin
    };
  }
});
</script>

<style scoped>
/* 漸變背景 */
.bg-gradient-to-b {
  background-image: url('https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?q=80&w=2070&auto=format&fit=crop');
  background-size: cover;
  background-position: center;
  background-attachment: fixed;
  position: relative;
}

/* 添加漸變疊加層 */
.bg-gradient-to-b::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, 
      rgba(28, 132, 198, 0.6) 0%, 
      rgba(35, 198, 200, 0.6) 100%);
  z-index: 1;
  animation: gradientAnimation 10s ease infinite;
}

@keyframes gradientAnimation {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

/* 確保內容在漸變層之上 */
.max-w-md {
  position: relative;
  z-index: 2;
}

/* 文本顏色 */
.text-primary {
  color: var(--primary-color);
}

.text-primary-dark:hover {
  color: color-mix(in srgb, var(--primary-color) 80%, black);
}

/* 背景顏色 */
.bg-primary {
  background-color: var(--primary-color);
}

.bg-primary-dark:hover {
  background-color: color-mix(in srgb, var(--primary-color) 80%, black);
}

/* 焦點環 */
.focus\:ring-primary:focus {
  --tw-ring-color: var(--primary-color);
  --tw-ring-opacity: 0.5;
}

/* 步驟指示器 */
.step-indicator {
  position: relative;
}

.step-line {
  position: absolute;
  top: 16px;
  left: 0;
  right: 0;
  height: 2px;
  background-color: #e5e7eb;
  z-index: 1;
}

.step-items {
  display: flex;
  justify-content: space-between;
  position: relative;
  z-index: 2;
}

.step-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 33.33%;
}

.step-number {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: #e5e7eb;
  color: #6b7280;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  margin-bottom: 8px;
  transition: all 0.3s;
}

.step-label {
  font-size: 12px;
  color: #6b7280;
  transition: all 0.3s;
}

.step-item.active .step-number {
  background-color: var(--primary-color);
  color: white;
}

.step-item.completed .step-number {
  background-color: var(--success-color);
  color: white;
}

.step-item.active .step-label,
.step-item.completed .step-label {
  color: #374151;
  font-weight: 500;
}

/* 成功圖標 */
.success-icon {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background-color: var(--success-color);
  color: white;
  font-size: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 禁用按鈕 */
button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}
</style> 
<script setup lang="ts">
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { useMessage, NForm, NFormItem, NInput, NButton, NSteps, NStep, NSpin } from 'naive-ui';
import axios from 'axios';

// 獲取基本 URL
const API_BASE_URL = 'http://127.0.0.1:8000';

// 創建 axios 實例
const apiInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Accept': 'application/json',
  },
});

const router = useRouter();
const message = useMessage();

// 當前步驟
const currentStep = ref(0);
// 重設令牌
const resetToken = ref('');
// 載入狀態
const loading = ref(false);
// 倒數計時器
const countdown = ref(0);
// 倒數計時器ID
let countdownTimer: ReturnType<typeof setInterval> | null = null;

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

// 發送郵件請求
async function sendResetEmail() {
  // 清除郵箱錯誤
  errors.email = '';
  
  // 驗證郵箱格式
  if (!formData.email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
    errors.email = '請輸入有效的電子郵件地址';
    return;
  }
  
  loading.value = true;
  
  try {
    const formDataObj = new FormData();
    formDataObj.append('email', formData.email);
    
    const response = await apiInstance.post('/password-reset/api/request/', formDataObj);
    
    if (response.data.success) {
      message.success('驗證碼已發送到您的郵箱！');
      resetToken.value = response.data.token;
      currentStep.value = 1;
      
      // 開始倒數計時
      countdown.value = 60;
      if (countdownTimer) clearInterval(countdownTimer);
      countdownTimer = setInterval(() => {
        if (countdown.value > 0) {
          countdown.value--;
        } else {
          if (countdownTimer) clearInterval(countdownTimer);
        }
      }, 1000);
    } else {
      message.error(response.data.error || '發送驗證碼失敗，請稍後再試');
    }
  } catch (error: any) {
    console.error('發送重設郵件錯誤:', error);
    if (error.response?.data?.error) {
      errors.email = error.response.data.error;
    } else {
      errors.email = '發送驗證碼失敗，請稍後再試';
    }
    message.error(errors.email);
  } finally {
    loading.value = false;
  }
}

// 驗證驗證碼
async function verifyCode() {
  // 清除驗證碼錯誤
  errors.code = '';
  
  // 驗證驗證碼格式
  if (!formData.code || formData.code.length !== 6 || !/^\d+$/.test(formData.code)) {
    errors.code = '請輸入6位數字驗證碼';
    return;
  }
  
  loading.value = true;
  
  try {
    const formDataObj = new FormData();
    formDataObj.append('token', resetToken.value);
    formDataObj.append('code', formData.code);
    
    const response = await apiInstance.post('/password-reset/api/verify/', formDataObj);
    
    if (response.data.success) {
      message.success('驗證碼正確！');
      currentStep.value = 2;
    } else {
      message.error(response.data.error || '驗證碼不正確，請重新輸入');
      errors.code = response.data.error || '驗證碼不正確，請重新輸入';
    }
  } catch (error: any) {
    console.error('驗證碼驗證錯誤:', error);
    if (error.response?.data?.error) {
      errors.code = error.response.data.error;
    } else {
      errors.code = '驗證碼驗證失敗，請稍後再試';
    }
    message.error(errors.code);
  } finally {
    loading.value = false;
  }
}

// 重設密碼
async function resetPassword() {
  // 清除密碼錯誤
  errors.password = '';
  errors.confirmPassword = '';
  
  // 驗證密碼
  if (!formData.password || formData.password.length < 8) {
    errors.password = '密碼長度必須至少為8個字符';
    return;
  }
  
  // 驗證確認密碼
  if (formData.password !== formData.confirmPassword) {
    errors.confirmPassword = '兩次輸入的密碼不一致';
    return;
  }
  
  loading.value = true;
  
  try {
    const formDataObj = new FormData();
    formDataObj.append('token', resetToken.value);
    formDataObj.append('password', formData.password);
    
    const response = await apiInstance.post('/password-reset/api/reset/', formDataObj);
    
    if (response.data.success) {
      message.success('密碼已成功重設！您可以使用新密碼登入');
      setTimeout(() => {
        router.push('/login');
      }, 2000);
    } else {
      message.error(response.data.error || '重設密碼失敗，請稍後再試');
    }
  } catch (error: any) {
    console.error('重設密碼錯誤:', error);
    if (error.response?.data?.error) {
      message.error(error.response.data.error);
    } else {
      message.error('重設密碼失敗，請稍後再試');
    }
  } finally {
    loading.value = false;
  }
}

// 重新發送郵件
async function resendEmail() {
  if (countdown.value > 0) return;
  
  await sendResetEmail();
}
</script>

<template>
  <div class="reset-password-container">
    <NSteps :current="currentStep" class="mb-8">
      <NStep title="提交郵箱" description="輸入您的註冊郵箱" />
      <NStep title="驗證身份" description="輸入驗證碼" />
      <NStep title="重設密碼" description="設置新密碼" />
    </NSteps>
    
    <NSpin :show="loading">
      <!-- 步驟一：輸入郵箱 -->
      <div v-if="currentStep === 0" class="step-container">
        <NForm>
          <NFormItem label="電子郵箱">
            <NInput 
              v-model:value="formData.email"
              placeholder="請輸入註冊時使用的電子郵箱"
              :disabled="loading"
            />
            <div v-if="errors.email" class="error-message">{{ errors.email }}</div>
          </NFormItem>
          
          <div class="action-buttons">
            <NButton 
              type="primary" 
              block 
              @click="sendResetEmail"
              :loading="loading"
              :disabled="loading || !formData.email"
            >
              發送驗證碼
            </NButton>
            <div class="text-center mt-4">
              <router-link to="/login" class="login-link">返回登入</router-link>
            </div>
          </div>
        </NForm>
      </div>
      
      <!-- 步驟二：輸入驗證碼 -->
      <div v-else-if="currentStep === 1" class="step-container">
        <NForm>
          <NFormItem label="驗證碼">
            <NInput 
              v-model:value="formData.code"
              placeholder="請輸入6位數驗證碼"
              :disabled="loading"
              maxlength="6"
            />
            <div v-if="errors.code" class="error-message">{{ errors.code }}</div>
          </NFormItem>
          
          <div class="resend-code">
            <a 
              href="javascript:void(0)" 
              @click="resendEmail"
              :class="{ 'disabled': countdown > 0 }"
            >
              {{ countdown > 0 ? `重新發送 (${countdown}s)` : '重新發送驗證碼' }}
            </a>
          </div>
          
          <div class="action-buttons">
            <NButton 
              type="primary" 
              block 
              @click="verifyCode"
              :loading="loading"
              :disabled="loading || !formData.code"
            >
              驗證
            </NButton>
            <NButton 
              quaternary
              block
              class="mt-2"
              @click="currentStep = 0"
              :disabled="loading"
            >
              返回上一步
            </NButton>
          </div>
        </NForm>
      </div>
      
      <!-- 步驟三：重設密碼 -->
      <div v-else-if="currentStep === 2" class="step-container">
        <NForm>
          <NFormItem label="新密碼">
            <NInput 
              v-model:value="formData.password"
              type="password"
              placeholder="請輸入新密碼"
              :disabled="loading"
              show-password-on="click"
            />
            <div v-if="errors.password" class="error-message">{{ errors.password }}</div>
            <div class="helper-text">密碼長度至少8個字符，建議包含字母、數字和特殊符號</div>
          </NFormItem>
          
          <NFormItem label="確認密碼">
            <NInput 
              v-model:value="formData.confirmPassword"
              type="password"
              placeholder="請再次輸入新密碼"
              :disabled="loading"
              show-password-on="click"
            />
            <div v-if="errors.confirmPassword" class="error-message">{{ errors.confirmPassword }}</div>
          </NFormItem>
          
          <div class="action-buttons">
            <NButton 
              type="primary" 
              block 
              @click="resetPassword"
              :loading="loading"
              :disabled="loading || !formData.password || !formData.confirmPassword"
            >
              重設密碼
            </NButton>
            <NButton 
              quaternary
              block
              class="mt-2"
              @click="currentStep = 1"
              :disabled="loading"
            >
              返回上一步
            </NButton>
          </div>
        </NForm>
      </div>
    </NSpin>
  </div>
</template>

<style scoped>
.reset-password-container {
  width: 100%;
  max-width: 450px;
  margin: 0 auto;
}

.step-container {
  margin-top: 20px;
}

.error-message {
  color: #e53935;
  font-size: 12px;
  margin-top: 4px;
}

.helper-text {
  color: #666;
  font-size: 12px;
  margin-top: 4px;
}

.action-buttons {
  margin-top: 24px;
}

.login-link {
  color: #1c84c6;
  text-decoration: none;
  font-size: 14px;
}

.login-link:hover {
  text-decoration: underline;
}

.resend-code {
  text-align: right;
  margin-top: 8px;
}

.resend-code a {
  color: #1c84c6;
  font-size: 14px;
  text-decoration: none;
}

.resend-code a:hover:not(.disabled) {
  text-decoration: underline;
}

.resend-code .disabled {
  color: #999;
  cursor: not-allowed;
}
</style> 
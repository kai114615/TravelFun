<!-- 重置密碼頁面主視圖 -->
<script setup lang="ts">
import { ref, onMounted } from 'vue';
import type { FormInst, FormRules } from 'naive-ui';
import { NForm, NFormItem, NInput, NButton, NText, NAlert, useMessage } from 'naive-ui';
import { useRouter, useRoute } from 'vue-router';
import { apiPasswordResetConfirm } from '@/utils/api';

const router = useRouter();
const route = useRoute();
const message = useMessage();

const formRef = ref<FormInst | null>(null);
const loading = ref(false);
const validationError = ref('');
const resetSuccess = ref(false);

// 從 URL 參數中獲取 uid 和 token
const uid = ref(route.params.uid as string);
const token = ref(route.params.token as string);

// 表單數據
const formValue = ref({
  password: '',
  confirmPassword: ''
});

// 表單驗證規則
const rules: FormRules = {
  password: [
    { required: true, message: '請輸入新密碼', trigger: 'blur' },
    { min: 8, message: '密碼長度至少為 8 個字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '請再次輸入密碼', trigger: 'blur' },
    {
      validator: (rule, value) => value === formValue.value.password,
      message: '兩次輸入的密碼不一致',
      trigger: 'blur'
    }
  ]
};

// 驗證參數
function validateParams() {
  if (!uid.value || !token.value) {
    validationError.value = '無效的密碼重置連結，請重新請求重置密碼';
    return false;
  }
  return true;
}

// 提交處理
async function handleSubmit() {
  try {
    if (!validateParams()) return;
    
    await formRef.value?.validate();
    loading.value = true;

    // 呼叫 API 確認重置密碼
    const response = await apiPasswordResetConfirm(uid.value, token.value, formValue.value.password);
    
    console.log('密碼重置回應:', response);
    
    if (response.data?.access) {
      // 儲存 token
      localStorage.setItem('access_token', response.data.access);
      if (response.data.refresh) {
        localStorage.setItem('refresh_token', response.data.refresh);
      }
      
      // 顯示成功訊息
      message.success('密碼重置成功！');
      resetSuccess.value = true;
      
      // 3秒後導航到登入頁面
      setTimeout(() => {
        router.push('/login');
      }, 3000);
    } else {
      throw new Error(response.data?.message || '密碼重置失敗');
    }
  } catch (error: any) {
    console.error('密碼重置失敗:', error);
    message.error(error.message || '密碼重置失敗，請稍後再試');
  } finally {
    loading.value = false;
  }
}

// 返回登入頁面
function backToLogin() {
  router.push('/login');
}

// 組件載入時驗證參數
onMounted(() => {
  validateParams();
});
</script>

<template>
  <div class="reset-password-view">
    <div class="loginColumns animated fadeInDown">
      <div class="ibox-content">
        <h2 class="font-bold">重置密碼</h2>
        <p>設定您的新密碼</p>
        
        <!-- 顯示驗證錯誤 -->
        <template v-if="validationError">
          <NAlert type="error" class="error-alert">
            <p>{{ validationError }}</p>
          </NAlert>
          <div class="button-container">
            <NButton
              type="primary"
              size="large"
              @click="backToLogin"
              class="reset-button"
              block
            >
              返回登入頁面
            </NButton>
          </div>
        </template>
        
        <!-- 顯示重置成功訊息 -->
        <template v-else-if="resetSuccess">
          <div class="success-message">
            <div class="success-icon">✓</div>
            <h3>密碼重置成功</h3>
            <p class="info-text">您的密碼已成功更新，正在跳轉至登入頁面...</p>
          </div>
        </template>
        
        <!-- 密碼重置表單 -->
        <template v-else>
          <NForm
            ref="formRef"
            :model="formValue"
            :rules="rules"
            class="reset-password-form"
          >
            <!-- 密碼輸入 -->
            <div class="form-item">
              <i class="fas fa-lock"></i>
              <NFormItem path="password" label="新密碼">
                <NInput
                  v-model:value="formValue.password"
                  type="password"
                  placeholder="請輸入新密碼"
                  maxlength="50"
                  show-password-on="click"
                  class="form-input"
                />
              </NFormItem>
            </div>
            
            <!-- 確認密碼輸入 -->
            <div class="form-item">
              <i class="fas fa-lock"></i>
              <NFormItem path="confirmPassword" label="確認密碼">
                <NInput
                  v-model:value="formValue.confirmPassword"
                  type="password"
                  placeholder="請再次輸入新密碼"
                  maxlength="50"
                  show-password-on="click"
                  class="form-input"
                />
              </NFormItem>
            </div>
            
            <!-- 提交按鈕 -->
            <div class="button-container">
              <NButton
                type="primary"
                size="large"
                :loading="loading"
                :disabled="loading"
                @click="handleSubmit"
                class="reset-button"
                block
              >
                {{ loading ? '處理中...' : '確認重置密碼' }}
              </NButton>
            </div>
          </NForm>
          
          <div class="login-link">
            <NText>記起密碼了？</NText>
            <router-link to="/login">
              返回登入
            </router-link>
          </div>
        </template>
      </div>
      <hr/>
      <div class="footer-text">
        <small>TravelFun 會員中心 &copy; 2024</small>
      </div>
    </div>
  </div>
</template>

<style scoped>
.reset-password-view {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: url('https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?q=80&w=2070&auto=format&fit=crop');
  background-size: cover;
  background-position: center;
  background-attachment: fixed;
  padding: 20px;
  position: relative;
}

.reset-password-view::before {
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

.loginColumns {
  max-width: 450px;
  margin: 50px auto;
  padding: 20px;
  position: relative;
  z-index: 2;
}

.ibox-content {
  background-color: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(15px);
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
}

.ibox-content:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.25);
}

.font-bold {
  font-family: 'Noto Serif TC', serif;
  font-size: 36px;
  margin-bottom: 5px;
  text-align: center;
  color: #2f4050;
  text-shadow: 2px 2px 4px rgba(255, 255, 255, 0.3);
  letter-spacing: 3px;
  font-weight: 600;
}

p {
  font-family: 'Noto Serif TC', serif;
  font-size: 20px;
  text-align: center;
  color: #2f4050;
  margin-bottom: 25px;
  letter-spacing: 1px;
  font-weight: 300;
}

.form-item {
  margin-bottom: 25px;
  position: relative;
}

.form-item i {
  position: absolute;
  left: 15px;
  top: 42px;
  color: #2f4050;
  opacity: 0.7;
  font-size: 16px;
  z-index: 1;
}

.form-item :deep(.n-form-item-label) {
  font-family: 'Noto Serif TC', serif;
  color: #2f4050;
  font-weight: 500;
}

.form-input {
  height: 50px;
  border-radius: 10px;
  background-color: rgba(255, 255, 255, 0.8);
  border: 2px solid rgba(47, 64, 80, 0.1);
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  padding-left: 45px !important;
  font-family: 'Noto Serif TC', serif;
  font-weight: 400;
}

.form-input:focus {
  background-color: rgba(255, 255, 255, 0.95);
  border-color: #1c84c6;
  box-shadow: 0 0 10px rgba(28, 132, 198, 0.2);
}

.reset-button {
  height: 50px;
  background: linear-gradient(135deg, #1c84c6 0%, #23c6c8 100%);
  border: none;
  border-radius: 10px;
  font-size: 18px;
  font-weight: 500;
  letter-spacing: 1px;
  transition: all 0.3s ease;
  box-shadow: 0 5px 15px rgba(28, 132, 198, 0.3);
  font-family: 'Noto Serif TC', serif;
}

.reset-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(28, 132, 198, 0.4);
  background: linear-gradient(135deg, #23c6c8 0%, #1c84c6 100%);
}

.login-link, .register-link {
  margin-top: 24px;
  text-align: center;
  padding: 16px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.login-link :deep(a), .register-link :deep(a) {
  color: #1c84c6;
  text-decoration: none;
  font-weight: 500;
  position: relative;
  transition: all 0.3s ease;
}

.login-link :deep(a:hover), .register-link :deep(a:hover) {
  color: #23c6c8;
  text-decoration: underline;
}

.animated {
  animation-duration: 1s;
}

.fadeInDown {
  animation-name: fadeInDown;
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translate3d(0, -30px, 0);
  }
  to {
    opacity: 1;
    transform: translate3d(0, 0, 0);
  }
}

hr {
  border-color: rgba(255, 255, 255, 0.3);
  margin: 30px 0;
}

.footer-text {
  color: white;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
  font-size: 14px;
  font-family: 'Noto Serif TC', serif;
  opacity: 0.9;
  font-weight: 300;
  text-align: center;
}

.error-alert {
  margin-bottom: 20px;
  border-radius: 10px;
}

.error-alert :deep(p) {
  margin: 0;
  font-size: 14px;
  text-align: left;
  color: inherit;
}

.success-message {
  text-align: center;
  padding: 20px;
  border-radius: 10px;
  background-color: rgba(255, 255, 255, 0.7);
}

.success-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #1c84c6 0%, #23c6c8 100%);
  color: white;
  font-size: 30px;
  margin-bottom: 15px;
}

.success-message h3 {
  font-family: 'Noto Serif TC', serif;
  color: #2f4050;
  font-size: 24px;
  margin-bottom: 15px;
  font-weight: 600;
}

.info-text {
  font-size: 16px;
  color: #4b5563;
  margin-bottom: 10px;
}

.button-container {
  margin-top: 24px;
}

/* 響應式設計 */
@media (max-width: 640px) {
  .ibox-content {
    padding: 30px 20px;
  }

  .font-bold {
    font-size: 28px;
  }
}
</style> 
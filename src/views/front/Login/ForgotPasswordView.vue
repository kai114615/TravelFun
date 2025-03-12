<!-- 忘記密碼頁面主視圖 -->
<script setup lang="ts">
import { ref } from 'vue';
import type { FormInst, FormRules } from 'naive-ui';
import { NForm, NFormItem, NInput, NButton, NText, useMessage } from 'naive-ui';
import { useRouter } from 'vue-router';
import { apiPasswordResetRequest } from '@/utils/api';

const router = useRouter();
const message = useMessage();

const formRef = ref<FormInst | null>(null);
const loading = ref(false);
const email = ref('');
const requestSent = ref(false);

// 表單驗證規則
const rules: FormRules = {
  email: [
    { required: true, message: '請輸入電子郵件', trigger: 'blur' },
    { type: 'email', message: '請輸入有效的電子郵件地址', trigger: 'blur' }
  ]
};

// 提交處理
async function handleSubmit() {
  try {
    await formRef.value?.validate();
    loading.value = true;

    // 呼叫 API 發送重置密碼請求
    await apiPasswordResetRequest(email.value);
    
    // 設置請求已發送標誌
    requestSent.value = true;
    
    // 顯示訊息
    message.success('如果該郵箱已註冊，您將收到重置密碼的郵件');
    
    // 清空表單
    email.value = '';
  } catch (error: any) {
    console.error('忘記密碼請求失敗:', error);
  } finally {
    loading.value = false;
  }
}

// 重置頁面狀態
function resetForm() {
  requestSent.value = false;
  email.value = '';
}
</script>

<template>
  <div class="forgot-password-view">
    <div class="loginColumns animated fadeInDown">
      <div class="ibox-content">
        <h2 class="font-bold">忘記密碼</h2>
        <p>重設您的帳戶密碼</p>
        
        <!-- 請求發送後顯示的訊息 -->
        <div v-if="requestSent" class="success-message">
          <div class="success-icon">✓</div>
          <h3>重設密碼郵件已發送</h3>
          <p class="info-text">如果該郵箱已註冊，您將收到一封包含重置密碼連結的郵件。</p>
          <p class="info-text">請檢查您的收件匣和垃圾郵件夾。</p>
          
          <div class="action-buttons">
            <NButton type="primary" class="reset-button" @click="resetForm">
              再次發送
            </NButton>
            <NButton class="login-return-button" @click="router.push('/login')">
              返回登入
            </NButton>
          </div>
        </div>
        
        <!-- 郵件表單 -->
        <template v-else>
          <div class="instruction-text">
            <p>請輸入您註冊時使用的電子郵件地址。我們將向您發送重置密碼的連結。</p>
          </div>
          
          <NForm
            ref="formRef"
            :model="{ email }"
            :rules="rules"
            class="forgot-password-form"
          >
            <!-- 電子郵件輸入 -->
            <div class="form-item">
              <i class="fas fa-envelope"></i>
              <NFormItem path="email" label="電子郵件">
                <NInput
                  v-model:value="email"
                  placeholder="請輸入電子郵件地址"
                  type="email"
                  :maxlength="100"
                  class="form-input"
                />
              </NFormItem>
            </div>

            <!-- 提交按鈕 -->
            <div class="button-container">
              <NButton
                type="primary"
                size="large"
                block
                :loading="loading"
                :disabled="loading"
                @click="handleSubmit"
                class="reset-button"
              >
                {{ loading ? '處理中...' : '發送重置郵件' }}
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
.forgot-password-view {
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

.forgot-password-view::before {
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

.action-buttons {
  display: flex;
  gap: 15px;
  justify-content: center;
  margin-top: 25px;
}

.login-return-button {
  height: 50px;
  border-radius: 10px;
  font-family: 'Noto Serif TC', serif;
}

.instruction-text p {
  font-size: 16px;
  line-height: 1.6;
}

/* 響應式設計 */
@media (max-width: 640px) {
  .ibox-content {
    padding: 30px 20px;
  }

  .font-bold {
    font-size: 28px;
  }
  
  .action-buttons {
    flex-direction: column;
  }
}
</style> 
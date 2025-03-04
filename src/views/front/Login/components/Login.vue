<script setup lang="ts">
import { onMounted, ref } from 'vue';
import type { FormInst, FormRules } from 'naive-ui';
import { useMessage } from 'naive-ui';
import { useRoute, useRouter } from 'vue-router';
import { useUserStore } from '@/stores/user';
import { api, apiGoogleSignin, apiUserSignin } from '@/utils/api';
import { request } from '@/utils/request';

// Google OAuth 配置
const GOOGLE_CLIENT_ID = '1063055916047-ic94ldh4ojm4gg18sbcqmenerdc98s2s.apps.googleusercontent.com';

const router = useRouter();
const route = useRoute();
const message = useMessage();
const userStore = useUserStore();

const formRef = ref<FormInst | null>(null);
const loading = ref(false);
const googleLoading = ref(false);
const captchaCanvas = ref<HTMLCanvasElement | null>(null);
const captchaText = ref('');

const formValue = ref({
  username: '',
  password: '',
  captcha: ''
});

// 表單驗證規則
const rules: FormRules = {
  username: [
    { required: true, message: '請輸入帳號', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '請輸入密碼', trigger: 'blur' }
  ],
  captcha: [
    { required: true, message: '請輸入驗證碼', trigger: 'blur' },
    {
      validator: (rule, value) => value.toLowerCase() === captchaText.value.toLowerCase(),
      message: '驗證碼錯誤',
      trigger: 'blur'
    }
  ]
};

// 一般登入處理
async function handleSubmit() {
  try {
    // @ts-expect-error 表單驗證需要類型細化，但目前的類型定義不完整
    await formRef.value?.validate();
    loading.value = true;

    // 驗證驗證碼
    if (formValue.value.captcha.toLowerCase() !== captchaText.value.toLowerCase()) {
      message.error('驗證碼錯誤');
      generateCaptcha();
      return;
    }

    const response = await apiUserSignin({
      username: formValue.value.username,
      password: formValue.value.password
    });

    if (response.data.success) {
      message.success('登入成功');

      // 保存 token
      localStorage.setItem('access_token', response.data.access);
      if (response.data.refresh) {
        localStorage.setItem('refresh_token', response.data.refresh);
      }

      // 更新用戶狀態
      await userStore.updateUserState(response.data.user, true);

      // 跳轉到會員中心儀表板
      const redirectPath = route.query.redirect?.toString() || '/member/dashboard';
      await router.push(redirectPath);

      // 確保跳轉成功
      setTimeout(() => {
        if (window.location.hash !== '#/member/dashboard') {
          window.location.href = '/#/member/dashboard';
        }
      }, 100);
    } else {
      throw new Error(response.data.message || '登入失敗');
    }
  } catch (error: any) {
    console.error('登入失敗:', error);
    message.error(error.response?.data?.message || error.message || '登入失敗');
    generateCaptcha();
  } finally {
    loading.value = false;
  }
}

// Google 登入處理
const handleGoogleLogin = async () => {
  try {
    googleLoading.value = true;
    await loadGoogleAPI();
    // @ts-expect-error Google API 類型定義不完整，需要使用 any 類型
    const google = (window as any).google;
    const client = google.accounts.oauth2.initTokenClient({
      client_id: GOOGLE_CLIENT_ID,
      scope: 'profile email',
      callback: async (response: any) => {
        try {
          console.log('Google OAuth 回調開始');
          console.log('獲取到的 Google token:', response.access_token);

          const result = await apiGoogleSignin({
            google_token: response.access_token
          });

          console.log('後端回應:', result);

          if (result.data?.access) {
            message.success('Google 登入成功！');

            // 獲取用戶資料
            const userResponse = await request.get(api.user.checkSigin);
            console.log('用戶資料:', userResponse.data);

            if (userResponse.data) {
              // 更新用戶狀態
              await userStore.updateUserState(userResponse.data, true);

              // 跳轉到會員中心儀表板
              const redirectPath = route.query.redirect?.toString() || '/member/dashboard';
              await router.push(redirectPath);

              // 確保跳轉成功
              setTimeout(() => {
                if (window.location.hash !== '#/member/dashboard') {
                  window.location.href = '/#/member/dashboard';
                }
              }, 100);
            }
          } else {
            throw new Error('登入失敗：未收到有效的認證令牌');
          }
        } catch (error: any) {
          console.error('Google 登入處理失敗:', error);
          const errorMessage = error.response?.data?.detail || error.message || 'Google 登入失敗，請稍後再試';
          message.error(errorMessage);
          console.log('完整錯誤信息:', error);
        } finally {
          googleLoading.value = false;
        }
      }
    });

    console.log('開始請求 Google token');
    client.requestAccessToken();
  } catch (error: any) {
    console.error('Google API 載入失敗:', error);
    message.error('Google 登入服務暫時無法使用');
    googleLoading.value = false;
  }
};

// 載入 Google API
function loadGoogleAPI(): Promise<void> {
  return new Promise((resolve, reject) => {
    // @ts-expect-error Google API 類型定義不完整，需要使用 any 類型
    if (window.google) {
      resolve();
      return;
    }

    const script = document.createElement('script');
    script.src = 'https://accounts.google.com/gsi/client';
    script.async = true;
    script.defer = true;
    script.onload = () => resolve();
    script.onerror = () => reject(new Error('Google API 載入失敗'));
    document.head.appendChild(script);
  });
}

// 生成驗證碼
function generateCaptcha() {
  const canvas = captchaCanvas.value;
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  // 清空畫布
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // 設置更大的字體大小 (原本 30px 增加 30%)
  const fontSize = 39;
  ctx.font = `bold ${fontSize}px Arial`;

  // 生成驗證碼
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz23456789';
  let text = '';
  for (let i = 0; i < 4; i++) {
    text += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  captchaText.value = text;

  // 設置漸變背景
  const gradient = ctx.createLinearGradient(0, 0, canvas.width, 0);
  gradient.addColorStop(0, '#f0f0f0');
  gradient.addColorStop(1, '#e0e0e0');
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  // 繪製文字 (調整間距以適應更大的字體)
  for (let i = 0; i < text.length; i++) {
    ctx.save();
    ctx.translate(40 + i * 45, canvas.height / 2); // 增加字元間距
    ctx.rotate((Math.random() - 0.5) * 0.3);
    ctx.fillStyle = `hsl(${Math.random() * 360}, 70%, 40%)`;
    ctx.fillText(text[i], 0, 0);
    ctx.restore();
  }

  // 添加干擾線 (增加線條寬度)
  for (let i = 0; i < 4; i++) {
    ctx.beginPath();
    ctx.strokeStyle = `rgba(${Math.random() * 255},${Math.random() * 255},${Math.random() * 255},0.3)`;
    ctx.lineWidth = 3; // 增加線條寬度
    ctx.moveTo(Math.random() * canvas.width, Math.random() * canvas.height);
    ctx.lineTo(Math.random() * canvas.width, Math.random() * canvas.height);
    ctx.stroke();
  }

  // 添加干擾點 (增加點的大小)
  for (let i = 0; i < 50; i++) {
    ctx.beginPath();
    ctx.arc(
      Math.random() * canvas.width,
      Math.random() * canvas.height,
      1.5, // 增加點的大小
      0,
      2 * Math.PI
    );
    ctx.fillStyle = `rgba(${Math.random() * 255},${Math.random() * 255},${Math.random() * 255},0.3)`;
    ctx.fill();
  }
}

// 組件掛載時生成驗證碼
onMounted(() => {
  generateCaptcha();
});
</script>

<template>
  <div class="login-container">
    <!-- 一般登入表單 -->
    <n-form
      ref="formRef"
      :model="formValue"
      :rules="rules"
      label-placement="left"
      label-width="auto"
      require-mark-placement="right-hanging"
      size="large"
      class="login-form"
    >
      <n-form-item label="帳號" path="username">
        <n-input v-model:value="formValue.username" placeholder="請輸入帳號" />
      </n-form-item>
      <n-form-item label="密碼" path="password">
        <n-input
          v-model:value="formValue.password"
          type="password"
          show-password-on="click"
          placeholder="請輸入密碼"
        />
      </n-form-item>

      <!-- 驗證碼 -->
      <n-form-item label="驗證碼" path="captcha">
        <div class="captcha-container">
          <n-input v-model:value="formValue.captcha" placeholder="請輸入驗證碼" />
          <canvas ref="captchaCanvas" @click="generateCaptcha" />
        </div>
      </n-form-item>

      <!-- 登入按鈕 -->
      <div class="button-container">
        <n-button
          type="primary"
          size="large"
          :loading="loading"
          :disabled="loading"
          block
          @click="handleSubmit"
        >
          登入
        </n-button>
      </div>

      <!-- Google 快速登入按鈕 -->
      <div class="google-login-container">
        <n-divider>或使用以下方式登入</n-divider>
        <n-button
          class="google-login-button"
          size="large"
          :loading="googleLoading"
          :disabled="googleLoading"
          block
          @click="handleGoogleLogin"
        >
          <template #icon>
            <img src="@/assets/images/google-icon.svg" alt="Google" class="google-icon">
          </template>
          使用 Google 帳號登入
        </n-button>
      </div>
    </n-form>
  </div>
</template>

<style scoped>
.login-container {
  width: 100%;
}

.login-form {
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.95) 0%, rgba(249, 250, 251, 0.95) 100%);
  padding: 40px;
  border-radius: 24px;
  box-shadow:
    0 8px 20px rgba(0, 0, 0, 0.06),
    0 2px 6px rgba(0, 0, 0, 0.04),
    0 0 1px rgba(0, 0, 0, 0.02);
  animation: fadeIn 0.5s ease-out;
  border: 1px solid rgba(255, 255, 255, 0.8);
  position: relative;
  overflow: hidden;
}

/* 添加表單背景效果 */
.login-form::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 6px;
  background: linear-gradient(90deg, #18a058, #36ad6a, #18a058);
  opacity: 0.8;
}

/* 美化輸入框 */
:deep(.n-input) {
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.9);
  transition: all 0.3s ease;
  border: 1px solid rgba(0, 0, 0, 0.08);
}

:deep(.n-input:hover) {
  transform: translateY(-1px);
  border-color: #36ad6a;
  box-shadow:
    0 4px 12px rgba(54, 173, 106, 0.08),
    0 0 0 2px rgba(54, 173, 106, 0.05);
}

:deep(.n-input:focus) {
  border-color: #36ad6a;
  box-shadow:
    0 4px 12px rgba(54, 173, 106, 0.1),
    0 0 0 2px rgba(54, 173, 106, 0.1);
}

:deep(.n-input .n-input__input-el) {
  font-size: 16px;
  padding: 16px 20px;
  height: 52px;
}

/* 美化表單標籤 */
:deep(.n-form-item-label) {
  font-weight: 600;
  color: #1f2937;
  font-size: 16px;
  padding-bottom: 10px;
  opacity: 0.85;
}

:deep(.n-form-item) {
  margin-bottom: 32px;
  position: relative;
}

/* 美化按鈕 */
:deep(.n-button) {
  font-weight: 600;
  height: 52px;
  border-radius: 16px;
  transition: all 0.3s ease;
  font-size: 17px;
  letter-spacing: 0.3px;
}

:deep(.n-button:not(:disabled)) {
  background: linear-gradient(135deg, #18a058 0%, #36ad6a 100%);
  border: none;
}

:deep(.n-button:not(:disabled):hover) {
  transform: translateY(-2px);
  box-shadow:
    0 6px 15px rgba(24, 160, 88, 0.3),
    0 0 0 1px rgba(24, 160, 88, 0.1);
  background: linear-gradient(135deg, #36ad6a 0%, #18a058 100%);
}

/* 驗證碼容器 */
.captcha-container {
  display: flex;
  gap: 20px;
  align-items: center;
}

.captcha-container canvas {
  width: 195px;
  height: 62px;
  cursor: pointer;
  border-radius: 16px;
  box-shadow:
    0 4px 8px rgba(0, 0, 0, 0.05),
    0 1px 3px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  background: white;
  border: 1px solid rgba(0, 0, 0, 0.08);
}

.captcha-container canvas:hover {
  transform: scale(1.02) translateY(-2px);
  box-shadow:
    0 8px 16px rgba(0, 0, 0, 0.08),
    0 2px 4px rgba(0, 0, 0, 0.12);
}

/* Google 登入按鈕 */
.google-login-button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  background-color: #fff;
  border: 1px solid rgba(0, 0, 0, 0.12);
  transition: all 0.3s ease;
  height: 52px;
  border-radius: 16px;
  font-weight: 600;
  font-size: 16px;
  color: #374151;
}

.google-login-button:hover {
  background-color: #f8f9fa;
  border-color: rgba(0, 0, 0, 0.2);
  transform: translateY(-2px);
  box-shadow:
    0 6px 15px rgba(0, 0, 0, 0.1),
    0 2px 4px rgba(0, 0, 0, 0.08);
}

.google-icon {
  width: 24px;
  height: 24px;
  transition: transform 0.3s ease;
}

.google-login-button:hover .google-icon {
  transform: scale(1.1) rotate(5deg);
}

/* 分隔線樣式 */
:deep(.n-divider) {
  margin: 40px 0;
  opacity: 0.8;
}

:deep(.n-divider__title) {
  font-size: 15px;
  font-weight: 500;
  color: #6b7280;
  background: linear-gradient(90deg, rgba(249, 250, 251, 0) 0%, rgba(249, 250, 251, 0.95) 25%, rgba(249, 250, 251, 0.95) 75%, rgba(249, 250, 251, 0) 100%);
  padding: 0 20px;
}

/* 按鈕容器 */
.button-container {
  margin-top: 40px;
}

.google-login-container {
  margin-top: 40px;
}

/* 添加動畫效果 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import type { FormInst, FormRules } from 'naive-ui';
import { NForm, NFormItem, NInput, NButton, NCheckbox, useMessage } from 'naive-ui';
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

    console.log('登入回應:', response); // 添加日誌

    // 檢查回應中是否包含 access token
    if (response.data?.access) {
      // 保存 token
      localStorage.setItem('access_token', response.data.access);
      if (response.data.refresh) {
        localStorage.setItem('refresh_token', response.data.refresh);
      }

      // 更新用戶狀態
      if (response.data.user) {
        await userStore.updateUserState(response.data.user, true);
      } else {
        // 如果回應中沒有用戶資料，嘗試獲取用戶資料
        const userResponse = await request.get(api.user.checkSigin);
        if (userResponse.data) {
          await userStore.updateUserState(userResponse.data, true);
        }
      }

      message.success('登入成功');

      // 確保跳轉成功
      const redirectPath = route.query.redirect?.toString() || '/member/dashboard';
      
      try {
        await router.push(redirectPath);
      } catch (error) {
        console.error('路由跳轉失敗，使用替代方法:', error);
        window.location.href = `/#${redirectPath}`;
      }
    } else {
      throw new Error('登入失敗：未收到有效的認證令牌');
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
    
    // 檢查網路連接
    try {
      const networkTest = await fetch('https://www.google.com/generate_204', { 
        method: 'HEAD',
        mode: 'no-cors',
        cache: 'no-store'
      });
      console.log('網路連接狀態:', {
        ok: true,
        type: networkTest.type
      });
    } catch (netError) {
      console.error('網路連接測試失敗:', netError);
      message.error('網路連接不穩定，無法連接到 Google 服務');
      googleLoading.value = false;
      return;
    }
    
    // 載入 Google API
    try {
      await loadGoogleAPI();
    } catch (apiError) {
      console.error('Google API 載入失敗:', apiError);
      message.error('無法載入 Google 登入服務，請稍後再試');
      googleLoading.value = false;
      return;
    }
    
    // 使用 gapi auth2 進行更傳統的 OAuth 流程，避免 FedCM 問題
    // @ts-expect-error Google API 類型定義不完整，需要使用 any 類型
    const google = (window as any).google;
    
    if (!google || !google.accounts || !google.accounts.oauth2) {
      console.error('Google OAuth API 未完全載入');
      message.error('Google 登入服務載入不完整，請刷新頁面後再試');
      googleLoading.value = false;
      return;
    }
    
    // 使用 OAuth 2.0 流程
    const tokenClient = google.accounts.oauth2.initTokenClient({
      client_id: '1063055916047-ic94ldh4ojm4gg18sbcqmenerdc98s2s.apps.googleusercontent.com',
      scope: 'email profile openid',
      callback: async (tokenResponse: any) => {
        try {
          if (!tokenResponse || tokenResponse.error) {
            console.error('Google OAuth 錯誤:', tokenResponse?.error || '未獲取到回應');
            message.error(`Google 登入失敗: ${tokenResponse?.error || '授權失敗'}`);
            googleLoading.value = false;
            return;
          }
          
          console.log('Google OAuth 成功:', {
            token存在: !!tokenResponse.access_token,
            token長度: tokenResponse.access_token?.length || 0
          });
          
          // 使用 access_token 獲取用戶信息
          try {
            const userInfoResponse = await fetch(
              'https://www.googleapis.com/oauth2/v3/userinfo',
              {
                headers: {
                  Authorization: `Bearer ${tokenResponse.access_token}`
                }
              }
            );
            
            if (!userInfoResponse.ok) {
              const errorText = await userInfoResponse.text();
              throw new Error(`獲取用戶信息失敗: ${errorText}`);
            }
            
            const userInfo = await userInfoResponse.json();
            console.log('獲取到 Google 用戶信息:', {
              email: userInfo.email,
              name: userInfo.name,
              sub: userInfo.sub
            });
            
            if (!userInfo.email) {
              throw new Error('Google 未提供電子郵件地址');
            }
            
            // 將用戶信息發送到後端進行登入
            const loginResult = await apiGoogleSignin({
              google_token: tokenResponse.access_token,
              email: userInfo.email,  // 明確傳送 email
              name: userInfo.name,    // 傳送姓名
              google_id: userInfo.sub // 傳送 Google ID
            });
            
            console.log('後端登入回應:', {
              status: loginResult.status,
              success: loginResult.data?.success,
              hasToken: !!loginResult.data?.access
            });
            
            if (loginResult.data?.access) {
              // 保存 token
              localStorage.setItem('access_token', loginResult.data.access);
              if (loginResult.data.refresh) {
                localStorage.setItem('refresh_token', loginResult.data.refresh);
              }
              
              // 獲取用戶資料
              const userResponse = await request.get(api.user.checkSigin);
              
              if (userResponse.data) {
                // 更新用戶狀態
                await userStore.updateUserState(userResponse.data, true);
                message.success('Google 登入成功！');
                
                // 跳轉到會員中心儀表板
                const redirectPath = route.query.redirect?.toString() || '/member/dashboard';
                try {
                  await router.push(redirectPath);
                } catch (error) {
                  console.error('路由跳轉失敗，使用替代方法:', error);
                  window.location.href = `/#${redirectPath}`;
                }
              } else {
                throw new Error('獲取用戶資料失敗');
              }
            } else {
              throw new Error(loginResult.data?.message || '登入失敗：後端未返回有效的認證令牌');
            }
          } catch (userInfoError: any) {
            console.error('處理用戶信息時出錯:', userInfoError);
            message.error(userInfoError.message || 'Google 用戶信息獲取失敗');
          }
        } catch (error: any) {
          console.error('Google 登入處理失敗:', error);
          message.error(error.message || 'Google 登入失敗，請稍後再試');
        } finally {
          googleLoading.value = false;
        }
      }
    });
    
    console.log('請求 Google 授權');
    tokenClient.requestAccessToken();
    
  } catch (error: any) {
    console.error('Google 登入整體錯誤:', error);
    message.error('Google 登入服務暫時無法使用，請稍後再試');
    googleLoading.value = false;
  }
};

// 載入 Google API
function loadGoogleAPI(): Promise<void> {
  return new Promise((resolve, reject) => {
    // @ts-expect-error Google API 類型定義不完整，需要使用 any 類型
    if (window.google && (window as any).google.accounts && (window as any).google.accounts.oauth2) {
      resolve();
      return;
    }

    const script = document.createElement('script');
    script.src = 'https://accounts.google.com/gsi/client';
    script.async = true;
    script.defer = true;
    script.onload = () => {
      // 確保 API 完全載入後再解析 Promise
      setTimeout(() => {
        // @ts-expect-error Google API 類型定義不完整，需要使用 any 類型
        if ((window as any).google && (window as any).google.accounts) {
          console.log('Google API 載入成功');
          resolve();
        } else {
          reject(new Error('Google API 加載不完整'));
        }
      }, 500); // 給予足夠時間讓 Google API 初始化
    };
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

  // 設置適中的字體大小
  const fontSize = 36; // 調整為更適中的大小
  ctx.font = `bold ${fontSize}px Arial`;

  // 生成驗證碼（減少使用容易混淆的字元）
  const chars = '23456789ABCDEFGHJKLMNPQRSTUVWXYZ'; // 移除容易混淆的字元
  let text = '';
  for (let i = 0; i < 4; i++) {
    text += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  captchaText.value = text;

  // 設置純色背景
  ctx.fillStyle = '#f5f5f5';
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  // 繪製文字（調整位置使更居中）
  for (let i = 0; i < text.length; i++) {
    ctx.save();
    ctx.translate(40 + i * 40, canvas.height / 2 + 2); // 調整間距和位置
    ctx.rotate((Math.random() - 0.5) * 0.2); // 保持較小的旋轉角度
    ctx.fillStyle = `hsl(${Math.random() * 360}, 80%, 45%)`; // 保持原有的顏色設定
    ctx.fillText(text[i], 0, 0);
    ctx.restore();
  }

  // 添加較少的干擾線
  for (let i = 0; i < 3; i++) {
    ctx.beginPath();
    ctx.strokeStyle = `rgba(${Math.random() * 255},${Math.random() * 255},${Math.random() * 255},0.2)`;
    ctx.lineWidth = 2;
    ctx.moveTo(Math.random() * canvas.width, Math.random() * canvas.height);
    ctx.lineTo(Math.random() * canvas.width, Math.random() * canvas.height);
    ctx.stroke();
  }

  // 添加較少的干擾點
  for (let i = 0; i < 30; i++) {
    ctx.beginPath();
    ctx.arc(
      Math.random() * canvas.width,
      Math.random() * canvas.height,
      1,
      0,
      2 * Math.PI
    );
    ctx.fillStyle = `rgba(${Math.random() * 255},${Math.random() * 255},${Math.random() * 255},0.2)`;
    ctx.fill();
  }
}

// 組件掛載時生成驗證碼
onMounted(() => {
  generateCaptcha();
});
</script>

<template>
  <div class="login-form-container">
    <NForm
      ref="formRef"
      :model="formValue"
      :rules="rules"
      class="login-form"
    >
      <!-- 帳號輸入 -->
      <NFormItem path="username" label="帳號">
        <NInput
          v-model:value="formValue.username"
          placeholder="請輸入帳號"
          :maxlength="30"
          class="form-input"
        />
      </NFormItem>

      <!-- 密碼輸入 -->
      <NFormItem path="password" label="密碼">
        <NInput
          v-model:value="formValue.password"
          type="password"
          placeholder="請輸入密碼"
          :maxlength="30"
          show-password-on="click"
          class="form-input"
        />
      </NFormItem>

      <!-- 驗證碼區域 -->
      <NFormItem path="captcha" label="驗證碼">
        <div class="captcha-container">
          <NInput
            v-model:value="formValue.captcha"
            placeholder="請輸入驗證碼"
            :maxlength="6"
            class="form-input captcha-input"
          />
          <canvas
            ref="captchaCanvas"
            width="200"
            height="50"
            class="captcha-canvas"
            @click="generateCaptcha"
          />
        </div>
      </NFormItem>

      <!-- 登入按鈕 -->
      <div class="button-container">
        <NButton
          type="primary"
          size="large"
          block
          :loading="loading"
          :disabled="loading"
          @click="handleSubmit"
        >
          {{ loading ? '登入中...' : '登入' }}
        </NButton>
      </div>

      <!-- Google 登入按鈕 -->
      <div class="google-login">
        <div class="divider">
          <span>或</span>
        </div>
        <NButton
          size="large"
          block
          :loading="googleLoading"
          :disabled="googleLoading"
          @click="handleGoogleLogin"
          class="google-button"
        >
          <template #icon>
            <img src="@/assets/images/google-icon.svg" alt="Google" class="google-icon" />
          </template>
          {{ googleLoading ? '處理中...' : '使用 Google 帳號登入' }}
        </NButton>
        <!-- 添加 Google 登入容器 -->
        <div id="googleLoginContainer" class="google-login-container"></div>
      </div>
    </NForm>
  </div>
</template>

<style scoped>
.login-form-container {
  width: 100%;
}

.login-form {
  width: 100%;
}

.form-input {
  width: 100%;
  border-radius: 8px;
}

.captcha-container {
  display: flex;
  gap: 16px;
  align-items: center;
}

.captcha-input {
  flex: 1;
}

.captcha-canvas {
  cursor: pointer;
  border-radius: 8px;
  transition: transform 0.2s ease;
}

.captcha-canvas:hover {
  transform: scale(1.02);
}

.button-container {
  margin-top: 24px;
}

.google-login {
  margin-top: 24px;
}

.divider {
  display: flex;
  align-items: center;
  text-align: center;
  margin: 16px 0;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  border-bottom: 1px solid #e5e7eb;
}

.divider span {
  padding: 0 16px;
  color: #6b7280;
  font-size: 14px;
}

.google-button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background-color: #ffffff;
  border: 1px solid #e5e7eb;
  color: #374151;
  font-weight: 500;
}

.google-button:hover {
  background-color: #f9fafb;
  border-color: #d1d5db;
}

.google-icon {
  width: 20px;
  height: 20px;
}

.google-login-container {
  margin-top: 16px;
  display: flex;
  justify-content: center;
  min-height: 40px;
}

:deep(.n-form-item .n-form-item-label) {
  font-weight: 500;
  color: #374151;
}

:deep(.n-input) {
  border-radius: 8px;
}

:deep(.n-button) {
  border-radius: 8px;
  height: 44px;
  font-weight: 500;
}
</style>

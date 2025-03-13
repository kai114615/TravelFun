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
  const fontSize = 24; // 調整為更小的大小
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
    ctx.translate(30 + i * 30, canvas.height / 2); // 調整間距和位置以適應更小的字體
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
      <div class="form-item">
        <i class="fas fa-user"></i>
        <NFormItem label="帳號" path="username">
          <NInput
            v-model:value="formValue.username"
            placeholder="請輸入帳號"
            maxlength="50"
            clearable
            class="form-input"
          />
        </NFormItem>
      </div>

      <div class="form-item">
        <i class="fas fa-lock"></i>
        <NFormItem label="密碼" path="password">
          <NInput
            v-model:value="formValue.password"
            type="password"
            placeholder="請輸入密碼"
            maxlength="50"
            clearable
            show-password-on="click"
            class="form-input"
          />
        </NFormItem>
      </div>

      <div class="forgot-password-link">
        <router-link to="/forgot-password">忘記密碼？</router-link>
      </div>

      <div class="form-item captcha-container">
        <i class="fas fa-shield-alt"></i>
        <NFormItem label="驗證碼" path="captcha">
          <div class="captcha-wrapper">
            <NInput
              v-model:value="formValue.captcha"
              placeholder="請輸入驗證碼"
              maxlength="6"
              class="form-input"
            />
            <div class="captcha-image">
              <canvas ref="captchaCanvas" width="150" height="50" @click="generateCaptcha"></canvas>
              <div class="refresh-button" @click="generateCaptcha">
                <i class="fas fa-sync-alt"></i>
              </div>
            </div>
          </div>
        </NFormItem>
      </div>

      <div class="button-container">
        <NButton
          type="primary"
          size="large"
          :loading="loading"
          :disabled="loading"
          @click="handleSubmit"
          class="login-button"
          block
        >
          {{ loading ? '登入中...' : '會員登入' }}
        </NButton>

        <NButton
          size="large"
          class="google-button"
          @click="handleGoogleLogin"
          :loading="googleLoading"
          :disabled="googleLoading"
          block
        >
          <template v-if="!googleLoading">
            <i class="fab fa-google" style="margin-right: 8px;"></i> 使用 Google 帳號登入
          </template>
          <template v-else>
            處理中...
          </template>
        </NButton>
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
  font-size: 14px; /* 整體表單字體縮小 */
}

.form-input {
  height: 45px; /* 輸入框高度縮小 */
  border-radius: 10px;
  background-color: rgba(255, 255, 255, 0.8);
  border: 2px solid rgba(47, 64, 80, 0.1);
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  padding-left: 45px !important;
  font-family: 'Noto Serif TC', serif;
  font-weight: 400;
  font-size: 14px; /* 輸入框文字縮小 */
}

.form-input:focus {
  background-color: rgba(255, 255, 255, 0.95);
  border-color: #1c84c6;
  box-shadow: 0 0 10px rgba(28, 132, 198, 0.2);
}

.form-item {
  margin-bottom: 20px; /* 縮小間距 */
  position: relative;
}

.form-item :deep(.n-form-item-label) {
  font-family: 'Noto Serif TC', serif;
  color: #2f4050;
  font-weight: 500;
  font-size: 14px; /* 表單標籤字體縮小 */
}

.form-item i {
  position: absolute;
  left: 15px;
  top: 38px; /* 調整圖示位置 */
  color: #2f4050;
  opacity: 0.7;
  font-size: 14px; /* 圖示縮小 */
  z-index: 1;
}

.login-button {
  height: 45px; /* 按鈕高度縮小 */
  background: linear-gradient(135deg, #1c84c6 0%, #23c6c8 100%);
  border: none;
  border-radius: 10px;
  font-size: 16px; /* 按鈕文字縮小 */
  font-weight: 500;
  letter-spacing: 1px;
  transition: all 0.3s ease;
  box-shadow: 0 5px 15px rgba(28, 132, 198, 0.3);
  font-family: 'Noto Serif TC', serif;
}

.login-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(28, 132, 198, 0.4);
  background: linear-gradient(135deg, #23c6c8 0%, #1c84c6 100%);
}

.google-button {
  height: 45px; /* 按鈕高度縮小 */
  border-radius: 10px;
  font-size: 14px; /* 按鈕文字縮小 */
  font-weight: 500;
  transition: all 0.3s ease;
  margin-top: 15px;
  font-family: 'Noto Serif TC', serif;
}

.forgot-password-link {
  text-align: right;
  margin-top: -5px; /* 縮小間距 */
  margin-bottom: 14px; /* 縮小間距 */
  display: block;
  width: 100%;
  visibility: visible;
}

.forgot-password-link a {
  color: #1c84c6;
  text-decoration: none;
  font-size: 13px; /* 忘記密碼文字縮小 */
  transition: color 0.2s ease;
  font-family: 'Noto Serif TC', serif;
  display: inline-block;
}

.forgot-password-link a:hover {
  color: #23c6c8;
  text-decoration: underline;
}

.captcha-container {
  margin-top: 16px;
  position: relative;
}

.captcha-wrapper {
  display: flex;
  gap: 10px;
  align-items: center;
}

.refresh-button {
  flex-shrink: 0;
  color: #1c84c6;
  cursor: pointer;
  transition: transform 0.3s ease;
}

.refresh-button:hover {
  transform: rotate(180deg);
  color: #23c6c8;
}

.captcha-image {
  position: relative;
}

.button-container {
  margin-top: 20px; /* 縮小間距 */
}

/* 新增樣式，確保所有輸入框內的文字大小一致 */
:deep(.n-input__input-el) {
  font-size: 14px !important;
}

/* 調整占位符文字大小 */
:deep(.n-input__placeholder) {
  font-size: 13px !important;
}
</style>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { NButton, NForm, NFormItem, NInput, useMessage } from 'naive-ui';
import { useRouter } from 'vue-router';
import { apiUserRegister } from '@/utils/api';
import { useUserStore } from '@/stores/user';

const router = useRouter();
const message = useMessage();
const loading = ref(false);
const userStore = useUserStore();

const formRef = ref(null);
const formValue = ref({
  username: '',
  full_name: '',
  email: '',
  password1: '',
  password2: '',
  captcha: ''
});

const rules = {
  username: {
    required: true,
    message: '請輸入帳號',
    trigger: 'blur'
  },
  full_name: {
    required: true,
    message: '請輸入全名',
    trigger: 'blur'
  },
  email: {
    required: true,
    type: 'email',
    message: '請輸入有效的電子郵箱',
    trigger: 'blur'
  },
  password1: {
    required: true,
    message: '請輸入密碼',
    trigger: 'blur',
    validator: (rule: any, value: string) => {
      if (value.length < 6)
        return new Error('密碼長度至少需要6個字符');

      return true;
    }
  },
  password2: {
    required: true,
    message: '請再次輸入密碼',
    trigger: 'blur',
    validator: (rule: any, value: string) => {
      return value === formValue.value.password1 ? true : new Error('兩次輸入的密碼不一致');
    }
  },
  captcha: {
    required: true,
    message: '請輸入驗證碼',
    trigger: 'blur',
    validator: (rule: any, value: string) => {
      return value.toLowerCase() === captchaText.value.toLowerCase() ? true : new Error('驗證碼錯誤');
    }
  }
};

async function handleSubmit () {
  try {
    await formRef.value?.validate();

    // 驗證表單
    if (formValue.value.captcha.toLowerCase() !== captchaText.value.toLowerCase()) {
      message.error('驗證碼錯誤');
      generateCaptcha();
      return;
    }

    loading.value = true;

    try {
      // 創建 FormData 對象
      const formData = new FormData();
      formData.append('username', formValue.value.username);
      formData.append('email', formValue.value.email);
      formData.append('password1', formValue.value.password1);
      formData.append('password2', formValue.value.password2);
      formData.append('full_name', formValue.value.full_name);

      // 輸出調試信息
      console.log('準備發送的註冊數據:');
      for (const [key, value] of formData.entries()) {
        console.log(`${key}:`, value);
      }

      // 發送註冊請求
      const response = await apiUserRegister(formData);

      if (response.data?.success) {
        message.success('註冊成功');

        // 自動登入
        await userStore.updateUserState(response.data.user, true);

        // 使用 window.location.href 進行頁面跳轉
        setTimeout(() => {
          window.location.href = `${window.location.origin}/#/member/dashboard`;
        }, 1000);
      }
    } catch (error: any) {
      console.error('註冊錯誤:', error);
      message.error(error.response?.data?.message || '註冊失敗，請稍後重試');
      generateCaptcha();
    } finally {
      loading.value = false;
    }
  } catch (error: any) {
    console.error('表單驗證錯誤:', error);
    message.error('請檢查表單填寫是否正確');
  }
}

// 驗證碼相關
const captchaText = ref('');
const captchaCanvas = ref<HTMLCanvasElement | null>(null);

function generateCaptcha () {
  const canvas = captchaCanvas.value;
  if (!canvas)
    return;

  const ctx = canvas.getContext('2d');
  if (!ctx)
    return;

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

// 在組件掛載後生成驗證碼
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
          :disabled="loading"
          class="form-input"
        />
      </NFormItem>

      <!-- 全名輸入 -->
      <NFormItem path="full_name" label="全名">
        <NInput
          v-model:value="formValue.full_name"
          placeholder="請輸入全名"
          :maxlength="30"
          :disabled="loading"
          class="form-input"
        />
      </NFormItem>

      <!-- 電子郵箱輸入 -->
      <NFormItem path="email" label="電子郵箱">
        <NInput
          v-model:value="formValue.email"
          placeholder="請輸入電子郵箱"
          :maxlength="50"
          :disabled="loading"
          class="form-input"
        />
      </NFormItem>

      <!-- 密碼輸入 -->
      <NFormItem path="password1" label="密碼">
        <NInput
          v-model:value="formValue.password1"
          type="password"
          placeholder="請輸入密碼"
          :maxlength="30"
          show-password-on="click"
          :disabled="loading"
          class="form-input"
        />
      </NFormItem>

      <!-- 確認密碼輸入 -->
      <NFormItem path="password2" label="確認密碼">
        <NInput
          v-model:value="formValue.password2"
          type="password"
          placeholder="請再次輸入密碼"
          :maxlength="30"
          show-password-on="click"
          :disabled="loading"
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
            :disabled="loading"
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

      <!-- 註冊按鈕 -->
      <div class="button-container">
        <NButton
          type="primary"
          size="large"
          block
          :loading="loading"
          :disabled="loading"
          @click="handleSubmit"
        >
          {{ loading ? '註冊中...' : '註冊' }}
        </NButton>
      </div>

      <!-- 返回登入選項 -->
      <div class="google-login">
        <div class="divider">
          <span>或</span>
        </div>
        <NButton
          size="large"
          block
          :disabled="loading"
          @click="router.push('/login')"
          class="login-button"
        >
          返回登入
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
  width: 100%;
  border-radius: 8px;
  font-size: 14px; /* 輸入框文字縮小 */
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
  font-size: 13px; /* 分隔線文字縮小 */
}

.login-button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background-color: #ffffff;
  border: 1px solid #e5e7eb;
  color: #374151;
  font-weight: 500;
  font-size: 14px; /* 登入按鈕文字縮小 */
}

.login-button:hover {
  background-color: #f9fafb;
  border-color: #d1d5db;
}

:deep(.n-form-item .n-form-item-label) {
  font-weight: 500;
  color: #374151;
  font-size: 14px; /* 表單標籤文字縮小 */
}

:deep(.n-input) {
  border-radius: 8px;
}

:deep(.n-button) {
  border-radius: 8px;
  height: 40px; /* 按鈕高度縮小 */
  font-weight: 500;
  font-size: 14px; /* 按鈕文字縮小 */
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

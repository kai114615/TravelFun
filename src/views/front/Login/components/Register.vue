<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue';
import { NForm, NFormItem, NInput, NButton, NUpload, NIcon, NSpace, NInputGroup, NCard, NDivider, useMessage } from 'naive-ui';
import { CloudUploadOutlined, RefreshOutlined } from '@vicons/material';
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
  avatar: null,
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
      if (value.length < 6) {
        return new Error('密碼長度至少需要6個字符');
      }
      return true;
    }
  },
  password2: {
    required: true,
    message: '請再次輸入密碼',
    trigger: 'blur',
    validator: (rule: any, value: string) => {
      return value === formValue.value.password1 ? true : new Error('兩次輸入的密碼不一致')
    }
  },
  captcha: {
    required: true,
    message: '請輸入驗證碼',
    trigger: 'blur',
    validator: (rule: any, value: string) => {
      return value.toLowerCase() === captchaText.value.toLowerCase() ? true : new Error('驗證碼錯誤')
    }
  }
};

const handleSubmit = async () => {
  try {
    // 驗證表單
    await formRef.value?.validate();
    
    // 創建 FormData 對象
    const formData = new FormData();
    
    // 添加基本資料
    formData.append('username', formValue.value.username);
    formData.append('email', formValue.value.email);
    formData.append('password1', formValue.value.password1);
    formData.append('password2', formValue.value.password2);
    formData.append('full_name', formValue.value.full_name);
    
    // 如果有頭像，添加到 FormData
    if (formValue.value.avatar instanceof File) {
      console.log('正在添加頭像到 FormData:', {
        fileName: formValue.value.avatar.name,
        fileType: formValue.value.avatar.type,
        fileSize: formValue.value.avatar.size
      });
      
      // 使用原始文件名添加文件
      formData.append('avatar', formValue.value.avatar);
      
      // 輸出 FormData 內容進行調試
      console.log('FormData 內容:');
      for (let [key, value] of formData.entries()) {
        if (value instanceof File) {
          console.log(`${key}:`, {
            name: value.name,
            type: value.type,
            size: value.size
          });
        } else {
          console.log(`${key}:`, value);
        }
      }
    } else {
      console.log('沒有頭像文件需要上傳');
    }

    // 驗證碼驗證
    if (formValue.value.captcha.toLowerCase() !== captchaText.value.toLowerCase()) {
      message.error('驗證碼錯誤');
      generateCaptcha();
      return;
    }

    loading.value = true;
    
    try {
      // 發送註冊請求
      const response = await apiUserRegister(formData);
      console.log('註冊響應:', response.data);

      if (response.data?.success) {
        message.success('註冊成功');
        
        // 自動登入
        await userStore.updateUserState(response.data.user, true);
        
        // 使用 window.location.href 進行頁面跳轉
        setTimeout(() => {
          window.location.href = window.location.origin + '/#/member/dashboard';
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
};

// 修改檔案上傳處理
const customRequest = ({ file }: { file: File }) => {
  console.log('收到文件:', {
    name: file.name,
    type: file.type,
    size: file.size,
    lastModified: file.lastModified
  });
  
  return new Promise((resolve, reject) => {
    // 檢查檔案類型
    if (!file.type.startsWith('image/')) {
      message.error('請上傳圖片檔案');
      reject(new Error('Invalid file type'));
      return;
    }
    
    // 檢查檔案大小 (2MB)
    if (file.size > 2 * 1024 * 1024) {
      message.error('圖片大小不能超過 2MB');
      reject(new Error('File too large'));
      return;
    }
    
    // 創建新的 File 對象，確保文件名和類型正確
    const newFile = new File([file], file.name, {
      type: file.type,
      lastModified: file.lastModified
    });
    
    // 保存文件到表單數據
    formValue.value.avatar = newFile;
    
    console.log('文件已保存到表單:', {
      fileName: newFile.name,
      fileType: newFile.type,
      fileSize: newFile.size
    });
    
    resolve();
  });
};

// 驗證碼相關
const captchaText = ref('');
const captchaCanvas = ref<HTMLCanvasElement | null>(null);

const generateCaptcha = () => {
  const canvas = captchaCanvas.value;
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  // 清空畫布
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // 生成隨機驗證碼
  const characters = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz';
  let code = '';
  for (let i = 0; i < 4; i++) {
    code += characters.charAt(Math.floor(Math.random() * characters.length));
  }
  captchaText.value = code;

  // 繪製背景
  ctx.fillStyle = '#f0f0f0';
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  // 繪製文字
  ctx.font = 'bold 24px Arial';
  ctx.fillStyle = '#333';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  
  // 在一條直線上繪製字符
  for (let i = 0; i < code.length; i++) {
    const x = 20 + i * 25;
    const y = canvas.height / 2;
    ctx.fillText(code[i], x, y);
  }

  // 添加干擾線
  for (let i = 0; i < 3; i++) {
    ctx.beginPath();
    ctx.strokeStyle = `rgba(${Math.random() * 255},${Math.random() * 255},${Math.random() * 255},0.5)`;
    ctx.moveTo(Math.random() * canvas.width, Math.random() * canvas.height);
    ctx.lineTo(Math.random() * canvas.width, Math.random() * canvas.height);
    ctx.stroke();
  }

  // 添加干擾點
  for (let i = 0; i < 50; i++) {
    ctx.fillStyle = `rgba(${Math.random() * 255},${Math.random() * 255},${Math.random() * 255},0.5)`;
    ctx.fillRect(Math.random() * canvas.width, Math.random() * canvas.height, 2, 2);
  }
};

// 在組件掛載後生成驗證碼
onMounted(() => {
  generateCaptcha();
});
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <NCard class="max-w-md w-full">
      <div class="text-center">
        <h2 class="text-2xl font-bold mb-6">註冊帳號</h2>
      </div>
      <NForm
        ref="formRef"
        :model="formValue"
        :rules="rules"
        label-placement="left"
        label-width="auto"
        require-mark-placement="right-hanging"
        size="large"
      >
        <NFormItem label="帳號" path="username">
          <NInput
            v-model:value="formValue.username"
            placeholder="請輸入帳號"
            :disabled="loading"
          />
        </NFormItem>

        <NFormItem label="全名" path="full_name">
          <NInput
            v-model:value="formValue.full_name"
            placeholder="請輸入全名"
            :disabled="loading"
          />
        </NFormItem>

        <NFormItem label="電子郵箱" path="email">
          <NInput
            v-model:value="formValue.email"
            placeholder="請輸入電子郵箱"
            :disabled="loading"
          />
        </NFormItem>

        <NFormItem label="密碼" path="password1">
          <NInput
            v-model:value="formValue.password1"
            type="password"
            placeholder="請輸入密碼"
            show-password-on="click"
            :disabled="loading"
          />
        </NFormItem>

        <NFormItem label="確認密碼" path="password2">
          <NInput
            v-model:value="formValue.password2"
            type="password"
            placeholder="請再次輸入密碼"
            show-password-on="click"
            :disabled="loading"
          />
        </NFormItem>

        <NFormItem label="驗證碼" path="captcha">
          <div class="flex gap-2">
            <NInput
              v-model:value="formValue.captcha"
              placeholder="請輸入驗證碼"
              :disabled="loading"
            />
            <div class="flex items-center gap-2">
              <canvas
                ref="captchaCanvas"
                width="120"
                height="40"
                class="border cursor-pointer"
                @click="generateCaptcha"
              />
              <NButton circle quaternary @click="generateCaptcha" :disabled="loading">
                <template #icon>
                  <NIcon>
                    <RefreshOutlined />
                  </NIcon>
                </template>
              </NButton>
            </div>
          </div>
        </NFormItem>

        <NFormItem label="頭像">
          <NUpload
            accept="image/*"
            :custom-request="customRequest"
            :max="1"
            list-type="image-card"
            :disabled="loading"
          >
            <div class="flex flex-col items-center justify-center">
              <NIcon size="20">
                <CloudUploadOutlined />
              </NIcon>
              <span class="mt-2">點擊上傳</span>
            </div>
          </NUpload>
        </NFormItem>

        <div class="flex flex-col gap-4 mt-6">
          <NButton
            type="primary"
            block
            secondary
            strong
            :loading="loading"
            :disabled="loading"
            @click="handleSubmit"
          >
            {{ loading ? '註冊中...' : '註冊' }}
          </NButton>

          <NDivider>或者</NDivider>

          <NButton
            block
            strong
            @click="router.push('/login')"
            :disabled="loading"
          >
            返回登入
          </NButton>
        </div>
      </NForm>
    </NCard>
  </div>
</template>

<style scoped>
.text-primary {
  color: #18a058;
}

canvas {
  background-color: white;
}
</style> 
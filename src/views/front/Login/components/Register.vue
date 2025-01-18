<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { NForm, NFormItem, NInput, NButton, NUpload, NIcon, NSpace, NInputGroup, NCard, NDivider, useMessage } from 'naive-ui';
import { CloudUploadOutlined, RefreshOutlined } from '@vicons/material';
import { useRouter } from 'vue-router';
import { apiUserRegister } from '@/utils/api';

const router = useRouter();
const message = useMessage();
const loading = ref(false);

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
    trigger: 'blur'
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
      return value === captchaText.value ? true : new Error('驗證碼錯誤')
    }
  }
};

const handleSubmit = () => {
  formRef.value?.validate(async (errors: any) => {
    if (!errors) {
      loading.value = true;
      try {
        const formData = new FormData();
        formData.append('username', formValue.value.username);
        formData.append('full_name', formValue.value.full_name);
        formData.append('email', formValue.value.email);
        formData.append('password1', formValue.value.password1);
        formData.append('password2', formValue.value.password2);
        if (formValue.value.avatar) {
          formData.append('avatar', formValue.value.avatar);
        }

        const response = await apiUserRegister(formData);
        
        if (response.data.success) {
          message.success('註冊成功！');
          router.push('/login');
        } else {
          throw new Error(response.data.message || '註冊失敗');
        }
      } catch (error: any) {
        message.error(error.message || '註冊失敗');
        generateCaptcha(); // 重新生成驗證碼
      } finally {
        loading.value = false;
      }
    }
  });
};

const customRequest = ({ file }: { file: File }) => {
  formValue.value.avatar = file;
  return Promise.resolve();
};

// 验证码相关
const captchaText = ref('');
const captchaCanvas = ref<HTMLCanvasElement | null>(null);

const generateCaptcha = () => {
  const canvas = captchaCanvas.value;
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  // 清空画布
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // 生成随机验证码
  const characters = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz';
  let code = '';
  for (let i = 0; i < 4; i++) {
    code += characters.charAt(Math.floor(Math.random() * characters.length));
  }
  captchaText.value = code;

  // 绘制背景
  ctx.fillStyle = '#f0f0f0';
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  // 绘制文字
  ctx.font = 'bold 24px Arial';
  ctx.fillStyle = '#333';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  
  // 在一条直线上绘制字符
  for (let i = 0; i < code.length; i++) {
    const x = 20 + i * 25;
    const y = canvas.height / 2;
    ctx.fillText(code[i], x, y);
  }

  // 添加干扰线
  for (let i = 0; i < 3; i++) {
    ctx.beginPath();
    ctx.strokeStyle = `rgba(${Math.random() * 255},${Math.random() * 255},${Math.random() * 255},0.5)`;
    ctx.moveTo(Math.random() * canvas.width, Math.random() * canvas.height);
    ctx.lineTo(Math.random() * canvas.width, Math.random() * canvas.height);
    ctx.stroke();
  }

  // 添加干扰点
  for (let i = 0; i < 50; i++) {
    ctx.fillStyle = `rgba(${Math.random() * 255},${Math.random() * 255},${Math.random() * 255},0.5)`;
    ctx.fillRect(Math.random() * canvas.width, Math.random() * canvas.height, 2, 2);
  }
};

// 在组件挂载后生成验证码
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
          />
        </NFormItem>

        <NFormItem label="全名" path="full_name">
          <NInput
            v-model:value="formValue.full_name"
            placeholder="請輸入全名"
          />
        </NFormItem>

        <NFormItem label="電子郵箱" path="email">
          <NInput
            v-model:value="formValue.email"
            placeholder="請輸入電子郵箱"
          />
        </NFormItem>

        <NFormItem label="密碼" path="password1">
          <NInput
            v-model:value="formValue.password1"
            type="password"
            placeholder="請輸入密碼"
            show-password-on="click"
          />
        </NFormItem>

        <NFormItem label="確認密碼" path="password2">
          <NInput
            v-model:value="formValue.password2"
            type="password"
            placeholder="請再次輸入密碼"
            show-password-on="click"
          />
        </NFormItem>

        <NFormItem label="驗證碼" path="captcha">
          <div class="flex gap-2">
            <NInput
              v-model:value="formValue.captcha"
              placeholder="請輸入驗證碼"
            />
            <div class="flex items-center gap-2">
              <canvas
                ref="captchaCanvas"
                width="120"
                height="40"
                class="border cursor-pointer"
                @click="generateCaptcha"
              />
              <NButton circle @click="generateCaptcha">
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
            @click="handleSubmit"
          >
            {{ loading ? '註冊中...' : '註冊' }}
          </NButton>

          <NDivider>或者</NDivider>

          <NButton
            block
            strong
            @click="$router.push('/login')"
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
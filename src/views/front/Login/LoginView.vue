<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { NCard, NForm, NFormItem, NInput, NButton, NCheckbox, NDivider, useMessage } from 'naive-ui';
import { useRouter, useRoute } from 'vue-router';
import { useUserStore } from '@/stores/user';

const router = useRouter();
const route = useRoute();
const message = useMessage();
const userStore = useUserStore();
const formRef = ref(null);
const captchaCanvas = ref<HTMLCanvasElement | null>(null);
const captchaText = ref('');
const loading = ref(false);

const formValue = ref({
  username: '',
  password: '',
  captcha: '',
  rememberMe: false
});

const rules = {
  username: {
    required: true,
    message: '請輸入帳號',
    trigger: 'blur'
  },
  password: {
    required: true,
    message: '請輸入密碼',
    trigger: 'blur'
  },
  captcha: {
    required: true,
    message: '請輸入驗證碼',
    trigger: 'blur',
    validator: (rule: any, value: string) => {
      return value.toLowerCase() === captchaText.value.toLowerCase() 
        ? true 
        : new Error('驗證碼錯誤');
    }
  }
};

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

const handleSubmit = () => {
  formRef.value?.validate(async (errors: any) => {
    if (!errors) {
      loading.value = true;
      try {
        await userStore.signin({
          username: formValue.value.username,
          password: formValue.value.password,
          rememberMe: formValue.value.rememberMe
        });
        message.success('登入成功');
        
        // 檢查是否有重定向路徑
        const redirect = route.query.redirect as string;
        setTimeout(() => {
          if (redirect) {
            window.location.href = window.location.origin + '/#' + redirect;
          } else {
            window.location.href = window.location.origin + '/#/member/dashboard';
          }
        }, 500);
      } catch (error: any) {
        message.error(error.response?.data?.detail || error.message || '登入失敗');
        generateCaptcha(); // 重新生成驗證碼
      } finally {
        loading.value = false;
      }
    }
  });
};

const goToRegister = () => {
  router.push('/register');
};

onMounted(() => {
  generateCaptcha();
});
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <NCard class="max-w-md w-full">
      <div class="text-center">
        <h2 class="text-2xl font-bold mb-6">會員登入</h2>
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

        <NFormItem label="密碼" path="password">
          <NInput
            v-model:value="formValue.password"
            type="password"
            show-password-on="click"
            placeholder="請輸入密碼"
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
                  <div class="i-material-symbols:refresh"></div>
                </template>
              </NButton>
            </div>
          </div>
        </NFormItem>

        <div class="flex justify-between items-center mb-4">
          <NCheckbox v-model:checked="formValue.rememberMe" :disabled="loading">
            記住我
          </NCheckbox>
          <NButton text type="primary" @click="router.push('/forgot-password')" :disabled="loading">
            忘記密碼？
          </NButton>
        </div>

        <div class="flex flex-col gap-4">
          <NButton
            type="primary"
            block
            secondary
            strong
            :loading="loading"
            :disabled="loading"
            @click="handleSubmit"
          >
            {{ loading ? '登入中...' : '登入' }}
          </NButton>

          <NDivider>或者</NDivider>

          <NButton
            block
            strong
            @click="goToRegister"
            :disabled="loading"
          >
            註冊新帳號
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

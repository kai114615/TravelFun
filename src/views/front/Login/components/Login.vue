<template>
  <!-- No changes to template section -->
</template>

<script setup>
import { ref, nextTick } from 'vue';
import { useRouter } from 'vue';
import { useUserStore } from '@/stores/user';
import { useMessage } from 'naive-ui';

const router = useRouter();
const userStore = useUserStore();
const message = useMessage();

const formRef = ref(null);
const formValue = ref({
  username: '',
  password: '',
  rememberMe: false
});
const loading = ref(false);

const handleSubmit = () => {
  formRef.value?.validate(async (errors: any) => {
    if (!errors) {
      loading.value = true;
      try {
        const loginResult = await userStore.signin({
          username: formValue.value.username,
          password: formValue.value.password,
          rememberMe: formValue.value.rememberMe
        });

        if (loginResult) {
          // 立即更新用戶狀態
          await userStore.checkLoginStatus();
          message.success('登入成功');
          
          // 使用 window.open 方式跳轉並重新載入
          const targetUrl = window.location.origin + '/#/member/dashboard';
          window.open(targetUrl, '_self');
        }
      } catch (error: any) {
        message.error(error.message || '登入失敗');
        if (typeof generateCaptcha === 'function') {
          generateCaptcha();
        }
      } finally {
        loading.value = false;
      }
    }
  });
};
</script> 
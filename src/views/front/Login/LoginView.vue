# 登入頁面主視圖
<script setup lang="ts">
import { NText } from 'naive-ui';
import Login from './components/Login.vue';
</script>

<template>
  <div class="login-view">
    <div class="login-container">
      <h1 class="login-title">
        會員登入
      </h1>
      <Login />
      <div class="register-link">
        <NText>還不是會員？</NText>
        <router-link to="/register">
          立即註冊
        </router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-view {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
  padding: 20px;
  position: relative;
  overflow: hidden;
}

/* 添加背景動畫效果 */
.login-view::before {
  content: '';
  position: absolute;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255,255,255,0.8) 0%, rgba(255,255,255,0) 60%);
  animation: rotate 30s linear infinite;
  z-index: 1;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

@keyframes rotate {
  from {
    transform: translate(-50%, -50%) rotate(0deg);
  }
  to {
    transform: translate(-50%, -50%) rotate(360deg);
  }
}

.login-container {
  width: 100%;
  max-width: 580px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  box-shadow:
    0 4px 6px -1px rgba(0, 0, 0, 0.1),
    0 2px 4px -1px rgba(0, 0, 0, 0.06),
    0 0 0 1px rgba(255, 255, 255, 0.1) inset;
  padding: 48px;
  position: relative;
  z-index: 2;
  backdrop-filter: blur(10px);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.login-container:hover {
  transform: translateY(-2px);
  box-shadow:
    0 10px 15px -3px rgba(0, 0, 0, 0.1),
    0 4px 6px -2px rgba(0, 0, 0, 0.05),
    0 0 0 1px rgba(255, 255, 255, 0.1) inset;
}

.login-title {
  text-align: center;
  font-size: 32px;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 36px;
  letter-spacing: -0.5px;
  position: relative;
}

.login-title::after {
  content: '';
  display: block;
  width: 40px;
  height: 3px;
  background: linear-gradient(90deg, #18a058 0%, #36ad6a 100%);
  margin: 12px auto 0;
  border-radius: 2px;
}

.register-link {
  margin-top: 24px;
  text-align: center;
  padding: 16px;
  background: rgba(24, 160, 88, 0.05);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.register-link :deep(a) {
  color: #18a058;
  text-decoration: none;
  font-weight: 500;
  position: relative;
  transition: all 0.3s ease;
}

.register-link :deep(a:hover) {
  color: #36ad6a;
}

.register-link :deep(a::after) {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 100%;
  height: 2px;
  background: currentColor;
  transform: scaleX(0);
  transition: transform 0.3s ease;
  transform-origin: right;
}

.register-link :deep(a:hover::after) {
  transform: scaleX(1);
  transform-origin: left;
}

/* 響應式設計 */
@media (max-width: 640px) {
  .login-container {
    padding: 36px 24px;
    margin: 20px;
  }

  .login-title {
    font-size: 28px;
  }
}
</style>

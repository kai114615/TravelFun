<!-- 註冊頁面主視圖 -->
<script setup lang="ts">
import { NText } from 'naive-ui';
import Register from './components/Register.vue';
</script>

<template>
  <div class="login-view">
    <div class="loginColumns animated fadeInDown">
      <div class="ibox-content">
        <h2 class="font-bold">會員註冊</h2>
        <p>加入 TravelFun 享受旅遊樂趣</p>
        <Register />
        <div class="register-link">
          <NText>已有帳號？</NText>
          <router-link to="/login">
            返回登入
          </router-link>
        </div>
      </div>
      <hr/>
      <div class="footer-text">
        <small>TravelFun 會員中心 &copy; 2024</small>
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
  background: url('https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?q=80&w=2070&auto=format&fit=crop');
  background-size: cover;
  background-position: center;
  background-attachment: fixed;
  padding: 20px;
  position: relative;
}

.login-view::before {
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
  margin-bottom: 30px;
  letter-spacing: 1px;
  font-weight: 300;
}

.register-link {
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

.register-link :deep(a) {
  color: #1c84c6;
  text-decoration: none;
  font-weight: 500;
  position: relative;
  transition: all 0.3s ease;
}

.register-link :deep(a:hover) {
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

/* 響應式設計 */
@media (max-width: 640px) {
  .ibox-content {
    padding: 30px 20px;
  }

  .font-bold {
    font-size: 28px;
  }
}
</style>

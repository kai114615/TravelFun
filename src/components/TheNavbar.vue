<!-- 導覽列 -->
<template>
  <nav class="bg-white shadow-sm">
    <div class="max-w-7xl mx-auto px-4">
      <div class="flex justify-between h-16">
        <!-- Logo 和主要導覽連結 -->
        <div class="flex items-center gap-8">
          <RouterLink to="/" class="flex items-center">
            <img src="@/assets/logo.png" alt="Travel Fun Logo" class="h-8">
          </RouterLink>
          
          <div class="flex items-center gap-4">
            <RouterLink to="/attractions" class="text-gray-700 hover:text-primary transition-colors">景點</RouterLink>
            <RouterLink to="/forum" class="text-gray-700 hover:text-primary transition-colors">討論區</RouterLink>
            <RouterLink to="/about" class="text-gray-700 hover:text-primary transition-colors">關於我們</RouterLink>
          </div>
        </div>

        <!-- 用戶資訊/登入區域 -->
        <div class="flex items-center gap-4">
          <template v-if="isLoggedIn">
            <!-- 登入狀態 -->
            <RouterLink to="/member" class="flex items-center gap-2 hover:opacity-80 transition-opacity">
              <NAvatar
                :src="userProfile.avatar || 'https://picsum.photos/200'"
                :size="32"
                round
              />
              <span class="font-medium">{{ userProfile.name }}</span>
            </RouterLink>
            <NButton @click="handleLogout" secondary size="small">
              登出
            </NButton>
          </template>
          <template v-else>
            <!-- 未登入狀態 -->
            <RouterLink to="/login">
              <NButton secondary size="small">登入/註冊</NButton>
            </RouterLink>
          </template>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { RouterLink } from 'vue-router';
import { NButton, NAvatar } from 'naive-ui';
import { useUserStore } from '@/stores/user';

const userStore = useUserStore();

// 判斷是否登入
const isLoggedIn = computed(() => userStore.isLoggedIn);

// 用戶資料
const userProfile = computed(() => userStore.userProfile);

// 處理登出
const handleLogout = async () => {
  try {
    await userStore.logout();
    window.location.href = '/login';
  } catch (error) {
    console.error('登出失敗:', error);
  }
};
</script>

<style scoped>
.router-link-active {
  color: var(--primary-color);
}

/* 隱藏特定的 SVG 圖示 */
#header .svg-icon {
  display: none;
}

/* 如果上面的選擇器不夠精確，可以使用更具體的選擇器 */
#header > div > div > div:nth-child(2) > div:first-child > a > i > svg {
  display: none;
}
</style> 
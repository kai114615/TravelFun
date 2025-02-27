<script setup lang="ts">
// 匯入 Vue 的響應式 API
import { ref } from 'vue';

// 匯入共用元件
import Banner from '@/components/Banner.vue';
import Footer from '@/components/Footer.vue';

// 匯入活動列表元件
import ActivityList from '@/views/front/Activity/ActivityList.vue';

// 設定頁面標題
const title = ref('主題育樂');
</script>

<template>
  <!-- 主要內容區塊 -->
  <main>
    <!-- 頁面橫幅 -->
    <Banner bg-url="/images/banner.jpg">
      <template #title>
        {{ title }}
      </template>
      <template #sec-title>
        探索精彩的主題活動
      </template>
    </Banner>

    <!-- 活動列表容器 -->
    <div class="container mx-auto px-4 py-8">
      <ActivityList />
    </div>

    <!-- 路由視圖 -->
    <router-view />
  </main>

  <!-- 頁尾區塊 -->
  <Footer />
</template>

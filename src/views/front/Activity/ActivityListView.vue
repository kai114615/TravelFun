// 主題育樂活動列表頁面元件
<script setup lang="ts">
import { ref } from 'vue';
import type { Ref } from 'vue';

// 匯入共用元件
import Banner from '@/components/Banner.vue';
import Footer from '@/components/Footer.vue';

// 匯入活動列表元件
import ActivityList from '@/views/front/Activity/ActivityList.vue';

// 設定頁面標題
const title: Ref<string> = ref('主題育樂');
const subTitle: Ref<string> = ref('探索精彩的主題活動');
</script>

<template>
  <main>
    <!-- 頁面橫幅 -->
    <Banner bg-url="/images/banner.jpg">
      <template #title>
        {{ title }}
      </template>
      <template #sec-title>
        {{ subTitle }}
      </template>
    </Banner>

    <!-- 活動列表容器 -->
    <div class="container mx-auto px-4 py-8">
      <ActivityList />
    </div>

    <!-- 路由視圖 -->
    <router-view />
  </main>

  <!-- 頁尾 -->
  <Footer />
</template>

<style scoped>
/* 主題育樂活動列表頁面樣式 */
.activity-list {
  min-height: 100vh;
  /* 最小高度為視窗高度 */
  background-color: #f5f7fa;
  /* 設定背景色 */
}
</style>

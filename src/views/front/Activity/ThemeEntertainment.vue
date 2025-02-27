// 主題育樂頁面元件
<script>
// 匯入活動列表元件
import ActivityList from '@/views/front/Activity/ActivityList.vue';

export default {
  name: 'ThemeEntertainment',
  components: {
    ActivityList, // 註冊活動列表元件
  },
};
</script>

<template>
  <!-- 主題育樂頁面容器 -->
  <div class="theme-entertainment">
    <!-- 活動列表元件 -->
    <ActivityList />
  </div>
</template>

<style scoped>
/* 主題育樂頁面樣式 */
.theme-entertainment {
  min-height: 100vh;
  /* 最小高度為視窗高度 */
  background-color: #f5f7fa;
  /* 設定背景色 */
}
</style>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import Banner from '@/components/Banner.vue';

const title = ref('商城中心');
const router = useRouter();

function navigateToProducts() {
  router.push({ name: 'MallProducts' });
}
</script>

<template>
  <main>
    <Banner bg-url="/images/banner.jpg">
      <template #title>
        {{ title }}
      </template>
      <template #sec-title>
        探索我們精選的商品
      </template>
    </Banner>
    <div class="container mx-auto px-4 py-0">
      <div class="text-center mt-4">
        <button class="cta-button" @click="navigateToProducts">
          立即查看所有商品
        </button> <!-- cta按鈕 -->
      </div>
      <h2 class="text-2xl font-bold mb-6">
        即將推出
      </h2>
      <p class="text-gray-600">
        我們正在準備更多精彩的商品，敬請期待！
      </p>

      {{ edit_2 }} <!-- 其他內容 -->
    </div>
  </main>
</template>

<style scoped>
.cta-button {
  background-color: green; /* 綠底 */
  color: white; /* 白字 */
  border: none; /* 無邊框 */
  border-radius: 8px; /* 圓角 */
  padding: 10px 20px; /* 內邊距 */
  font-size: 16px; /* 字體大小 */
  font-weight: bold;
  cursor: pointer; /* 鼠標指針 */
  margin-top: 0px; /* 按鈕與上方內容的間距 */

}
.cta-button:hover {
  background-color: darkgreen; /* 滑鼠懸停時的顏色 */
}
</style>

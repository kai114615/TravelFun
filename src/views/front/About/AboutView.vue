<script setup lang="ts">
import { ref } from 'vue';
import Banner from '@/components/Banner.vue';

const title = ref('關於我們');
</script>

<template>
  <main>
    <Banner bg-url="/images/banner.jpg">
      <template #title>
        {{ title }}
      </template>
      <template #sec-title>
        了解更多關於我們的資訊
      </template>
    </Banner>
    <div class="container mx-auto px-4 py-8">
      <div class="max-w-3xl mx-auto">
        <h2 class="text-2xl font-bold mb-6">我們的故事</h2>
        <p class="text-gray-600 mb-8">
          Travel Fun 是一個專注於提供優質旅遊體驗的平台。我們致力於為用戶提供最好的旅遊規劃、門票預訂和行程推薦服務。
        </p>
        
        <h2 class="text-2xl font-bold mb-6">我們的服務</h2>
        <ul class="list-disc list-inside text-gray-600 mb-8 space-y-2">
          <li>精選商品：嚴選優質旅遊商品和門票</li>
          <li>主題育樂：提供多樣化的主題樂園門票</li>
          <li>AI推薦：智能推薦最適合您的旅遊行程</li>
          <li>社群交流：分享旅遊經驗和心得</li>
        </ul>

        <h2 class="text-2xl font-bold mb-6">聯絡我們</h2>
        <p class="text-gray-600">
          如果您有任何問題或建議，歡迎與我們聯繫。
        </p>
      </div>
    </div>
  </main>
</template> 
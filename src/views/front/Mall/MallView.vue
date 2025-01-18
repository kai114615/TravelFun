<script setup lang="ts">
import { ref } from 'vue';
import Banner from '@/components/Banner.vue';

const title = ref('商城中心');
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
    <div class="container mx-auto px-4 py-8">
      <h2 class="text-2xl font-bold mb-6">即將推出</h2>
      <p class="text-gray-600">我們正在準備更多精彩的商品，敬請期待！</p>
    </div>
  </main>
</template> 
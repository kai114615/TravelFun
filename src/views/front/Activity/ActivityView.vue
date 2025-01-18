<script setup lang="ts">
import { ref } from 'vue';
import Banner from '@/components/Banner.vue';

const title = ref('主題育樂');
</script>

<template>
  <main>
    <Banner bg-url="/images/banner.jpg">
      <template #title>
        {{ title }}
      </template>
      <template #sec-title>
        探索精彩的主題活動
      </template>
    </Banner>
    <div class="container mx-auto px-4 py-8">
      <h2 class="text-2xl font-bold mb-6">即將推出</h2>
      <p class="text-gray-600">我們正在籌備更多精彩的主題活動，敬請期待！</p>
    </div>
  </main>
</template> 
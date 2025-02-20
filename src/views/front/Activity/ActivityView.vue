<script setup lang="ts">
import { ref } from 'vue';
import Banner from '@/components/Banner.vue';
import Footer from '@/components/Footer.vue';
import EventsList from '@/components/EventsList.vue';

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
      <EventsList />
    </div>
    <router-view />
  </main>
  <Footer />
</template>

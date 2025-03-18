<script setup lang="ts">
// Vue 相關
import { storeToRefs } from 'pinia';
import { useRouter } from 'vue-router';

// 資料與狀態管理
import { useProductStore } from '@/stores';
import { mockHotCitys, mockNews } from './_Context';

// 頁面元件
import Banner from '@/components/Banner.vue';
import Footer from '@/components/Footer.vue';
import HotCity from './components/HotCity.vue';
import Member from './components/Member.vue';
import Search from './components/Search.vue';
import { SwiperNews, SwiperProduct } from '@/components/Swiper';

// 路由控制
const router = useRouter();

// 商品資料
const productStore = useProductStore();
const { getByNewest, getByPopular } = storeToRefs(productStore);
const { getFilterData } = productStore;

// 頁面方法
const goCountry = () => router.push({ name: 'Country', params: { countryName: 'taiwan' } });
</script>

<template>
  <main>
    <!-- 橫幅 -->
    <Banner bg-url="/images/banner.jpg" :center="false">
      <template #title>
        <span>旅遊趣</span>
        陪你去台灣各地
      </template>
      <template #sec-title>
        讓我們帶著你一同欣賞台灣的美
      </template>
      <Search />
    </Banner>

    <!-- 新聞輪播 -->
    <div class="mb-4 md:mt-[60px] md:mb-0">
      <SwiperNews :news="mockNews" />
    </div>

    <!-- 裝飾圖片 -->
    <img src="/images/travel-the-world.png" alt="travel world fun" class="-z-10 hidden -translate-y-8 md:block">

    <!-- 熱門商品 -->
    <SwiperProduct title="Top 10 商品" sec-title="尋找最受歡迎的商品嗎？別再猶豫，立刻挑選！" :products="getFilterData(getByPopular)" />

    <!-- 裝飾圖片 -->
    <img src="/images/home-bg.png" alt="home bg" class="my-6" loading="lazy">

    <!-- 最新商品 -->
    <SwiperProduct title="最新產品" sec-title="一直關注最新產品的我們，給您帶來最好的選擇和品質！" :btn="{ text: '查看更多' }"
      :products="getFilterData(getByNewest)" @btn-click="goCountry" />

    <!-- 熱門城市 -->
    <HotCity :hot-citys="mockHotCitys" />

    <!-- 會員區塊 -->
    <Member />
  </main>

  <!-- 頁腳 -->
  <Footer />
</template>

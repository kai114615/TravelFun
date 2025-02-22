<script setup lang="ts">
import { onMounted, ref, watch } from 'vue';
import { useCartStore } from '@/stores/cart';

const cartStore = useCartStore();
const showPreview = ref(false);

onMounted(() => {
  // 初始化購物車
  const savedCart = localStorage.getItem('cart');
  console.log('Saved cart data:', savedCart);

  if (savedCart) {
    try {
      const cartData = JSON.parse(savedCart);
      console.log('Parsed cart data:', cartData);
      cartStore.$patch({ items: cartData });
      console.log('Cart store after initialization:', cartStore.items);
    } catch (error) {
      console.error('Failed to parse cart data:', error);
    }
  }
});

// 監聽購物車變化
watch(() => cartStore.items, (newItems) => {
  console.log('Cart items changed:', newItems);
}, { deep: true });
</script>

<template>
  <!-- 購物車按鈕 -->
  <div class="relative" @mouseenter="showPreview = true" @mouseleave="showPreview = false">
    <router-link to="/cart" class="relative inline-block">
      <i class="fas fa-shopping-cart text-xl" />
      <span
        v-if="cartStore.totalQuantity > 0"
        class="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center"
      >
        {{ cartStore.totalQuantity }}
      </span>
    </router-link>

    <!-- 購物車預覽視窗 -->
    <div
      v-show="showPreview && cartStore.items.length > 0"
      class="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-lg z-50 border border-gray-200"
    >
      <!-- 預覽視窗標題 -->
      <div class="p-4 border-b border-gray-200">
        <div class="flex justify-between items-center">
          <h3 class="text-lg font-semibold">
            購物車內容
          </h3>
          <span class="text-sm text-gray-600">共 {{ cartStore.items.length }} 件商品</span>
        </div>
      </div>

      <!-- 商品列表 -->
      <div class="max-h-60 overflow-y-auto p-4">
        <div v-for="item in cartStore.items" :key="item.id" class="flex items-center gap-3 mb-3 pb-3 border-b border-gray-100 last:border-b-0 last:mb-0 last:pb-0">
          <img :src="item.image_url" :alt="item.name" class="w-16 h-16 object-cover rounded">
          <div class="flex-grow">
            <p class="text-sm font-medium line-clamp-1">
              {{ item.name }}
            </p>
            <p class="text-xs text-gray-500">
              數量: {{ item.quantity }}
            </p>
            <p class="text-sm font-semibold text-green-600">
              NT$ {{ item.price * item.quantity }}
            </p>
          </div>
        </div>
      </div>

      <!-- 底部總計和按鈕 -->
      <div class="p-4 border-t border-gray-200 bg-gray-50">
        <div class="flex justify-between items-center mb-3">
          <span class="font-medium">總計:</span>
          <span class="font-semibold text-green-600">NT$ {{ cartStore.totalAmount }}</span>
        </div>
        <router-link
          to="/cart"
          class="block w-full bg-green-600 text-white text-center py-2 rounded-lg hover:bg-green-700 transition-colors"
        >
          前往購物車
        </router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.line-clamp-1 {
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>

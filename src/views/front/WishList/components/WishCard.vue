<script setup lang="ts">
import { NButton, NEllipsis, NIcon, NThing } from 'naive-ui';
import { FavoriteOutlined, ShoppingCartOutlined } from '@vicons/material';
import { ElMessage } from 'element-plus';
import type { Product } from '@/types';
import { currency } from '@/utils/global';
import { useCartStore, useFavoriteStore } from '@/stores';

const props = defineProps<Product>();

const favoriteStore = useFavoriteStore();
const cartStore = useCartStore();

const { removeFavorite } = favoriteStore;

// 加入購物車
function addToCart (event: Event) {
  event.stopPropagation(); // 阻止事件冒泡，避免觸發父元素的點擊事件

  try {
    // 添加到購物車 store
    cartStore.addToCart({
      id: Number(props.id),
      name: props.title,
      price: props.price,
      quantity: 1,
      image_url: props.imageUrl,
      stock: 99 // 默認庫存
    });

    ElMessage.success('成功加入購物車！');
  } catch (error) {
    console.error('加入購物車失敗:', error);
    ElMessage.error('加入購物車失敗，請稍後再試');
  }
}
</script>

<template>
  <NThing :title="title" class="p-2">
    <template #header>
      <div class="text-lg font-medium text-gray-800 hover:text-green-600 transition-colors">
        {{ title }}
      </div>
    </template>
    <template #header-extra>
      <div class="flex gap-2">
        <NButton text class="flex items-center justify-center hover:bg-green-50 rounded-full w-10 h-10 transition-colors" @click.stop="addToCart">
          <NIcon size="24" color="#4CAF50" class="icon-hover">
            <ShoppingCartOutlined />
          </NIcon>
        </NButton>
        <NButton text class="flex items-center justify-center hover:bg-red-50 rounded-full w-10 h-10 transition-colors" @click.stop="removeFavorite(id, title)">
          <NIcon size="24" color="#EE5220" class="icon-hover">
            <FavoriteOutlined />
          </NIcon>
        </NButton>
      </div>
    </template>
    <template #description>
      <div class="my-2">
        <NEllipsis :line-clamp="2" class="text-gray-600">
          {{ description }}
        </NEllipsis>
      </div>
    </template>
    <template #footer>
      <div class="flex justify-between items-center mt-2 pt-2 border-t border-gray-100">
        <div class="text-sm text-gray-500 bg-gray-100 px-2 py-1 rounded">
          {{ category }}
        </div>
        <h5 class="font-bold text-green-600">
          {{ currency(price) }}
        </h5>
      </div>
    </template>
  </NThing>
</template>

<style scoped>
.icon-hover {
  transition: transform 0.2s ease;
}
.icon-hover:hover {
  transform: scale(1.1);
}
</style>

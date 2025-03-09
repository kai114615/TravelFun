<script setup lang="ts">
import { onBeforeRouteUpdate, onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';
import { ShoppingAPI } from '@/api/shopping';
import type { Product } from '@/api/shopping';
import Header from '@/components/Header.vue';

const route = useRoute();
const product = ref<Product | null>(null);
const loading = ref(true);
const error = ref<string | null>(null);

async function loadProduct() {
  loading.value = true;
  error.value = null;
  try {
    const productId = Number.parseInt(route.params.productId as string);
    const data = await ShoppingAPI.getProduct(productId);
    product.value = data;
  }
  catch (err) {
    error.value = '載入商品失敗，請稍後再試';
    console.error('載入商品失敗:', err);
  }
  finally {
    loading.value = false;
  }
}

onMounted(() => {
  loadProduct();
})

onBeforeRouteUpdate((to, from) => {
  if (to.params.productId !== from.params.productId)
    loadProduct();
})
</script>

<template>
  <div>
    <Header />
    <n-layout>
      <n-layout-content class="container mx-auto px-4 py-8">
        <n-card v-if="!loading">
          <template #header>
            <div class="flex justify-between items-center">
              <h1 class="text-2xl font-bold">
                {{ product?.name }}
              </h1>
            </div>
          </template>

          <div class="grid grid-cols-2 gap-8">
            <!-- 商品圖片 -->
            <div>
              <n-image
                :src="product?.image_url || '/src/assets/images/placeholder.jpg'"
                :alt="product?.name"
                object-fit="cover"
                class="w-full"
                preview-disabled
              />
            </div>

            <!-- 商品資訊 -->
            <div class="space-y-4">
              <div class="text-xl font-bold text-green-600">
                NT$ {{ product?.price }}
              </div>

              <div class="text-gray-600">
                {{ product?.description }}
              </div>

              <div class="text-sm">
                庫存: {{ product?.stock }}
              </div>

              <n-button
                type="success"
                size="large"
                block
                :disabled="!product?.is_active || product?.stock <= 0"
              >
                {{ product?.is_active && product?.stock > 0 ? '加入購物車' : '暫無庫存' }}
              </n-button>
            </div>
          </div>
        </n-card>
        <n-spin v-else size="large" />

        <!-- 錯誤提示 -->
        <n-alert
          v-if="error"
          type="error"
          :title="error"
          style="margin-top: 16px"
        />
      </n-layout-content>
    </n-layout>
  </div>
</template>

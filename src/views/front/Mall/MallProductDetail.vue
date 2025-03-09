<script setup lang="ts">
import { onMounted, ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import {
  NAlert,
  NBreadcrumb,
  NBreadcrumbItem,
  NButton,
  NCard,
  NCarousel,
  NCarouselItem,
  NImage,
  NInputNumber,
  NSelect,
  NSpin,
  NTag,
} from 'naive-ui';
import { ShoppingAPI } from '@/api/shopping';
import type { Product } from '@/api/shopping';
import Header from '@/components/Header.vue';

// 添加 props 定義
const props = defineProps<{
  id?: string
}>();
const route = useRoute();
const product = ref<Product | null>(null);
const loading = ref(true);
const error = ref<string | null>(null);
const quantity = ref(1);
const selectedSize = ref(null);
const installment = ref(true);

// 根據實際商品圖片動態設置
const productImages = ref<string[]>([]);

// 根據商品資料動態設置
const sizeOptions = ref([
  { label: '女生US07', value: 'US07' },
  { label: '女生US08', value: 'US08' },
  { label: '女生US09', value: 'US09' },
]);

// 根據商品資料動態設置
const productTags = ref<string[]>([]);

async function loadProduct() {
  loading.value = true;
  error.value = null;
  try {
    const productId = Number.parseInt(props.id || route.params.id as string);
    console.log('Loading product with ID:', productId);
    const data = await ShoppingAPI.getProduct(productId);
    console.log('Loaded product data:', data);

    product.value = data;

    // 設置商品圖片
    if (data.image_url)
      productImages.value = [data.image_url];

    // 設置商品標籤
    if (data.category) {
      productTags.value = [
        data.category,
        `${data.category} ${data.brand}`,
        data.brand,
      ];
    }
  }
  catch (err) {
    console.error('載入商品失敗:', err);
    error.value = '載入商品失敗，請稍後再試';
  }
  finally {
    loading.value = false;
  }
}

// 修改路由參數監聽
watch(
  () => route.params.id,
  (newId) => {
    if (newId)
      loadProduct();
  },
);

onMounted(() => {
  loadProduct();
})

// 加入購物車
function addToCart() {
  if (!selectedSize.value) {
    // 可以添加提示用戶選擇尺寸的邏輯
    return;
  }
  // TODO: 實作加入購物車邏輯
  console.log('加入購物車:', {
    productId: product.value?.id,
    quantity: quantity.value,
    size: selectedSize.value,
  });
}

// 立即購買
function buyNow() {
  if (!selectedSize.value) {
    // 可以添加提示用戶選擇尺寸的邏輯
    return;
  }
  // TODO: 實作立即購買邏輯
  console.log('立即購買:', {
    productId: product.value?.id,
    quantity: quantity.value,
    size: selectedSize.value,
  });
}
</script>

<template>
  <div>
    <Header />
    <n-layout>
      <n-layout-content class="container mx-auto px-4 py-8">
        <div v-if="loading" class="flex justify-center items-center min-h-[400px]">
          <NSpin size="large" />
        </div>

        <div v-else-if="error" class="flex justify-center items-center min-h-[400px]">
          <NAlert type="error" :title="error" />
        </div>

        <template v-else>
          <!-- 麵包屑導航 -->
          <div class="text-sm mb-4">
            <NBreadcrumb>
              <NBreadcrumbItem>{{ product?.category }}</NBreadcrumbItem>
              <NBreadcrumbItem>{{ product?.name }}</NBreadcrumbItem>
            </NBreadcrumb>
          </div>

          <NCard>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
              <!-- 左側商品圖片 -->
              <div>
                <NCarousel
                  show-arrow
                  dot-type="line"
                  effect="fade"
                  class="carousel-container"
                >
                  <NCarouselItem v-for="(image, index) in productImages" :key="index">
                    <NImage
                      :src="image || '/src/assets/images/placeholder.jpg'"
                      :alt="product?.name"
                      object-fit="cover"
                      class="w-full h-full"
                      preview-disabled
                    />
                  </NCarouselItem>
                </NCarousel>
              </div>

              <!-- 右側商品資訊 -->
              <div class="space-y-6">
                <!-- 品牌名稱 -->
                <div class="text-gray-600">
                  {{ product?.brand }}
                </div>

                <!-- 商品名稱 -->
                <h1 class="text-2xl font-bold">
                  {{ product?.name }}
                </h1>

                <!-- 價格資訊 -->
                <div class="space-y-2">
                  <div class="text-2xl font-bold text-green-600">
                    NT$ {{ product?.price }}
                  </div>
                  <div v-if="product?.original_price" class="text-gray-400 line-through">
                    NT$ {{ product?.original_price }}
                  </div>
                  <div v-if="product?.discount" class="text-red-500">
                    ({{ product.discount }}折)
                  </div>
                </div>

                <!-- 分期付款資訊 -->
                <div v-if="installment" class="bg-gray-50 p-4 rounded-lg">
                  <div class="text-sm text-gray-600">
                    6 期 0 利率 每期 NT$ {{ Math.floor(Number(product?.price) / 6) }}
                  </div>
                </div>

                <!-- 尺寸選擇 -->
                <div class="space-y-2">
                  <div class="font-medium">
                    尺寸
                  </div>
                  <NSelect v-model:value="selectedSize" :options="sizeOptions" />
                </div>

                <!-- 數量選擇 -->
                <div class="space-y-2">
                  <div class="font-medium">
                    數量
                  </div>
                  <NInputNumber
                    v-model:value="quantity"
                    :min="1"
                    :max="product?.stock || 1"
                  />
                  <div class="text-sm text-gray-500">
                    庫存: {{ product?.stock }}
                  </div>
                </div>

                <!-- 按鈕群組 -->
                <div class="space-y-4">
                  <NButton
                    type="primary"
                    size="large"
                    block
                    :disabled="!product?.is_active || product?.stock <= 0"
                    @click="addToCart"
                  >
                    加入購物車
                  </NButton>
                  <NButton
                    type="success"
                    size="large"
                    block
                    :disabled="!product?.is_active || product?.stock <= 0"
                    @click="buyNow"
                  >
                    立即購買
                  </NButton>
                </div>

                <!-- 商品標籤 -->
                <div class="flex flex-wrap gap-2">
                  <NTag
                    v-for="tag in productTags"
                    :key="tag"
                    size="small"
                    :bordered="false"
                  >
                    {{ tag }}
                  </NTag>
                </div>
              </div>
            </div>
          </NCard>
        </template>
      </n-layout-content>
    </n-layout>
  </div>
</template>

<style scoped>
.container {
  max-width: 1200px;
}

.carousel-container {
  width: 100%;
  height: 400px;
}

.n-carousel-item {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>

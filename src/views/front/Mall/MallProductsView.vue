<script setup lang="ts">
import { computed, ref } from 'vue';
import { useRouter } from 'vue-router';
import categoriesData from './data/categories.json';
import productsData from './data/MallProduct.json';

const router = useRouter();
const categories = ref(categoriesData.categories);
const products = ref(productsData);
const selectedCategory = ref('');
const selectedBrand = ref('');

// 切換分類
function toggleCategory(categoryId: string) {
  if (selectedCategory.value === categoryId) {
    selectedCategory.value = '';
    selectedBrand.value = '';
  }
  else {
    selectedCategory.value = categoryId;
    selectedBrand.value = '';
  }
}

// 選擇品牌
function selectBrand(categoryId: string, brand: string) {
  selectedCategory.value = categoryId;
  selectedBrand.value = brand;
}

// 過濾商品
const filteredProducts = computed(() => {
  if (!selectedBrand.value)
    return products.value;

  return products.value.filter(product => product.category === selectedBrand.value);
});

// 查看商品詳情
function viewProductDetail(productId: number) {
  router.push({ name: 'MallProductDetail', params: { id: productId } });
}
</script>

<template>
  <div class="container mx-auto px-4 py-8">
    <div class="flex">
      <!-- 左側分類欄 -->
      <div class="w-1/4 pr-8">
        <div class="bg-white rounded-lg shadow p-4">
          <h2 class="text-xl font-bold mb-4">
            商品分類
          </h2>
          <!-- 第一階層分類按鈕 -->
          <div v-for="category in categories" :key="category.id" class="mb-4">
            <button
              class="w-full text-left px-4 py-2 rounded-lg transition-colors duration-200"
              :class="{
                'bg-green-600 text-white': selectedCategory === category.id,
                'hover:bg-green-100': selectedCategory !== category.id,
              }"
              @click="toggleCategory(category.id)"
            >
              {{ category.name }}
            </button>
            <!-- 第二階層品牌按鈕 -->
            <div
              v-if="selectedCategory === category.id"
              class="ml-4 mt-2 space-y-2"
            >
              <button
                v-for="brand in category.brands"
                :key="brand"
                class="w-full text-left px-3 py-1 text-sm rounded transition-colors duration-200"
                :class="{
                  'bg-green-200 text-green-800': selectedBrand === brand,
                  'hover:bg-gray-100': selectedBrand !== brand,
                }"
                @click="selectBrand(category.id, brand)"
              >
                {{ brand }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 右側商品列表 -->
      <div class="w-3/4">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div
            v-for="product in filteredProducts"
            :key="product.id"
            class="bg-white rounded-lg shadow overflow-hidden hover:shadow-lg transition-shadow duration-300"
          >
            <img
              :src="product.image_url"
              :alt="product.name"
              class="w-full h-48 object-cover"
            >
            <div class="p-4">
              <h3 class="text-lg font-semibold mb-2 line-clamp-2">
                {{ product.name }}
              </h3>
              <p class="text-gray-600 mb-2 line-clamp-2">
                {{ product.description }}
              </p>
              <div class="flex justify-between items-center">
                <span class="text-green-600 font-bold">NT$ {{ product.price }}</span>
                <button
                  class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition-colors duration-200"
                  @click="viewProductDetail(product.id)"
                >
                  查看詳情
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>

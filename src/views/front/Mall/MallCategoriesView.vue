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

// 價格範圍
const priceRange = ref({
  min: null as number | null,
  max: null as number | null,
});

// 排序選項
const sortOption = ref('default');

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

// 套用價格過濾
function applyPriceFilter() {
  // 價格過濾邏輯已整合到 computed 屬性中
}

// 套用排序
function applySorting() {
  // 排序邏輯已整合到 computed 屬性中
}

// 過濾和排序商品
const sortedAndFilteredProducts = computed(() => {
  let filteredProducts = products.value;

  // 品牌過濾
  if (selectedBrand.value) {
    // 使用品牌名稱進行過濾
    filteredProducts = filteredProducts.filter(product =>
      product.category === selectedBrand.value,
    );
  }
  else if (selectedCategory.value) {
    // 如果只選擇了類別，顯示該類別下所有品牌的商品
    const selectedCategoryData = categories.value.find(c => c.id === selectedCategory.value);
    if (selectedCategoryData) {
      filteredProducts = filteredProducts.filter(product =>
        selectedCategoryData.brands.includes(product.category),
      );
    }
  }

  // 價格範圍過濾
  if (priceRange.value.min !== null || priceRange.value.max !== null) {
    filteredProducts = filteredProducts.filter((product) => {
      const price = Number.parseFloat(product.price);
      const minOk = priceRange.value.min === null || price >= priceRange.value.min;
      const maxOk = priceRange.value.max === null || price <= priceRange.value.max;
      return minOk && maxOk;
    });
  }

  // 排序
  switch (sortOption.value) {
    case 'price-asc':
      return [...filteredProducts].sort((a, b) => Number.parseFloat(a.price) - Number.parseFloat(b.price));
    case 'price-desc':
      return [...filteredProducts].sort((a, b) => Number.parseFloat(b.price) - Number.parseFloat(a.price));
    case 'name-asc':
      return [...filteredProducts].sort((a, b) => a.name.localeCompare(b.name));
    case 'name-desc':
      return [...filteredProducts].sort((a, b) => b.name.localeCompare(a.name));
    default:
      return filteredProducts;
  }
});

// 查看商品詳情
function viewProductDetail(productId: number) {
  router.push({ name: 'MallProductDetail', params: { id: productId } });
}
</script>

<template>
  <div class="container mx-auto px-4 py-8">
    <div class="flex">
      <!-- 左側篩選欄 -->
      <div class="w-1/4 pr-8 space-y-6">
        <!-- 商品分類 -->
        <div class="bg-white rounded-lg shadow p-4">
          <h2 class="text-xl font-bold mb-4">
            商品分類
          </h2>
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

        <!-- 價格範圍 -->
        <div class="bg-white rounded-lg shadow p-4">
          <h2 class="text-xl font-bold mb-4">
            價格範圍
          </h2>
          <div class="space-y-4">
            <div>
              <label class="block text-sm text-gray-600 mb-1">最低價格</label>
              <input
                v-model.number="priceRange.min"
                type="number"
                class="w-full px-3 py-2 border rounded focus:outline-none focus:border-green-500"
                placeholder="最低價格"
              >
            </div>
            <div>
              <label class="block text-sm text-gray-600 mb-1">最高價格</label>
              <input
                v-model.number="priceRange.max"
                type="number"
                class="w-full px-3 py-2 border rounded focus:outline-none focus:border-green-500"
                placeholder="最高價格"
              >
            </div>
            <button
              class="w-full bg-green-600 text-white py-2 rounded hover:bg-green-700 transition-colors duration-200"
              @click="applyPriceFilter"
            >
              套用價格範圍
            </button>
          </div>
        </div>

        <!-- 排序方式 -->
        <div class="bg-white rounded-lg shadow p-4">
          <h2 class="text-xl font-bold mb-4">
            排序方式
          </h2>
          <select
            v-model="sortOption"
            class="w-full px-3 py-2 border rounded focus:outline-none focus:border-green-500"
            @change="applySorting"
          >
            <option value="default">
              預設排序
            </option>
            <option value="price-asc">
              價格由低到高
            </option>
            <option value="price-desc">
              價格由高到低
            </option>
            <option value="name-asc">
              名稱 A-Z
            </option>
            <option value="name-desc">
              名稱 Z-A
            </option>
          </select>
        </div>
      </div>

      <!-- 右側商品列表 -->
      <div class="w-3/4">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div
            v-for="product in sortedAndFilteredProducts"
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

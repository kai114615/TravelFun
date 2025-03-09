<script>
import categoriesData from '@/data/categories.json';
import airMattresses from '@/data/momo_air_mattresses.json';
import campingTables from '@/data/momo_camping_tables.json';
import campingTents from '@/data/momo_camping_tents.json';
import chargers from '@/data/momo_chargers.json';

export default {
  name: 'ProductList',
  data() {
    return {
      allProducts: [],
      searchQuery: '',
      sortOrder: '',
      expandedCategories: {},
      selectedFilters: {}, // 格式: { categoryId: Set(brands) }
      currentPage: 1,
      itemsPerPage: 12,
      categories: categoriesData.categories,
    };
  },
  computed: {
    filteredProducts() {
      let result = this.allProducts;

      // 搜尋過濾
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase();
        result = result.filter(product =>
          product.商品名稱.toLowerCase().includes(query)
          || product.品牌.toLowerCase().includes(query),
        );
      }

      // 分類和品牌過濾
      const hasActiveFilters = Object.values(this.selectedFilters).some(brands => brands.size > 0);
      if (hasActiveFilters) {
        result = result.filter((product) => {
          const categoryBrands = this.selectedFilters[product.category];
          return categoryBrands.size === 0 || categoryBrands.has(product.品牌);
        })
      }

      // 價格排序
      if (this.sortOrder) {
        result = [...result].sort((a, b) => {
          const priceA = Number.parseInt(a.價格);
          const priceB = Number.parseInt(b.價格);
          return this.sortOrder === 'asc' ? priceA - priceB : priceB - priceA;
        })
      }

      return result;
    },

    // 分頁相關計算
    totalPages() {
      return Math.ceil(this.filteredProducts.length / this.itemsPerPage);
    },

    paginatedProducts() {
      const start = (this.currentPage - 1) * this.itemsPerPage;
      const end = start + this.itemsPerPage;
      return this.filteredProducts.slice(start, end);
    },
  },
  watch: {
    // 當搜尋條件改變時，重置頁碼
    searchQuery() {
      this.currentPage = 1;
    },
    sortOrder() {
      this.currentPage = 1;
    },
  },
  created() {
    // 初始化商品資料
    this.allProducts = [
      ...airMattresses.map(item => ({ ...item, category: 'air_mattresses' })),
      ...campingTables.map(item => ({ ...item, category: 'camping_tables' })),
      ...campingTents.map(item => ({ ...item, category: 'camping_tents' })),
      ...chargers.map(item => ({ ...item, category: 'chargers' })),
    ];

    // 初始化分類展開狀態和過濾器
    this.categories.forEach((category) => {
      this.expandedCategories[category.id] = false;
      this.selectedFilters[category.id] = new Set();
    })
  },
  methods: {
    toggleCategory(categoryId) {
      this.$set(this.expandedCategories, categoryId, !this.expandedCategories[categoryId]);
    },
    toggleBrandFilter(categoryId, brand) {
      if (this.selectedFilters[categoryId].has(brand))
        this.selectedFilters[categoryId].delete(brand);
      else
        this.selectedFilters[categoryId].add(brand);

      this.currentPage = 1;
      this.$forceUpdate();
    },
    isSelectedBrand(categoryId, brand) {
      return this.selectedFilters[categoryId].has(brand);
    },
  },
};
</script>

<template>
  <div class="product-list container mx-auto px-4 py-8">
    <!-- 搜尋和過濾區 -->
    <div class="mb-8 space-y-4">
      <!-- 搜尋框 -->
      <div class="flex gap-4">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="搜尋商品..."
          class="p-2 border rounded-lg flex-grow"
        >
        <!-- 價格排序 -->
        <select
          v-model="sortOrder"
          class="p-2 border rounded-lg"
        >
          <option value="">
            價格排序
          </option>
          <option value="asc">
            價格由低到高
          </option>
          <option value="desc">
            價格由高到低
          </option>
        </select>
      </div>

      <!-- 分類過濾 - 改為階層式 -->
      <div class="flex flex-col gap-2">
        <div v-for="category in categories" :key="category.id" class="category-group">
          <!-- 分類標題 -->
          <button
            class="w-full flex justify-between items-center px-4 py-2 bg-gray-100 rounded-lg hover:bg-gray-200"
            @click="toggleCategory(category.id)"
          >
            <span>{{ category.name }}</span>
            <span class="transform transition-transform" :class="{ 'rotate-180': expandedCategories[category.id] }">
              ▼
            </span>
          </button>

          <!-- 品牌列表 -->
          <div v-if="expandedCategories[category.id]" class="ml-4 mt-2 space-y-2">
            <button
              v-for="brand in category.brands"
              :key="brand"
              class="px-4 py-2 rounded-full w-full text-left" :class="[
                isSelectedBrand(category.id, brand)
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-200 text-gray-700',
              ]"
              @click="toggleBrandFilter(category.id, brand)"
            >
              {{ brand }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 商品列表 -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <div v-for="product in paginatedProducts" :key="product.id" class="product-card">
        <div class="bg-white rounded-lg shadow-md p-4">
          <img :src="product.圖片網址" :alt="product.商品名稱" class="w-full h-48 object-cover rounded-t-lg">
          <div class="p-4">
            <h3 class="text-lg font-semibold mb-2">
              {{ product.商品名稱 }}
            </h3>
            <p class="text-gray-600 mb-2">
              品牌: {{ product.品牌 }}
            </p>
            <p class="text-red-600 font-bold">
              NT$ {{ product.價格 }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- 分頁控制 -->
    <div class="mt-8 flex justify-center gap-2">
      <button
        :disabled="currentPage === 1"
        class="px-4 py-2 rounded-lg bg-blue-500 text-white disabled:bg-gray-300"
        @click="currentPage--"
      >
        上一頁
      </button>
      <span class="px-4 py-2">{{ currentPage }} / {{ totalPages }}</span>
      <button
        :disabled="currentPage === totalPages"
        class="px-4 py-2 rounded-lg bg-blue-500 text-white disabled:bg-gray-300"
        @click="currentPage++"
      >
        下一頁
      </button>
    </div>
  </div>
</template>

  <style scoped>
  .product-card {
    transition: transform 0.2s;
  }

  .product-card:hover {
    transform: translateY(-5px);
  }

  button:disabled {
    cursor: not-allowed;
  }
  </style>

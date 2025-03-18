<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import {
  NButton,
  NCard,
  NCollapse,
  NCollapseItem,
  NEmpty,
  NGrid,
  NGridItem,
  NImage,
  NInputNumber,
  NLayout,
  NLayoutContent,
  NPagination,
  NResult,
  NSelect,
  NSpace,
  NSpin,
  NTag,
  NText,
} from 'naive-ui';
import { useRouter, useRoute } from 'vue-router';
import Header from '@/components/Header.vue';
import { type Product as BaseProduct, ShoppingAPI } from '@/api/shopping';

// 擴展Product類型，添加product_type_id
interface Product extends BaseProduct {
  product_type_id?: number;
}

// 添加圖片代理處理函數
function getProxiedImageUrl(originalUrl: string) {
  // 如果URL為空，返回默認圖片
  if (!originalUrl || originalUrl.trim() === '') {
    console.log('圖片URL為空，使用默認圖片');
    return '/images/no-image.png';
  }
  
  // 檢查是否為相對URL（本地資源）
  if (originalUrl.startsWith('/') || originalUrl.startsWith('./')) {
    return originalUrl;
  }
  
  // 檢查URL是否已經為代理URL
  if (originalUrl.includes('/api/proxy/image/')) {
    return originalUrl;
  }
  
  try {
    // 記錄原始URL，便於調試
    console.log('原始圖片URL:', originalUrl);
    
    // 對URL進行編碼
    const encodedUrl = encodeURIComponent(originalUrl);
    const proxyUrl = `http://localhost:8000/api/proxy/image/?url=${encodedUrl}`;
    
    console.log('代理後的URL:', proxyUrl);
    return proxyUrl;
  } catch (e) {
    console.error('處理圖片URL時出錯:', e);
    return '/images/no-image.png';
  }
}

// 處理圖片載入錯誤的函數
function handleImageError(event: Event) {
  console.error('圖片載入失敗，使用默認圖片替代');
  const img = event.target as HTMLImageElement;
  img.src = '/images/no-image.png';
  img.onerror = null; // 防止無限循環
}

interface CategoryType {
  id: string;
  name: string;
  brands: string[];
}

interface CategoriesData {
  categories: CategoryType[];
}

// 商品列表
const products = ref<Product[]>([]);
const loading = ref(true);
const error = ref<string | null>(null);

// 新增：路由和查詢參數處理
const router = useRouter();
const route = useRoute();

// 新增：從URL查詢參數獲取當前選中的分類和品牌
const currentCategory = computed(() => route.query.category as string || '');
const currentBrand = computed(() => route.query.brand as string || '');

// 新增：存儲從categories.json加載的分類數據
const categoriesData = ref<CategoryType[]>([]);

// 分類相關
const expandedCategories = ref<Record<string, boolean>>({});
const selectedBrands = ref<Record<string, Set<string>>>({});

// 價格範圍
const minPrice = ref<number | null>(null);
const maxPrice = ref<number | null>(null);

// 排序方式
const sortOption = ref('default');

// 分頁相關
const currentPage = ref(1);
const pageSize = 25;

// 方法
function toggleCategory(categoryId: string) {
  expandedCategories.value[categoryId] = !expandedCategories.value[categoryId];
}

function toggleBrandFilter(categoryId: string, brand: string) {
  if (!selectedBrands.value[categoryId])
    selectedBrands.value[categoryId] = new Set();

  const brands = selectedBrands.value[categoryId];
  if (brands.has(brand))
    brands.delete(brand);
  else
    brands.add(brand);
    
  // 更新過濾結果
  console.log(`切換品牌 ${brand} 在分類 ${categoryId}`);
}

function isSelectedBrand(categoryId: string, brand: string) {
  return selectedBrands.value[categoryId]?.has(brand) || false;
}

// 獲取目前活躍的分類名稱
const activeCategory = computed(() => {
  if (!currentCategory.value) return '所有商品';
  
  const category = categoriesData.value.find(c => c.id === currentCategory.value);
  return category ? category.name : '所有商品';
});

// 修改過濾商品的computed屬性，增加對URL查詢參數的處理
const filteredProducts = computed(() => {
  let result = [...products.value];

  // 根據URL查詢參數處理分類過濾
  if (currentCategory.value) {
    console.log('根據URL分類過濾:', currentCategory.value);
    if (currentCategory.value === 'hiking_backpacks') {
      // 過濾登山背包，對應product_type_id=5
      result = result.filter(product => product.product_type_id === 5);
    } else if (currentCategory.value === 'air_mattresses') {
      // 過濾充氣床墊，對應product_type_id=1
      result = result.filter(product => product.product_type_id === 1);
    } else if (currentCategory.value === 'camping_tables') {
      // 過濾露營桌，對應product_type_id=2
      result = result.filter(product => product.product_type_id === 2);
    } else if (currentCategory.value === 'camping_tents') {
      // 過濾帳篷，對應product_type_id=3
      result = result.filter(product => product.product_type_id === 3);
    } else if (currentCategory.value === 'chargers') {
      // 過濾充電器，對應product_type_id=4
      result = result.filter(product => product.product_type_id === 4);
    } else if (currentCategory.value === 'hiking_poles') {
      // 過濾登山杖，對應product_type_id=6
      result = result.filter(product => product.product_type_id === 6);
    } else if (currentCategory.value === 'phones') {
      // 過濾手機，對應product_type_id=7
      result = result.filter(product => product.product_type_id === 7);
    } else if (currentCategory.value === 'luggage') {
      // 過濾行李箱，對應product_type_id=8
      result = result.filter(product => product.product_type_id === 8);
    } else if (currentCategory.value === 'gas_stoves') {
      // 過濾瓦斯爐，對應product_type_id=9
      result = result.filter(product => product.product_type_id === 9);
    }
  }

  // 根據URL查詢參數處理品牌過濾
  if (currentBrand.value) {
    console.log('根據URL品牌過濾:', currentBrand.value);
    result = result.filter(product => 
      product.category?.toLowerCase() === currentBrand.value.toLowerCase()
    );
  }

  // 檢查是否有選中的品牌（通過UI選擇）
  const hasSelectedBrands = Object.values(selectedBrands.value).some(brands => brands.size > 0);

  if (hasSelectedBrands) {
    // 如果有選中的品牌，只顯示選中品牌的商品
    result = result.filter((product) => {
      // 遍歷所有選中的分類和品牌
      for (const [catId, brands] of Object.entries(selectedBrands.value)) {
        if (brands.size === 0) continue;
        // 在後端數據中，product.category存放的是品牌名稱
        if (Array.from(brands).some(brand => product.category?.toLowerCase() === brand.toLowerCase())) {
          return true;
        }
      }
      return false;
    });
  }

  // 應用價格範圍過濾
  if (minPrice.value !== null)
    result = result.filter(product => Number(product.price) >= minPrice.value!);

  if (maxPrice.value !== null)
    result = result.filter(product => Number(product.price) <= maxPrice.value!);

  // 應用排序
  switch (sortOption.value) {
    case 'price_asc':
      result.sort((a, b) => Number(a.price) - Number(b.price));
      break;
    case 'price_desc':
      result.sort((a, b) => Number(b.price) - Number(a.price));
      break;
  }

  console.log('過濾後的商品數量:', result.length);
  return result;
})

// 計算總頁數
const totalPages = computed(() => Math.ceil(filteredProducts.value.length / pageSize));

// 當前頁面的商品
const currentPageProducts = computed(() => {
  const start = (currentPage.value - 1) * pageSize;
  const end = start + pageSize;
  return filteredProducts.value.slice(start, end);
})

// 頁面切換方法
function changePage(page: number) {
  currentPage.value = page;
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// 載入商品數據
async function loadProducts() {
  try {
    loading.value = true;
    error.value = null;
    const data = await ShoppingAPI.getAllProducts();
    products.value = data as Product[];
    console.log('已載入產品數據，總數:', data.length);
    console.log('URL參數分類:', currentCategory.value, '品牌:', currentBrand.value);
  }
  catch (err) {
    error.value = '載入商品失敗，請稍後再試';
    console.error('載入商品錯誤:', err);
  }
  finally {
    loading.value = false;
  }
}

// 載入分類數據
async function loadCategories() {
  try {
    console.log('開始載入分類數據...');
    const response = await ShoppingAPI.getCategories();
    console.log('分類數據載入成功:', response);

    if (response && response.categories && Array.isArray(response.categories)) {
      categoriesData.value = response.categories;
      
      // 根據URL參數展開對應分類
      if (currentCategory.value) {
        const category = categoriesData.value.find(cat => cat.id === currentCategory.value);
        if (category) {
          expandedCategories.value[category.id] = true;
        }
      }
    } else {
      console.error('分類數據格式不正確:', response);
    }
  } catch (err) {
    console.error('載入分類數據失敗:', err);
  }
}

// 組件掛載時載入數據
onMounted(() => {
  loadProducts();
  loadCategories();
})

// 新增：監聽路由變化，重新過濾產品
watch(() => [route.query.category, route.query.brand], () => {
  console.log('路由參數變化，重新過濾產品');
  
  // 清除所有選中的品牌
  selectedBrands.value = {};
  
  // 展開當前選中的分類
  if (currentCategory.value) {
    for (const category of categoriesData.value) {
      expandedCategories.value[category.id] = (category.id === currentCategory.value);
    }
  }
}, { immediate: true });

// 導航方法
function navigateToProduct(productId: number) {
  router.push({
    path: `/mall-products/detail/${productId}`,
  });
}
</script>

<template>
  <div>
    <Header />
    <NLayout>
      <NLayoutContent class="container mx-auto px-4 py-8">
        <NGrid :cols="24" :x-gap="24">
          <!-- 左側過濾條件 -->
          <NGridItem span="6">
            <!-- 分類過濾 -->
            <NCard title="商品分類" class="mb-4">
              <NSpace vertical>
                <NCollapse>
                  <NCollapseItem
                    v-for="category in categoriesData"
                    :key="category.id"
                    :title="category.name"
                    :name="category.id"
                    :default-expanded="expandedCategories[category.id]"
                  >
                    <!-- 品牌列表 -->
                    <NSpace vertical>
                      <NTag
                        v-for="brand in category.brands"
                        :key="brand"
                        :type="isSelectedBrand(category.id, brand) ? 'primary' : 'default'"
                        :bordered="false"
                        style="cursor: pointer; width: 100%"
                        @click="toggleBrandFilter(category.id, brand)"
                      >
                        {{ brand }}
                      </NTag>
                    </NSpace>
                  </NCollapseItem>
                </NCollapse>
              </NSpace>
            </NCard>

            <!-- 價格範圍 -->
            <NCard title="價格範圍" class="mb-4">
              <NSpace vertical>
                <NInputNumber
                  v-model:value="minPrice"
                  placeholder="最低價格"
                  clearable
                />
                <NInputNumber
                  v-model:value="maxPrice"
                  placeholder="最高價格"
                  clearable
                />
              </NSpace>
            </NCard>

            <!-- 排序方式 -->
            <NCard title="排序方式">
              <NSelect
                v-model:value="sortOption"
                :options="[
                  { label: '預設排序', value: 'default' },
                  { label: '價格由低到高', value: 'price_asc' },
                  { label: '價格由高到低', value: 'price_desc' },
                ]"
              />
            </NCard>
          </NGridItem>

          <!-- 右側商品列表 -->
          <NGridItem span="18">
            <NCard>
              <template #header>
                <div class="flex justify-between items-center">
                  <h1 class="text-2xl font-bold">
                    {{ activeCategory }}
                    <NTag type="info" round>
                      {{ filteredProducts.length }}
                    </NTag>
                  </h1>
                </div>
              </template>

              <!-- 載入中狀態 -->
              <div v-if="loading" class="py-8">
                <NSpin size="large" />
              </div>

              <!-- 錯誤狀態 -->
              <div v-else-if="error" class="py-8">
                <NResult
                  status="error"
                  :title="error"
                  description="請稍後重試"
                >
                  <template #footer>
                    <NButton
                      type="primary"
                      @click="loadProducts"
                    >
                      重新載入
                    </NButton>
                  </template>
                </NResult>
              </div>

              <!-- 商品列表 -->
              <template v-else>
                <div v-if="filteredProducts.length > 0">
                  <NGrid :cols="3" :x-gap="12" :y-gap="12">
                    <NGridItem
                      v-for="product in currentPageProducts"
                      :key="product.id"
                    >
                      <NCard hoverable class="product-card">
                        <template #cover>
                          <NImage
                            :src="getProxiedImageUrl(product.image_url)"
                            :alt="product.name"
                            object-fit="cover"
                            class="product-image"
                            preview-disabled
                            fallback-src="/images/no-image.png"
                            @error="handleImageError"
                          />
                        </template>
                        <div class="product-content">
                          <NButton
                            class="product-title-button"
                            text
                            @click="navigateToProduct(product.id)"
                          >
                            <div class="product-title">{{ product.name }}</div>
                          </NButton>
                          <div class="price-container">
                            <div class="product-price">NT$ {{ product.price }}</div>
                            <div v-if="product.original_price" class="original-price">
                              NT$ {{ product.original_price }}
                            </div>
                          </div>
                          <div class="product-info">
                            <div class="product-brand">{{ product.category }}</div>
                            <div class="product-stock" :class="{ 'text-red-500': product.stock <= 5 }">
                              庫存: {{ product.stock }}
                            </div>
                          </div>
                          <NButton
                            class="product-button"
                            type="primary"
                            block
                            @click="navigateToProduct(product.id)"
                          >
                            查看詳情
                          </NButton>
                        </div>
                      </NCard>
                    </NGridItem>
                  </NGrid>

                  <!-- 分頁 -->
                  <div class="flex justify-center my-8">
                    <NPagination
                      v-if="totalPages > 1"
                      v-model:page="currentPage"
                      :page-count="totalPages"
                      :page-sizes="[10, 25, 50, 100]"
                      :page-size="pageSize"
                      show-size-picker
                      @update:page="changePage"
                    />
                  </div>
                </div>
                <NEmpty v-else description="沒有找到符合條件的商品" class="py-12" />
              </template>
            </NCard>
          </NGridItem>
        </NGrid>
      </NLayoutContent>
    </NLayout>
  </div>
</template>

<style scoped>
.container {
  max-width: 1400px;
}

.product-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.product-content {
  display: flex;
  flex-direction: column;
  flex-grow: 1;
  padding: 8px;
}

.product-title {
  font-weight: 500;
  margin-bottom: 8px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  height: 2.75rem;
}

.product-title-button {
  padding: 0;
  text-align: left;
  height: auto;
  margin-bottom: 8px;
  color: #18a058;
  text-decoration: none;
}

.price-container {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.product-price {
  font-size: 1.25rem;
  color: #18a058;
}

.original-price {
  font-size: 0.875rem;
  color: #999;
  text-decoration: line-through;
}

.product-description {
  font-family: 'Open Sans', sans-serif;
  font-size: 0.875rem;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  flex-grow: 1;
}

.product-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 8px 0;
}

.product-stock {
  font-size: 0.875rem; /* 14px */
}

.product-brand {
  font-size: 0.875rem; /* 14px */
  color: #666;
}

.product-button {
  margin-top: auto; /* 確保按鈕在底部對齊 */
  height: 36px; /* 固定按鈕高度 */
}

.category-group {
  @apply mb-2;
}

.product-image {
  max-height: 200px;
  object-fit: cover;
}
</style>

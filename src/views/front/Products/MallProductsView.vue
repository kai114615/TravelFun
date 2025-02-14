<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
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
import { useRouter } from 'vue-router';
import Header from '@/components/Header.vue';
import { type Product, ShoppingAPI } from '@/api/shopping';

interface Category {
  id: number
  name: string
  brands: string[]
}

// 商品列表
const products = ref<Product[]>([]);
const loading = ref(true);
const error = ref<string | null>(null);

// 分類相關
const categories = computed(() => {
  const categoryMap = new Map<string, Set<string>>();

  // 從商品數據中提取分類和品牌
  products.value.forEach((product) => {
    if (!categoryMap.has(product.category))
      categoryMap.set(product.category, new Set());

    const brands = categoryMap.get(product.category);
    if (brands && product.brand)
      brands.add(product.brand);
  });

  // 轉換為所需的格式
  return Array.from(categoryMap.entries()).map(([category, brands], index) => ({
    id: index + 1,
    name: category,
    brands: Array.from(brands),
  }));
});

const expandedCategories = ref<Record<number, boolean>>({});
const selectedBrands = ref<Record<number, Set<string>>>({});

// 價格範圍
const minPrice = ref<number | null>(null);
const maxPrice = ref<number | null>(null);

// 排序方式
const sortOption = ref('default');

// 分頁相關
const currentPage = ref(1);
const pageSize = 25;

// 方法
function toggleCategory(categoryId: number) {
  expandedCategories.value[categoryId] = !expandedCategories.value[categoryId];
}

function toggleBrandFilter(categoryId: number, brand: string) {
  if (!selectedBrands.value[categoryId])
    selectedBrands.value[categoryId] = new Set();

  const brands = selectedBrands.value[categoryId];
  if (brands.has(brand))
    brands.delete(brand);
  else
    brands.add(brand);
}

function isSelectedBrand(categoryId: number, brand: string) {
  return selectedBrands.value[categoryId]?.has(brand) || false;
}

// 修改過濾商品的computed屬性
const filteredProducts = computed(() => {
  let result = [...products.value];

  // 檢查是否有選中的品牌
  const hasSelectedBrands = Object.values(selectedBrands.value).some(brands => brands.size > 0);

  if (hasSelectedBrands) {
    // 如果有選中的品牌，只顯示選中品牌的商品
    result = result.filter((product) => {
      // 檢查產品的類別是否有選中的品牌
      const categoryId = categories.value.find(c => c.name === product.category)?.id;
      if (!categoryId || !selectedBrands.value[categoryId])
        return false;

      return Array.from(selectedBrands.value[categoryId]).some(brand =>
        product.brand.toLowerCase() === brand.toLowerCase(),
      );
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

  return result;
});

// 計算總頁數
const totalPages = computed(() => Math.ceil(filteredProducts.value.length / pageSize));

// 當前頁面的商品
const currentPageProducts = computed(() => {
  const start = (currentPage.value - 1) * pageSize;
  const end = start + pageSize;
  return filteredProducts.value.slice(start, end);
});

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
    products.value = data;
  }
  catch (err) {
    error.value = '載入商品失敗，請稍後再試';
    console.error('載入商品錯誤:', err);
  }
  finally {
    loading.value = false;
  }
}

// 組件掛載時載入數據
onMounted(() => {
  loadProducts();
});

const router = useRouter();

// 新增導航方法
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
          <!-- 左側篩選區 -->
          <NGridItem span="6">
            <!-- 商品分類 -->
            <NCard title="商品分類" class="mb-4">
              <NSpace vertical>
                <NCollapse>
                  <NCollapseItem
                    v-for="category in categories"
                    :key="category.id"
                    :title="category.name"
                  >
                    <NSpace vertical>
                      <n-tag
                        v-for="brand in category.brands"
                        :key="brand"
                        :type="isSelectedBrand(category.id, brand) ? 'primary' : 'default'"
                        :bordered="false"
                        style="cursor: pointer; width: 100%"
                        @click="toggleBrandFilter(category.id, brand)"
                      >
                        {{ brand }}
                      </n-tag>
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
                    所有商品
                    <n-tag type="info" round>
                      {{ filteredProducts.length }}
                    </n-tag>
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
                            :src="product.image_url || '/src/assets/images/placeholder.jpg'"
                            :alt="product.name"
                            object-fit="cover"
                            class="product-image"
                            preview-disabled
                            fallback-src="/src/assets/images/placeholder.jpg"
                          />
                        </template>
                        <div class="product-content">
                          <NButton
                            class="product-title-button"
                            @click="navigateToProduct(product.id)"
                            text
                          >
                            {{ product.name }}
                          </NButton>

                          <NText depth="3" class="product-description">
                            {{ product.description }}
                          </NText>

                          <div class="product-info">
                            <div class="price-container">
                              <NText type="success" strong class="product-price">
                                NT$ {{ product.price }}
                              </NText>
                              <NText v-if="product.original_price" class="original-price">
                                NT$ {{ product.original_price }}
                              </NText>
                            </div>
                            <NText depth="3" class="product-stock">
                              庫存: {{ product.stock }}
                            </NText>
                          </div>

                          <NButton
                            block
                            type="success"
                            class="product-button"
                            :disabled="!product.is_active || product.stock <= 0"
                          >
                            {{ product.is_active && product.stock > 0 ? '加入購物車' : '暫無庫存' }}
                          </NButton>
                        </div>
                      </NCard>
                    </NGridItem>
                  </NGrid>

                  <!-- 分頁控制 -->
                  <div class="mt-8 flex justify-center">
                    <NPagination
                      v-model:page="currentPage"
                      :page-count="totalPages"
                      :page-size="pageSize"
                      show-quick-jumper
                    />
                  </div>
                </div>
                <NEmpty
                  v-else
                  description="沒有找到符合條件的商品"
                />
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
  height: 460px; /* 增加卡片高度，確保有足夠空間顯示完整標題 */
  display: flex;
  flex-direction: column;
}

.product-image {
  height: 200px !important;
  width: 100%;
  object-fit: cover;
}

.product-content {
  display: flex;
  flex-direction: column;
  flex: 1;
  padding: 12px;
  gap: 8px;
}

.product-title-button {
  width: 100%;
  text-align: left;
  padding: 0;
  font-size: 1.125rem;
  font-family: 'Noto Sans TC', sans-serif;
  font-weight: 600;
  line-height: 1.4;
  color: #333;
  transition: color 0.3s ease;
  margin-bottom: 4px;
  white-space: normal;
  height: auto;
  min-height: 2.8em;
}

.product-title-button:hover {
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

.product-button {
  margin-top: auto; /* 確保按鈕在底部對齊 */
  height: 36px; /* 固定按鈕高度 */
}

.category-group {
  @apply mb-2;
}

.category-group button {
  @apply transition-all duration-200;
}
</style>

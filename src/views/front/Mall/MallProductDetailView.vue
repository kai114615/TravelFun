<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import productsData from './data/MallProduct.json';
import 'element-plus/dist/index.css';
import { useCartStore } from '@/stores/cart';
import useFavoriteStore from '@/stores/favorite';
import useProductStore from '@/stores/product';

const route = useRoute();
const router = useRouter();
const cartStore = useCartStore();
const favoriteStore = useFavoriteStore();
const productStore = useProductStore();
const productId = computed(() => Number(route.params.id));
const quantity = ref(1);
const selectedTab = ref('description');

// 取得商品資料
const product = computed(() => {
  return productsData.find(p => p.id === productId.value);
});

// 相關商品推薦（同類別的其他商品）
const relatedProducts = computed(() => {
  if (!product.value)
    return [];
  return productsData
    .filter(p => p.category === product.value?.category && p.id !== product.value?.id)
    .slice(0, 4);
});

// 檢查商品是否已收藏
const isFavorite = computed(() => {
  return favoriteStore.checkFavorite(productId.value.toString());
});

// 切換收藏狀態
function toggleFavorite () {
  if (!product.value) return;

  const id = productId.value.toString();
  const title = product.value.name;

  if (isFavorite.value) {
    favoriteStore.removeFavorite(id, title);
  } else {
    favoriteStore.addFavorite(id, title);

    // 確保商品數據在 productStore 中
    if (!productStore.productList.some(p => p.id === id)) {
      // 將商品數據轉換為 Product 類型並添加到 productStore
      productStore.productList.push({
        id,
        title: product.value.name,
        imageUrl: product.value.image_url,
        price: Number(product.value.price),
        origin_price: Number(product.value.price) * 1.2,
        description: product.value.description || '',
        city: 'taipei', // 默認值
        address: '',
        category: product.value.category,
        unit: '個',
        evaluate: 5, // 默認值
        evaluateNum: 0,
        date: Date.now(),
        coordinates: { lat: 0, lng: 0 },
        is_enabled: product.value.is_active
      });
    }
  }
}

// 數量增減
function decreaseQuantity () {
  if (quantity.value > 1)
    quantity.value--;
}

function increaseQuantity () {
  if (quantity.value < (product.value?.stock || 0))
    quantity.value++;
}

// 加入購物車
async function addToCart () {
  if (!product.value) {
    ElMessage.error('商品資料載入失敗');
    return;
  }

  try {
    // 檢查庫存
    if (product.value.stock < quantity.value) {
      ElMessage.error('商品庫存不足');
      return;
    }

    // 添加到購物車 store
    cartStore.addToCart({
      id: product.value.id,
      name: product.value.name,
      price: Number(product.value.price),
      quantity: quantity.value,
      image_url: product.value.image_url,
      stock: product.value.stock
    });

    ElMessage.success('成功加入購物車！');
  } catch (error) {
    console.error('加入購物車失敗:', error);
    ElMessage.error('加入購物車失敗，請稍後再試');
  }
}

// 立即購買
async function buyNow () {
  if (!product.value) {
    ElMessage.error('商品資料載入失敗');
    return;
  }

  try {
    // 檢查庫存
    if (product.value.stock < quantity.value) {
      ElMessage.error('商品庫存不足');
      return;
    }

    // 添加到購物車 store
    cartStore.addToCart({
      id: product.value.id,
      name: product.value.name,
      price: Number(product.value.price),
      quantity: quantity.value,
      image_url: product.value.image_url,
      stock: product.value.stock
    });

    // 導向購物車頁面
    router.push('/cart');
  } catch (error) {
    console.error('立即購買失敗:', error);
    ElMessage.error('操作失敗，請稍後再試');
  }
}

// 新增：點擊品牌按鈕的處理函數
function openBrandProducts (brand: string) {
  // 直接使用品牌名稱作為參數
  const url = `${window.location.origin}/#/mall-products?brand=${encodeURIComponent(brand)}`;
  window.open(url, '_blank');
}

onMounted(() => {
  // 頁面載入時滾動到頂部
  window.scrollTo(0, 0);

  // 初始化 productStore，確保它有數據
  if (productStore.productList.length === 0) {
    // 將 MallProduct.json 中的數據轉換為 Product 類型並添加到 productStore
    productsData.forEach(p => {
      if (!productStore.productList.some(product => product.id === p.id.toString())) {
        productStore.productList.push({
          id: p.id.toString(),
          title: p.name,
          imageUrl: p.image_url,
          price: Number(p.price),
          origin_price: Number(p.price) * 1.2,
          description: p.description || '',
          city: 'taipei', // 默認值
          address: '',
          category: p.category,
          unit: '個',
          evaluate: 5, // 默認值
          evaluateNum: 0,
          date: Date.now(),
          coordinates: { lat: 0, lng: 0 },
          is_enabled: p.is_active
        });
      }
    });
  }
});
</script>

<template>
  <div v-if="product" class="container mx-auto px-4 py-6">
    <!-- 商品主要資訊區 -->
    <div class="flex flex-col lg:flex-row gap-8 max-w-6xl mx-auto">
      <!-- 左側商品圖片 -->
      <div class="lg:w-1/2">
        <div class="aspect-square bg-white rounded-lg overflow-hidden border border-gray-200">
          <img
            :src="product.image_url"
            :alt="product.name"
            class="w-full h-full object-contain"
          >
        </div>
      </div>

      <!-- 右側商品資訊 -->
      <div class="lg:w-1/2">
        <div class="bg-white rounded-lg p-6 shadow-sm space-y-6 lg:mt-8">
          <!-- 商品標籤 -->
          <div class="flex flex-wrap gap-2">
            <button
              v-if="product.category"
              class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-gray-100 text-gray-800 hover:bg-gray-200 transition-colors cursor-pointer"
              @click="openBrandProducts(product.category)"
            >
              {{ product.category }}
            </button>
            <span
              v-if="product.stock > 0"
              class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800"
            >
              現貨
            </span>
            <span
              v-if="product.is_active"
              class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800"
            >
              銷售中
            </span>
            <span
              class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-yellow-100 text-yellow-800"
            >
              免運費
            </span>
          </div>

          <!-- 商品基本資訊 -->
          <h1 class="text-2xl font-bold text-gray-900">
            {{ product.name }}
          </h1>
          <div class="text-3xl font-bold text-green-600">
            NT$ {{ product.price }}
          </div>

          <!-- 購買數量選擇 -->
          <div class="py-4 border-t border-gray-100">
            <label class="block text-sm font-medium text-gray-700 mb-2">數量</label>
            <div class="flex items-center space-x-3">
              <button
                class="w-10 h-10 rounded-lg border border-gray-300 flex items-center justify-center hover:bg-gray-100 transition-colors"
                :disabled="quantity <= 1"
                @click="decreaseQuantity"
              >
                -
              </button>
              <input
                v-model="quantity"
                type="number"
                min="1"
                :max="product.stock"
                class="w-20 text-center border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
              >
              <button
                class="w-10 h-10 rounded-lg border border-gray-300 flex items-center justify-center hover:bg-gray-100 transition-colors"
                :disabled="quantity >= product.stock"
                @click="increaseQuantity"
              >
                +
              </button>

              <!-- 加入收藏按鈕 -->
              <button
                class="ml-4 flex items-center px-4 py-2 rounded-lg border transition-colors"
                :class="isFavorite ? 'border-red-300 bg-red-50 text-red-600 hover:bg-red-100' : 'border-gray-300 hover:bg-gray-100'"
                @click="toggleFavorite"
              >
                <i class="mr-2" :class="isFavorite ? 'fas fa-heart text-red-500' : 'far fa-heart'" />
                {{ isFavorite ? '已收藏' : '加入收藏' }}
              </button>
            </div>
          </div>

          <!-- 購買按鈕 -->
          <div class="flex space-x-4 pt-4 border-t border-gray-100">
            <button
              class="flex-1 bg-gray-900 text-white py-3 rounded-lg hover:bg-gray-800 transition-colors text-base font-medium"
              :disabled="product.stock <= 0"
              @click="addToCart"
            >
              加入購物車
            </button>
            <button
              class="flex-1 bg-green-600 text-white py-3 rounded-lg hover:bg-green-700 transition-colors text-base font-medium"
              :disabled="product.stock <= 0"
              @click="buyNow"
            >
              立即購買
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 商品詳細資訊標籤頁 -->
    <div class="mt-8 max-w-6xl mx-auto">
      <div class="border-b border-gray-200">
        <nav class="flex space-x-6">
          <button
            class="py-3 px-1 border-b-2 font-medium text-sm"
            :class="selectedTab === 'description' ? 'border-green-500 text-green-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'"
            @click="selectedTab = 'description'"
          >
            商品說明
          </button>
          <button
            class="py-3 px-1 border-b-2 font-medium text-sm"
            :class="selectedTab === 'specifications' ? 'border-green-500 text-green-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'"
            @click="selectedTab = 'specifications'"
          >
            商品規格
          </button>
          <button
            class="py-3 px-1 border-b-2 font-medium text-sm"
            :class="selectedTab === 'shipping' ? 'border-green-500 text-green-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'"
            @click="selectedTab = 'shipping'"
          >
            運送說明
          </button>
        </nav>
      </div>

      <!-- 標籤頁內容 -->
      <div class="py-8">
        <div v-if="selectedTab === 'description'" class="prose max-w-none">
          <div v-html="product.description" />
        </div>
        <div v-else-if="selectedTab === 'specifications'" class="prose max-w-none">
          <h3 class="text-lg font-bold mb-4">
            商品規格
          </h3>
          <div class="bg-gray-50 p-6 rounded-lg">
            <ul class="space-y-4">
              <li class="flex items-center">
                <span class="w-32 text-gray-500">商品分類</span>
                <span class="text-gray-900">{{ product.category }}</span>
              </li>
              <li class="flex items-center">
                <span class="w-32 text-gray-500">庫存數量</span>
                <span class="text-gray-900">{{ product.stock }}</span>
              </li>
              <li class="flex items-center">
                <span class="w-32 text-gray-500">商品狀態</span>
                <span class="text-gray-900">{{ product.is_active ? '銷售中' : '已下架' }}</span>
              </li>
            </ul>
          </div>
        </div>
        <div v-else-if="selectedTab === 'shipping'" class="prose max-w-none">
          <h3>運送說明</h3>
          <ul>
            <li>全台灣免運費</li>
            <li>預計 2-3 個工作天到貨</li>
            <li>提供貨到付款服務</li>
            <li>離島地區需額外運費</li>
          </ul>
        </div>
      </div>
    </div>

    <!-- 相關商品推薦 -->
    <div class="mt-12">
      <h2 class="text-2xl font-bold mb-6">
        相關商品推薦
      </h2>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div
          v-for="relatedProduct in relatedProducts"
          :key="relatedProduct.id"
          class="bg-white rounded-lg shadow overflow-hidden hover:shadow-lg transition-shadow duration-300"
        >
          <img
            :src="relatedProduct.image_url"
            :alt="relatedProduct.name"
            class="w-full h-48 object-cover"
          >
          <div class="p-4">
            <h3 class="text-lg font-semibold mb-2 line-clamp-2">
              {{ relatedProduct.name }}
            </h3>
            <div class="flex justify-between items-center">
              <span class="text-green-600 font-bold">NT$ {{ relatedProduct.price }}</span>
              <button
                class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition-colors duration-200"
                @click="$router.push({ name: 'MallProductDetail', params: { id: relatedProduct.id } })"
              >
                查看詳情
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- 找不到商品時顯示的內容 -->
  <div v-else class="container mx-auto px-4 py-8 text-center">
    <h1 class="text-2xl font-bold mb-4">
      找不到商品
    </h1>
    <p class="text-gray-600 mb-8">
      抱歉，您要查看的商品不存在或已下架。
    </p>
    <button
      class="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 transition-colors"
      @click="$router.push({ name: 'MallProducts' })"
    >
      返回商品列表
    </button>
  </div>
</template>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 移除數量輸入框的上下箭頭 */
input[type="number"]::-webkit-inner-spin-button,
input[type="number"]::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

input[type="number"] {
  -moz-appearance: textfield;
}
</style>

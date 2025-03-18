<script setup lang="ts">
import { NBreadcrumb, NBreadcrumbItem, NCard, NEmpty, NList, NListItem, NPageHeader } from 'naive-ui';
import { computed, onMounted, ref } from 'vue';
import { storeToRefs } from 'pinia';
import { useRouter } from 'vue-router';
import { useDeviceStore, useFavoriteStore, useProductStore, useCartStore } from '@/stores';
import productsData from '@/views/front/Mall/data/MallProduct.json';

const router = useRouter();
const deviceStore = useDeviceStore();
const favoriteStore = useFavoriteStore();
const productStore = useProductStore();
const cartStore = useCartStore();

const { isMobile } = storeToRefs(deviceStore);
const { favoriteList } = storeToRefs(favoriteStore);
const { productList } = storeToRefs(productStore);

// 收藏列表是否已加載
const isLoaded = ref(false);

const getBreadcrumbs = computed(() => [
  {
    title: '會員中心',
    pathName: 'MemberDashboard',
  },
  {
    title: '我的收藏',
  },
]);

// 確保 productStore 中有 MallProduct.json 的數據
onMounted(() => {
  isLoaded.value = false;
  
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
  
  // 確保顯示收藏項目
  setTimeout(() => {
    console.log('會員中心-收藏列表:', favoriteList.value);
    console.log('會員中心-產品列表:', productList.value);
    isLoaded.value = true;
  }, 500);
});

const getFavoriteProductList = computed(() => {
  // 從 productList 中過濾出收藏的商品
  const favoriteProducts = productList.value.filter(({ id }) => favoriteList.value.includes(id));

  // 如果沒有找到收藏的商品，嘗試從 MallProduct.json 中查找
  if (favoriteProducts.length === 0 && favoriteList.value.length > 0) {
    return favoriteList.value.map(id => {
      const mallProduct = productsData.find(p => p.id.toString() === id);
      if (mallProduct) {
        // 將 MallProduct 轉換為 Product 類型
        return {
          id,
          title: mallProduct.name,
          imageUrl: mallProduct.image_url,
          price: Number(mallProduct.price),
          origin_price: Number(mallProduct.price) * 1.2,
          description: mallProduct.description || '',
          city: 'taipei', // 默認值
          address: '',
          category: mallProduct.category,
          unit: '個',
          evaluate: 5, // 默認值
          evaluateNum: 0,
          date: Date.now(),
          coordinates: { lat: 0, lng: 0 },
          is_enabled: mallProduct.is_active
        };
      }
      return null;
    }).filter(Boolean);
  }

  return favoriteProducts;
});

// 跳轉到商品詳情頁面
function goToProductDetail(productId: string) {
  router.push({ name: 'MallProductDetail', params: { id: productId } });
}

// 添加商品到購物車
function addToCart(event: Event, product: any) {
  event.stopPropagation(); // 阻止事件冒泡
  cartStore.addToCart({
    id: product.id,
    name: product.title,
    price: product.price,
    quantity: 1,
    image_url: product.imageUrl,
    stock: 100 // 假設庫存充足
  });
}

// 從收藏清單中移除商品
function removeFromFavorite(event: Event, product: any) {
  event.stopPropagation(); // 阻止事件冒泡
  favoriteStore.removeFavorite(product.id, product.title);
}
</script>

<template>
  <div>
    <!-- 頁面標題 -->
    <NPageHeader>
      <template #title>
        <div class="text-2xl font-bold">
          我的收藏清單
        </div>
      </template>
      <template #subtitle>
        <div class="text-gray-600">
          在這裡管理您收藏的商品，點擊商品可查看詳情，或直接加入購物車
        </div>
      </template>
    </NPageHeader>

    <!-- 麵包屑導航 -->
    <NBreadcrumb separator=">" class="mb-4">
      <template v-for="{ title, pathName } in getBreadcrumbs" :key="title">
        <NBreadcrumbItem v-if="pathName">
          <RouterLink :to="{ name: pathName }">
            {{ title }}
          </RouterLink>
        </NBreadcrumbItem>
        <NBreadcrumbItem v-else>
          {{ title }}
        </NBreadcrumbItem>
      </template>
    </NBreadcrumb>

    <!-- 載入狀態顯示 -->
    <div v-if="!isLoaded" class="py-10 text-center text-gray-500">
      <i class="fas fa-spinner fa-spin text-2xl mb-3"></i>
      <p>正在載入收藏商品...</p>
    </div>

    <!-- 開發測試用按鈕 -->
    <div class="mb-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg" v-if="isLoaded && favoriteList.length === 0">
      <p class="text-yellow-700 mb-2">收藏清單為空，但您可以使用下方測試按鈕添加幾個測試商品：</p>
      <button @click="favoriteStore.addToFavoriteList('1')" class="bg-blue-600 text-white px-3 py-1 rounded-lg mr-2">
        添加商品 #1
      </button>
      <button @click="favoriteStore.addToFavoriteList('2')" class="bg-blue-600 text-white px-3 py-1 rounded-lg mr-2">
        添加商品 #2
      </button>
      <button @click="favoriteStore.addToFavoriteList('3')" class="bg-blue-600 text-white px-3 py-1 rounded-lg">
        添加商品 #3
      </button>
    </div>

    <!-- 商品列表卡片 -->
    <NCard
      v-if="isLoaded"
      class="my-5"
      size="large"
      :bordered="false"
      :segmented="{
        content: true,
        footer: true,
      }"
    >
      <template v-if="favoriteList.length !== 0">
        <NList hoverable clickable>
          <template v-for="product in getFavoriteProductList" :key="product.id">
            <NListItem class="hover:bg-gray-50 transition-colors" @click="goToProductDetail(product.id)">
              <template v-if="!isMobile" #prefix>
                <div class="w-[200px] aspect-[4/3] rounded-lg overflow-hidden shadow-sm">
                  <img class="img" :src="product?.imageUrl" alt="商品圖片">
                </div>
              </template>
              <div v-if="isMobile" class="w-full aspect-video mb-4 rounded-lg overflow-hidden shadow-sm">
                <img class="img" :src="product?.imageUrl" alt="商品圖片">
              </div>
              <div class="flex flex-col ml-4">
                <h3 class="text-lg font-semibold mb-2">{{ product.title }}</h3>
                <div class="mb-2 text-gray-500">{{ product.description }}</div>
                <div class="flex items-center mt-auto">
                  <span class="text-red-600 font-bold text-lg">NT$ {{ product.price }}</span>
                  <span class="text-gray-400 line-through ml-2">NT$ {{ product.origin_price }}</span>
                  <div class="ml-auto flex">
                    <button 
                      class="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg transition-colors mr-2" 
                      @click="removeFromFavorite($event, product)"
                    >
                      <i class="fas fa-heart-broken mr-2"></i>移除收藏
                    </button>
                    <button 
                      class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors" 
                      @click="addToCart($event, product)"
                    >
                      <i class="fas fa-shopping-cart mr-2"></i>加入購物車
                    </button>
                  </div>
                </div>
              </div>
            </NListItem>
          </template>
        </NList>
      </template>
      <NEmpty v-else size="huge" description="您目前沒有收藏的商品" />
    </NCard>
  </div>
</template>

<style scoped>
.img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
</style> 
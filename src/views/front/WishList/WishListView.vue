<script setup lang="ts">
import { NBreadcrumb, NBreadcrumbItem, NCard, NEmpty, NList, NListItem } from 'naive-ui';
import { computed, onMounted } from 'vue';
import { storeToRefs } from 'pinia';
import { useRouter } from 'vue-router';
import WishCard from '@/views/front/WishList/components/WishCard.vue';
import Container from '@/layout/Container.vue';
import { useDeviceStore, useFavoriteStore, useProductStore } from '@/stores';
import productsData from '@/views/front/Mall/data/MallProduct.json';

const router = useRouter();
const deviceStore = useDeviceStore();
const favoriteStore = useFavoriteStore();
const productStore = useProductStore();

const { isMobile } = storeToRefs(deviceStore);
const { favoriteList } = storeToRefs(favoriteStore);
const { productList } = storeToRefs(productStore);

const getBreadcrumbs = computed(() => [
  {
    title: '首頁',
    pathName: 'Home',
  },
  {
    title: '我的收藏',
  },
]);

// 確保 productStore 中有 MallProduct.json 的數據
onMounted(() => {
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
function goToProductDetail (productId: string) {
  router.push({ name: 'MallProductDetail', params: { id: productId } });
}
</script>

<template>
  <section class="bg-cc-other-7/80 py-5 flex-1">
    <Container size="sm">
      <div class="mb-6">
        <h1 class="text-2xl font-bold mb-2">
          我的收藏清單
        </h1>
        <p class="text-gray-600">
          在這裡管理您收藏的商品，點擊商品可查看詳情，或直接加入購物車
        </p>
      </div>

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

      <NCard
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
                    <img class="img" :src="product?.imageUrl">
                  </div>
                </template>
                <div v-if="isMobile" class="w-full aspect-video mb-4 rounded-lg overflow-hidden shadow-sm">
                  <img class="img" :src="product?.imageUrl">
                </div>
                <WishCard v-bind="product" />
              </NListItem>
            </template>
          </NList>
        </template>
        <NEmpty v-else size="huge" description="您目前沒有收藏的商品" />
      </NCard>
    </Container>
  </section>
</template>

<style scoped>
.img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
</style>

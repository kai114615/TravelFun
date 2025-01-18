<template>
  <section class="flex min-h-screen flex-col">
    <Header />
    <div class="relative flex-1 flex flex-col items-stretch">
      <RouterView v-if="isDone" />
    </div>
    <Footer />
  </section>
</template>

<script setup lang="ts">
import { useLoadingBar } from 'naive-ui';
import { storeToRefs } from 'pinia';
import { computed, onMounted, ref } from 'vue';
import { RouterView, useRoute, useRouter } from 'vue-router';

import Footer from '../components/Footer.vue';
import Header from '../components/Header';
import { useCartStore, useProductStore } from '../stores';
import { apiUserCheckSignin, apiUserGetAllProducts, apiUserGetCarts } from '../utils/api';
import { useUserStore } from '@/stores/user';

const route = useRoute();
const router = useRouter();

const loadingBar = useLoadingBar();

const isDone = ref(false);

const cartStore = useCartStore();
const productStore = useProductStore();
const userStore = useUserStore();

const { cartList, total, finalTotal } = storeToRefs(cartStore);
const { productList } = storeToRefs(productStore);
const { userInfo } = storeToRefs(userStore);

const canLoadingBar = computed(() => route.name !== 'Product');

const getInitialProducts = async () => {
  if (canLoadingBar.value) {
    loadingBar.start();
  }

  isDone.value = false;

  try {
    // 檢查登入狀態，只有登入時才獲取資料
    const token = document.cookie.replace(/(?:(?:^|.*;\s*)token\s*=\s*([^;]*).*$)|^.*$/, '$1');
    if (!token) {
      isDone.value = true;
      if (canLoadingBar.value) {
        loadingBar.finish();
      }
      return;
    }

    const [getProductsRes, getCartsRes] = await Promise.all([
      apiUserGetAllProducts(),
      apiUserGetCarts(),
    ]);

    productList.value = getProductsRes?.data?.products ?? [];
    cartList.value = getCartsRes?.data?.data?.carts ?? [];
    total.value = getCartsRes?.data?.data?.total;
    finalTotal.value = getCartsRes?.data?.data?.final_total;
  } catch (error) {
    // 如果是認證錯誤，靜默處理
    if (error?.response?.status === 401) {
      console.log('User not authenticated, skipping data fetch');
    } else {
      loadingBar.error();
    }
  } finally {
    loadingBar.finish();
    isDone.value = true;
  }
};

onMounted(async () => {
  await getInitialProducts();
});

router.beforeEach(async (to, _from, next) => {
  const title = to.meta?.title as string;
  const requiresAuth = to.meta?.requiresAuth;

  if (title)
    document.title = title;

  if (requiresAuth) {
    loadingBar.start();

    try {
      const res = await apiUserCheckSignin();

      const { data: { success } } = res;

      if (success)
        next();
      else
        next({ name: 'Home' });
    }
    catch {
      loadingBar.error();
      next({ name: 'Home' });
    }
    finally {
      loadingBar.finish();
    }
  }
  else {
    next();
  }
});

// 登出處理
const handleLogout = async () => {
  try {
    await userStore.logout()
    router.push('/login')
  } catch (error) {
    console.error('Logout failed:', error)
  }
}
</script>

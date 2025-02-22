<script setup lang="ts">
import { computed } from 'vue';
import { storeToRefs } from 'pinia';
import { ElMessage } from 'element-plus';
import { useRouter } from 'vue-router';
import { useCartStore } from '@/stores/cart';

const router = useRouter();
const cartStore = useCartStore();
const { items } = storeToRefs(cartStore);

// 計算總金額
const totalAmount = computed(() => {
  return items.value.reduce((total, item) => total + item.price * item.quantity, 0);
})

// 更新商品數量
function updateItemQuantity (productId: number, quantity: number) {
  cartStore.updateQuantity(productId, quantity);
}

// 移除商品
function removeItem (productId: number) {
  cartStore.removeFromCart(productId);
  ElMessage.success('商品已從購物車移除');
}

// 前往結帳
function proceedToCheckout () {
  const token = localStorage.getItem('access_token');
  if (!token) {
    // 將當前頁面路徑保存到 localStorage
    localStorage.setItem('checkout_redirect', '/checkout');
    // 導向登入頁面，並帶上重定向路徑
    router.push({
      path: '/login',
      query: { redirect: '/checkout' }
    });
    return;
  }

  // 已登入，直接前往結帳頁面
  router.push('/checkout');
}

// 前往商品列表
function goToProducts () {
  router.push('/mall-products');
}
</script>

<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-2xl font-bold mb-8">
      購物車
    </h1>

    <!-- 購物車為空時顯示 -->
    <div v-if="items.length === 0" class="text-center py-12">
      <i class="fas fa-shopping-cart text-4xl text-gray-400 mb-4" />
      <p class="text-gray-500 mb-4">
        購物車目前沒有商品
      </p>
      <button
        class="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 transition-colors"
        @click="goToProducts"
      >
        去逛逛
      </button>
    </div>

    <!-- 購物車有商品時顯示 -->
    <div v-else class="flex flex-col lg:flex-row gap-8">
      <!-- 左側商品列表 -->
      <div class="lg:w-2/3">
        <div class="bg-white rounded-lg shadow overflow-hidden">
          <!-- 表頭 -->
          <div class="grid grid-cols-12 gap-4 p-4 bg-gray-50 border-b border-gray-200">
            <div class="col-span-6">
              商品資訊
            </div>
            <div class="col-span-2 text-center">
              單價
            </div>
            <div class="col-span-2 text-center">
              數量
            </div>
            <div class="col-span-2 text-center">
              小計
            </div>
          </div>

          <!-- 商品列表 -->
          <div class="divide-y divide-gray-200">
            <div
              v-for="item in items"
              :key="item.id"
              class="grid grid-cols-12 gap-4 p-4 items-center"
            >
              <!-- 商品資訊 -->
              <div class="col-span-6 flex gap-4">
                <img
                  :src="item.image_url"
                  :alt="item.name"
                  class="w-20 h-20 object-cover rounded-lg"
                >
                <div class="flex flex-col justify-between py-1">
                  <h3 class="text-sm font-medium line-clamp-2">
                    {{ item.name }}
                  </h3>
                  <button
                    class="text-red-500 hover:text-red-700 text-sm flex items-center gap-1"
                    @click="removeItem(item.id)"
                  >
                    <i class="fas fa-trash text-xs" />
                    <span>刪除</span>
                  </button>
                </div>
              </div>

              <!-- 單價 -->
              <div class="col-span-2 text-center">
                <p class="text-gray-900">
                  NT$ {{ item.price }}
                </p>
              </div>

              <!-- 數量控制 -->
              <div class="col-span-2 flex justify-center items-center">
                <div class="flex items-center border rounded-lg overflow-hidden">
                  <button
                    class="w-8 h-8 flex items-center justify-center bg-gray-50 hover:bg-gray-100 transition-colors text-gray-700"
                    :disabled="item.quantity <= 1"
                    :class="{ 'opacity-50 cursor-not-allowed': item.quantity <= 1 }"
                    @click="updateItemQuantity(item.id, item.quantity - 1)"
                  >
                    －
                  </button>
                  <input
                    v-model="item.quantity"
                    type="number"
                    class="w-12 h-8 text-center border-x focus:outline-none text-gray-800"
                    :min="1"
                    :max="item.stock"
                  >
                  <button
                    class="w-8 h-8 flex items-center justify-center bg-gray-50 hover:bg-gray-100 transition-colors text-gray-700"
                    :disabled="item.quantity >= item.stock"
                    :class="{ 'opacity-50 cursor-not-allowed': item.quantity >= item.stock }"
                    @click="updateItemQuantity(item.id, item.quantity + 1)"
                  >
                    ＋
                  </button>
                </div>
              </div>

              <!-- 小計 -->
              <div class="col-span-2 text-center">
                <p class="text-green-600 font-bold">
                  NT$ {{ item.price * item.quantity }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右側訂單摘要 -->
      <div class="lg:w-1/3">
        <div class="bg-white rounded-lg shadow p-6 sticky top-4">
          <!-- 折價券區塊 -->
          <div class="mb-6">
            <h2 class="text-xl font-bold mb-4">
              折價券
            </h2>
            <div class="flex gap-2">
              <input
                type="text"
                placeholder="輸入折扣碼 (每次僅限使用一組)"
                class="flex-grow px-3 py-2 border rounded-lg focus:outline-none focus:border-green-500"
              >
              <button
                class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
              >
                使用
              </button>
            </div>
          </div>

          <!-- 訂單摘要 -->
          <div class="space-y-4">
            <div class="flex justify-between">
              <span>商品小計</span>
              <span>NT$ {{ totalAmount }}</span>
            </div>
            <div class="flex justify-between">
              <span>商品折扣</span>
              <span class="text-red-500">- NT$ 0</span>
            </div>
            <div class="flex justify-between">
              <span>運費</span>
              <span>NT$ 0</span>
            </div>
            <div class="flex justify-between text-lg font-bold pt-4 border-t">
              <span>結帳總金額</span>
              <span class="text-green-600">NT$ {{ totalAmount }}</span>
            </div>
            <button
              class="w-full bg-green-600 text-white py-3 rounded-lg hover:bg-green-700 transition-colors"
              @click="proceedToCheckout"
            >
              前往結帳
            </button>
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

/* 移除數量輸入框的上下箭頭 */
input[type="number"]::-webkit-inner-spin-button,
input[type="number"]::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

input[type="number"] {
  -moz-appearance: textfield;
}

/* 讓右側訂單摘要在滾動時保持固定 */
.sticky {
  position: sticky;
  top: 1rem;
}
</style>

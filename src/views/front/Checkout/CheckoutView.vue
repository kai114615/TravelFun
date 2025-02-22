<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { storeToRefs } from 'pinia';
import { useCartStore } from '@/stores/cart';
import api from '@/api/config';
import type { CartItem } from '@/stores/cart';

const router = useRouter();
const cartStore = useCartStore();
const { items, totalAmount } = storeToRefs(cartStore);

// 收件資訊表單
const form = ref({
  name: '',
  phone: '',
  address: '',
  note: ''
});

// 表單驗證規則
const rules = {
  name: [{ required: true, message: '請輸入收件人姓名', trigger: 'blur' }],
  phone: [{ required: true, message: '請輸入聯絡電話', trigger: 'blur' }],
  address: [{ required: true, message: '請輸入收件地址', trigger: 'blur' }]
};

// 提交訂單
async function submitOrder () {
  try {
    // 檢查購物車是否為空
    if (items.value.length === 0) {
      ElMessage.warning('購物車是空的，請先選購商品');
      router.push('/mall-products');
      return;
    }

    // 建立訂單
    const response = await api.post('/shop/api/shopping/orders/create/', {
      items: items.value.map((item: CartItem) => ({
        product_id: item.id,
        quantity: item.quantity
      })),
      shipping_info: {
        name: form.value.name,
        phone: form.value.phone,
        address: form.value.address,
        note: form.value.note
      }
    });

    if (response.data.success) {
      // 清空購物車
      cartStore.clearCart();
      ElMessage.success('訂單建立成功');
      // 導向訂單詳情頁面
      router.push(`/orders/${response.data.order_number}`);
    } else {
      ElMessage.error(response.data.message || '訂單建立失敗');
    }
  } catch (error: any) {
    console.error('建立訂單時發生錯誤:', error);
    ElMessage.error(error.response?.data?.message || '訂單建立失敗，請稍後再試');
  }
}
</script>

<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-2xl font-bold mb-8">
      結帳
    </h1>

    <div class="flex flex-col lg:flex-row gap-8">
      <!-- 左側收件資訊 -->
      <div class="lg:w-2/3">
        <div class="bg-white rounded-lg shadow p-6">
          <h2 class="text-xl font-bold mb-6">
            收件資訊
          </h2>
          <form class="space-y-6" @submit.prevent="submitOrder">
            <!-- 收件人姓名 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                收件人姓名
                <span class="text-red-500">*</span>
              </label>
              <input
                v-model="form.name"
                type="text"
                class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                placeholder="請輸入收件人姓名"
                required
              >
            </div>

            <!-- 聯絡電話 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                聯絡電話
                <span class="text-red-500">*</span>
              </label>
              <input
                v-model="form.phone"
                type="tel"
                class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                placeholder="請輸入聯絡電話"
                required
              >
            </div>

            <!-- 收件地址 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                收件地址
                <span class="text-red-500">*</span>
              </label>
              <input
                v-model="form.address"
                type="text"
                class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                placeholder="請輸入完整收件地址"
                required
              >
            </div>

            <!-- 訂單備註 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                訂單備註
              </label>
              <textarea
                v-model="form.note"
                rows="3"
                class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                placeholder="有什麼想告訴我們的嗎？"
              />
            </div>
          </form>
        </div>
      </div>

      <!-- 右側訂單摘要 -->
      <div class="lg:w-1/3">
        <div class="bg-white rounded-lg shadow p-6 sticky top-4">
          <h2 class="text-xl font-bold mb-6">
            訂單摘要
          </h2>

          <!-- 商品列表 -->
          <div class="space-y-4 mb-6">
            <div v-for="item in items" :key="item.id" class="flex gap-4">
              <img
                :src="item.image_url"
                :alt="item.name"
                class="w-16 h-16 object-cover rounded"
              >
              <div class="flex-grow">
                <h3 class="text-sm font-medium">
                  {{ item.name }}
                </h3>
                <p class="text-sm text-gray-500">
                  數量: {{ item.quantity }}
                </p>
                <p class="text-sm font-medium text-green-600">
                  NT$ {{ item.price * item.quantity }}
                </p>
              </div>
            </div>
          </div>

          <!-- 金額計算 -->
          <div class="space-y-4 pt-6 border-t">
            <div class="flex justify-between">
              <span>商品小計</span>
              <span>NT$ {{ totalAmount }}</span>
            </div>
            <div class="flex justify-between">
              <span>運費</span>
              <span>免費</span>
            </div>
            <div class="flex justify-between text-lg font-bold pt-4 border-t">
              <span>結帳總金額</span>
              <span class="text-green-600">NT$ {{ totalAmount }}</span>
            </div>
          </div>

          <!-- 送出訂單按鈕 -->
          <button
            class="w-full mt-6 bg-green-600 text-white py-3 rounded-lg hover:bg-green-700 transition-colors font-medium"
            @click="submitOrder"
          >
            確認送出訂單
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.sticky {
  position: sticky;
  top: 1rem;
}
</style>

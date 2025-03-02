<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { useCartStore } from '@/stores/cart';
import api from '@/api/config';

// 確保 window 可以在模板中訪問
const window = globalThis.window;

const router = useRouter();
const cartStore = useCartStore();

// 全形數字轉半形函數
function toHalfWidth (str: string): string {
  if (!str) return '';

  // 全形數字的 Unicode 範圍是 U+FF10 到 U+FF19
  // 半形數字的 Unicode 範圍是 U+0030 到 U+0039
  return str.replace(/[\uFF10-\uFF19]/g, (match) => {
    return String.fromCharCode(match.charCodeAt(0) - 0xFEE0);
  });
}

// 訂單資訊
const orderInfo = ref({
  orderNumber: '',
  items: [] as any[],
  shippingInfo: {
    name: '',
    phone: '',
    address: '',
    note: ''
  },
  totalAmount: 0,
  discount: 0,
  finalAmount: 0,
  shippingFee: 0
});

// 付款方式
const paymentMethod = ref('credit_card');
// 訂單提交中狀態
const isSubmitting = ref(false);

// 載入訂單資訊
onMounted(() => {
  // 從路由參數或 localStorage 獲取訂單資訊
  const savedOrderInfo = window.localStorage.getItem('pendingOrderInfo');
  if (savedOrderInfo) {
    const parsedInfo = JSON.parse(savedOrderInfo);

    // 處理收件人資料中的全形數字
    if (parsedInfo.shippingInfo) {
      parsedInfo.shippingInfo.phone = toHalfWidth(parsedInfo.shippingInfo.phone);
      parsedInfo.shippingInfo.address = toHalfWidth(parsedInfo.shippingInfo.address);
    }

    orderInfo.value = parsedInfo;
  } else {
    // 如果沒有訂單資訊，返回結帳頁面
    ElMessage.warning('找不到訂單資訊，請重新結帳');
    router.push('/checkout');
  }
});

// 計算最終金額
const finalAmount = computed(() => {
  return orderInfo.value.totalAmount - orderInfo.value.discount + orderInfo.value.shippingFee;
});

// 提交付款
async function submitPayment () {
  try {
    if (isSubmitting.value) return;
    isSubmitting.value = true;

    ElMessage.info('正在處理訂單...');

    // 準備提交到後端的訂單數據
    const orderData = {
      items: orderInfo.value.items.map(item => ({
        product_id: item.id,
        quantity: item.quantity
      })),
      shipping_info: {
        name: orderInfo.value.shippingInfo.name,
        phone: orderInfo.value.shippingInfo.phone,
        address: orderInfo.value.shippingInfo.address,
        note: orderInfo.value.shippingInfo.note || ''
      },
      payment_method: paymentMethod.value
    };

    // 調用後端API創建訂單
    const response = await api.post('/api/shopping/orders/create/', orderData);

    if (response.data.success) {
      // 清空購物車和暫存的訂單資訊
      cartStore.clearCart();
      window.localStorage.removeItem('pendingOrderInfo');

      // 顯示成功訊息
      ElMessage.success('訂單建立成功！');

      // 導向訂單完成頁面
      router.push({
        name: 'OrderComplete',
        params: { orderNumber: response.data.order_number }
      });
    } else {
      throw new Error(response.data.message || '訂單處理失敗');
    }
  } catch (error: any) {
    console.error('訂單處理失敗:', error);
    ElMessage.error(error.response?.data?.message || error.message || '訂單處理失敗，請稍後再試');
  } finally {
    isSubmitting.value = false;
  }
}

// 返回修改訂單
function goBackToCheckout () {
  router.push('/checkout');
}

// 導向登入頁面
function goToLogin () {
  router.push('/login');
}
</script>

<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-2xl font-bold mb-8">
      確認訂單
    </h1>

    <div class="flex flex-col lg:flex-row gap-8">
      <!-- 左側訂單資訊 -->
      <div class="lg:w-2/3">
        <!-- 帳號資訊 -->
        <div class="bg-white rounded-lg shadow p-6 mb-6">
          <div class="flex justify-between items-center mb-4">
            <h2 class="text-xl font-bold">
              會員帳號
            </h2>
            <button class="text-gray-500 hover:text-gray-700">
              <i class="fas fa-chevron-down" />
            </button>
          </div>
          <p class="text-gray-500">
            {{ window.localStorage.getItem('user') ? JSON.parse(window.localStorage.getItem('user') || '{}').username : '未登入' }}
          </p>
          <button class="text-blue-600 hover:text-blue-800 text-sm mt-2" @click="goToLogin">
            登入其他帳戶
          </button>
        </div>

        <!-- 收件人資料 -->
        <div class="bg-white rounded-lg shadow p-6 mb-6">
          <div class="flex justify-between items-center mb-4">
            <h2 class="text-xl font-bold">
              收件人資料
            </h2>
            <button class="text-gray-500 hover:text-gray-700">
              <i class="fas fa-chevron-down" />
            </button>
          </div>
          <div class="mb-4 space-y-2">
            <div>
              <span class="text-gray-500 font-medium">收件人姓名：</span>
              <span class="text-gray-700">{{ orderInfo.shippingInfo.name }}</span>
            </div>
            <div>
              <span class="text-gray-500 font-medium">收件地址：</span>
              <span class="text-gray-700">{{ orderInfo.shippingInfo.address }}</span>
            </div>
            <div>
              <span class="text-gray-500 font-medium">聯絡電話：</span>
              <span class="text-gray-700">{{ orderInfo.shippingInfo.phone }}</span>
            </div>
            <div v-if="orderInfo.shippingInfo.note">
              <span class="text-gray-500 font-medium">訂單備註：</span>
              <span class="text-gray-700">{{ orderInfo.shippingInfo.note }}</span>
            </div>
          </div>
          <button class="text-blue-600 hover:text-blue-800 text-sm" @click="goBackToCheckout">
            使用其他地址
          </button>
        </div>

        <!-- 運費 -->
        <div class="bg-white rounded-lg shadow p-6 mb-6">
          <div class="flex justify-between items-center mb-4">
            <h2 class="text-xl font-bold">
              運費
            </h2>
            <button class="text-gray-500 hover:text-gray-700">
              <i class="fas fa-chevron-down" />
            </button>
          </div>
          <div class="flex justify-between items-center">
            <div>
              <p class="font-medium">
                宅配到府
              </p>
              <p class="text-sm text-gray-500">
                預計 3-5 個工作天送達
              </p>
            </div>
            <p class="font-medium">
              {{ orderInfo.shippingFee > 0 ? `NT$ ${orderInfo.shippingFee}` : '免費' }}
            </p>
          </div>
        </div>

        <!-- 付款方式 -->
        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex justify-between items-center mb-4">
            <h2 class="text-xl font-bold">
              付款方式
            </h2>
            <button class="text-gray-500 hover:text-gray-700">
              <i class="fas fa-chevron-down" />
            </button>
          </div>

          <div class="space-y-4">
            <!-- 信用卡付款 -->
            <div class="border rounded-lg p-4" :class="{ 'border-blue-500 bg-blue-50': paymentMethod === 'credit_card' }">
              <label class="flex items-center cursor-pointer">
                <input
                  v-model="paymentMethod"
                  type="radio"
                  name="payment"
                  value="credit_card"
                  class="form-radio h-5 w-5 text-blue-600"
                >
                <span class="ml-2 flex-grow">信用卡・LINE Pay</span>
                <div class="flex space-x-2">
                  <i class="fab fa-cc-visa text-blue-600 text-xl" />
                  <i class="fab fa-cc-mastercard text-red-600 text-xl" />
                  <i class="fab fa-cc-jcb text-green-600 text-xl" />
                  <i class="fab fa-line text-green-500 text-xl" />
                </div>
              </label>
              <div v-if="paymentMethod === 'credit_card'" class="mt-4 text-center text-gray-600">
                <div class="border rounded p-4 mx-auto max-w-md">
                  <div class="flex justify-center items-center mb-3">
                    <i class="fas fa-credit-card text-4xl text-gray-400 mr-3" />
                    <i class="fas fa-lock text-3xl text-green-600" />
                  </div>
                  <p class="text-sm">
                    您將被導入信用卡付款頁面進行信用卡安全結帳
                  </p>
                </div>
              </div>
            </div>

            <!-- ATM 轉帳 -->
            <div class="border rounded-lg p-4" :class="{ 'border-blue-500 bg-blue-50': paymentMethod === 'atm' }">
              <label class="flex items-center cursor-pointer">
                <input
                  v-model="paymentMethod"
                  type="radio"
                  name="payment"
                  value="atm"
                  class="form-radio h-5 w-5 text-blue-600"
                >
                <span class="ml-2">ATM 轉帳</span>
              </label>
              <div v-if="paymentMethod === 'atm'" class="mt-4 text-sm text-gray-600">
                <p>請於訂單成立後 3 天內完成轉帳，逾期訂單將自動取消</p>
                <p>轉帳資訊將顯示在訂單確認信中</p>
              </div>
            </div>
          </div>

          <div class="mt-8">
            <p class="text-sm text-gray-600 mb-2">
              全程採用 TLS 1.2 安全憑證加密，付款過程均受保護，請安心使用。
            </p>
          </div>
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
            <div v-for="item in orderInfo.items" :key="item.id" class="flex gap-4">
              <div class="relative">
                <img
                  :src="item.image_url"
                  :alt="item.name"
                  class="w-16 h-16 object-cover rounded"
                >
                <div class="absolute -top-2 -right-2 bg-gray-700 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                  {{ item.quantity }}
                </div>
              </div>
              <div class="flex-grow">
                <h3 class="text-sm font-medium">
                  {{ item.name }}
                </h3>
                <p class="text-sm font-medium text-green-600">
                  NT$ {{ item.price * item.quantity }}
                </p>
              </div>
            </div>
          </div>

          <!-- 折扣碼 -->
          <div class="mb-6">
            <div class="flex gap-2">
              <input
                type="text"
                placeholder="請輸入折扣碼"
                class="flex-grow px-3 py-2 border rounded-lg focus:outline-none focus:border-green-500"
              >
              <button
                class="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors"
              >
                套用
              </button>
            </div>
          </div>

          <!-- 金額計算 -->
          <div class="space-y-4 pt-6 border-t">
            <div class="flex justify-between">
              <span>商品小計</span>
              <span>NT$ {{ orderInfo.totalAmount }}</span>
            </div>
            <div v-if="orderInfo.discount > 0" class="flex justify-between">
              <span>總節省金額</span>
              <span class="text-red-500">-NT$ {{ orderInfo.discount }}</span>
            </div>
            <div class="flex justify-between">
              <span>運費</span>
              <span>{{ orderInfo.shippingFee > 0 ? `NT$ ${orderInfo.shippingFee}` : '免費' }}</span>
            </div>
            <div class="flex justify-between text-lg font-bold pt-4 border-t">
              <span>結帳總金額</span>
              <span class="text-green-600">NT$ {{ finalAmount }}</span>
            </div>
          </div>

          <!-- 送出訂單按鈕 -->
          <button
            class="w-full mt-6 bg-green-600 text-white py-3 rounded-lg hover:bg-green-700 transition-colors font-medium"
            :disabled="isSubmitting"
            @click="submitPayment"
          >
            {{ isSubmitting ? '處理中...' : '立即付款' }}
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

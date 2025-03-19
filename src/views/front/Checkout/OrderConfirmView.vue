<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, ElMessageBox, ElDialog, ElButton, ElForm, ElFormItem, ElInput } from 'element-plus';
import { useCartStore } from '@/stores/cart';
import { useUserStore } from '@/stores/user';
import api from '@/api/config';
import { CashIcon, TruckIcon } from '@heroicons/vue/outline'
import axios from 'axios';

// 確保 window 可以在模板中訪問
const window = globalThis.window;

const router = useRouter();
const cartStore = useCartStore();
const userStore = useUserStore();

// 取得用戶登入狀態和資訊
const isLoggedIn = computed(() => userStore.loginStatus || localStorage.getItem('access_token') !== null);
const userDisplayName = computed(() => userStore.displayName || '');
const userEmail = computed(() => userStore.userInfo?.email || '');

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
const orderInfo = ref(JSON.parse(window.localStorage.getItem('pendingOrderInfo') || '{}'));

// 付款方式
const paymentMethod = ref('cash_on_delivery');
// 訂單提交中狀態
const isSubmitting = ref(false);

// 載入訂單資訊
onMounted(async () => {
  // 強制檢查登入狀態
  if(localStorage.getItem('access_token')) {
    await userStore.checkLoginStatus();
    console.log('登入狀態檢查完成:', userStore.loginStatus);
  }
  
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

// 提交付款 - 使用單一真實API路徑
const submitPayment = async () => {
  try {
    isSubmitting.value = true;
    ElMessage.info('正在處理訂單...');
    
    // 驗證必填資訊
    if (!orderInfo.value.shippingInfo.name || !orderInfo.value.shippingInfo.phone || !orderInfo.value.shippingInfo.address) {
      ElMessage.error('請填寫完整的收件人資訊');
      isSubmitting.value = false;
      return;
    }
    
    // 建立訂單資料 - 確保符合後端期望的格式
    const orderData = {
      payment_method: 'cash_on_delivery',
      shipping_name: orderInfo.value.shippingInfo.name,
      shipping_phone: orderInfo.value.shippingInfo.phone,
      shipping_address: orderInfo.value.shippingInfo.address,
      shipping_note: orderInfo.value.shippingInfo.note || '',
      items: orderInfo.value.items.map((item: any) => ({
        product_id: item.id,
        quantity: item.quantity
      }))
    };
    
    // 使用較短的API路徑，確保與後端匹配 (嘗試shopping路徑)
    const API_URL = '/api/shopping/orders/create/';

    console.log('使用API配置中的axios實例發送請求到:', API_URL);

    try {
      console.log('訂單數據:', orderData);
      
      // 使用不同路徑嘗試 - 這是原始配置的路徑
      const response = await api.post(API_URL, orderData);
      
      console.log('訂單API請求成功:', response.data);
      const responseData = response.data;
      
      // 處理成功響應
      if (responseData && responseData.success) {
        // 清空購物車
        try {
          localStorage.removeItem('cartItems');
          localStorage.removeItem('cartCount');
          cartStore.clearCart();
          console.log('購物車已清空');
        } catch (cartError) {
          console.error('清空購物車時發生錯誤:', cartError);
        }
        
        // 儲存訂單資訊到本地
        const orderNumber = responseData.order_number || responseData.order_id;
        localStorage.setItem('lastOrderNumber', orderNumber);
        localStorage.setItem('orderTotal', String(orderInfo.value.totalAmount));
        
        // 顯示成功訊息並導向訂單頁面
        ElMessage.success('訂單建立成功！我們將盡快處理您的訂單。');
        router.push({
          path: `/member/orders`,
          query: { 
            just_ordered: 'true',
            order_number: orderNumber
          }
        });
      } else {
        // 處理後端返回的錯誤信息
        console.error('訂單創建失敗:', responseData);
        ElMessage.error(responseData.message || '訂單處理失敗');
      }
    } catch (error: any) {
      console.error('訂單提交出錯:', error);
      
      // 提供詳細錯誤信息以便調試
      if (error.response) {
        console.error('錯誤響應:', error.response.data);
        console.error('錯誤狀態碼:', error.response.status);
        ElMessage.error(`訂單處理失敗 (${error.response.status}): ${error.response.data?.message || '伺服器錯誤'}`);
      } else if (error.request) {
        console.error('請求發送但無響應:', error.request);
        ElMessage.error('伺服器無響應，請檢查網絡連接');
      } else {
        ElMessage.error(`錯誤: ${error.message}`);
      }
    }
  } catch (error: any) {
    console.error('訂單提交出錯:', error);
    
    // 提供詳細錯誤信息以便調試
    if (error.response) {
      console.error('錯誤響應:', error.response.data);
      console.error('錯誤狀態碼:', error.response.status);
      ElMessage.error(`訂單處理失敗 (${error.response.status}): ${error.response.data?.message || '伺服器錯誤'}`);
    } else if (error.request) {
      console.error('請求發送但無響應:', error.request);
      ElMessage.error('伺服器無響應，請檢查網絡連接');
    } else {
      ElMessage.error(`錯誤: ${error.message}`);
    }
  } finally {
    isSubmitting.value = false;
  }
};

// 返回修改訂單
function goBackToCheckout () {
  router.push('/checkout');
}

// 導向登入頁面或切換帳戶
async function goToLogin() {
  // 如果用戶已登入，顯示確認對話框
  if (isLoggedIn.value) {
    try {
      await ElMessageBox.confirm(
        '切換帳戶將會將您登出目前的帳號，確定要繼續嗎？',
        '確認切換帳戶',
        {
          confirmButtonText: '確定',
          cancelButtonText: '取消',
          type: 'warning',
          center: true
        }
      );
      
      // 用戶點擊確定，執行登出操作
      await userStore.logout();
      ElMessage.success('已成功登出，請重新登入');
      router.push('/login');
    } catch (error) {
      // 用戶點擊取消，不執行任何操作
      return;
    }
  } else {
    // 用戶未登入，直接跳轉到登入頁面
    router.push('/login');
  }
}

// 選擇付款方式 (修改預設為貨到付款)
const selectPaymentMethod = (method) => {
  paymentMethod.value = method
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
          
          <!-- 已登入狀態 -->
          <div v-if="isLoggedIn" class="mb-2">
            <p class="text-gray-700 font-medium">
              {{ userDisplayName }}
              <span class="inline-flex items-center ml-2 px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                <i class="fas fa-check-circle mr-1"></i>已登入
              </span>
            </p>
            <p v-if="userEmail" class="text-gray-500 text-sm">
              <i class="fas fa-envelope mr-1"></i> {{ userEmail }}
            </p>
          </div>
          
          <!-- 未登入狀態 -->
          <div v-else class="mb-2">
            <p class="text-gray-500">
              <i class="fas fa-user-slash mr-1"></i> 未登入
            </p>
            <p class="text-gray-500 text-sm">登入後可享會員購物優惠及訂單追蹤</p>
          </div>
          
          <button class="text-blue-600 hover:text-blue-800 text-sm mt-2" @click="goToLogin">
            {{ isLoggedIn ? '切換帳戶' : '立即登入' }}
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
        <div class="payment-section mb-8">
          <h2 class="section-title mb-4">付款方式</h2>
          
          <div class="payment-options">
            <div class="payment-option p-4 border rounded-lg mb-4 bg-white">
              <div class="flex items-start">
                <NRadio checked disabled value="cash_on_delivery" label="貨到付款" />
                <div class="ml-2">
                  <h3 class="font-medium">貨到付款</h3>
                  <p class="text-gray-600 text-sm">商品送達時付款，我們的送貨人員會收取商品費用</p>
                </div>
              </div>
            </div>
            
            <div class="mt-4">
              <p class="text-sm text-gray-600 mb-2">
                全程採用安全的物流配送，收到貨後再付款，安全又方便。
              </p>
            </div>
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
            {{ isSubmitting ? '處理中...' : '確認訂單並送出' }}
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

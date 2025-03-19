<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import Banner from '@/components/Banner.vue';
import api from '@/api/config';
import { useUserStore } from '@/stores/user';

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();
const orderNumber = ref(route.params.orderNumber as string);
const orderDetails = ref<any>(null);
const isLoading = ref(true);
const isLoggedIn = ref(userStore.isAuthenticated);

// 格式化付款方式顯示
const formatPaymentMethod = (method: string) => {
  const methodMap: Record<string, string> = {
    'credit_card': '信用卡',
    'atm': 'ATM轉帳',
    'line_pay': 'LINE Pay',
    'ecpay': '綠界金流',
    'CREDIT': '信用卡',
    'WebATM': '網路ATM',
    'ATM': 'ATM轉帳',
    'CVS': '超商代碼',
    'BARCODE': '超商條碼',
    'cash_on_delivery': '貨到付款'
  };
  return methodMap[method] || method;
};

// 格式化訂單狀態顯示
const formatOrderStatus = (status: string) => {
  const statusMap: Record<string, { text: string, color: string }> = {
    'pending': { text: '待付款', color: 'text-yellow-500' },
    'paid': { text: '已付款', color: 'text-green-500' },
    'shipped': { text: '已出貨', color: 'text-blue-500' },
    'completed': { text: '已完成', color: 'text-green-700' },
    'cancelled': { text: '已取消', color: 'text-red-500' }
  };
  return statusMap[status] || { text: status, color: 'text-gray-500' };
};

// 格式化物流狀態
const formatLogisticsStatus = (status: string) => {
  if (!status) return '等待處理';
  
  const statusMap = {
    'processing': '處理中',
    'shipping': '配送中',
    'delivered': '已送達',
    'returned': '已退回',
    'failed': '配送失敗'
  };
  
  return statusMap[status] || status;
};

// 獲取訂單詳情
const fetchOrderDetails = async () => {
  try {
    isLoading.value = true;
    
    // 如果用戶已登入，使用API獲取訂單詳情
    if (isLoggedIn.value) {
      try {
        const response = await api.get(`/api/shopping/orders/?order_number=${orderNumber.value}`);
        if (response.data && response.data.data && response.data.data.length > 0) {
          orderDetails.value = response.data.data[0];
          console.log('訂單詳情:', orderDetails.value);
        } else {
          ElMessage.warning('找不到訂單詳情');
        }
      } catch (error) {
        console.error('獲取訂單詳情失敗:', error);
        // 如果API請求失敗，回退到本地儲存的訂單資訊
        const lastOrderNumber = localStorage.getItem('lastOrderNumber');
        if (lastOrderNumber === orderNumber.value) {
          ElMessage.info('使用本地訂單資訊');
        } else {
          ElMessage.warning('找不到訂單資訊');
        }
      }
    } else {
      // 未登入用戶，檢查本地存儲的訂單信息
      const lastOrderNumber = localStorage.getItem('lastOrderNumber');
      if (lastOrderNumber !== orderNumber.value) {
        ElMessage.warning('找不到訂單資訊');
      }
    }
  } catch (error) {
    console.error('處理訂單詳情失敗:', error);
    ElMessage.error('獲取訂單信息失敗');
  } finally {
    isLoading.value = false;
  }
};

// 返回購物頁面
const backToShopping = () => {
  router.push('/mall-products');
};

// 查看訂單
const viewOrders = () => {
  if (isLoggedIn.value) {
    router.push('/member/orders');
  } else {
    router.push({
      path: '/login',
      query: { redirect: '/member/orders' }
    });
  }
};

onMounted(() => {
  if (!orderNumber.value) {
    ElMessage.error('訂單編號不存在');
    router.push('/');
    return;
  }
  
  fetchOrderDetails();
});
</script>

<template>
  <div>
    <Banner bg-url="/images/banner.jpg">
      <template #title>
        訂單完成
      </template>
      <template #sec-title>
        感謝您的購買！您的訂單已成功提交
      </template>
    </Banner>

    <div class="container mx-auto px-4 py-8">
      <div class="max-w-2xl mx-auto bg-white rounded-lg shadow-md p-8">
        <!-- 訂單成功圖標 -->
        <div class="text-center my-6">
          <div class="inline-flex items-center justify-center h-24 w-24 rounded-full bg-green-100 mb-4">
            <i class="fas fa-check-circle text-green-500 text-5xl"></i>
          </div>
          <h2 class="text-2xl font-bold text-gray-800 mb-2">訂單已成功提交！</h2>
          <p class="text-gray-600">
            訂單編號: <span class="font-semibold">{{ orderNumber }}</span>
          </p>
          
          <!-- 訂單狀態 -->
          <div v-if="orderDetails" class="mt-4">
            <p class="text-lg">
              訂單狀態: 
              <span :class="formatOrderStatus(orderDetails.status).color" class="font-semibold">
                {{ formatOrderStatus(orderDetails.status).text }}
              </span>
            </p>
            <p class="text-gray-600 mt-1">
              付款方式: {{ formatPaymentMethod(orderDetails.payment_method) }}
            </p>
          </div>
        </div>

        <!-- 付款指引 -->
        <div v-if="orderDetails && orderDetails.status === 'pending'" class="bg-yellow-50 p-4 rounded-lg my-6">
          <h3 class="font-semibold text-yellow-700 mb-2">
            <i class="fas fa-exclamation-circle mr-2"></i>付款提醒
          </h3>
          <p class="text-yellow-700">訂單已建立，但尚未完成付款。請盡快完成付款流程，以確保訂單能順利處理。</p>
          
          <!-- 付款相關資訊 -->
          <div v-if="orderDetails.payment_info" class="mt-4 text-sm">
            <div v-if="orderDetails.payment_info.atm_info" class="mb-2">
              <p><span class="font-semibold">ATM繳費帳號:</span> {{ orderDetails.payment_info.atm_info }}</p>
            </div>
            <div v-if="orderDetails.payment_info.cvs_info" class="mb-2">
              <p><span class="font-semibold">超商代碼:</span> {{ orderDetails.payment_info.cvs_info }}</p>
            </div>
            <div v-if="orderDetails.payment_info.expire_date" class="mb-2">
              <p><span class="font-semibold">繳費期限:</span> {{ orderDetails.payment_info.expire_date }}</p>
            </div>
          </div>
        </div>

        <!-- 付款方式資訊 -->
        <div class="p-6 bg-white rounded-lg shadow-md mb-6">
          <h2 class="text-xl font-bold mb-4">付款資訊</h2>
          
          <div class="flex items-center mb-4">
            <div class="p-2 bg-green-100 rounded-full mr-3">
              <i class="fas fa-money-bill-wave text-green-600"></i>
            </div>
            <div>
              <p class="font-medium">貨到付款</p>
              <p class="text-sm text-gray-600">商品送達時向送貨人員付款</p>
            </div>
          </div>
          
          <div class="border-t border-gray-200 pt-4 mt-2">
            <div class="flex justify-between mb-2">
              <span class="text-gray-600">訂單金額</span>
              <span class="font-medium">NT$ {{ orderDetails.total_amount || '0' }}</span>
            </div>
            <div class="flex justify-between mb-2">
              <span class="text-gray-600">配送費用</span>
              <span class="font-medium">NT$ 0</span>
            </div>
            <div class="flex justify-between font-bold text-lg mt-2 pt-2 border-t border-gray-200">
              <span>應付金額</span>
              <span class="text-green-600">NT$ {{ orderDetails.total_amount || '0' }}</span>
            </div>
          </div>
          
          <div class="mt-4 p-3 bg-yellow-50 border border-yellow-100 rounded-lg">
            <div class="flex">
              <div class="text-yellow-500 mr-2">
                <i class="fas fa-info-circle"></i>
              </div>
              <div class="text-sm text-gray-700">
                <p class="font-medium">貨到付款提醒</p>
                <p>商品會在 2-3 個工作天內送達，請保持電話暢通並備妥現金。</p>
              </div>
            </div>
          </div>
        </div>

        <!-- 物流資訊 -->
        <div v-if="orderDetails.logistics_id" class="p-6 bg-white rounded-lg shadow-md mb-6">
          <h2 class="text-xl font-bold mb-4">物流資訊</h2>
          
          <div class="flex items-center mb-4">
            <div class="p-2 bg-blue-100 rounded-full mr-3">
              <i class="fas fa-truck text-blue-600"></i>
            </div>
            <div>
              <p class="font-medium">宅配到府</p>
              <p class="text-sm text-gray-600">由物流公司配送到指定地址</p>
            </div>
          </div>
          
          <div class="border-t border-gray-200 pt-4">
            <div class="grid grid-cols-2 gap-4 mb-4">
              <div>
                <p class="text-sm text-gray-500">物流單號</p>
                <p class="font-medium">{{ orderDetails.logistics_id }}</p>
              </div>
              <div>
                <p class="text-sm text-gray-500">配送狀態</p>
                <p class="font-medium">
                  <span class="inline-block px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">
                    {{ formatLogisticsStatus(orderDetails.logistics_status) }}
                  </span>
                </p>
              </div>
            </div>
            
            <div class="mt-4">
              <p class="text-sm text-gray-500 mb-2">配送進度</p>
              
              <div class="relative">
                <!-- 物流時間軸 -->
                <div class="absolute left-3 top-0 bottom-0 w-0.5 bg-gray-200"></div>
                
                <div class="relative pl-10 pb-5">
                  <div class="absolute left-0 top-1 w-6 h-6 rounded-full bg-blue-500 flex items-center justify-center">
                    <i class="fas fa-check text-white text-xs"></i>
                  </div>
                  <div>
                    <p class="font-medium">訂單已建立</p>
                    <p class="text-xs text-gray-500">{{ formatDate(orderDetails.created_at) }}</p>
                  </div>
                </div>
                
                <div class="relative pl-10 pb-5">
                  <div class="absolute left-0 top-1 w-6 h-6 rounded-full bg-gray-300 flex items-center justify-center">
                    <i class="fas fa-box text-white text-xs"></i>
                  </div>
                  <div>
                    <p class="font-medium">商品包裝中</p>
                    <p class="text-xs text-gray-500">預計 1 個工作天內完成</p>
                  </div>
                </div>
                
                <div class="relative pl-10">
                  <div class="absolute left-0 top-1 w-6 h-6 rounded-full bg-gray-300 flex items-center justify-center">
                    <i class="fas fa-truck text-white text-xs"></i>
                  </div>
                  <div>
                    <p class="font-medium">配送中</p>
                    <p class="text-xs text-gray-500">預計 2-3 個工作天送達</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 訂單資訊 -->
        <div v-if="orderDetails" class="border-t border-gray-200 pt-6 mt-6">
          <h3 class="text-xl font-semibold mb-4">訂單資訊</h3>
          
          <div class="mb-4">
            <p class="font-medium text-gray-700 mb-1">收件人資訊</p>
            <p>{{ orderDetails.shipping_name || '收件人' }}</p>
            <p>{{ orderDetails.shipping_address }}</p>
            <p>{{ orderDetails.shipping_phone }}</p>
          </div>
          
          <div v-if="orderDetails.items && orderDetails.items.length" class="mb-4">
            <p class="font-medium text-gray-700 mb-1">訂購商品</p>
            <div class="overflow-x-auto">
              <table class="min-w-full">
                <thead>
                  <tr class="border-b border-gray-200">
                    <th class="py-2 text-left">商品</th>
                    <th class="py-2 text-right">單價</th>
                    <th class="py-2 text-right">數量</th>
                    <th class="py-2 text-right">小計</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in orderDetails.items" :key="item.id" class="border-b border-gray-200">
                    <td class="py-2">{{ item.product_name }}</td>
                    <td class="py-2 text-right">NT$ {{ item.price }}</td>
                    <td class="py-2 text-right">{{ item.quantity }}</td>
                    <td class="py-2 text-right">NT$ {{ item.subtotal }}</td>
                  </tr>
                </tbody>
                <tfoot>
                  <tr>
                    <td colspan="3" class="py-2 text-right font-medium">總金額:</td>
                    <td class="py-2 text-right font-bold">NT$ {{ orderDetails.total_amount }}</td>
                  </tr>
                </tfoot>
              </table>
            </div>
          </div>
        </div>

        <div class="text-center mt-8">
          <p class="text-gray-600 mb-6">感謝您的購買，如有任何問題請聯繫我們的客服</p>
          <div class="flex flex-col sm:flex-row justify-center gap-4">
            <button @click="backToShopping" class="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors">
              繼續購物
            </button>
            <button @click="viewOrders" class="bg-gray-200 text-gray-800 px-6 py-3 rounded-lg hover:bg-gray-300 transition-colors">
              查看我的訂單
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

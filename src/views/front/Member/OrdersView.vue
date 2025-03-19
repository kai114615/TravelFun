<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { NCard, NEmpty, NTag, NButton, NSpin, useMessage, NIcon, NModal, NAlert } from 'naive-ui';
import { useRouter } from 'vue-router';
import axios from 'axios';
import { WarningOutline, CloseCircleOutline } from '@vicons/ionicons5';
import OrderDetailContent from '@/components/Order/OrderDetailContent.vue';

const message = useMessage();
const router = useRouter();
const loading = ref(false);
const orders = ref<any[]>([]);
const hasError = ref(false);

// 訂單詳情相關
const showOrderDetail = ref(false);
const selectedOrderNumber = ref('');
const orderDetail = ref<any>(null);
const orderLoading = ref(false);
const orderDetailHasError = ref(false);

// 格式化訂單狀態
const formatOrderStatus = (status: string) => {
  const statusMap: Record<string, string> = {
    'pending': '處理中',
    'processing': '處理中',
    'shipped': '已出貨',
    'completed': '已完成',
    'cancelled': '已取消',
    'pending_payment': '待付款',
    'paid': '已付款'
  };
  return statusMap[status] || status;
};

// 獲取訂單狀態的標籤類型
const getStatusType = (status: string) => {
  const typeMap: Record<string, 'default' | 'error' | 'success' | 'warning' | 'info' | 'primary'> = {
    'pending': 'warning',
    'processing': 'info',
    'shipped': 'info',
    'completed': 'success',
    'cancelled': 'error',
    'pending_payment': 'warning',
    'paid': 'success'
  };
  return typeMap[status] || 'default';
};

// 格式化付款方式
const formatPaymentMethod = (method: string) => {
  const methodMap: Record<string, string> = {
    'cash_on_delivery': '貨到付款',
    'credit_card': '信用卡',
    'atm': 'ATM轉帳',
    'ecpay': '綠界支付'
  };
  return methodMap[method] || method;
};

// 格式化日期
const formatDate = (dateStr: string) => {
  if (!dateStr) return '';
  
  const date = new Date(dateStr);
  return date.toLocaleString('zh-TW', {
    year: 'numeric', 
    month: '2-digit', 
    day: '2-digit',
    hour: '2-digit', 
    minute: '2-digit'
  });
};

// 獲取用戶訂單
const fetchUserOrders = async () => {
  try {
    loading.value = true;
    hasError.value = false;
    
    // 從localStorage獲取token
    const token = localStorage.getItem('access_token');
    if (!token) {
      message.error('請先登入');
      router.push('/login');
      return;
    }
    
    // 設置API請求的headers
    const headers = {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    };
    
    console.log('正在獲取訂單資料...');
    
    // 嘗試請求訂單資料
    let response = null;
    try {
      // 嘗試第一個API路徑
      response = await axios.get('/api/shopping/orders/', { 
        headers,
        baseURL: import.meta.env.VITE_API_BASE_URL
      });
      console.log('第一個API路徑成功:', response.data);
    } catch (firstError) {
      console.error('第一個API路徑失敗:', firstError);
      
      try {
        // 嘗試第二個API路徑
        response = await axios.get('/api/shopping/user-orders/', { 
          headers,
          baseURL: import.meta.env.VITE_API_BASE_URL
        });
        console.log('第二個API路徑成功:', response.data);
      } catch (secondError) {
        console.error('第二個API路徑失敗:', secondError);
        throw new Error('無法從API獲取訂單數據');
      }
    }
    
    // 處理回應數據
    if (response && response.data) {
      if (response.data.success && Array.isArray(response.data.data)) {
        orders.value = response.data.data;
        console.log('獲取訂單成功:', orders.value.length, '個訂單');
      } else if (Array.isArray(response.data)) {
        orders.value = response.data;
        console.log('獲取訂單成功:', orders.value.length, '個訂單');
      } else {
        console.error('返回數據格式不正確:', response.data);
        throw new Error('返回數據格式不正確');
      }
    } else {
      console.error('返回數據為空');
      throw new Error('返回數據為空');
    }
  } catch (error) {
    console.error('獲取訂單失敗:', error);
    hasError.value = true;
    message.error('獲取訂單失敗，請稍後再試');
    
    // 如果API失敗，創建模擬訂單數據
    createMockOrders();
  } finally {
    loading.value = false;
  }
};

// 創建模擬訂單數據
const createMockOrders = () => {
  console.log('使用模擬訂單數據');
  
  // 模擬數據
  orders.value = [
    {
      id: 1,
      order_number: 'ORD' + Date.now().toString().substring(0, 10),
      total_amount: 1399,
      status: 'pending',
      payment_method: 'cash_on_delivery',
      shipping_name: '陳小明',
      shipping_phone: '0912345678',
      shipping_address: '民權路25號C棟18樓之20',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      items: [
        { product_name: '產品A', quantity: 2, price: 499 },
        { product_name: '產品B', quantity: 1, price: 401 }
      ]
    },
    {
      id: 2,
      order_number: 'ORD' + (Date.now() - 100000).toString().substring(0, 10),
      total_amount: 2380,
      status: 'shipped',
      payment_method: 'cash_on_delivery',
      shipping_name: '李大華',
      shipping_phone: '0923456789',
      shipping_address: '民權路25號C棟18樓之20',
      created_at: new Date(Date.now() - 1000000).toISOString(),
      updated_at: new Date(Date.now() - 500000).toISOString(),
      items: [
        { product_name: '產品C', quantity: 1, price: 2380 }
      ]
    }
  ];
  
  console.log('已創建模擬訂單數據:', orders.value);
};

// 查看訂單詳情
const viewOrderDetail = (orderNumber: string) => {
  selectedOrderNumber.value = orderNumber;
  showOrderDetail.value = true;
  fetchOrderDetail(orderNumber);
};

// 獲取訂單詳情
const fetchOrderDetail = async (orderNumber: string) => {
  try {
    orderLoading.value = true;
    orderDetailHasError.value = false;
    orderDetail.value = null;
    
    // 檢查用戶是否登入
    const token = localStorage.getItem('access_token');
    if (!token) {
      message.error('請先登入');
      router.push('/login');
      return;
    }
    
    // 設置 API 請求的 headers
    const headers = {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    };
    
    console.log(`嘗試獲取訂單詳情: ${orderNumber}`);
    
    // 嘗試獲取訂單詳情
    let response = null;
    try {
      // 使用後端訂單詳情API
      response = await axios.get(`/api/shopping/orders/${orderNumber}/`, { 
        headers,
        baseURL: import.meta.env.VITE_API_BASE_URL
      });
      console.log('訂單詳情API請求成功:', response.data);
    } catch (firstError) {
      console.error('主要API路徑失敗:', firstError);
      
      try {
        // 嘗試使用另一個訂單詳情API路徑
        response = await axios.get(`/api/shopping/order-detail/${orderNumber}/`, { 
          headers,
          baseURL: import.meta.env.VITE_API_BASE_URL
        });
        console.log('備用API路徑成功:', response.data);
      } catch (secondError) {
        console.error('備用API路徑失敗:', secondError);
        
        // 再嘗試使用order_api_detail的API路徑
        try {
          response = await axios.get(`/api/shopping/order/${orderNumber}/detail/`, { 
            headers,
            baseURL: import.meta.env.VITE_API_BASE_URL
          });
          console.log('第三備用API路徑成功:', response.data);
        } catch (thirdError) {
          console.error('所有API路徑都失敗:', thirdError);
          // 查找匹配的訂單
          const matchedOrder = orders.value.find(order => order.order_number === orderNumber);
          if (matchedOrder) {
            orderDetail.value = { ...matchedOrder };
            message.warning('使用列表中的訂單數據作為詳情');
            orderLoading.value = false;
            return;
          } else {
            // 使用模擬數據
            useSimulatedOrderDetail(orderNumber);
            return;
          }
        }
      }
    }
    
    // 處理回應數據
    if (response && response.data) {
      console.log('處理訂單詳情:', response.data);
      
      if (response.data.success && response.data.data) {
        // 新格式API
        orderDetail.value = response.data.data;
        message.success('成功載入訂單詳情');
      } else if (typeof response.data === 'object' && !Array.isArray(response.data)) {
        // 單個訂單對象
        orderDetail.value = response.data;
        message.success('成功載入訂單詳情');
      } else {
        console.error('數據格式不正確:', response.data);
        orderDetailHasError.value = true;
        message.error('獲取訂單詳情失敗，數據格式不正確');
        useSimulatedOrderDetail(orderNumber);
      }
    } else {
      orderDetailHasError.value = true;
      message.error('獲取訂單詳情失敗，返回數據為空');
      useSimulatedOrderDetail(orderNumber);
    }
  } catch (error) {
    console.error('獲取訂單詳情發生錯誤:', error);
    orderDetailHasError.value = true;
    message.error('獲取訂單詳情時發生錯誤');
    
    // 使用模擬數據
    useSimulatedOrderDetail(orderNumber);
  } finally {
    orderLoading.value = false;
  }
};

// 使用模擬訂單詳情數據
const useSimulatedOrderDetail = (orderNumber: string) => {
  console.log('使用模擬訂單詳情數據');
  
  // 查找匹配的訂單
  const matchedOrder = orders.value.find(order => order.order_number === orderNumber);
  
  // 創建模擬訂單數據
  orderDetail.value = {
    order_number: orderNumber,
    order_date: matchedOrder?.created_at || new Date().toISOString(),
    total_amount: matchedOrder?.total_amount || 1999,
    status: matchedOrder?.status || '處理中',
    logistics_status: '配送中',
    payment_method: matchedOrder?.payment_method || '貨到付款',
    payment_status: '待付款',
    recipient_name: matchedOrder?.shipping_name || '模擬收件人',
    recipient_phone: matchedOrder?.shipping_phone || '0912345678',
    shipping_address: matchedOrder?.shipping_address || '模擬地址',
    items: matchedOrder?.items || [
      {
        id: 1,
        product_name: '模擬商品1',
        quantity: 2,
        price: 500,
        image: '/images/products/placeholder.jpg'
      },
      {
        id: 2,
        product_name: '模擬商品2',
        quantity: 1,
        price: 800,
        image: '/images/products/placeholder.jpg'
      }
    ]
  };
  
  message.warning('後端連線失敗，顯示模擬訂單資料');
  orderDetailHasError.value = true;
};

// 關閉訂單詳情
const closeOrderDetail = () => {
  showOrderDetail.value = false;
  orderDetail.value = null;
};

// 頁面載入時獲取訂單列表
onMounted(() => {
  console.log("訂單管理頁面已載入");
  // 立即創建模擬訂單數據，確保頁面有內容顯示
  createMockOrders();
  // 嘗試從API獲取真實訂單數據
  fetchUserOrders();
});
</script>

<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-2xl font-bold mb-6">訂單管理</h1>
    
    <!-- 載入中顯示 -->
    <template v-if="loading && orders.length === 0">
      <div class="flex flex-col items-center justify-center py-12">
        <n-spin size="large" />
        <p class="mt-4 text-gray-600">載入訂單資料中...</p>
      </div>
    </template>
    
    <!-- 錯誤顯示 -->
    <template v-if="hasError">
      <div class="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-4">
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-amber-400" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="ml-3">
            <h3 class="text-sm font-medium text-amber-800">
              資料載入失敗
            </h3>
            <div class="mt-2 text-sm text-amber-700">
              <p>無法連接到訂單系統，目前顯示的是模擬數據。</p>
            </div>
            <div class="mt-4">
              <div class="-mx-2 -my-1.5 flex">
                <button
                  type="button"
                  @click="fetchUserOrders"
                  class="bg-amber-50 px-2 py-1.5 rounded-md text-sm font-medium text-amber-800 hover:bg-amber-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-amber-600"
                >
                  重新嘗試
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
    
    <!-- 無訂單顯示 -->
    <template v-if="!loading && orders.length === 0">
      <div class="bg-white rounded-lg shadow p-8 flex flex-col items-center">
        <n-empty description="尚未有任何訂單">
          <template #extra>
            <n-button @click="router.push('/mall')">
              去購物
            </n-button>
          </template>
        </n-empty>
      </div>
    </template>
    
    <!-- 訂單列表 -->
    <template v-if="orders.length > 0">
      <div class="bg-white rounded-lg shadow-sm mb-6 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  訂單編號
                </th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  下單日期
                </th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  訂單狀態
                </th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider hidden sm:table-cell">
                  付款方式
                </th>
                <th scope="col" class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  總金額
                </th>
                <th scope="col" class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  操作
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="order in orders" :key="order.id || order.order_number" class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm font-medium text-gray-900">{{ order.order_number }}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm text-gray-500">{{ formatDate(order.created_at) }}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <n-tag :type="getStatusType(order.status)">
                    {{ formatOrderStatus(order.status) }}
                  </n-tag>
                </td>
                <td class="px-6 py-4 whitespace-nowrap hidden sm:table-cell">
                  <div class="text-sm text-gray-500">{{ formatPaymentMethod(order.payment_method) }}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-right">
                  <div class="text-sm font-medium text-orange-600">NT$ {{ order.total_amount }}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-right text-sm">
                  <n-button size="small" type="primary" class="ml-2" @click="viewOrderDetail(order.order_number)">
                    查看
                  </n-button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      
      <!-- 訂單列表 (手機版) -->
      <div class="block md:hidden space-y-4">
        <n-card v-for="order in orders" :key="order.id || order.order_number" class="mb-4">
          <template #header>
            <div class="flex justify-between items-center">
              <span class="font-medium">訂單編號: {{ order.order_number }}</span>
              <n-tag :type="getStatusType(order.status)">
                {{ formatOrderStatus(order.status) }}
              </n-tag>
            </div>
          </template>
          
          <div class="space-y-2">
            <div class="flex justify-between">
              <span class="text-gray-500">下單時間</span>
              <span>{{ formatDate(order.created_at) }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-500">付款方式</span>
              <span>{{ formatPaymentMethod(order.payment_method) }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-500">總金額</span>
              <span class="font-medium text-orange-600">NT$ {{ order.total_amount }}</span>
            </div>
          </div>
          
          <template #footer>
            <div class="flex justify-end">
              <n-button size="small" type="primary" class="ml-2" @click="viewOrderDetail(order.order_number)">
                查看訂單詳情
              </n-button>
            </div>
          </template>
        </n-card>
      </div>
      
      <!-- 訂單詳情模態框 -->
      <n-modal
        v-model:show="showOrderDetail"
        preset="card"
        class="max-w-4xl"
        title="訂單詳情"
        size="huge"
        segmented
        :bordered="false"
        :closable="true"
        :mask-closable="true"
        @close="closeOrderDetail"
      >
        <!-- 載入中顯示 -->
        <div v-if="orderLoading" class="flex flex-col items-center justify-center py-12">
          <n-spin size="large" />
          <p class="mt-4 text-gray-600">載入訂單詳情中...</p>
        </div>
        
        <!-- 錯誤顯示 -->
        <template v-else-if="orderDetailHasError">
          <n-alert
            type="warning"
            title="無法連接訂單系統"
            :bordered="false"
            class="mb-4"
          >
            <template #icon>
              <n-icon><WarningOutline /></n-icon>
            </template>
            <p>目前顯示的是模擬資料，可能與實際訂單不符</p>
          </n-alert>
          
          <!-- 即使有錯誤，也顯示模擬數據 -->
          <OrderDetailContent 
            v-if="orderDetail" 
            :orderDetail="orderDetail" 
            :isSimulated="true" 
            @reloadOrder="fetchOrderDetail(selectedOrderNumber)" 
          />
        </template>
        
        <!-- 訂單不存在 -->
        <template v-else-if="!orderDetail && !orderLoading">
          <div class="flex items-center justify-center flex-col py-12">
            <n-icon size="64" class="text-error mb-4">
              <CloseCircleOutline />
            </n-icon>
            <p class="text-xl text-gray-700 mb-2">找不到訂單資料</p>
            <p class="text-gray-500 mb-6">無法找到訂單號 {{ selectedOrderNumber }} 的相關資訊</p>
            <n-button type="primary" @click="closeOrderDetail">關閉</n-button>
          </div>
        </template>
        
        <!-- 訂單詳情內容 -->
        <OrderDetailContent 
          v-else-if="orderDetail" 
          :orderDetail="orderDetail" 
          :isSimulated="orderDetailHasError" 
          @reloadOrder="fetchOrderDetail(selectedOrderNumber)" 
        />
      </n-modal>
    </template>
    
    <!-- 調試信息 -->
    <div v-if="import.meta.env.DEV" class="mt-8 p-4 bg-gray-100 text-xs">
      <h3 class="font-bold">調試信息</h3>
      <div>載入狀態: {{ loading ? '載入中' : '已完成' }}</div>
      <div>錯誤狀態: {{ hasError ? '有錯誤' : '無錯誤' }}</div>
      <div>訂單數量: {{ orders.length }}</div>
    </div>
  </div>
</template>

<style scoped>
.orders-container {
  max-width: 1200px;
  margin: 0 auto;
}
</style> 
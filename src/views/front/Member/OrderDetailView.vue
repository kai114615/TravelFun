<script setup lang="ts">
import { ref, onMounted, h, watch, computed } from 'vue';
import { NCard, NEmpty, NTag, NButton, NSpace, useMessage, NBreadcrumb, NBreadcrumbItem, NSpin, NDataTable, NIcon } from 'naive-ui';
import { useRoute, useRouter } from 'vue-router';
import api from '@/api/config';
import axios from 'axios';
import { WarningOutline, AlertCircleOutline, ImageOutline, CloseCircleOutline, ArrowForwardOutline, BagCheckOutline } from '@vicons/ionicons5';
import OrderDetailContent from '@/components/Order/OrderDetailContent.vue';

const message = useMessage();
const route = useRoute();
const router = useRouter();
const orderNumber = computed(() => route.params.orderNumber || route.query.order_number);
const orderLoading = ref(false);
const orderNotFound = ref(false);
const orderDetail = ref(null);
const hasError = ref(false);
const fromCheckout = computed(() => route.query.from_checkout === 'true');

// 創建商品表格的列定義
const columns = [
  {
    title: '商品',
    key: 'product',
    render: (row) => {
      return h('div', { class: 'flex items-center' }, [
        h('div', { class: 'w-12 h-12 bg-gray-200 rounded overflow-hidden mr-3' }, [
          h('img', { src: row.product_image || '/placeholder-image.png', alt: row.product_name, class: 'w-full h-full object-cover' })
        ]),
        h('div', [
          h('p', { class: 'font-medium' }, row.product_name)
        ])
      ]);
    }
  },
  {
    title: '單價',
    key: 'price',
    render: (row) => `NT$ ${row.price}`
  },
  {
    title: '數量',
    key: 'quantity'
  },
  {
    title: '小計',
    key: 'subtotal',
    render: (row) => `NT$ ${row.price * row.quantity}`
  }
];

// 格式化訂單狀態
const formatOrderStatus = (status) => {
  const statusMap = {
    'pending': '處理中',
    'processing': '處理中',
    'shipped': '已出貨',
    'delivered': '已送達',
    'completed': '已完成',
    'cancelled': '已取消',
    'refunded': '已退款',
    'pending_payment': '待付款',
    'paid': '已付款'
  };
  return statusMap[status] || status;
};

// 獲取狀態對應的類型
const getStatusType = (status) => {
  const typeMap = {
    'pending': 'warning',
    'paid': 'success',
    'shipped': 'info',
    'completed': 'success',
    'cancelled': 'error',
    'payment_failed': 'error'
  };
  return typeMap[status] || 'default';
};

// 格式化物流狀態
const formatLogisticsStatus = (status) => {
  const statusMap = {
    'waiting': '準備中',
    'processing': '處理中',
    'shipping': '運送中',
    'delivered': '已送達',
    'failed': '配送失敗'
  };
  return statusMap[status] || status;
};

// 格式化付款方式
const formatPaymentMethod = (method) => {
  const methodMap = {
    'cash_on_delivery': '貨到付款',
    'credit_card': '信用卡',
    'atm': 'ATM轉帳',
    'ecpay': '綠界支付'
  };
  return methodMap[method] || method;
};

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString('zh-TW', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
};

// 獲取物流事件的方法
const logisticsEvents = computed(() => {
  if (!orderDetail.value || !orderDetail.value.logistics_info) return [];
  
  try {
    const logisticsInfo = typeof orderDetail.value.logistics_info === 'string' 
      ? JSON.parse(orderDetail.value.logistics_info) 
      : orderDetail.value.logistics_info;
    
    if (logisticsInfo.tracking_events && Array.isArray(logisticsInfo.tracking_events)) {
      return logisticsInfo.tracking_events;
    }
    
    return [];
  } catch (error) {
    console.error('解析物流信息錯誤:', error);
    return [];
  }
});

// 獲取訂單詳情
const fetchOrderDetail = async () => {
  try {
    orderLoading.value = true;
    orderNotFound.value = false;
    hasError.value = false;
    
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
    
    // 獲取訂單號
    const currentOrderNumber = orderNumber.value;
    if (!currentOrderNumber) {
      message.error('訂單號不存在');
      router.push('/member/orders');
      return;
    }
    
    console.log(`嘗試獲取訂單詳情: ${currentOrderNumber}`);
    
    // 嘗試獲取訂單詳情
    let response = null;
    try {
      // 使用相對路徑加上baseURL參數
      response = await axios.get(`/api/shopping/orders/${currentOrderNumber}/`, { 
        headers,
        baseURL: import.meta.env.VITE_API_BASE_URL
      });
      console.log('訂單詳情API請求成功:', response.data);
    } catch (firstError) {
      console.error('主要API路徑失敗:', firstError);
      
      try {
        response = await axios.get(`/api/shopping/orders/detail/${currentOrderNumber}/`, { 
          headers,
          baseURL: import.meta.env.VITE_API_BASE_URL
        });
        console.log('備用API路徑成功:', response.data);
      } catch (secondError) {
        console.error('備用API路徑失敗:', secondError);
        
        // 如果用戶訂單ID存在於localStorage，則創建模擬數據
        useSimulatedOrderDetail(currentOrderNumber);
        return;
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
        hasError.value = true;
        message.error('獲取訂單詳情失敗，數據格式不正確');
        useSimulatedOrderDetail(currentOrderNumber);
      }
    } else {
      hasError.value = true;
      message.error('獲取訂單詳情失敗，返回數據為空');
      useSimulatedOrderDetail(currentOrderNumber);
    }
  } catch (error) {
    console.error('獲取訂單詳情發生錯誤:', error);
    hasError.value = true;
    message.error('獲取訂單詳情時發生錯誤');
    
    // 使用模擬數據
    useSimulatedOrderDetail(orderNumber.value);
  } finally {
    orderLoading.value = false;
  }
};

// 如果API失敗，使用模擬訂單詳情數據
const useSimulatedOrderDetail = (orderNumber) => {
  console.log('使用模擬訂單詳情數據');
  
  // 從localStorage獲取上次訂單，作為模擬數據的基礎
  const lastOrderStr = localStorage.getItem('lastOrder');
  let baseOrder = null;
  
  if (lastOrderStr) {
    try {
      baseOrder = JSON.parse(lastOrderStr);
      console.log('已找到上次訂單資料作為模擬基礎:', baseOrder);
    } catch (e) {
      console.error('解析上次訂單資料失敗:', e);
    }
  }
  
  // 創建模擬訂單數據
  orderDetail.value = {
    order_number: orderNumber || 'SIM' + Math.floor(Math.random() * 1000000),
    order_date: new Date().toISOString(),
    total_amount: baseOrder?.total_amount || Math.floor(Math.random() * 10000) + 800,
    status: '處理中',
    logistics_status: '配送中',
    payment_method: '貨到付款',
    payment_status: '待付款',
    recipient_name: baseOrder?.recipient_name || '模擬收件人',
    recipient_phone: baseOrder?.recipient_phone || '0912345678',
    shipping_address: baseOrder?.shipping_address || '模擬地址',
    items: baseOrder?.items || [
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
  hasError.value = true;
};

// 前往付款
const goToPayment = () => {
  message.info('目前為貨到付款方式，無需線上支付');
};

// 確認收貨
const confirmDelivery = async () => {
  try {
    if (!orderDetail.value || !orderDetail.value.id) {
      message.error('訂單資訊不完整，無法確認收貨');
      return;
    }
    
    message.loading('正在處理確認收貨...');
    
    const token = localStorage.getItem('access_token');
    if (!token) {
      message.error('請先登入');
      return;
    }
    
    const response = await axios.post(
      `${import.meta.env.VITE_API_BASE_URL}/api/shopping/orders/${orderDetail.value.id}/confirm-delivery/`,
      {},
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      }
    );
    
    if (response.data && response.data.success) {
      message.success('已確認收貨');
      orderDetail.value.status = 'completed';
    } else {
      message.error(response.data?.message || '確認收貨失敗');
    }
  } catch (error) {
    console.error('確認收貨錯誤:', error);
    message.error('確認收貨失敗，請稍後再試');
  }
};

// 物流事件類型
const getLogisticsEventType = (status) => {
  if (status.includes('收貨') || status.includes('完成') || status.includes('送達')) {
    return 'success';
  }
  if (status.includes('問題') || status.includes('延遲') || status.includes('退回')) {
    return 'error';
  }
  return 'info';
};

// 頁面載入時獲取訂單詳情
onMounted(() => {
  fetchOrderDetail();
});

// 路由更新時重新獲取訂單詳情
watch(() => route.params.orderNumber || route.query.order_number, (newValue) => {
  if (newValue && newValue !== orderNumber.value) {
    orderNumber.value = newValue;
    fetchOrderDetail();
  }
});
</script>

<template>
  <div class="bg-gray-50 min-h-screen pt-8 pb-16">
    <div class="container mx-auto px-4">
      <!-- 麵包屑導航 -->
      <div class="mb-6">
        <div class="text-sm text-gray-600 mb-1">
          <router-link to="/" class="hover:text-primary transition">首頁</router-link>
          <span class="mx-2">/</span>
          <router-link to="/member/orders" class="hover:text-primary transition">訂單管理</router-link>
          <span class="mx-2">/</span>
          <span class="text-gray-800">訂單詳情</span>
        </div>
        <h1 class="text-2xl font-bold text-gray-900">訂單詳情</h1>
      </div>
      
      <!-- 訂單成功提示 -->
      <div v-if="fromCheckout" class="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
        <div class="flex items-center">
          <div class="flex-shrink-0 bg-green-100 rounded-full p-2">
            <n-icon class="text-green-600" size="24">
              <BagCheckOutline />
            </n-icon>
          </div>
          <div class="ml-3">
            <h3 class="text-lg font-medium text-green-800">訂單已成功提交！</h3>
            <div class="mt-2 text-sm text-green-700">
              <p>感謝您的購買，我們將盡快處理您的訂單。您可以在此頁面查看訂單詳情及追蹤物流狀態。</p>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 載入中狀態 -->
      <div v-if="orderLoading" class="py-12 flex justify-center">
        <n-spin size="large" />
        <span class="ml-3 text-gray-600">載入訂單詳情中...</span>
      </div>
      
      <!-- 錯誤提示 -->
      <template v-else-if="hasError">
        <div class="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div class="flex items-center justify-center flex-col py-8">
            <n-icon size="48" class="text-warning mb-4">
              <WarningOutline />
            </n-icon>
            <p class="text-lg text-gray-700 mb-2">無法連接訂單系統</p>
            <p class="text-gray-500 mb-4">目前顯示的是模擬資料，可能與實際訂單不符</p>
            <n-button type="primary" @click="fetchOrderDetail">重新載入</n-button>
          </div>
        </div>
        
        <!-- 即使有錯誤，也顯示模擬數據 -->
        <OrderDetailContent 
          v-if="orderDetail" 
          :orderDetail="orderDetail" 
          :isSimulated="true" 
          @reloadOrder="fetchOrderDetail" 
        />
      </template>
      
      <!-- 訂單不存在 -->
      <template v-else-if="!orderDetail && !orderLoading">
        <div class="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div class="flex items-center justify-center flex-col py-12">
            <n-icon size="64" class="text-error mb-4">
              <CloseCircleOutline />
            </n-icon>
            <p class="text-xl text-gray-700 mb-2">找不到訂單資料</p>
            <p class="text-gray-500 mb-6">無法找到訂單號 {{ orderNumber }} 的相關資訊</p>
            <n-button type="primary" @click="router.push('/member/orders')">返回訂單列表</n-button>
          </div>
        </div>
      </template>
      
      <!-- 訂單詳情內容 -->
      <OrderDetailContent 
        v-else-if="orderDetail" 
        :orderDetail="orderDetail" 
        :isSimulated="hasError" 
        @reloadOrder="fetchOrderDetail" 
      />
    </div>
  </div>
</template>

<style scoped>
.order-detail-container {
  max-width: 1200px;
  margin: 0 auto;
}
</style> 
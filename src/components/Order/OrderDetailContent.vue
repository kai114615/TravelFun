<template>
  <div class="bg-white rounded-lg shadow-sm overflow-hidden">
    <!-- 訂單頭部信息 -->
    <div class="p-6 border-b border-gray-200">
      <div class="flex flex-wrap justify-between items-center">
        <div>
          <h2 class="text-xl font-bold">訂單編號：{{ orderDetail.order_number }}</h2>
          <p class="text-gray-500 mt-1">下單時間：{{ formatDate(orderDetail.order_date || orderDetail.created_at) }}</p>
        </div>
        
        <div class="mt-3 sm:mt-0 flex items-center space-x-2">
          <n-tag v-if="isSimulated" type="warning" size="small">模擬數據</n-tag>
          <n-tag size="medium" :type="getStatusType(orderDetail.status)">
            {{ formatOrderStatus(orderDetail.status) }}
          </n-tag>
        </div>
      </div>
    </div>
    
    <!-- 訂單內容 -->
    <div class="p-6 grid grid-cols-1 md:grid-cols-2 gap-8">
      <!-- 左側：訂單信息 -->
      <div>
        <h3 class="text-lg font-medium mb-4">訂單信息</h3>
        
        <div class="space-y-3">
          <div class="flex border-b border-gray-100 pb-2">
            <div class="w-32 text-gray-500">付款方式</div>
            <div class="flex-1 font-medium">{{ formatPaymentMethod(orderDetail.payment_method) }}</div>
          </div>
          
          <div class="flex border-b border-gray-100 pb-2">
            <div class="w-32 text-gray-500">訂單狀態</div>
            <div class="flex-1 font-medium">{{ formatOrderStatus(orderDetail.status) }}</div>
          </div>
          
          <div class="flex border-b border-gray-100 pb-2">
            <div class="w-32 text-gray-500">訂單總額</div>
            <div class="flex-1 font-medium text-orange-600">NT${{ orderDetail.total_amount }}</div>
          </div>
          
          <div v-if="orderDetail.logistics_id" class="flex border-b border-gray-100 pb-2">
            <div class="w-32 text-gray-500">物流單號</div>
            <div class="flex-1 font-medium">{{ orderDetail.logistics_id }}
              <n-tag v-if="orderDetail.logistics_status" size="small" type="info" class="ml-2">
                {{ formatLogisticsStatus(orderDetail.logistics_status) }}
              </n-tag>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 右側：收件信息 -->
      <div>
        <h3 class="text-lg font-medium mb-4">收件信息</h3>
        
        <div class="space-y-3">
          <div class="flex border-b border-gray-100 pb-2">
            <div class="w-32 text-gray-500">收件人</div>
            <div class="flex-1 font-medium">{{ orderDetail.recipient_name || orderDetail.shipping_name }}</div>
          </div>
          
          <div class="flex border-b border-gray-100 pb-2">
            <div class="w-32 text-gray-500">聯絡電話</div>
            <div class="flex-1 font-medium">{{ orderDetail.recipient_phone || orderDetail.shipping_phone }}</div>
          </div>
          
          <div class="flex border-b border-gray-100 pb-2">
            <div class="w-32 text-gray-500">收件地址</div>
            <div class="flex-1 font-medium">{{ orderDetail.shipping_address }}</div>
          </div>
          
          <div v-if="orderDetail.shipping_note" class="flex border-b border-gray-100 pb-2">
            <div class="w-32 text-gray-500">訂單備註</div>
            <div class="flex-1 font-medium">{{ orderDetail.shipping_note }}</div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 物流追蹤 -->
    <div v-if="hasLogisticsInfo" class="px-6 py-4 border-t border-gray-200">
      <h3 class="text-lg font-medium mb-4">物流追蹤</h3>
      
      <n-timeline>
        <n-timeline-item v-for="(event, index) in logisticsEvents" :key="index" :type="getLogisticsEventType(event.status)">
          <div class="font-medium">{{ event.status }}</div>
          <div class="text-sm text-gray-500">
            {{ formatDate(event.time) }}
            <span v-if="event.location">• {{ event.location }}</span>
          </div>
          <div v-if="event.description" class="text-sm mt-1">{{ event.description }}</div>
        </n-timeline-item>
      </n-timeline>
    </div>
    
    <!-- 訂單商品列表 -->
    <div class="px-6 py-6 border-t border-gray-200">
      <h3 class="text-lg font-medium mb-4">訂單商品</h3>
      
      <table class="w-full border-collapse">
        <thead>
          <tr class="border-b border-gray-200">
            <th class="text-left pb-3">商品</th>
            <th class="text-right pb-3 hidden md:table-cell">單價</th>
            <th class="text-right pb-3 hidden md:table-cell">數量</th>
            <th class="text-right pb-3">小計</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in orderDetail.items" :key="item.id" class="border-b border-gray-100">
            <td class="py-4">
              <div class="flex items-center">
                <div class="w-16 h-16 bg-gray-100 rounded-md overflow-hidden mr-3">
                  <img 
                    v-if="item.product_image || item.image" 
                    :src="item.product_image || item.image" 
                    alt="商品圖片" 
                    class="w-full h-full object-cover" 
                  />
                  <div v-else class="w-full h-full flex items-center justify-center bg-gray-200">
                    <n-icon><ImageOutline /></n-icon>
                  </div>
                </div>
                <div>
                  <p class="font-medium">{{ item.product_name }}</p>
                  <p class="text-xs text-gray-500 md:hidden">
                    {{ item.quantity }} 件 × NT${{ item.price }}
                  </p>
                </div>
              </div>
            </td>
            <td class="py-4 text-right hidden md:table-cell">NT${{ item.price }}</td>
            <td class="py-4 text-right hidden md:table-cell">{{ item.quantity }}</td>
            <td class="py-4 text-right">NT${{ item.subtotal || item.price * item.quantity }}</td>
          </tr>
        </tbody>
        <tfoot>
          <tr>
            <td colspan="3" class="pt-4 text-right font-medium">訂單總計</td>
            <td class="pt-4 text-right font-bold text-lg">NT${{ orderDetail.total_amount }}</td>
          </tr>
        </tfoot>
      </table>
    </div>
    
    <!-- 操作按鈕 -->
    <div class="flex justify-end p-6 border-t border-gray-200 gap-4">
      <n-button @click="router.push('/member/orders')">
        返回訂單列表
      </n-button>
      
      <template v-if="orderDetail.status === 'pending_payment'">
        <n-button type="primary" @click="goToPayment">
          前往付款
        </n-button>
      </template>
      
      <template v-if="orderDetail.status === 'shipped' && orderDetail.logistics_status === 'delivered'">
        <n-button type="success" @click="confirmDelivery">
          確認收貨
        </n-button>
      </template>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import { ImageOutline } from '@vicons/ionicons5';

const router = useRouter();

// 定義props
const props = defineProps({
  orderDetail: {
    type: Object,
    required: true
  },
  isSimulated: {
    type: Boolean,
    default: false
  }
});

// 定義emit
const emit = defineEmits(['reloadOrder']);

// 計算物流信息是否存在
const hasLogisticsInfo = computed(() => {
  if (!props.orderDetail.logistics_info) return false;
  
  let logisticsInfo;
  try {
    if (typeof props.orderDetail.logistics_info === 'string') {
      logisticsInfo = JSON.parse(props.orderDetail.logistics_info);
    } else {
      logisticsInfo = props.orderDetail.logistics_info;
    }
    
    return logisticsInfo && logisticsInfo.tracking_events && 
      Array.isArray(logisticsInfo.tracking_events) && 
      logisticsInfo.tracking_events.length > 0;
  } catch (e) {
    console.error('解析物流信息失敗:', e);
    return false;
  }
});

// 獲取物流追蹤事件
const logisticsEvents = computed(() => {
  if (!hasLogisticsInfo.value) return [];
  
  try {
    let logisticsInfo;
    if (typeof props.orderDetail.logistics_info === 'string') {
      logisticsInfo = JSON.parse(props.orderDetail.logistics_info);
    } else {
      logisticsInfo = props.orderDetail.logistics_info;
    }
    
    return logisticsInfo.tracking_events || [];
  } catch (e) {
    console.error('獲取物流事件失敗:', e);
    return [];
  }
});

// 格式化函數 - 訂單狀態
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

// 格式化函數 - 物流狀態
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

// 格式化函數 - 支付方式
const formatPaymentMethod = (method) => {
  const methodMap = {
    'cash_on_delivery': '貨到付款',
    'credit_card': '信用卡',
    'atm': 'ATM轉帳',
    'ecpay': '綠界支付'
  };
  return methodMap[method] || method;
};

// 格式化函數 - 日期
const formatDate = (dateStr) => {
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

// 獲取訂單狀態的Tag類型
const getStatusType = (status) => {
  const typeMap = {
    'pending': 'warning',
    'processing': 'info',
    'shipped': 'success',
    'delivered': 'success',
    'completed': 'success',
    'cancelled': 'error',
    'refunded': 'warning',
    'pending_payment': 'warning',
    'paid': 'success'
  };
  return typeMap[status] || 'default';
};

// 獲取物流事件的類型
const getLogisticsEventType = (status) => {
  const typeMap = {
    '訂單處理中': 'info',
    '包裹已出貨': 'success',
    '運送中': 'info',
    '已送達': 'success',
    '配送失敗': 'error'
  };
  return typeMap[status] || 'default';
};

// 前往付款
const goToPayment = () => {
  console.log('前往付款');
  // 實作付款邏輯
};

// 確認收貨
const confirmDelivery = () => {
  console.log('確認收貨');
  // 實作確認收貨邏輯
};
</script> 
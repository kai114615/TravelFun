<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage, ElLoading } from 'element-plus';
import api from '@/api/config';

const route = useRoute();
const router = useRouter();
const orderId = ref(route.query.orderId as string);
const orderNumber = ref(route.query.orderNumber as string);

// 支付狀態
const paymentStatus = reactive({
  isLoading: false,
  isSubmitting: false,
  errorMessage: '',
  htmlForm: '',
});

// 訂單詳情
const orderDetails = ref({
  id: '',
  order_number: '',
  total_amount: 0,
  items: [],
  shipping_info: {
    name: '',
    phone: '',
    address: '',
  },
  status: '',
  created_at: '',
});

// 測試卡號資訊
const testCardInfo = [
  {
    type: '一般信用卡',
    numbers: [
      { card: '4311-9511-1111-1111', note: '安全碼: 任意三碼' },
      { card: '4311-9522-2222-2222', note: '安全碼: 任意三碼' },
    ]
  },
  {
    type: '海外信用卡',
    numbers: [
      { card: '4000-2011-1111-1111', note: '安全碼: 任意三碼' },
    ]
  },
  {
    type: '美國運通信用卡',
    numbers: [
      { card: '3403-532780-80900', note: '國內卡' },
      { card: '3712-222222-22222', note: '國外卡' },
    ]
  },
  {
    type: '圓夢彈性分期信用卡',
    numbers: [
      { card: '4938-1777-7777-7777', note: '安全碼: 任意三碼' },
    ]
  },
];

// 格式化金額
function formatPrice(price: number) {
  return new Intl.NumberFormat('zh-TW', {
    style: 'currency',
    currency: 'TWD',
    minimumFractionDigits: 0
  }).format(price);
}

// 複製到剪貼板
function copyToClipboard(text: string) {
  navigator.clipboard.writeText(text)
    .then(() => {
      ElMessage.success('已複製到剪貼板');
    })
    .catch(() => {
      ElMessage.error('複製失敗，請手動複製');
    });
}

// 載入訂單詳情
async function loadOrderDetails() {
  try {
    if (!orderId.value && !orderNumber.value) {
      ElMessage.error('找不到訂單資訊');
      router.push('/');
      return;
    }
    
    const loading = ElLoading.service({ 
      fullscreen: true,
      text: '載入訂單資訊中...'
    });
    
    const query = orderId.value ? `?order_id=${orderId.value}` : 
                 orderNumber.value ? `?order_number=${orderNumber.value}` : '';
    
    const response = await api.get(`/shop/api/shopping/orders/detail/${query}`);
    if (response.data.status === 'success') {
      orderDetails.value = response.data.data;
      
      // 獲取訂單ID和編號，如果未在URL中提供
      if (!orderId.value) orderId.value = orderDetails.value.id;
      if (!orderNumber.value) orderNumber.value = orderDetails.value.order_number;
      
      // 立即載入綠界金流表單
      await loadECPayForm();
    } else {
      throw new Error(response.data.message || '無法載入訂單詳情');
    }
    
    loading.close();
  } catch (error) {
    ElMessage.error(`載入訂單詳情失敗: ${error.message}`);
    router.push('/');
  }
}

// 載入綠界金流表單
async function loadECPayForm() {
  try {
    paymentStatus.isLoading = true;
    paymentStatus.errorMessage = '';
    
    const ecpayPaymentData = {
      order_id: orderId.value,
      frontend_domain: window.location.origin
    };
    
    console.log('綠界金流請求數據:', ecpayPaymentData);
    
    let ecpayResponse;
    try {
      // 嘗試主要的綠界金流API路徑
      ecpayResponse = await api.post('/shop/api/shopping/ecpay/payment/', ecpayPaymentData);
      console.log('綠界金流回應 (主要路徑):', ecpayResponse.data);
    } catch (ecpayApiError) {
      console.error('主要綠界API路徑失敗:', ecpayApiError);
      
      // 嘗試其他可能的路徑
      const possiblePaths = [
        '/api/shopping/ecpay/payment/',
        '/shop/api/ecpay/payment/',
        '/api/ecpay/payment/'
      ];
      
      let success = false;
      for (const path of possiblePaths) {
        console.log(`嘗試綠界路徑: ${path}`);
        try {
          ecpayResponse = await api.post(path, ecpayPaymentData);
          console.log(`綠界路徑 ${path} 成功:`, ecpayResponse.data);
          success = true;
          break;
        } catch (err) {
          console.error(`綠界路徑 ${path} 失敗:`, err);
        }
      }
      
      if (!success) {
        throw new Error('所有綠界API路徑都失敗');
      }
    }
    
    if (ecpayResponse.data.success) {
      // 儲存綠界支付表單HTML
      paymentStatus.htmlForm = ecpayResponse.data.html_form;
      console.log('獲得綠界HTML表單', paymentStatus.htmlForm.substring(0, 100) + '...');
    } else {
      throw new Error(ecpayResponse.data.message || '無法載入支付頁面');
    }
  } catch (error) {
    console.error('綠界支付請求失敗:', error);
    paymentStatus.errorMessage = `無法載入綠界支付: ${error.message}`;
  } finally {
    paymentStatus.isLoading = false;
  }
}

// 提交綠界支付表單
function submitECPayForm() {
  try {
    paymentStatus.isSubmitting = true;
    ElMessage.info('正在跳轉至綠界金流支付頁面...');
    
    // 創建一個臨時的容器來放置表單
    const formContainer = document.createElement('div');
    formContainer.innerHTML = paymentStatus.htmlForm;
    
    // 取得表單元素
    const form = formContainer.querySelector('form');
    if (form) {
      // 將表單添加到文檔中（但隱藏起來）
      form.style.display = 'none';
      document.body.appendChild(form);
      
      // 提交表單
      form.submit();
      console.log('綠界支付表單已提交');
    } else {
      throw new Error('找不到綠界支付表單');
    }
  } catch (error) {
    console.error('提交綠界支付表單失敗:', error);
    paymentStatus.errorMessage = `無法提交支付: ${error.message}`;
    paymentStatus.isSubmitting = false;
    ElMessage.error('無法提交支付，請稍後再試');
  }
}

// 取消付款返回訂單頁面
function cancelPayment() {
  router.push({
    name: 'OrderComplete',
    params: { orderNumber: orderNumber.value }
  });
}

// 頁面加載時獲取訂單資訊
onMounted(() => {
  loadOrderDetails();
});
</script>

<template>
  <div class="container mx-auto px-4 py-8">
    <div class="max-w-4xl mx-auto">
      <!-- 頁面標題 -->
      <h1 class="text-2xl font-bold mb-8 text-center">
        綠界金流支付
      </h1>
      
      <!-- 主要內容區 -->
      <div class="bg-white rounded-lg shadow-lg overflow-hidden">
        <!-- 訂單資訊 -->
        <div class="p-6 bg-gray-50 border-b">
          <h2 class="text-xl font-bold mb-4">訂單資訊</h2>
          <div class="flex justify-between mb-2">
            <span class="text-gray-600">訂單編號:</span>
            <span class="font-medium">{{ orderNumber }}</span>
          </div>
          <div class="flex justify-between mb-2">
            <span class="text-gray-600">訂單金額:</span>
            <span class="font-medium text-green-600">{{ formatPrice(orderDetails.total_amount) }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-600">購買商品:</span>
            <span class="font-medium">共 {{ orderDetails.items?.length || 0 }} 件商品</span>
          </div>
        </div>
        
        <!-- 載入中狀態 -->
        <div v-if="paymentStatus.isLoading" class="p-10 text-center">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-green-500 mx-auto mb-4"></div>
          <p class="text-gray-600">載入綠界金流付款資訊中，請稍候...</p>
        </div>
        
        <!-- 錯誤訊息 -->
        <div v-else-if="paymentStatus.errorMessage" class="p-10 text-center">
          <div class="bg-red-100 text-red-600 p-4 rounded-lg mb-4">
            <i class="fas fa-exclamation-circle mr-2"></i>
            {{ paymentStatus.errorMessage }}
          </div>
          <button 
            @click="loadECPayForm" 
            class="bg-blue-600 text-white py-2 px-6 rounded-lg hover:bg-blue-700 transition-colors"
          >
            <i class="fas fa-sync-alt mr-2"></i>重新載入
          </button>
        </div>
        
        <!-- 支付表單 -->
        <div v-else class="p-6">
          <!-- 信用卡測試資訊 -->
          <div class="mb-8 p-4 bg-blue-50 rounded-lg">
            <h3 class="font-bold text-blue-800 mb-3 flex items-center">
              <i class="fas fa-info-circle mr-2"></i>
              測試環境信用卡資訊
            </h3>
            <div class="grid md:grid-cols-2 gap-4">
              <div v-for="(category, index) in testCardInfo" :key="index" class="bg-white p-3 rounded shadow-sm">
                <h4 class="font-medium text-gray-800 mb-2">{{ category.type }}</h4>
                <ul class="space-y-2">
                  <li v-for="(card, cardIndex) in category.numbers" :key="cardIndex" class="flex justify-between">
                    <div class="flex-1">
                      <span class="font-mono text-green-700">{{ card.card }}</span>
                      <span class="block text-xs text-gray-500">{{ card.note }}</span>
                    </div>
                    <button 
                      @click="copyToClipboard(card.card.replace(/-/g, ''))" 
                      class="text-blue-600 text-sm hover:text-blue-800"
                    >
                      <i class="far fa-copy"></i>
                    </button>
                  </li>
                </ul>
              </div>
            </div>
            
            <div class="mt-4 text-sm text-gray-600">
              <p>以上卡號僅用於綠界金流測試環境，實際交易將使用正式的支付處理系統。</p>
            </div>
          </div>
          
          <!-- 支付按鈕 -->
          <div class="text-center space-y-4">
            <p class="text-gray-600 mb-4">點擊下方按鈕將跳轉至綠界金流付款頁面，請依照指示完成付款</p>
            
            <button 
              @click="submitECPayForm" 
              class="bg-green-600 text-white py-3 px-8 rounded-lg hover:bg-green-700 transition-colors font-medium w-full md:w-auto"
              :disabled="paymentStatus.isSubmitting"
              :class="{'opacity-50 cursor-not-allowed': paymentStatus.isSubmitting}"
            >
              <i class="fas fa-credit-card mr-2"></i>
              {{ paymentStatus.isSubmitting ? '處理中...' : '前往綠界金流支付' }}
            </button>
            
            <button 
              @click="cancelPayment" 
              class="bg-gray-200 text-gray-800 py-3 px-8 rounded-lg hover:bg-gray-300 transition-colors mt-2 w-full md:w-auto"
              :disabled="paymentStatus.isSubmitting"
            >
              取消付款
            </button>
          </div>
          
          <!-- 支付保障說明 -->
          <div class="mt-8 border-t pt-6">
            <div class="flex flex-col md:flex-row justify-center items-center gap-6 text-center">
              <div class="flex items-center">
                <i class="fas fa-shield-alt text-2xl text-gray-500 mr-2"></i>
                <span class="text-sm text-gray-600">256位元加密傳輸</span>
              </div>
              <div class="flex items-center">
                <i class="fas fa-lock text-2xl text-gray-500 mr-2"></i>
                <span class="text-sm text-gray-600">資料安全保障</span>
              </div>
              <div class="flex items-center">
                <i class="fas fa-user-shield text-2xl text-gray-500 mr-2"></i>
                <span class="text-sm text-gray-600">隱私資訊保護</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 綠界支付說明 -->
      <div class="mt-8 text-center text-sm text-gray-500">
        <p>本站使用綠界科技ECPay提供金流服務，交易過程均受到保護</p>
        <p class="mt-1">遇到問題？請聯繫我們的客服團隊 <a href="mailto:support@example.com" class="text-blue-600 hover:underline">support@example.com</a></p>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 可在此添加自定義樣式 */
</style> 
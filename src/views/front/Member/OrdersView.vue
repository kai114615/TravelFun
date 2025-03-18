<script setup lang="ts">
import { ref, onMounted, h, computed } from 'vue';
import { NCard, NEmpty, NList, NListItem, NTag, NButton, NModal, NDescriptions, NDescriptionsItem, NSpace, NDataTable, useMessage } from 'naive-ui';
import api from '@/api/config';
import { ShoppingAPI } from '@/api/shopping';
import axios from 'axios';

// 定義訂單項目類型
interface OrderItem {
  id: number;
  product_id: number | null;
  product_name: string;
  product_image: string;
  quantity: number;
  price: string;
  subtotal: string;
}

// 定義訂單類型
interface Order {
  id: number;
  order_number: string;
  total_amount: string;
  status: 'pending' | 'paid' | 'shipped' | 'completed' | 'cancelled';
  status_display: string;
  shipping_address: string;
  contact_phone: string;
  created_at: string;
  updated_at: string;
  items: OrderItem[];
}

const message = useMessage();
const orders = ref<Order[]>([]);
const pendingOrdersCount = ref(0);
const totalOrdersCount = ref(0);
const completedOrdersCount = ref(0);
const loading = ref(false);
const showOrderDetail = ref(false);
const currentOrder = ref<Order | null>(null);
const filterStatus = ref<string | null>(null);

// 訂單狀態對應的顏色
const statusColors: Record<string, 'warning' | 'success' | 'info' | 'error'> = {
  pending: 'warning',
  paid: 'success',
  shipped: 'info',
  completed: 'success',
  cancelled: 'error'
};

// 訂單狀態對應的中文
const statusText: Record<string, string> = {
  pending: '待付款',
  paid: '已付款',
  shipped: '已出貨',
  completed: '已完成',
  cancelled: '已取消'
};

// 獲取用戶訂單
async function fetchUserOrders() {
  loading.value = true;
  try {
    console.log('開始獲取用戶訂單...');
    
    // 檢查用戶登入狀態
    const token = localStorage.getItem('access_token');
    if (!token) {
      console.error('未找到訪問令牌，無法獲取訂單數據');
      message.error('請先登入以查看您的訂單');
      loading.value = false;
      return;
    }
    
    console.log('已找到認證令牌:', token.substring(0, 10) + '...');
    
    // 嘗試使用不同方法獲取訂單數據
    try {
      console.log('使用API獲取訂單...');
      
      // 使用 ShoppingAPI 而不是直接使用axios，確保授權頭設置正確
      const apiResponse = await ShoppingAPI.getUserOrders();
      console.log('ShoppingAPI訂單響應:', apiResponse);
      
      if (apiResponse.success) {
        // ShoppingAPI方法返回成功 - 從 ShoppingAPI 獲取訂單
        console.log('成功從ShoppingAPI獲取訂單:', apiResponse);
        orders.value = apiResponse.orders || [];
        pendingOrdersCount.value = apiResponse.pending_orders_count || 0;
        totalOrdersCount.value = apiResponse.total_orders_count || 0;
        completedOrdersCount.value = orders.value.filter(order => order.status === 'completed').length;
        
        if (orders.value.length === 0) {
          console.log('用戶沒有訂單記錄 (ShoppingAPI)');
          message.info('您目前沒有任何訂單記錄');
        } else {
          console.log(`成功獲取 ${orders.value.length} 筆訂單記錄 (ShoppingAPI)`);
        }
        return;
      } else {
        console.error('ShoppingAPI獲取訂單失敗:', apiResponse.message);
      }
    } catch (apiError) {
      console.error('ShoppingAPI方法出錯:', apiError);
    }
    
    // 嘗試直接使用axios獲取訂單
    try {
      console.log('嘗試直接使用axios獲取訂單...');
      const directUrl = 'http://127.0.0.1:8000/shop/api/shopping/orders/user/';
      console.log('請求URL:', directUrl);
      console.log('使用令牌:', token.substring(0, 10) + '...');
      
      const response = await axios.get(directUrl, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      });
      
      console.log('直接API響應狀態:', response.status);
      console.log('直接API響應數據:', response.data);
      
      // 檢查返回格式，適配不同的響應結構
      if (response.data) {
        let ordersData = [];
        let pendingCount = 0;
        let totalCount = 0;
        let completedCount = 0;
        
        // 檢查返回數據結構
        if (Array.isArray(response.data)) {
          console.log('API返回數據是數組');
          ordersData = response.data;
          totalCount = ordersData.length;
          pendingCount = ordersData.filter(order => order.status === 'pending').length;
          completedCount = ordersData.filter(order => order.status === 'completed').length;
        } else if (response.data.orders) {
          // 如果返回 { orders: [...] } 結構
          console.log('API返回 orders 字段');
          ordersData = response.data.orders;
          pendingCount = response.data.pending_orders_count || 0;
          totalCount = response.data.total_orders_count || ordersData.length;
          completedCount = ordersData.filter(order => order.status === 'completed').length;
        } else if (response.data.results) {
          // 如果返回 { results: [...] } 結構 (Django REST框架分頁)
          console.log('API返回 results 字段');
          ordersData = response.data.results;
          totalCount = response.data.count || ordersData.length;
          pendingCount = ordersData.filter(order => order.status === 'pending').length;
          completedCount = ordersData.filter(order => order.status === 'completed').length;
        }
        
        // 檢查是否有數據並更新UI
        console.log(`處理後找到 ${ordersData.length} 筆訂單`);
        if (ordersData.length > 0) {
          // 檢查每個訂單是否有必要的屬性
          const validOrders = ordersData.map(order => {
            // 確保訂單項目是數組
            if (!order.items) {
              order.items = [];
            } else if (!Array.isArray(order.items)) {
              order.items = [];
            }
            
            // 確保其他必要屬性存在
            if (!order.order_number) {
              order.order_number = `ORDER-${order.id}`;
            }
            
            return order;
          });
          
          // 更新狀態
          orders.value = validOrders;
          pendingOrdersCount.value = pendingCount;
          totalOrdersCount.value = totalCount;
          completedOrdersCount.value = completedCount;
          
          console.log(`成功處理 ${validOrders.length} 筆有效訂單`);
        } else {
          orders.value = [];
          pendingOrdersCount.value = 0;
          totalOrdersCount.value = 0;
          completedOrdersCount.value = 0;
          console.log('找不到有效訂單');
          message.info('您目前沒有任何訂單記錄');
        }
      }
    } catch (directError) {
      console.error('直接獲取訂單出錯:', directError);
      console.error('錯誤詳情:', {
        message: directError.message,
        response: directError.response?.data,
        status: directError.response?.status
      });
      
      if (directError.response?.status === 401) {
        message.error('您的登入已過期，請重新登入');
        // 嘗試使用localStorage中的refresh_token刷新token
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          try {
            console.log('嘗試使用refresh token刷新認證...');
            const refreshResponse = await axios.post('http://127.0.0.1:8000/api/token/refresh/', {
              refresh: refreshToken
            });
            
            if (refreshResponse.data.access) {
              localStorage.setItem('access_token', refreshResponse.data.access);
              message.success('已刷新認證令牌，請再次嘗試');
              // 延遲後重新載入訂單
              setTimeout(() => fetchUserOrders(), 1000);
              return;
            }
          } catch (refreshError) {
            console.error('刷新令牌失敗:', refreshError);
            message.error('您的登入已完全過期，請重新登入');
          }
        }
      } else {
        message.error('獲取訂單失敗，請稍後再試');
      }
    }
  } catch (error) {
    console.error('獲取訂單失敗:', error);
    message.error('獲取訂單失敗，請稍後再試');
  } finally {
    loading.value = false;
  }
}

// 過濾後的訂單列表
const filteredOrders = computed(() => {
  if (!filterStatus.value) return orders.value;
  return orders.value.filter(order => order.status === filterStatus.value);
});

// 取消過濾
function clearFilter() {
  filterStatus.value = null;
}

// 設置過濾器
function setFilter(status: string) {
  filterStatus.value = status === filterStatus.value ? null : status;
}

// 表格列定義
const tableColumns = [
  {
    title: '訂單編號',
    key: 'order_number'
  },
  {
    title: '訂單狀態',
    key: 'status',
    render(row: Order) {
      return h(
        NTag,
        {
          type: statusColors[row.status]
        },
        { default: () => statusText[row.status] || row.status }
      );
    }
  },
  {
    title: '下單時間',
    key: 'created_at',
    render(row: Order) {
      return formatDate(row.created_at);
    }
  },
  {
    title: '商品數量',
    key: 'items_count',
    render(row: Order) {
      return row.items?.length || 0;
    }
  },
  {
    title: '訂單金額',
    key: 'total_amount',
    render(row: Order) {
      return `NT$ ${row.display_total_amount || row.total_amount}`;
    }
  },
  {
    title: '操作',
    key: 'actions',
    render(row: Order) {
      return h(
        NButton,
        {
          type: 'primary',
          size: 'small',
          onClick: () => viewOrderDetail(row)
        },
        { default: () => '詳情' }
      );
    }
  }
];

// 查看訂單詳情
function viewOrderDetail(order: Order) {
  console.log('查看訂單詳情:', order.order_number);
  console.log('訂單項目數量:', order.items.length);
  console.log('訂單項目詳情:', JSON.stringify(order.items, null, 2));
  console.log('訂單狀態:', order.status);
  console.log('訂單創建時間:', order.created_at);
  
  // 添加詳細的金額對賬
  let totalItemsAmount = 0;
  if (order.items && order.items.length > 0) {
    console.log('逐一檢查訂單項目:');
    order.items.forEach((item, index) => {
      const itemSubtotal = parseFloat(item.subtotal);
      const calculatedSubtotal = parseFloat(item.price) * item.quantity;
      
      console.log(`[${index + 1}] ${item.product_name}`);
      console.log(`  產品ID: ${item.product_id || '無ID'}`);
      console.log(`  數量: ${item.quantity}`);
      console.log(`  單價: ${item.price}`);
      console.log(`  小計(API返回): ${item.subtotal}`);
      console.log(`  小計(重新計算): ${calculatedSubtotal.toFixed(2)}`);
      console.log(`  圖片URL: ${item.product_image || '無圖片'}`);
      
      // 檢查單項小計是否一致
      if (Math.abs(itemSubtotal - calculatedSubtotal) > 0.01) {
        console.warn(`  警告: 項目 ${index + 1} 的小計金額計算不一致!`);
        // 使用重新計算的金額作為小計
        item.subtotal = calculatedSubtotal.toFixed(2);
      }
      
      totalItemsAmount += parseFloat(item.subtotal);
    });
    
    console.log('項目總金額(累計):', totalItemsAmount.toFixed(2));
    console.log('訂單總金額(API):', order.total_amount);
    
    // 檢查總金額是否一致，並更新顯示的訂單總金額
    if (Math.abs(totalItemsAmount - parseFloat(order.total_amount)) > 0.01) {
      console.warn('警告: 項目總金額與訂單總金額不一致!');
      console.warn(`項目總和: ${totalItemsAmount.toFixed(2)}, 訂單總額: ${order.total_amount}`);
      console.warn('差額:', (parseFloat(order.total_amount) - totalItemsAmount).toFixed(2));
      // 使用計算出的項目總額作為訂單總額顯示
      order.display_total_amount = totalItemsAmount.toFixed(2);
    } else {
      order.display_total_amount = order.total_amount;
      console.log('金額核對: 訂單總金額與項目總金額一致');
    }
  } else {
    console.warn('警告: 此訂單沒有項目記錄!');
    order.display_total_amount = order.total_amount;
  }
  
  // 確保所有項目的圖片URLs都有值，避免空值顯示
  if (order.items) {
    order.items.forEach(item => {
      if (!item.product_image) {
        item.product_image = '/placeholder-image.png'; // 使用預設圖片
      }
    });
  }
  
  currentOrder.value = order;
  showOrderDetail.value = true;
}

// 格式化日期
function formatDate(dateString: string): string {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleString('zh-TW', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  });
}

// 訂單項目表格列
const columns = [
  {
    title: '商品圖片',
    key: 'product_image',
    render(row: OrderItem) {
      return h('img', {
        src: row.product_image,
        alt: row.product_name,
        style: 'width: 50px; height: 50px; object-fit: cover; border-radius: 4px;'
      });
    }
  },
  {
    title: '商品名稱',
    key: 'product_name'
  },
  {
    title: '單價',
    key: 'price',
    render(row: OrderItem) {
      return `NT$ ${row.price}`;
    }
  },
  {
    title: '數量',
    key: 'quantity'
  },
  {
    title: '小計',
    key: 'subtotal',
    render(row: OrderItem) {
      return `NT$ ${row.subtotal}`;
    }
  }
];

// 計算訂單項目總金額
function getItemsTotal(order: Order | null): number {
  if (!order || !order.items) return 0;
  return order.items.reduce((sum, item) => sum + parseFloat(item.subtotal), 0);
}

onMounted(() => {
  console.log('訂單頁面已掛載，準備獲取訂單數據...');
  
  // 檢查用戶登入狀態
  const token = localStorage.getItem('access_token');
  const user = localStorage.getItem('user');
  const userInfo = localStorage.getItem('userInfo');
  
  console.log('登入狀態檢查:');
  console.log('- access_token 存在:', !!token);
  if (token) {
    console.log('- token 前10個字符:', token.substring(0, 10) + '...');
  }
  console.log('- user 存在:', !!user);
  console.log('- userInfo 存在:', !!userInfo);
  
  if (user) {
    try {
      const userData = JSON.parse(user);
      console.log('- 用戶名:', userData.username);
      console.log('- 認證狀態:', userData.isAuthenticated);
    } catch (e) {
      console.error('解析 user 數據失敗:', e);
    }
  }
  
  if (userInfo) {
    try {
      const userInfoData = JSON.parse(userInfo);
      console.log('- 用戶ID:', userInfoData.id);
      console.log('- 用戶名:', userInfoData.username);
    } catch (e) {
      console.error('解析 userInfo 數據失敗:', e);
    }
  }
  
  // 開始獲取訂單
  fetchUserOrders();
});
</script>

<template>
  <div class="container mx-auto px-4 py-8">
    <!-- 頁面標題 -->
    <h1 class="text-2xl font-bold mb-8">訂單管理</h1>

    <!-- 統計數據和過濾按鈕 -->
    <div class="mb-6 flex justify-between items-center">
      <!-- 統計數據 -->
      <div class="flex gap-4">
        <n-statistic label="待處理訂單" :value="pendingOrdersCount" class="bg-white rounded shadow p-3">
          <template #suffix>筆</template>
        </n-statistic>
        <n-statistic label="已完成訂單" :value="completedOrdersCount" class="bg-white rounded shadow p-3">
          <template #suffix>筆</template>
        </n-statistic>
        <n-statistic label="訂單總數" :value="totalOrdersCount" class="bg-white rounded shadow p-3">
          <template #suffix>筆</template>
        </n-statistic>
      </div>
      
      <!-- 過濾按鈕 -->
      <n-space>
        <n-button-group>
          <n-button 
            :type="filterStatus === null ? 'primary' : 'default'" 
            @click="clearFilter">
            全部
          </n-button>
          <n-button 
            :type="filterStatus === 'pending' ? 'warning' : 'default'" 
            @click="setFilter('pending')">
            待付款
          </n-button>
          <n-button 
            :type="filterStatus === 'paid' ? 'success' : 'default'" 
            @click="setFilter('paid')">
            已付款
          </n-button>
          <n-button 
            :type="filterStatus === 'shipped' ? 'info' : 'default'" 
            @click="setFilter('shipped')">
            已出貨
          </n-button>
          <n-button 
            :type="filterStatus === 'completed' ? 'success' : 'default'" 
            @click="setFilter('completed')">
            已完成
          </n-button>
        </n-button-group>
        <n-button type="primary" @click="fetchUserOrders" :loading="loading">
          刷新訂單
        </n-button>
      </n-space>
    </div>

    <!-- 載入中顯示 -->
    <n-card v-if="loading">
      <div class="flex justify-center p-8">
        <n-spin size="large" />
      </div>
    </n-card>
    
    <!-- 無訂單顯示 -->
    <n-empty v-else-if="orders.length === 0" description="您還沒有訂單記錄">
      <template #extra>
        <n-button @click="$router.push('/mall-products')">
          開始購物
        </n-button>
      </template>
    </n-empty>
    
    <!-- 訂單表格 -->
    <n-data-table
      v-else
      :columns="tableColumns"
      :data="filteredOrders"
      :pagination="{ pageSize: 10 }"
      :bordered="false"
      :single-line="false"
    />

    <!-- 訂單詳情彈窗 -->
    <n-modal v-model:show="showOrderDetail" style="width: 800px; max-width: 90vw">
      <n-card
        v-if="currentOrder"
        :title="`訂單詳情 #${currentOrder.order_number}`"
        :bordered="false"
        class="max-h-[90vh] overflow-auto"
      >
        <n-descriptions bordered>
          <n-descriptions-item label="訂單狀態">
            <n-tag :type="statusColors[currentOrder.status]">
              {{ statusText[currentOrder.status] }}
            </n-tag>
          </n-descriptions-item>
          <n-descriptions-item label="訂單日期">
            {{ formatDate(currentOrder.created_at) }}
          </n-descriptions-item>
          <n-descriptions-item label="總金額">
            NT$ {{ currentOrder.display_total_amount || currentOrder.total_amount }}
          </n-descriptions-item>
          <n-descriptions-item label="收件地址">
            {{ currentOrder.shipping_address }}
          </n-descriptions-item>
          <n-descriptions-item label="聯絡電話">
            {{ currentOrder.contact_phone }}
          </n-descriptions-item>
          <n-descriptions-item v-if="currentOrder.note" label="備註">
            {{ currentOrder.note }}
          </n-descriptions-item>
        </n-descriptions>
        
        <div class="mt-6">
          <h3 class="text-lg font-bold mb-3">
            訂單項目 ({{ currentOrder.items?.length || 0 }} 件)
          </h3>
          <n-data-table
            :columns="columns"
            :data="currentOrder.items || []"
            :bordered="false"
            :single-line="false"
            :pagination="false"
          />
        </div>

        <n-space justify="end" class="mt-4">
          <n-button @click="showOrderDetail = false">
            關閉
          </n-button>
        </n-space>
      </n-card>
    </n-modal>
  </div>
</template>

<style scoped>
.n-list-item {
  transition: all 0.2s ease;
}
.n-list-item:hover {
  background-color: #f9fafb;
}
</style> 
<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import Banner from '@/components/Banner.vue';

const route = useRoute();
const router = useRouter();
const orderNumber = ref(route.params.orderNumber as string);

// 如果沒有訂單編號則返回首頁
if (!orderNumber.value) {
  ElMessage.error('找不到訂單資訊');
  router.push('/');
}

// 顯示時間
const deadline = ref('');
onMounted(() => {
  // 計算付款截止時間（目前時間的三天後）
  const deadlineDate = new Date();
  deadlineDate.setDate(deadlineDate.getDate() + 3);
  deadline.value = deadlineDate.toLocaleDateString('zh-TW', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
});

// 生成模擬的銀行帳號
const bankAccount = ref('015-123456-789012');
const amount = ref(Math.floor(Math.random() * 10000) + 1000);

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

// 完成訂單
function completeOrder() {
  router.push({
    name: 'OrderComplete',
    params: { orderNumber: orderNumber.value }
  });
}
</script>

<template>
  <div>
    <Banner bg-url="/images/banner.jpg">
      <template #title>
        ATM 轉帳付款
      </template>
      <template #sec-title>
        請依照以下資訊完成轉帳付款，以確保訂單處理順利
      </template>
    </Banner>

    <div class="container mx-auto px-4 py-8">
      <div class="max-w-2xl mx-auto bg-white rounded-lg shadow-md p-8">
        <div class="mb-8 pb-4 border-b">
          <div class="flex justify-between items-center mb-4">
            <h2 class="text-xl font-bold">訂單資訊</h2>
            <span class="bg-blue-100 text-blue-800 text-sm font-medium px-3 py-1 rounded-full">等待付款</span>
          </div>
          <p class="text-gray-700">
            <span class="font-medium">訂單編號:</span> {{ orderNumber }}
          </p>
          <p class="text-gray-700">
            <span class="font-medium">應付金額:</span> <span class="text-xl font-bold text-green-600">NT$ {{ amount }}</span>
          </p>
          <p class="text-gray-700">
            <span class="font-medium">付款期限:</span> {{ deadline }} 前
          </p>
          <p class="text-red-600 text-sm mt-2">
            <i class="fas fa-exclamation-circle mr-1"></i> 超過付款期限，訂單將自動取消
          </p>
        </div>

        <div class="mb-8">
          <h2 class="text-xl font-bold mb-4">轉帳資訊</h2>
          
          <!-- 銀行資訊 -->
          <div class="bg-gray-50 p-4 rounded-lg mb-4">
            <div class="flex justify-between items-center mb-2">
              <p class="text-gray-700"><span class="font-medium">銀行名稱:</span> 台灣銀行</p>
              <button @click="copyToClipboard('台灣銀行')" class="text-blue-600 text-sm hover:text-blue-800">
                <i class="far fa-copy mr-1"></i> 複製
              </button>
            </div>
            <div class="flex justify-between items-center mb-2">
              <p class="text-gray-700"><span class="font-medium">銀行代碼:</span> 015</p>
              <button @click="copyToClipboard('015')" class="text-blue-600 text-sm hover:text-blue-800">
                <i class="far fa-copy mr-1"></i> 複製
              </button>
            </div>
            <div class="flex justify-between items-center mb-2">
              <p class="text-gray-700"><span class="font-medium">帳號:</span> {{ bankAccount }}</p>
              <button @click="copyToClipboard(bankAccount)" class="text-blue-600 text-sm hover:text-blue-800">
                <i class="far fa-copy mr-1"></i> 複製
              </button>
            </div>
            <div class="flex justify-between items-center">
              <p class="text-gray-700"><span class="font-medium">戶名:</span> 台灣旅遊樂股份有限公司</p>
              <button @click="copyToClipboard('台灣旅遊樂股份有限公司')" class="text-blue-600 text-sm hover:text-blue-800">
                <i class="far fa-copy mr-1"></i> 複製
              </button>
            </div>
          </div>
          
          <!-- 轉帳金額 -->
          <div class="bg-green-50 p-4 rounded-lg">
            <div class="flex justify-between items-center">
              <p class="text-gray-700"><span class="font-medium">轉帳金額:</span> <span class="text-xl font-bold text-green-600">NT$ {{ amount }}</span></p>
              <button @click="copyToClipboard(amount.toString())" class="text-blue-600 text-sm hover:text-blue-800">
                <i class="far fa-copy mr-1"></i> 複製
              </button>
            </div>
          </div>
          
          <div class="mt-4 text-sm text-gray-600">
            <p>請於轉帳時備註您的訂單編號 {{ orderNumber }}，以便我們核對付款。</p>
          </div>
        </div>
        
        <div class="mb-8">
          <h2 class="text-xl font-bold mb-4">注意事項</h2>
          <ul class="list-disc pl-5 space-y-2 text-gray-700">
            <li>請確保轉入的金額與訂單金額完全相符</li>
            <li>轉帳完成後，系統將在 1-2 個工作天內確認款項並更新訂單狀態</li>
            <li>若轉帳過程中有任何問題，請聯繫客服</li>
            <li>轉帳完成後，請保留轉帳收據或證明，以備查核</li>
          </ul>
        </div>
        
        <div class="flex flex-col md:flex-row gap-4 justify-center">
          <button 
            @click="completeOrder" 
            class="bg-green-600 text-white py-3 px-6 rounded-lg hover:bg-green-700 transition-colors font-medium"
          >
            <i class="fas fa-check-circle mr-2"></i>我已完成付款
          </button>
          <button 
            @click="router.push('/member/orders')" 
            class="bg-gray-200 text-gray-800 py-3 px-6 rounded-lg hover:bg-gray-300 transition-colors"
          >
            <i class="fas fa-list-alt mr-2"></i>查看我的訂單
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 如有需要，可在此處添加自定義樣式 */
</style> 
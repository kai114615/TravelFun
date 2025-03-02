<script setup lang="ts">
import { ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const router = useRouter();
const route = useRoute();
const orderNumber = ref(route.params.orderNumber || '');

// 返回商城
function goToMall () {
  router.push('/mall-products');
}

// 查看訂單詳情
function viewOrderDetails () {
  router.push({
    name: 'MemberDashboard',
    query: { tab: 'orders' }
  });
}
</script>

<template>
  <div class="container mx-auto px-4 py-12">
    <div class="max-w-2xl mx-auto bg-white rounded-lg shadow p-8 text-center">
      <div class="mb-6">
        <div class="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <i class="fas fa-check text-3xl text-green-600" />
        </div>
        <h1 class="text-2xl font-bold mb-2">
          訂單已成功建立
        </h1>
        <p class="text-gray-600">
          感謝您的購買！我們已收到您的訂單。
        </p>
      </div>

      <div class="border-t border-b py-6 mb-6">
        <div class="mb-4">
          <p class="text-gray-600">
            訂單編號
          </p>
          <p class="font-bold text-lg">
            {{ orderNumber }}
          </p>
        </div>
        <p class="text-sm text-gray-500">
          訂單確認信已發送至您的電子郵件信箱
        </p>
      </div>

      <div class="space-y-4">
        <button
          class="w-full bg-green-600 text-white py-3 rounded-lg hover:bg-green-700 transition-colors font-medium"
          @click="viewOrderDetails"
        >
          查看訂單詳情
        </button>
        <button
          class="w-full bg-gray-100 text-gray-800 py-3 rounded-lg hover:bg-gray-200 transition-colors font-medium"
          @click="goToMall"
        >
          繼續購物
        </button>
      </div>
    </div>
  </div>
</template>

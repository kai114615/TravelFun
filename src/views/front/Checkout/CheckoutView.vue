<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { storeToRefs } from 'pinia';
import { useCartStore } from '@/stores/cart';

const router = useRouter();
const cartStore = useCartStore();
const { items, totalAmount } = storeToRefs(cartStore);

// 全形數字轉半形函數
function toHalfWidth (str: string): string {
  if (!str) return '';

  // 全形數字的 Unicode 範圍是 U+FF10 到 U+FF19
  // 半形數字的 Unicode 範圍是 U+0030 到 U+0039
  return str.replace(/[\uFF10-\uFF19]/g, (match) => {
    return String.fromCharCode(match.charCodeAt(0) - 0xFEE0);
  });
}

// 收件資訊表單
const form = ref({
  name: '',
  phone: '',
  address: '',
  note: ''
});

// 表單驗證規則
// const rules = {
//   name: [{ required: true, message: '請輸入收件人姓名', trigger: 'blur' }],
//   phone: [{ required: true, message: '請輸入聯絡電話', trigger: 'blur' }],
//   address: [{ required: true, message: '請輸入收件地址', trigger: 'blur' }]
// };

// 提交訂單
async function submitOrder () {
  try {
    // 檢查購物車是否為空
    if (items.value.length === 0) {
      ElMessage.warning('購物車是空的，請先選購商品');
      router.push('/mall-products');
      return;
    }

    // 檢查收件資訊是否填寫完整
    if (!form.value.name || !form.value.phone || !form.value.address) {
      ElMessage.error('請確認收件資訊已填寫完成');
      return;
    }

    // 轉換全形數字為半形
    form.value.phone = toHalfWidth(form.value.phone);
    form.value.address = toHalfWidth(form.value.address);

    // 生成臨時訂單編號 (縮短長度，避免超出數據庫限制)
    const tempOrderNumber = `ORD${Date.now().toString().slice(-6)}${Math.floor(Math.random() * 100)}`;

    // 準備訂單資訊
    const orderInfo = {
      orderNumber: tempOrderNumber,
      items: items.value,
      shippingInfo: {
        name: form.value.name,
        phone: form.value.phone,
        address: form.value.address,
        note: form.value.note
      },
      totalAmount: totalAmount.value,
      discount: 0,
      shippingFee: 0
    };

    // 保存訂單資訊到 localStorage
    localStorage.setItem('pendingOrderInfo', JSON.stringify(orderInfo));

    // 導向訂單確認頁面
    router.push('/order-confirm');
  } catch (error) {
    console.error('處理訂單時發生錯誤:', error);
    ElMessage.error('處理訂單時發生錯誤，請稍後再試');
  }
}
</script>

<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-2xl font-bold mb-8">
      結帳
    </h1>

    <div class="flex flex-col lg:flex-row gap-8">
      <!-- 左側收件資訊 -->
      <div class="lg:w-2/3">
        <div class="bg-white rounded-lg shadow p-6">
          <h2 class="text-xl font-bold mb-6">
            收件資訊
          </h2>
          <form class="space-y-6" @submit.prevent="submitOrder">
            <!-- 收件人姓名 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                收件人姓名
                <span class="text-red-500">*</span>
              </label>
              <input
                v-model="form.name"
                type="text"
                class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                placeholder="請輸入收件人姓名"
                required
              >
            </div>

            <!-- 聯絡電話 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                聯絡電話
                <span class="text-red-500">*</span>
              </label>
              <input
                v-model="form.phone"
                type="tel"
                class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                placeholder="請輸入聯絡電話"
                required
              >
            </div>

            <!-- 收件地址 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                收件地址
                <span class="text-red-500">*</span>
              </label>
              <input
                v-model="form.address"
                type="text"
                class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                placeholder="請輸入完整收件地址"
                required
              >
            </div>

            <!-- 訂單備註 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                訂單備註
              </label>
              <textarea
                v-model="form.note"
                rows="3"
                class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                placeholder="有什麼想告訴我們的嗎？(限制300字)"
                maxlength="300"
              />
            </div>
          </form>
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
            <div v-for="item in items" :key="item.id" class="flex gap-4">
              <img
                :src="item.image_url"
                :alt="item.name"
                class="w-16 h-16 object-cover rounded"
              >
              <div class="flex-grow">
                <h3 class="text-sm font-medium">
                  {{ item.name }}
                </h3>
                <p class="text-sm text-gray-500">
                  數量: {{ item.quantity }}
                </p>
                <p class="text-sm font-medium text-green-600">
                  NT$ {{ item.price * item.quantity }}
                </p>
              </div>
            </div>
          </div>

          <!-- 金額計算 -->
          <div class="space-y-4 pt-6 border-t">
            <div class="flex justify-between">
              <span>商品小計</span>
              <span>NT$ {{ totalAmount }}</span>
            </div>
            <div class="flex justify-between">
              <span>運費</span>
              <span>免費</span>
            </div>
            <div class="flex justify-between text-lg font-bold pt-4 border-t">
              <span>結帳總金額</span>
              <span class="text-green-600">NT$ {{ totalAmount }}</span>
            </div>
          </div>

          <!-- 送出訂單按鈕 -->
          <button
            class="w-full mt-6 bg-green-600 text-white py-3 rounded-lg hover:bg-green-700 transition-colors font-medium"
            @click="submitOrder"
          >
            確認送出訂單
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

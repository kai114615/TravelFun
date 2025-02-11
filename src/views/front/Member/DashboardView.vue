<template>
  <div>
    <n-message-provider>
      <!-- 歡迎區塊 -->
      <div class="bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg shadow-md p-8 mb-8">
        <div class="flex items-center space-x-6">
          <div class="relative">
            <img
              :src="avatarUrl"
              alt="用戶頭像"
              class="h-20 w-20 rounded-full object-cover border-4 border-white shadow-md"
            />
            <div class="absolute -bottom-2 -right-2 bg-green-500 p-1.5 rounded-full border-2 border-white">
              <i class="fas fa-check text-white text-xs"></i>
            </div>
          </div>
          <div class="text-white">
            <h1 class="text-3xl font-bold mb-2">
              歡迎回來，{{ userInfo?.full_name || userInfo?.username }}
            </h1>
            <p class="text-blue-100 flex items-center">
              <i class="fas fa-clock mr-2"></i>
              上次登入時間：{{ formatDate(userInfo?.last_login) }}
            </p>
          </div>
        </div>
      </div>
    </n-message-provider>

    <!-- 功能卡片網格 -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
      <!-- 訂單管理 -->
      <div
        class="bg-white rounded-lg shadow-sm p-6 hover:shadow-md transition-all duration-200 transform hover:-translate-y-1 cursor-pointer border border-gray-100"
        @click="router.push('/member/orders')"
      >
        <div class="flex items-center justify-between mb-4">
          <div class="bg-blue-100 p-3 rounded-lg">
            <i class="fas fa-shopping-bag text-2xl text-blue-600"></i>
          </div>
          <span class="text-sm font-medium text-gray-500">訂單管理</span>
        </div>
        <h3 class="text-2xl font-bold text-gray-900 mb-2">{{ pendingOrders }}</h3>
        <p class="text-sm text-gray-600">待處理訂單</p>
        <div class="mt-4 flex items-center text-blue-600 hover:text-blue-700">
          <span class="text-sm font-medium">查看詳情</span>
          <i class="fas fa-arrow-right ml-2 text-xs"></i>
        </div>
      </div>

      <!-- 購物車 -->
      <div
        class="bg-white rounded-lg shadow-sm p-6 hover:shadow-md transition-all duration-200 transform hover:-translate-y-1 cursor-pointer border border-gray-100"
        @click="router.push('/cart')"
      >
        <div class="flex items-center justify-between mb-4">
          <div class="bg-green-100 p-3 rounded-lg">
            <i class="fas fa-shopping-cart text-2xl text-green-600"></i>
          </div>
          <span class="text-sm font-medium text-gray-500">購物車</span>
        </div>
        <h3 class="text-2xl font-bold text-gray-900 mb-2">{{ cartItemCount }}</h3>
        <p class="text-sm text-gray-600">商品數量</p>
        <div class="mt-4 flex items-center text-green-600 hover:text-green-700">
          <span class="text-sm font-medium">前往購物車</span>
          <i class="fas fa-arrow-right ml-2 text-xs"></i>
        </div>
      </div>

      <!-- 收藏清單 -->
      <div
        class="bg-white rounded-lg shadow-sm p-6 hover:shadow-md transition-all duration-200 transform hover:-translate-y-1 cursor-pointer border border-gray-100"
        @click="router.push('/member/wishlist')"
      >
        <div class="flex items-center justify-between mb-4">
          <div class="bg-red-100 p-3 rounded-lg">
            <i class="fas fa-heart text-2xl text-red-600"></i>
          </div>
          <span class="text-sm font-medium text-gray-500">收藏清單</span>
        </div>
        <h3 class="text-2xl font-bold text-gray-900 mb-2">{{ wishlistCount }}</h3>
        <p class="text-sm text-gray-600">收藏商品</p>
        <div class="mt-4 flex items-center text-red-600 hover:text-red-700">
          <span class="text-sm font-medium">查看收藏</span>
          <i class="fas fa-arrow-right ml-2 text-xs"></i>
        </div>
      </div>

      <!-- 個人資料 -->
      <div
        class="bg-white rounded-lg shadow-sm p-6 hover:shadow-md transition-all duration-200 transform hover:-translate-y-1 cursor-pointer border border-gray-100"
        @click="router.push('/member/profile')"
      >
        <div class="flex items-center justify-between mb-4">
          <div class="bg-purple-100 p-3 rounded-lg">
            <i class="fas fa-user-circle text-2xl text-purple-600"></i>
          </div>
          <span class="text-sm font-medium text-gray-500">個人資料</span>
        </div>
        <h3 class="text-lg font-medium text-gray-900 mb-2">個人資訊</h3>
        <p class="text-sm text-gray-600">上次更新：{{ formatDate(userInfo?.updated_at) }}</p>
        <div class="mt-4 flex items-center text-purple-600 hover:text-purple-700">
          <span class="text-sm font-medium">編輯資料</span>
          <i class="fas fa-arrow-right ml-2 text-xs"></i>
        </div>
      </div>

      <!-- 訊息中心 -->
      <div
        class="bg-white rounded-lg shadow-sm p-6 hover:shadow-md transition-all duration-200 transform hover:-translate-y-1 cursor-pointer border border-gray-100"
        @click="router.push('/member/messages')"
      >
        <div class="flex items-center justify-between mb-4">
          <div class="bg-yellow-100 p-3 rounded-lg">
            <i class="fas fa-envelope text-2xl text-yellow-600"></i>
          </div>
          <span class="text-sm font-medium text-gray-500">訊息中心</span>
        </div>
        <h3 class="text-2xl font-bold text-gray-900 mb-2">{{ unreadMessages }}</h3>
        <p class="text-sm text-gray-600">未讀訊息</p>
        <div class="mt-4 flex items-center text-yellow-600 hover:text-yellow-700">
          <span class="text-sm font-medium">查看訊息</span>
          <i class="fas fa-arrow-right ml-2 text-xs"></i>
        </div>
      </div>

      <!-- 優惠券 -->
      <div
        class="bg-white rounded-lg shadow-sm p-6 hover:shadow-md transition-all duration-200 transform hover:-translate-y-1 cursor-pointer border border-gray-100"
        @click="router.push('/member/coupons')"
      >
        <div class="flex items-center justify-between mb-4">
          <div class="bg-orange-100 p-3 rounded-lg">
            <i class="fas fa-ticket-alt text-2xl text-orange-600"></i>
          </div>
          <span class="text-sm font-medium text-gray-500">優惠券</span>
        </div>
        <h3 class="text-2xl font-bold text-gray-900 mb-2">{{ availableCoupons }}</h3>
        <p class="text-sm text-gray-600">可用優惠券</p>
        <div class="mt-4 flex items-center text-orange-600 hover:text-orange-700">
          <span class="text-sm font-medium">查看優惠</span>
          <i class="fas fa-arrow-right ml-2 text-xs"></i>
        </div>
      </div>
    </div>

    <!-- 最近活動 -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-100">
      <div class="p-6 border-b border-gray-100">
        <h2 class="text-xl font-bold text-gray-900">最近活動</h2>
      </div>
      <div class="divide-y divide-gray-100">
        <div
          v-for="activity in recentActivities"
          :key="activity.id"
          class="p-6 hover:bg-gray-50 transition-colors"
        >
          <div class="flex items-start space-x-4">
            <div class="flex-shrink-0">
              <div class="w-10 h-10 rounded-lg flex items-center justify-center" :style="{ backgroundColor: activity.iconBg || '#EBF5FF' }">
                <i :class="[activity.icon, 'text-lg']" :style="{ color: activity.iconColor }"></i>
              </div>
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-semibold text-gray-900">
                {{ activity.title }}
              </p>
              <p class="text-sm text-gray-500 mt-1">
                {{ activity.description }}
              </p>
            </div>
            <div class="flex-shrink-0">
              <time class="text-sm text-gray-500">{{ formatDate(activity.date) }}</time>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 個人資料表單 -->
    <div class="bg-white rounded-lg shadow-sm p-6 mt-8">
      <h2 class="text-xl font-bold text-gray-900 mb-6">編輯個人資料</h2>
      
      <!-- 頭像上傳 -->
      <div class="mb-6">
        <div class="flex items-center space-x-4">
          <img
            :src="avatarUrl"
            alt="用戶頭像"
            class="h-20 w-20 rounded-full object-cover border-2 border-gray-200"
          />
          <NUpload
            accept="image/*"
            :max="1"
            @change="handleAvatarUpload"
          >
            <NButton>更換頭像</NButton>
          </NUpload>
        </div>
      </div>

      <!-- 表單 -->
      <NForm>
        <NFormItem label="姓名" required>
          <NInput v-model:value="userForm.full_name" placeholder="請輸入姓名" />
        </NFormItem>

        <NFormItem label="地址">
          <NInput v-model:value="userForm.address" placeholder="請輸入地址" />
        </NFormItem>

        <div class="flex justify-end mt-6">
          <NButton type="primary" @click="saveProfile">
            保存修改
          </NButton>
        </div>
      </NForm>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { storeToRefs } from 'pinia'
import axios from 'axios'
import { NForm, NFormItem, NInput, NButton, NUpload, NMessageProvider, useMessage } from 'naive-ui'
import type { UploadFileInfo } from 'naive-ui'

// 創建 axios 實例
const axiosInstance = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  withCredentials: true
})

// 獲取 CSRF token
const getCsrfToken = () => {
  const name = 'csrftoken='
  const decodedCookie = decodeURIComponent(document.cookie)
  const cookieArray = decodedCookie.split(';')
  for (let cookie of cookieArray) {
    cookie = cookie.trim()
    if (cookie.indexOf(name) === 0) {
      return cookie.substring(name.length, cookie.length)
    }
  }
  return null
}

// 添加請求攔截器
axiosInstance.interceptors.request.use(config => {
  const csrfToken = getCsrfToken()
  if (csrfToken) {
    config.headers['X-CSRFToken'] = csrfToken
  }
  config.headers['X-Requested-With'] = 'XMLHttpRequest'
  return config
})

const router = useRouter()
const userStore = useUserStore()
const { userInfo } = storeToRefs(userStore)

const baseUrl = 'http://127.0.0.1:8000'
const avatarUrl = computed(() => {
  if (!userInfo.value?.avatar) {
    return 'https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y'
  }
  
  let url = userInfo.value.avatar
  // 移除開頭的斜線（如果存在）
  url = url.replace(/^\/+/, '')
  // 移除重複的 media 前綴
  url = url.replace(/^media\/media\//, 'media/')
  // 確保使用正斜線
  url = url.replace(/\\/g, '/')
  
  // 組合完整 URL
  return `${baseUrl}/${url}`
})

// 模擬數據
const pendingOrders = ref(3)
const cartItemCount = ref(5)
const wishlistCount = ref(12)
const unreadMessages = ref(2)
const availableCoupons = ref(4)

const recentActivities = ref([
  {
    id: 1,
    icon: 'fas fa-shopping-bag',
    iconColor: '#3B82F6',
    iconBg: '#EBF5FF',
    title: '新訂單已建立',
    description: '您的訂單 #12345 已成功建立',
    date: new Date(2024, 0, 15, 14, 30)
  },
  {
    id: 2,
    icon: 'fas fa-heart',
    iconColor: '#EF4444',
    iconBg: '#FEF2F2',
    title: '新增收藏商品',
    description: '您將「精選旅遊套票」加入收藏清單',
    date: new Date(2024, 0, 15, 10, 15)
  },
  {
    id: 3,
    icon: 'fas fa-ticket-alt',
    iconColor: '#F97316',
    iconBg: '#FFF7ED',
    title: '獲得新優惠券',
    description: '系統發送一張95折優惠券給您',
    date: new Date(2024, 0, 14, 16, 45)
  }
])

// 格式化日期
const formatDate = (date: Date | string | undefined) => {
  if (!date) return '無資料'
  const d = new Date(date)
  return d.toLocaleDateString('zh-TW', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 用戶資料表單
const userForm = ref({
  full_name: '',
  address: '',
})

// 監聽 userInfo 變化，更新表單數據
watch(() => userInfo.value, (newUserInfo) => {
  if (newUserInfo) {
    userForm.value.full_name = newUserInfo.full_name || ''
    userForm.value.address = newUserInfo.address || ''
  }
}, { immediate: true })

const message = useMessage()

// 處理頭像上傳
const handleAvatarUpload = async (options: { file: UploadFileInfo }) => {
  try {
    const formData = new FormData();
    formData.append('avatar', options.file.file as File);

    const token = localStorage.getItem('access_token');
    if (!token) {
      throw new Error('請先登入');
    }

    const response = await axios.post('http://127.0.0.1:8000/api/member/profile/update/', formData, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'multipart/form-data',
        'X-Requested-With': 'XMLHttpRequest'
      },
      withCredentials: true
    });

    if (response.status === 200) {
      message.success('頭像上傳成功');
      // 更新用戶資料
      await userStore.checkLoginStatus();
      // 更新本地頭像顯示
      userInfo.value.avatar = response.data.avatar;
    } else {
      throw new Error(response.data.message || '上傳失敗');
    }
  } catch (error: any) {
    console.error('上傳頭像失敗:', error);
    message.error(error.response?.data?.message || '上傳頭像失敗，請稍後再試');
  }
};

// 保存個人資料
const saveProfile = async () => {
  try {
    const formData = new FormData();
    formData.append('full_name', userForm.value.full_name);
    formData.append('address', userForm.value.address);

    const token = localStorage.getItem('access_token');
    if (!token) {
      throw new Error('請先登入');
    }

    const response = await axios.post('http://127.0.0.1:8000/api/member/profile/update/', formData, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'multipart/form-data',
        'X-Requested-With': 'XMLHttpRequest'
      },
      withCredentials: true
    });

    if (response.status === 200) {
      message.success('個人資料更新成功');
      await userStore.checkLoginStatus();
    } else {
      throw new Error('更新失敗');
    }
  } catch (error: any) {
    console.error('更新個人資料失敗:', error);
    message.error('更新個人資料失敗，請稍後再試');
  }
};

// 在組件掛載時獲取最新數據
onMounted(async () => {
  try {
    // 這裡可以添加API調用來獲取實際數據
    // await fetchDashboardData()
  } catch (error) {
    console.error('Failed to fetch dashboard data:', error)
  }
})
</script>

<style scoped>
.bg-gradient-to-r {
  background-size: 200% 200%;
  animation: gradient 15s ease infinite;
}

@keyframes gradient {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

.n-form-item {
  max-width: 600px;
}
</style> 
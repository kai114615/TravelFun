<script lang="ts">
import { defineComponent } from 'vue';
import type { AxiosError, AxiosInstance } from 'axios';
import axios from 'axios';
import type { ApiResponse as ActivityApiResponse, Event as ActivityEvent, EventStatus } from '@/types/activity';
import { STATUS_CLASSES, STATUS_MAP, STATUS_OPTIONS } from '@/types/activity';

export default defineComponent({
  name: 'ThemeEntertainmentAdmin',

  emits: ['showError'],

  data() {
    return {
      events: [] as ActivityEvent[],
      total: 0,
      loading: false,
      error: null as string | null,
      baseURL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000',
      axiosInstance: null as AxiosInstance | null,
      statusOptions: STATUS_OPTIONS,
    };
  },

  created() {
    this.initializeAxios();
    this.fetchEvents();
  },

  methods: {
    // 初始化 Axios 實例
    initializeAxios(): void {
      this.axiosInstance = axios.create({
        baseURL: this.baseURL,
        withCredentials: true,
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      });

      this.axiosInstance.interceptors.request.use((config) => {
        const token = localStorage.getItem('token');
        if (token)
          config.headers.Authorization = `Bearer ${token}`;

        return config;
      });
    },

    // 取得活動列表
    async fetchEvents(): Promise<void> {
      if (!this.axiosInstance)
        return;

      try {
        this.loading = true;
        const response = await this.axiosInstance.get<ActivityApiResponse>('/admin-dashboard/entertainment/activities/');

        if (response.data.status === 'success') {
          this.events = response.data.data.map(event => ({
            ...event,
            start_date: this.formatDate(event.start_date),
            end_date: this.formatDate(event.end_date),
          }));
          this.total = response.data.total;
        }
        else {
          throw new Error(response.data.message || '獲取數據失敗');
        }
      }
      catch (error) {
        console.error('獲取活動列表錯誤:', error);
        this.error = this.handleError(error as AxiosError);
        this.$emit('showError', this.error);
      }
      finally {
        this.loading = false;
      }
    },

    // 格式化日期
    formatDate(dateString: string): string {
      if (!dateString)
        return '';
      const date = new Date(dateString);
      return date.toISOString().split('T')[0];
    },

    // 格式化日期範圍
    formatDateRange(start: string, end: string): string {
      return `${start} ~ ${end}`;
    },

    // 取得活動狀態文字
    getStatusText(event: ActivityEvent): keyof typeof STATUS_CLASSES {
      const today = new Date();
      const startDate = new Date(event.start_date);
      const endDate = new Date(event.end_date);
      const threeDays = 3 * 24 * 60 * 60 * 1000; // 3天的毫秒數

      // 檢查是否為當日活動
      const isSameDay = startDate.toDateString() === endDate.toDateString();
      if (isSameDay && startDate.toDateString() === today.toDateString())
        return '只限今日';

      // 檢查是否已結束
      if (endDate < today)
        return '已結束';

      // 檢查是否即將結束（3天內）
      const endDiff = endDate.getTime() - today.getTime();
      if (endDiff <= threeDays && endDiff > 0)
        return '即將結束';

      // 檢查是否進行中
      if (today >= startDate)
        return '進行中';

      // 檢查是否即將開始（3天內）
      const startDiff = startDate.getTime() - today.getTime();
      if (startDiff <= threeDays)
        return '即將開始';

      // 檢查是否未開始
      if (startDiff > threeDays)
        return '未開始';

      // 默認情況
      return '未知';
    },

    // 取得狀態樣式類別
    getStatusClass(event: ActivityEvent): string {
      const status = this.getStatusText(event);
      const baseClasses = 'px-2 py-1 text-xs font-medium rounded-full';
      return `${baseClasses} ${STATUS_CLASSES[status]}`;
    },

    // 取得特定狀態的活動數量
    getStatusCount(status: string): number {
      const targetStatus = STATUS_MAP[status as keyof typeof STATUS_MAP];
      return this.events.filter(event => this.getStatusText(event) === targetStatus).length;
    },

    // 處理錯誤訊息
    handleError(error: AxiosError): string {
      if (error.response) {
        const status = error.response.status;
        const errorMessages = {
          401: '未授權訪問，請重新登入',
          403: '沒有權限訪問此資源',
          404: '找不到請求的資源',
          500: '伺服器錯誤，請稍後再試',
        };
        return errorMessages[status as keyof typeof errorMessages]
          || (error.response.data as any).message
          || '發生未知錯誤';
      }
      if (error.request)
        return '無法連接到伺服器，請檢查網路連接';

      return error.message || '發生未知錯誤';
    },

    // 重新整理資料
    async handleRefresh(): Promise<void> {
      await this.fetchEvents();
    },
  },
});
</script>

<template>
  <div class="theme-entertainment-admin">
    <!-- 錯誤提示 -->
    <div v-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4">
      <strong class="font-bold">錯誤！</strong>
      <span class="block sm:inline">{{ error }}</span>
      <button class="absolute top-0 right-0 px-4 py-3" @click="error = null">
        <span class="sr-only">關閉</span>
        <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>

    <!-- 頂部功能區 -->
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold">
        主題育樂活動管理
      </h2>
      <div class="flex gap-4">
        <button
          class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
          :disabled="loading" @click="handleRefresh"
        >
          <span v-if="!loading">重新整理</span>
          <span v-else>載入中...</span>
        </button>
      </div>
    </div>

    <!-- 數據統計卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <!-- 總活動數 -->
      <div class="bg-white p-6 rounded-lg shadow-lg hover:shadow-xl transition-shadow duration-300">
        <div class="flex items-center justify-between">
          <div>
            <div class="text-sm text-gray-500 mb-1">
              總活動數
            </div>
            <div class="text-3xl font-bold text-gray-800">
              {{ total }}
            </div>
          </div>
          <div class="text-purple-500">
            <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
              />
            </svg>
          </div>
        </div>
      </div>

      <!-- 進行中活動 -->
      <div class="bg-white p-6 rounded-lg shadow-lg hover:shadow-xl transition-shadow duration-300">
        <div class="flex items-center justify-between">
          <div>
            <div class="text-sm text-gray-500 mb-1">
              進行中
            </div>
            <div class="text-3xl font-bold text-green-600">
              {{ getStatusCount('ongoing') }}
            </div>
          </div>
          <div class="text-green-500">
            <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
        </div>
      </div>

      <!-- 即將開始活動 -->
      <div class="bg-white p-6 rounded-lg shadow-lg hover:shadow-xl transition-shadow duration-300">
        <div class="flex items-center justify-between">
          <div>
            <div class="text-sm text-gray-500 mb-1">
              即將開始
            </div>
            <div class="text-3xl font-bold text-blue-600">
              {{ getStatusCount('upcoming') }}
            </div>
          </div>
          <div class="text-blue-500">
            <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>
        </div>
      </div>

      <!-- 已結束活動 -->
      <div class="bg-white p-6 rounded-lg shadow-lg hover:shadow-xl transition-shadow duration-300">
        <div class="flex items-center justify-between">
          <div>
            <div class="text-sm text-gray-500 mb-1">
              已結束
            </div>
            <div class="text-3xl font-bold text-gray-600">
              {{ getStatusCount('ended') }}
            </div>
          </div>
          <div class="text-gray-500">
            <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
          </div>
        </div>
      </div>
    </div>

    <!-- 活動列表 -->
    <div class="bg-white rounded-lg shadow-lg overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                活動資訊
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                主辦單位
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                地點
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                時間
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                狀態
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="event in events" :key="event.id" class="hover:bg-gray-50 transition-colors duration-200">
              <td class="px-6 py-4">
                <div class="flex items-center space-x-3">
                  <div class="flex-shrink-0 w-10 h-10">
                    <img
                      class="w-10 h-10 rounded-full object-cover" :src="event.image_url || '/default-image.jpg'"
                      :alt="event.activity_name"
                    >
                  </div>
                  <div>
                    <div class="text-sm font-medium text-gray-900">
                      {{ event.activity_name }}
                    </div>
                    <div class="text-sm text-gray-500">
                      {{ event.description?.substring(0, 50) }}...
                    </div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">
                  {{ event.organizer }}
                </div>
              </td>
              <td class="px-6 py-4">
                <div class="text-sm text-gray-900">
                  {{ event.location }}
                </div>
                <div class="text-xs text-gray-500">
                  {{ event.address }}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">
                  {{ formatDateRange(event.start_date, event.end_date) }}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="getStatusClass(event)" class="inline-flex items-center px-3 py-1 rounded-full text-sm">
                  <span
                    class="w-2 h-2 mr-2 rounded-full" :class="{
                      'bg-green-500': getStatusText(event) === '進行中',
                      'bg-blue-500': getStatusText(event) === '即將開始',
                      'bg-yellow-500': getStatusText(event) === '即將結束',
                      'bg-red-500': getStatusText(event) === '只限今日',
                      'bg-purple-500': getStatusText(event) === '未開始',
                      'bg-gray-500': getStatusText(event) === '已結束',
                    }"
                  />
                  {{ getStatusText(event) }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Loading 狀態 -->
    <div v-if="loading" class="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-white" />
    </div>
  </div>
</template>

<style scoped>
.theme-entertainment-admin {
  padding: 1.5rem;
  min-height: 100vh;
  background-color: #f3f4f6;
}

/* 添加卡片動畫效果 */
.hover\:shadow-xl {
  transition: all 0.3s ease;
}

/* 添加表格動畫效果 */
.transition-colors {
  transition: background-color 0.2s ease;
}
</style>

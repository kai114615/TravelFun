<script>
// 匯入所需的套件與工具
import axios from 'axios';
import { NButton, NCard, NSpace } from 'naive-ui';

// import { ArrowBackOutline, BusinessOutline, CalendarOutline, ChevronBackOutline, ChevronForwardOutline, LocationOutline, TicketOutline } from '@vicons/ionicons5';

import { defaultActivityImages } from './ActivityList.vue'; // 從 ActivityList 匯入預設圖片設定

export default {
  name: 'ActivityDetail',

  // 註冊元件
  components: {
    NCard, // 卡片容器元件
    // NIcon, // 圖示元件
    NButton, // 按鈕元件
    NSpace, // 間距排版元件
    // LocationOutline, // 地點圖示
    // CalendarOutline, // 行事曆圖示
    // TicketOutline, // 票券圖示
    // ArrowBackOutline, // 返回箭頭圖示
    // BusinessOutline, // 商業圖示
    // ChevronBackOutline,
    // ChevronForwardOutline,
  },

  // 元件資料定義
  data() {
    return {
      activity: null, // 活動詳細資料
      loading: true, // 讀取狀態標記
      error: null, // 錯誤訊息
      defaultImages: defaultActivityImages, // 預設圖片清單
      currentImageIndex: 0, // 目前顯示的圖片索引
      randomDefaultImageIndex: Math.floor(Math.random() * defaultActivityImages.length), // 隨機預設圖片索引
      hasMultipleImages: false, // 是否有多張圖片標記
    };
  },

  // 生命週期鉤子 - 元件建立時取得資料
  async created() {
    await this.fetchActivityDetail();
  },

  // 方法定義
  methods: {
    // === 資料取得相關方法 ===

    // 從靜態 JSON 檔案和 API 取得活動詳細資料
    async fetchActivityDetail() {
      try {
        const id = this.$route.params.id;

        // 先嘗試從靜態 JSON 檔案讀取資料
        try {
          const staticData = await import('@/assets/theme_entertainment/events_data.json');
          const foundActivity = staticData.default.find(activity => activity.uid === id);

          if (foundActivity) {
            this.activity = foundActivity;
            return;
          }
        }
        catch (staticError) {
          console.warn('無法從靜態檔案讀取資料:', staticError);
        }

        // 如果靜態檔案中沒有找到資料，則從 API 獲取
        const response = await axios.get(`/theme_entertainment/activities/api/${id}/`);

        if (response.data.status === 'success')
          this.activity = response.data.data;
        else
          throw new Error(response.data.message || '取得資料失敗');
      }
      catch (error) {
        console.error('錯誤:', error);
        this.error = '無法載入活動詳細資訊';
      }
      finally {
        this.loading = false;
      }
    },

    // === 日期格式化方法 ===

    // 將日期字串格式化為本地日期格式
    formatDate(dateString) {
      if (!dateString)
        return '時間未定';
      const date = new Date(dateString);
      const formattedDate = date.toLocaleDateString('zh-TW', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      });
      const hours = String(date.getHours()).padStart(2, '0');
      const minutes = String(date.getMinutes()).padStart(2, '0');
      return `${formattedDate} ${hours}:${minutes}`;
    },

    // === 導覽相關方法 ===

    // 返回上一頁
    goBack() {
      this.$router.back();
    },

    // === 圖片處理相關方法 ===

    // 取得目前顯示的圖片網址
    getImageUrl() {
      if (!this.activity)
        return '';

      const imageUrls = this.getActivityImageUrls();
      if (imageUrls.length > 0) {
        this.hasMultipleImages = imageUrls.length > 1;
        return imageUrls[this.currentImageIndex % imageUrls.length];
      }

      return this.defaultImages[this.randomDefaultImageIndex];
    },

    // 取得活動的所有圖片網址
    getActivityImageUrls() {
      if (!this.activity?.image_url)
        return [];

      try {
        let imageUrls = [];
        if (typeof this.activity.image_url === 'string')
          imageUrls = this.parseImageUrlString(this.activity.image_url);

        else if (Array.isArray(this.activity.image_url))
          imageUrls = this.activity.image_url;

        return this.filterAndCleanImageUrls(imageUrls);
      }
      catch (e) {
        console.error('圖片網址處理錯誤:', e);
        return [];
      }
    },

    // 解析圖片網址字串
    parseImageUrlString(urlString) {
      try {
        return JSON.parse(urlString);
      }
      catch {
        if (urlString.includes('|'))
          return urlString.split('|');
        if (urlString.includes(','))
          return urlString.split(',');
        return [urlString];
      }
    },

    // 過濾並清理圖片網址清單
    filterAndCleanImageUrls(urls) {
      return urls
        .filter(url => url && url.trim()) // 過濾無效網址
        .map(url => url.trim()); // 清理網址字串
    },

    // === 輪播控制方法 ===

    // 顯示上一張圖片
    prevImage() {
      const totalImages = this.getTotalImages();
      this.currentImageIndex = (this.currentImageIndex - 1 + totalImages) % totalImages;
    },

    // 顯示下一張圖片
    nextImage() {
      const totalImages = this.getTotalImages();
      this.currentImageIndex = (this.currentImageIndex + 1) % totalImages;
    },

    // 取得圖片總數
    getTotalImages() {
      if (!this.activity)
        return 1;

      const imageUrls = this.getActivityImageUrls();
      return imageUrls.length || 1;
    },

    // === 錯誤處理方法 ===

    // 處理圖片載入錯誤
    handleImageError(e) {
      if (this.activity) {
        const storageKey = `activity_image_${this.activity.id}`;
        const newIndex = this.getRandomUniqueImageIndex();
        localStorage.setItem(storageKey, newIndex);
        e.target.src = this.defaultImages[newIndex];
      }
      e.target.onerror = null;
    },

    // 取得隨機且未使用的圖片索引
    getRandomUniqueImageIndex() {
      // 取得已使用的圖片索引
      const usedIndexes = new Set();
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key.startsWith('activity_image_'))
          usedIndexes.add(Number.parseInt(localStorage.getItem(key)));
      }

      // 產生可用的圖片索引清單
      let availableIndexes = Array.from(
        { length: this.defaultImages.length },
        (_, i) => i,
      ).filter(i => !usedIndexes.has(i));

      // 若所有圖片都被使用過，重新開始
      if (availableIndexes.length === 0) {
        availableIndexes = Array.from(
          { length: this.defaultImages.length },
          (_, i) => i,
        );
      }

      // 回傳隨機索引
      return availableIndexes[Math.floor(Math.random() * availableIndexes.length)];
    },
  },
};
</script>

<template>
  <!-- 主容器 -->
  <div class="max-w-[68rem] mx-auto px-0 py-4">
    <!-- 返回按鈕區域 -->
    <div class="mb-6">
      <NButton class="flex items-center" @click="goBack">
        <i class="fas fa-arrow-left mr-2" />
        返回活動列表
      </NButton>
    </div>

    <!-- 載入中狀態 -->
    <template v-if="loading">
      <div class="text-center py-12">
        <div class="loading-spinner mx-auto mb-4" />
        <p class="text-gray-600">
          載入中...
        </p>
      </div>
    </template>

    <!-- 錯誤狀態 -->
    <template v-else-if="error">
      <NCard class="bg-red-50 border border-red-200">
        <p class="text-red-600">
          {{ error }}
        </p>
      </NCard>
    </template>

    <!-- 活動詳情內容 -->
    <template v-else>
      <NCard class="overflow-hidden">
        <!-- 活動圖片區域 -->
        <div class="relative aspect-video mb-6 overflow-hidden rounded-lg">
          <!-- 主圖片 -->
          <img
            :src="getImageUrl()" :alt="activity.activity_name" class="w-full h-full object-cover"
            @error="handleImageError"
          >

          <!-- 輪播控制按鈕 -->
          <div
            v-if="hasMultipleImages"
            class="absolute inset-0 flex items-center justify-between px-4 opacity-0 hover:opacity-100 transition-all duration-300"
          >
            <button class="carousel-button opacity-60 hover:opacity-100" @click="prevImage">
              <i class="fas fa-chevron-left" />
            </button>
            <button class="carousel-button opacity-60 hover:opacity-100" @click="nextImage">
              <i class="fas fa-chevron-right" />
            </button>
          </div>

          <!-- 輪播指示器 -->
          <div v-if="hasMultipleImages" class="absolute bottom-4 left-1/2 transform -translate-x-1/2 flex space-x-2">
            <button
              v-for="index in getTotalImages()" :key="index" class="carousel-indicator"
              :class="index - 1 === currentImageIndex ? 'active' : ''" @click="currentImageIndex = index - 1"
            />
          </div>
        </div>

        <!-- 活動內容區域 -->
        <div class="space-y-6">
          <!-- 標題區域 -->
          <div class="mb-4">
            <h1 class="text-5xl font-bold text-gray-900 mb-4 leading-tight">
              {{ activity.activity_name }}
            </h1>
            <div class="flex items-center text-md text-gray-500 space-x-6">
              <!-- <span>ID: {{ activity.id }}</span> -->
              <span>建立時間: {{ formatDate(activity.created_at) }}</span>
              <span>更新時間: {{ formatDate(activity.updated_at) }}</span>
            </div>
          </div>

          <!-- 基本資訊區域 -->
          <NSpace vertical class="bg-gray-50 p-6 rounded-lg space-y-2">
            <!-- 地點信息 -->
            <div class="flex items-center text-gray-700">
              <div class="w-12 flex justify-center">
                <i class="fas fa-map-marker-alt text-xl text-[#0F4BB4]" />
              </div>
              <span class="font-bold text-lg ml-1">活動地點：</span>
              <span class="text-lg ml-3">{{ activity.location || '地點未定' }}</span>
            </div>
            <!-- 日期信息 -->
            <div class="flex items-center text-gray-700">
              <div class="w-12 flex justify-center">
                <i class="far fa-calendar text-xl text-[#0F4BB4]" />
              </div>
              <span class="font-bold text-lg ml-1">起訖時間：</span>
              <span class="text-lg ml-3">
                {{ (activity.start_date === '無資料' || activity.end_date === '無資料') ? '起訖時間無相關資訊'
                  : `${formatDate(activity.start_date)} ~ ${formatDate(activity.end_date)}` }}
              </span>
            </div>
            <!-- 主辦單位信息 -->
            <div class="flex items-center text-gray-700">
              <div class="w-12 flex justify-center">
                <i class="fas fa-building text-xl text-[#0F4BB4]" />
              </div>
              <span class="font-bold text-lg ml-1">主辦單位：</span>
              <span class="text-lg ml-3">{{ activity.organizer || '未提供' }}</span>
            </div>
            <!-- 票價信息 -->
            <div class="flex items-center text-gray-700">
              <div class="w-12 flex justify-center">
                <i class="fas fa-ticket-alt text-xl text-[#0F4BB4]" />
              </div>
              <span class="font-bold text-lg ml-1">票價資訊：</span>
              <span class="text-lg ml-3">{{ activity.ticket_price === '無資料' ? '無售票資訊' : (activity.ticket_price
                || '無售票資訊') }}</span>
            </div>
          </NSpace>

          <!-- 活動描述區域 -->
          <div class="space-y-4">
            <h2 class="text-xl font-semibold text-gray-900">
              活動介紹
            </h2>
            <div class="prose max-w-none">
              <p class="text-lg text-gray-600 leading-relaxed" style="text-indent: 2em !important;">
                {{ activity.description === '無資料' ? '無活動相關簡介及說明' : (activity.description
                  || '無活動相關簡介及說明') }}
              </p>
            </div>
          </div>

          <!-- Google Map 地圖顯示 -->
          <div v-if="activity.latitude && activity.longitude" class="space-y-4">
            <h2 class="text-xl font-semibold text-gray-900">
              <span class="text-lg mr-2">在 Google Maps 位置</span>
              <i class="fas fa-map-marked-alt text-2xl" />
            </h2>
            <div class="w-full h-[400px] rounded-lg overflow-hidden">
              <iframe
                :src="`https://maps.google.com/maps?q=${activity.latitude},${activity.longitude}&z=15&t=p&output=embed`"
                class="w-full h-full border-0" loading="lazy" referrerpolicy="no-referrer-when-downgrade"
              />
            </div>
          </div>

          <!-- 其他資訊區域 -->
          <div class="border-t pt-6 mt-6">
            <h2 class="text-xl font-semibold text-gray-900 mb-4">
              其他資訊
            </h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <!-- 相關連結區域 -->
              <div class="bg-gray-50 p-4 rounded-lg">
                <h3 class="font-medium text-lg text-gray-900 mb-2">
                  相關連結
                </h3>
                <a
                  v-if="activity.source_url" :href="activity.source_url" target="_blank"
                  class="text-blue-600 hover:underline"
                >
                  官方網站
                </a>
                <p v-else class="text-gray-600">
                  未提供
                </p>
              </div>

              <!-- 活動圖片列表區域 -->
              <div class="bg-gray-50 p-4 rounded-lg">
                <h3 class="font-medium text-lg text-gray-900 mb-2">
                  活動圖片列表
                </h3>
                <div class="grid grid-cols-2 md:grid-cols-3 gap-2">
                  <!-- 圖片縮略圖 -->
                  <div
                    v-for="(url, index) in getActivityImageUrls()" :key="index"
                    class="aspect-square relative overflow-hidden rounded-lg cursor-pointer"
                    @click="currentImageIndex = index"
                  >
                    <img
                      :src="url" :alt="`${activity.activity_name} 圖片 ${index + 1}`"
                      class="w-full h-full object-cover hover:opacity-75 transition-opacity" @error="handleImageError"
                    >
                    <!-- 圖片編號 -->
                    <div class="absolute bottom-0 right-0 bg-black/50 text-white px-2 py-1 text-xs">
                      {{ index + 1 }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </NCard>
    </template>
  </div>
</template>

<style scoped>
/* 載入動畫樣式 */
.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  /* 外圈顏色 */
  border-top: 4px solid #3498db;
  /* 旋轉部分顏色 */
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

/* 輪播按鈕基礎樣式 */
.carousel-button {
  background-color: rgba(255, 255, 255, 0.8);
  color: #1a1a1a;
  padding: 16px;
  border-radius: 50%;
  cursor: pointer;
  backdrop-filter: blur(4px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 輪播按鈕懸停效果 */
.carousel-button:hover {
  background-color: rgba(255, 255, 255, 0.95);
  transform: scale(1.1);
  box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15);
}

/* 輪播指示器基礎樣式 */
.carousel-indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background-color: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  border: 2px solid rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(4px);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  margin: 0 4px;
}

/* 輪播指示器啟動狀態 */
.carousel-indicator.active {
  background-color: white;
  transform: scale(1.2);
  border-color: white;
  box-shadow: 0 0 10px rgba(255, 255, 255, 0.5);
}

/* 載入動畫關鍵幀定義 */
@keyframes spin {
  0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(360deg);
  }
}

/* 響應式設計調整 */
@media (max-width: 768px) {
  .carousel-button {
    padding: 12px;
  }

  .carousel-indicator {
    width: 8px;
    height: 8px;
    margin: 0 3px;
  }
}

/* 移除舊的 icon-wrapper 相關樣式 */
.icon-wrapper {
  display: none;
}

.info-icon {
  display: none;
}
</style>

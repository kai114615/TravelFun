<script>
import axios from 'axios';
import { NButton, NCard, NIcon, NSpace } from 'naive-ui';
import { ArrowBackOutline, CalendarOutline, LocationOutline, TicketOutline } from '@vicons/ionicons5';
import ActivityList from './ActivityList.vue';

import { defaultActivityImages } from './ActivityList.vue'; // 引入預設圖片設定

export default {
  name: 'ActivityDetail',
  components: {
    NCard,
    NIcon,
    NButton,
    NSpace,
    LocationOutline,
    CalendarOutline,
    TicketOutline,
    ArrowBackOutline,
  },
  data() {
    return {
      activity: null,
      loading: true,
      error: null,
      defaultImages: defaultActivityImages,
      currentImageIndex: 0,
      randomDefaultImageIndex: Math.floor(Math.random() * defaultActivityImages.length), // 隨機選擇一個預設圖片索引
      hasMultipleImages: false, // 控制是否顯示輪播功能
    };
  },
  async created() {
    await this.fetchActivityDetail();
  },
  methods: {
    async fetchActivityDetail() {
      try {
        const id = this.$route.params.id;
        const response = await axios.get(`/theme_entertainment/activities/api/${id}/`);
        // this.activity = response.data;
        console.log(response.data);

        // 確保我們使用正確的數據結構
        if (response.data.status === 'success')
          this.activity = response.data.data;
        else
          throw new Error(response.data.message || '獲取數據失敗');
      }
      catch (error) {
        this.error = '無法載入活動詳細資訊';
        console.error('Error:', error);
      }
      finally {
        this.loading = false;
      }
    },
    formatDate(dateString) {
      if (!dateString)
        return '時間未定';
      return new Date(dateString).toLocaleDateString('zh-TW', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      });
    },
    goBack() {
      this.$router.back();
    },
    getImageUrl() {
      if (!this.activity)
        return '';

      let imageUrls = [];
      if (this.activity.image_url) {
        try {
          // 處理字串形式的 image_url
          if (typeof this.activity.image_url === 'string') {
            // 嘗試解析 JSON
            try {
              imageUrls = JSON.parse(this.activity.image_url);
            }
            catch {
              // 如果不是 JSON，檢查是否包含分隔符號
              if (this.activity.image_url.includes('|'))
                imageUrls = this.activity.image_url.split('|');
              else if (this.activity.image_url.includes(','))
                imageUrls = this.activity.image_url.split(',');
              else
                imageUrls = [this.activity.image_url];
            }
          }
          // 處理陣列形式的 image_url
          else if (Array.isArray(this.activity.image_url)) {
            imageUrls = this.activity.image_url;
          }

          // 過濾空值和清理 URL
          imageUrls = imageUrls
            .filter(url => url && url.trim())
            .map(url => url.trim());
        }
        catch (e) {
          console.error('圖片 URL 處理錯誤:', e);
          imageUrls = [];
        }
      }

      // 更新是否有多張圖片的狀態
      this.hasMultipleImages = imageUrls.length > 1;

      // 如果有有效的圖片 URL
      if (imageUrls.length > 0)
        return imageUrls[this.currentImageIndex % imageUrls.length];

      // 如果沒有有效的圖片，使用預設圖片
      return this.defaultImages[this.randomDefaultImageIndex];
    },
    handleImageError(e) {
      const activity = this.paginatedActivities.find(
        a => a.id === e.target.dataset.activityId,
      );
      if (activity) {
        const storageKey = `activity_image_${activity.id}`;
        const newIndex = this.getRandomUniqueImageIndex();
        localStorage.setItem(storageKey, newIndex);
        e.target.src = this.defaultImages[newIndex];
      }
      e.target.onerror = null;
    },
    prevImage() {
      const totalImages = this.getTotalImages();
      this.currentImageIndex = (this.currentImageIndex - 1 + totalImages) % totalImages;
    },
    nextImage() {
      const totalImages = this.getTotalImages();
      this.currentImageIndex = (this.currentImageIndex + 1) % totalImages;
    },
    getTotalImages() {
      if (!this.activity)
        return 1;

      const imageUrls = this.getAllImageUrls();
      return imageUrls.length || 1;
    },
    getAllImageUrls() {
      if (!this.activity)
        return [];

      let imageUrls = [];
      if (this.activity.image_url) {
        try {
          if (typeof this.activity.image_url === 'string') {
            try {
              imageUrls = JSON.parse(this.activity.image_url);
            }
            catch {
              if (this.activity.image_url.includes('|'))
                imageUrls = this.activity.image_url.split('|');
              else if (this.activity.image_url.includes(','))
                imageUrls = this.activity.image_url.split(',');
              else
                imageUrls = [this.activity.image_url];
            }
          }
          else if (Array.isArray(this.activity.image_url)) {
            imageUrls = this.activity.image_url;
          }

          // 過濾和清理 URL
          return imageUrls
            .filter(url => url && url.trim())
            .map(url => url.trim());
        }
        catch (e) {
          console.error('圖片 URL 列表處理錯誤:', e);
          return [];
        }
      }
      return [];
    },
  },
};
</script>

<template>
  <div class="max-w-4xl mx-auto px-4 py-8">
    <!-- 返回按鈕 -->
    <div class="mb-6">
      <NButton class="flex items-center" @click="goBack">
        <template #icon>
          <NIcon>
            <ArrowBackOutline />
          </NIcon>
        </template>
        返回活動列表
      </NButton>
    </div>

    <template v-if="loading">
      <div class="text-center py-12">
        <div class="loading-spinner mx-auto mb-4" />
        <p class="text-gray-600">
          載入中...
        </p>
      </div>
    </template>

    <template v-else-if="error">
      <NCard class="bg-red-50 border border-red-200">
        <p class="text-red-600">
          {{ error }}
        </p>
      </NCard>
    </template>

    <template v-else>
      <NCard class="overflow-hidden">
        <!-- 活動圖片 -->
        <div class="relative aspect-video mb-6 overflow-hidden rounded-lg">
          <img
            :src="getImageUrl()" :alt="activity.activity_name" class="w-full h-full object-cover"
            @error="handleImageError"
          >

          <!-- 輪播控制按鈕 - 只在多張圖片時顯示 -->
          <div
            v-if="hasMultipleImages"
            class="absolute inset-0 flex items-center justify-between px-4 opacity-0 hover:opacity-100 transition-opacity"
          >
            <button
              class="bg-black/50 text-white p-2 rounded-full hover:bg-black/70 transition-colors"
              @click="prevImage"
            >
              <i class="fas fa-chevron-left" />
            </button>
            <button
              class="bg-black/50 text-white p-2 rounded-full hover:bg-black/70 transition-colors"
              @click="nextImage"
            >
              <i class="fas fa-chevron-right" />
            </button>
          </div>

          <!-- 圖片指示器 - 只在多張圖片時顯示 -->
          <div v-if="hasMultipleImages" class="absolute bottom-4 left-1/2 transform -translate-x-1/2 flex space-x-2">
            <button
              v-for="index in getTotalImages()" :key="index" class="w-2 h-2 rounded-full transition-all"
              :class="index - 1 === currentImageIndex ? 'bg-white scale-125' : 'bg-white/50'"
              @click="currentImageIndex = index - 1"
            />
          </div>
        </div>

        <!-- 活動內容 -->
        <div class="space-y-6">
          <!-- 標題區 -->
          <div>
            <h1 class="text-3xl font-bold text-gray-900 mb-2">
              {{ activity.activity_name }}
            </h1>
            <div class="flex items-center text-sm text-gray-500">
              <span class="mr-4">ID: {{ activity.id }}</span>
              <span>建立時間: {{ formatDate(activity.created_at) }}</span>
            </div>
          </div>

          <!-- 基本資訊 -->
          <NSpace vertical class="bg-gray-50 p-4 rounded-lg">
            <div class="flex items-center text-gray-700">
              <NIcon class="mr-2 text-blue-500">
                <LocationOutline />
              </NIcon>
              <span class="font-medium">活動地點：</span>
              <span class="ml-2">{{ activity.location || '地點未定' }}</span>
            </div>
            <div class="flex items-center text-gray-700">
              <NIcon class="mr-2 text-blue-500">
                <CalendarOutline />
              </NIcon>
              <span class="font-medium">活動日期：</span>
              <span class="ml-2">
                {{ formatDate(activity.start_date) }} ~ {{ formatDate(activity.end_date) }}
              </span>
            </div>
            <div class="flex items-center text-gray-700">
              <NIcon class="mr-2 text-blue-500">
                <TicketOutline />
              </NIcon>
              <span class="font-medium">主辦單位：</span>
              <span class="ml-2">{{ activity.organizer || '免費' }}</span>
            </div>
            <div class="flex items-center text-gray-700">
              <NIcon class="mr-2 text-blue-500">
                <TicketOutline />
              </NIcon>
              <span class="font-medium">票價資訊：</span>
              <span class="ml-2">{{ activity.ticket_price || '免費' }}</span>
            </div>
          </NSpace>

          <!-- 活動描述 -->
          <div class="space-y-4">
            <h2 class="text-xl font-semibold text-gray-900">
              活動介紹
            </h2>
            <div class="prose max-w-none">
              <p class="text-gray-600 leading-relaxed">
                {{ activity.description }}
              </p>
            </div>
          </div>

          <!-- 其他資訊 -->
          <div class="border-t pt-6 mt-6">
            <h2 class="text-xl font-semibold text-gray-900 mb-4">
              其他資訊
            </h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div class="bg-gray-50 p-4 rounded-lg">
                <h3 class="font-medium text-gray-900 mb-2">
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
              <div class="bg-gray-50 p-4 rounded-lg">
                <h3 class="font-medium text-gray-900 mb-2">
                  活動圖片列表
                </h3>
                <div class="grid grid-cols-2 md:grid-cols-3 gap-2">
                  <div
                    v-for="(url, index) in getAllImageUrls()" :key="index"
                    class="aspect-square relative overflow-hidden rounded-lg cursor-pointer"
                    @click="currentImageIndex = index"
                  >
                    <img
                      :src="url" :alt="`${activity.activity_name} 圖片 ${index + 1}`"
                      class="w-full h-full object-cover hover:opacity-75 transition-opacity" @error="handleImageError"
                    >
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
.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(360deg);
  }
}

/* 添加新的輪播相關樣式 */
.carousel-button {
  @apply bg-black/50 text-white p-2 rounded-full hover:bg-black/70 transition-colors;
}

.carousel-indicator {
  @apply w-2 h-2 rounded-full transition-all;
}

.carousel-indicator.active {
  @apply bg-white scale-125;
}

.carousel-indicator:not(.active) {
  @apply bg-white/50;
}
</style>

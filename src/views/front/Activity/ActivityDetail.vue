<script>
import axios from 'axios';
import { NButton, NCard, NIcon, NSpace } from 'naive-ui';
import { ArrowBackOutline, CalendarOutline, LocationOutline, TicketOutline } from '@vicons/ionicons5';
import ActivityList from './ActivityList.vue';

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
      defaultImages: [
        'https://images.unsplash.com/photo-1504280390367-361c6d9f38f4?w=800&auto=format&fit=crop&q=80',
        'https://images.unsplash.com/photo-1522163182402-834f871fd851?w=800&auto=format&fit=crop&q=80',
        'https://images.unsplash.com/photo-1502680390469-be75c86b636f?w=800&auto=format&fit=crop&q=80',
      ],
      currentImageIndex: 0,
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

      if (Array.isArray(this.activity.image_url) && this.activity.image_url.length > 0)
        return this.activity.image_url[this.currentImageIndex];

      if (typeof this.activity.image_url === 'string' && this.activity.image_url)
        return this.activity.image_url;

      return this.defaultImages[this.currentImageIndex % this.defaultImages.length];
    },
    handleImageError(e) {
      const randomIndex = Math.floor(Math.random() * this.defaultImages.length);
      e.target.src = this.defaultImages[randomIndex];
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
      if (Array.isArray(this.activity?.image_url))
        return this.activity.image_url.length;

      if (typeof this.activity?.image_url === 'string')
        return 1;

      return this.defaultImages.length;
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

          <!-- 輪播控制按鈕 -->
          <div
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

          <!-- 圖片指示器 -->
          <div class="absolute bottom-4 left-1/2 transform -translate-x-1/2 flex space-x-2">
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
                  主辦單位
                </h3>
                <p class="text-gray-600">
                  {{ activity.organizer || '未提供' }}
                </p>
              </div>
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

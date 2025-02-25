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
    };
  },
  async created() {
    await this.fetchActivityDetail();
  },
  methods: {
    async fetchActivityDetail() {
      try {
        const id = this.$route.params.id;
        const response = await axios.get(`/theme_entertainment/activities/api/${event_id}/`);
        this.activity = response.data;
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
  },
};
</script>

<template>
  <div class="max-w-4xl mx-auto px-4 py-8">
    <!-- 返回按鈕 -->
    <div class="mb-6">
      <NButton class="flex items-center" @click="goBack">
        <template #icon>
          <NIcon><ArrowBackOutline /></NIcon>
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
          <img :src="activity.image_url" :alt="activity.activity_name" class="w-full h-full object-cover">
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
</style>

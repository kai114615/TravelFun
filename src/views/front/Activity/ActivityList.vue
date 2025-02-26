<script>
import axios from 'axios';
import { NButton, NCard, NIcon, NPagination } from 'naive-ui';
import { CalendarOutline, LocationOutline, TicketOutline } from '@vicons/ionicons5';

export default {
  name: 'ActivityList',
  components: {
    NCard,
    NButton,
    NPagination,
    NIcon,
    LocationOutline,
    CalendarOutline,
    TicketOutline,
  },
  data() {
    return {
      activities: [],
      allActivities: [], // 儲存所有活動的原始資料
      loading: false,
      error: null,
      searchQuery: '', // 新增搜尋查詢字串
      baseURL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000',
      currentPage: 1,
      itemsPerPage: 12,
      maxDisplayPages: 5,
      searchDate: '',
      minDate: '',
      maxDate: '',
      defaultImages: [
        // 露營 Camping
        'https://images.unsplash.com/photo-1504280390367-361c6d9f38f4?w=800&auto=format&fit=crop&q=80',
        // 攀岩 Climbing
        'https://images.unsplash.com/photo-1522163182402-834f871fd851?w=800&auto=format&fit=crop&q=80',
        // 衝浪 Surfing
        'https://images.unsplash.com/photo-1502680390469-be75c86b636f?w=800&auto=format&fit=crop&q=80',
        // 健行 Hiking
        'https://images.unsplash.com/photo-1551632811-561732d1e306?w=800&auto=format&fit=crop&q=80',
        // 單車 Cycling
        'https://images.unsplash.com/photo-1541625602330-2277a4c46182?w=800&auto=format&fit=crop&q=80',
        // 游泳 Swimming
        'https://images.unsplash.com/photo-1530549387789-4c1017266635?w=800&auto=format&fit=crop&q=80',
        // 瑜珈 Yoga
        'https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=800&auto=format&fit=crop&q=80',
        // 跑步 Running
        'https://images.unsplash.com/photo-1552674605-db6ffd4facb5?w=800&auto=format&fit=crop&q=80',
        // 滑板 Skateboarding
        'https://images.unsplash.com/photo-1520045892732-304bc3ac5d8e?w=800&auto=format&fit=crop&q=80',
        // 籃球 Basketball
        'https://images.unsplash.com/photo-1546519638-68e109498ffc?w=800&auto=format&fit=crop&q=80',
        // 網球 Tennis
        'https://images.unsplash.com/photo-1595435934249-5df7ed86e1c0?w=800&auto=format&fit=crop&q=80',
        // 高爾夫 Golf
        'https://images.unsplash.com/photo-1535131749006-b7f58c99034b?w=800&auto=format&fit=crop&q=80',
        // 舞蹈 Dancing
        'https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?w=800&auto=format&fit=crop&q=80',
        // 攝影 Photography
        'https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=800&auto=format&fit=crop&q=80',
        // 繪畫 Painting
        'https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=800&auto=format&fit=crop&q=80',
        // 烹飪 Cooking
        'https://images.unsplash.com/photo-1556911220-bff31c812dba?w=800&auto=format&fit=crop&q=80',
        // 園藝 Gardening
        'https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=800&auto=format&fit=crop&q=80',
        // 手工藝 Crafting
        'https://images.unsplash.com/photo-1452860606245-08befc0ff44b?w=800&auto=format&fit=crop&q=80',
        // 音樂 Music
        'https://images.unsplash.com/photo-1511379938547-c1f69419868d?w=800&auto=format&fit=crop&q=80',
        // 冥想 Meditation
        'https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=800&auto=format&fit=crop&q=80',
        // 寵物 Pets
        'https://images.unsplash.com/photo-1450778869180-41d0601e046e?w=800&auto=format&fit=crop&q=80',
        // 閱讀 Reading
        'https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?w=800&auto=format&fit=crop&q=80',
        // 遊戲 Gaming
        'https://images.unsplash.com/photo-1538481199705-c710c4e965fc?w=800&auto=format&fit=crop&q=80',
        // 旅行 Traveling
        'https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=800&auto=format&fit=crop&q=80',
        // 露營車 RV Camping
        'https://images.unsplash.com/photo-1523987355523-c7b5b0dd90a7?w=800&auto=format&fit=crop&q=80',
      ],
      currentImageIndexes: {}, // 改用 localStorage 來持久化儲存
    };
  },
  computed: {
    totalPages() {
      return Math.ceil(this.activities.length / this.itemsPerPage);
    },

    paginatedActivities() {
      const start = (this.currentPage - 1) * this.itemsPerPage;
      const end = start + this.itemsPerPage;
      return this.activities.slice(start, end);
    },

    displayedPages() {
      let start = Math.max(1, this.currentPage - Math.floor(this.maxDisplayPages / 2));
      const end = Math.min(this.totalPages, start + this.maxDisplayPages - 1);

      if (end - start + 1 < this.maxDisplayPages)
        start = Math.max(1, end - this.maxDisplayPages + 1);

      return Array.from({ length: end - start + 1 }, (_, i) => start + i);
    },
  },
  watch: {
    searchQuery: {
      handler(newVal, oldVal) {
        if (newVal !== oldVal)
          this.handleSearch();
      },
      immediate: false,
    },
    searchDate: {
      handler(newVal, oldVal) {
        if (newVal !== oldVal)
          this.handleSearch();
      },
      immediate: false,
    },
  },
  mounted() {
    this.fetchActivities();
    const today = new Date();
    this.minDate = new Date(today.getFullYear() - 1, today.getMonth(), today.getDate())
      .toISOString().split('T')[0];
    this.maxDate = new Date(today.getFullYear() + 1, today.getMonth(), today.getDate())
      .toISOString().split('T')[0];
  },
  methods: {
    async fetchActivities() {
      this.loading = true;
      this.error = null;

      try {
        // 首先嘗試使用本地 JSON 檔案
        const localData = await import('@/assets/theme_entertainment/events_data.json');
        if (Array.isArray(localData.default)) {
          this.allActivities = this.sortActivities(localData.default);
          this.activities = [...this.allActivities];
          console.log('使用本地數據');
        }
      }
      catch (localError) {
        console.error('Local data error:', localError);

        // 如果本地數據載入失敗，嘗試從 API 獲取
        try {
          const response = await axios.get('/theme_entertainment/activities/api/list/');
          const data = response.data;

          if (Array.isArray(data)) {
            this.allActivities = this.sortActivities(data);
            this.activities = [...this.allActivities];
          }
          else if (data.status === 'success' && Array.isArray(data.data)) {
            this.allActivities = this.sortActivities(data.data);
            this.activities = [...this.allActivities];
          }
          else {
            throw new Error('API 返回的數據格式無效');
          }
        }
        catch (apiError) {
          console.error('API Error:', apiError);
          this.error = '無法載入活動資料，請稍後再試';
        }
      }
      finally {
        this.loading = false;
      }
    },

    sortActivities(activities) {
      const now = new Date();

      // 將活動分類
      const categorizedActivities = activities.reduce((acc, activity) => {
        const startDate = new Date(activity.start_date);
        const endDate = new Date(activity.end_date);

        if (now < startDate)
          acc.upcoming.push({ ...activity, timeDistance: startDate - now });
        else if (now > endDate)
          acc.ended.push({ ...activity, timeDistance: endDate - now });
        else
          acc.ongoing.push({ ...activity, timeDistance: startDate - now });

        return acc;
      }, { upcoming: [], ongoing: [], ended: [] });

      // 排序每個類別
      categorizedActivities.upcoming.sort((a, b) => a.timeDistance - b.timeDistance);
      categorizedActivities.ongoing.sort((a, b) => a.timeDistance - b.timeDistance);
      categorizedActivities.ended.sort((a, b) => b.timeDistance - a.timeDistance);

      // 合併所有活動：即將開始 -> 進行中 -> 已結束
      return [
        ...categorizedActivities.upcoming,
        ...categorizedActivities.ongoing,
        ...categorizedActivities.ended,
      ];
    },

    handleSearch() {
      const query = this.searchQuery.trim();
      const searchDate = this.searchDate ? new Date(this.searchDate) : null;

      if (!query && !searchDate) {
        this.activities = [...this.allActivities]; // 已排序的活動列表
      }
      else {
        const filteredActivities = this.allActivities.filter((activity) => {
          const matchesQuery = !query
            || activity.activity_name?.toLowerCase().includes(query.toLowerCase())
            || activity.location?.toLowerCase().includes(query.toLowerCase())
            || activity.description?.toLowerCase().includes(query.toLowerCase());

          const matchesDate = !searchDate
            || (new Date(activity.start_date) <= searchDate
              && new Date(activity.end_date) >= searchDate);

          return matchesQuery && matchesDate;
        });

        this.activities = filteredActivities; // 保持原有排序
      }

      if (this.currentPage !== 1)
        this.currentPage = 1;
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

    getImageUrl(activity) {
      // 如果活動有自己的圖片，優先使用
      if (Array.isArray(activity.image_url) && activity.image_url.length > 0)
        return activity.image_url[0];

      if (activity.image_url)
        return activity.image_url;

      // 使用 localStorage 來保存圖片分配
      const storageKey = `activity_image_${activity.id}`;
      let imageIndex = localStorage.getItem(storageKey);

      // 如果沒有儲存過，分配新的圖片索引
      if (imageIndex === null) {
        imageIndex = this.getRandomUniqueImageIndex();
        localStorage.setItem(storageKey, imageIndex);
      }

      return this.defaultImages[Number.parseInt(imageIndex)];
    },

    getRandomUniqueImageIndex() {
      // 從 localStorage 獲取所有已使用的索引
      const usedIndexes = new Set();
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key.startsWith('activity_image_'))
          usedIndexes.add(Number.parseInt(localStorage.getItem(key)));
      }

      // 獲取可用的索引
      let availableIndexes = Array.from(
        { length: this.defaultImages.length },
        (_, i) => i,
      ).filter(i => !usedIndexes.has(i));

      // 如果所有圖片都被使用過，重新開始分配
      if (availableIndexes.length === 0) {
        availableIndexes = Array.from(
          { length: this.defaultImages.length },
          (_, i) => i,
        );
      }

      // 隨機選擇一個可用索引
      return availableIndexes[Math.floor(Math.random() * availableIndexes.length)];
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

    getStatusText(activity) {
      // 如果沒有開始或結束日期，返回未知狀態
      if (!activity.start_date || !activity.end_date)
        return '未知';

      // 獲取今天的日期（不含時間）
      const today = new Date();
      today.setHours(0, 0, 0, 0);

      // 獲取3天後的日期
      const threeDaysLater = new Date(today);
      threeDaysLater.setDate(today.getDate() + 3);

      const startDate = new Date(activity.start_date);
      startDate.setHours(0, 0, 0, 0);
      const endDate = new Date(activity.end_date);
      endDate.setHours(23, 59, 59, 999);

      // 如果開始日期在今天到3天內，則為"即將開始"
      if (startDate > today && startDate <= threeDaysLater)
        return '即將開始';

      // 如果今天在活動期間內（包含開始日和結束日），則為"進行中"
      if (today >= startDate && today <= endDate)
        return '進行中';

      // 如果結束日期在今天之前，則為"已結束"
      if (endDate < today)
        return '已結束';

      // 開始日期在3天後
      if (startDate > threeDaysLater)
        return '未開始';

      return '進行中';
    },

    getStatusClass(activity) {
      const status = this.getStatusText(activity);
      return {
        'status-upcoming': status === '即將開始',
        'status-ongoing': status === '進行中',
        'status-ended': status === '已結束',
      };
    },

    changePage(page) {
      if (page >= 1 && page <= this.totalPages) {
        this.currentPage = page;
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    },

    viewDetails(activity) {
      this.$router.push({
        name: 'ActivityDetail',
        params: { id: activity.uid },
      });
    },

    // 輪播控制方法
    prevImage(activityId) {
      const images = this.activities.find(a => a.id === activityId).image_url;
      const currentIndex = this.currentImageIndexes[activityId] || 0;
      this.currentImageIndexes[activityId] = (currentIndex - 1 + images.length) % images.length;
    },

    nextImage(activityId) {
      const images = this.activities.find(a => a.id === activityId).image_url;
      const currentIndex = this.currentImageIndexes[activityId] || 0;
      this.currentImageIndexes[activityId] = (currentIndex + 1) % images.length;
    },

    setImage(activityId, index) {
      this.currentImageIndexes[activityId] = index;
    },
  },
};
</script>

<template>
  <div class="activity-list">
    <div class="search-container">
      <div class="search-bar">
        <input v-model="searchQuery" type="text" placeholder="搜尋活動名稱、地點..." class="search-input">
        <div class="date-picker-container">
          <input v-model="searchDate" type="date" class="date-input" :min="minDate" :max="maxDate">
        </div>
        <button class="search-button" @click="handleSearch">
          <i class="fas fa-search" />
        </button>
      </div>
    </div>

    <template v-if="loading">
      <div class="loading-state">
        <div class="loading-spinner" />
        <p>載入活動資料中...</p>
      </div>
    </template>

    <template v-else-if="error">
      <div class="error-state">
        <p>{{ error }}</p>
        <button class="retry-button" @click="fetchActivities">
          重試
        </button>
      </div>
    </template>

    <template v-else>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-4">
        <template v-for="activity in paginatedActivities" :key="activity.id">
          <NCard
            class="activity-card transform transition-all duration-300 hover:-translate-y-1" :bordered="false"
            size="medium" :segmented="{ content: true }" :hoverable="true"
            style="box-shadow: 0 2px 8px rgba(0,0,0,0.08);"
          >
            <!-- 圖片容器 -->
            <div class="relative aspect-[16/9] overflow-hidden rounded-t-lg">
              <img
                :src="getImageUrl(activity)" :alt="activity.activity_name" :data-activity-id="activity.id"
                class="w-full h-full object-cover" @error="handleImageError"
              >
              <!-- 活動狀態標籤 -->
              <div
                class="absolute top-3 right-3 px-4 py-1.5 min-w-[80px] text-center rounded-md text-sm font-medium text-white transition-transform duration-300"
                :class="[
                  {
                    'bg-yellow-500/80': getStatusText(activity) === '即將開始',
                    'bg-green-500/80 animate-pulse-soft': getStatusText(activity) === '進行中',
                    'bg-gray-400/80': getStatusText(activity) === '已結束',
                    'bg-amber-900/80': getStatusText(activity) === '未知',
                    'bg-gray-700/80': getStatusText(activity) === '未開始',
                  },
                ]"
              >
                {{ getStatusText(activity) }}
              </div>
            </div>

            <!-- 活動內容 -->
            <div class="p-4">
              <!-- 活動標題 -->
              <h3 class="text-lg font-semibold text-gray-900 mb-2 line-clamp-2">
                {{ activity.activity_name }}
              </h3>

              <!-- 活動資訊 -->
              <div class="space-y-2 text-sm text-gray-600">
                <div class="flex items-center">
                  <NIcon class="mr-2">
                    <LocationOutline />
                  </NIcon>
                  {{ activity.location || '地點未定' }}
                </div>
                <div class="flex items-center">
                  <NIcon class="mr-2">
                    <CalendarOutline />
                  </NIcon>
                  {{ formatDate(activity.start_date) }} ~ {{ formatDate(activity.end_date) }}
                </div>
                <div class="flex items-center">
                  <NIcon class="mr-2">
                    <TicketOutline />
                  </NIcon>
                  {{ activity.ticket_price || '免費' }}
                </div>
              </div>

              <!-- 活動描述 -->
              <p class="mt-3 text-sm text-gray-500 line-clamp-2">
                {{ activity.description }}
              </p>

              <!-- 按鈕區域 -->
              <div class="mt-4 flex justify-end">
                <NButton
                  type="primary" size="small" class="hover:shadow-md transition-shadow"
                  @click="viewDetails(activity)"
                >
                  查看詳情
                </NButton>
              </div>
            </div>
          </NCard>
        </template>
      </div>

      <div class="flex justify-center mt-8 mb-12">
        <NPagination
          v-model:page="currentPage" :page-count="totalPages" :page-sizes="[12, 24, 36]" show-size-picker
          @update:page="changePage"
        />
      </div>
    </template>
  </div>
</template>

<style scoped>
/* 主要容器樣式 */
.activity-list {
  max-width: 80rem;
  margin: 0 auto;
  padding: 0 1rem;
}

/* 搜尋區塊樣式 */
.search-container {
  margin-bottom: 2rem;
}

.search-bar {
  width: 100%;
  max-width: 800px;
  display: flex;
  align-items: center;
  background: #fff;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  overflow: hidden;
  gap: 15px;
}

.search-input {
  flex: 1;
  padding: 10px 15px;
  border: none;
  outline: none;
  font-size: 14px;
  color: #495057;
}

.search-button {
  padding: 10px 20px;
  background: #007bff;
  color: white;
  border: none;
  cursor: pointer;
  transition: background 0.2s;
}

.search-button:hover {
  background: #0056b3;
}

/* 日期選擇器樣式 */
.date-picker-container {
  min-width: 150px;
}

.date-input {
  padding: 10px 15px;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  font-size: 14px;
  color: #495057;
  background-color: #fff;
  outline: none;
  transition: border-color 0.2s;
}

.date-input:focus {
  border-color: #80bdff;
  box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
}

/* 載入狀態樣式 */
.loading-state {
  text-align: center;
  padding: 30px;
  color: #6c757d;
}

.loading-spinner {
  border: 3px solid #f3f3f3;
  border-top: 3px solid #007bff;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  animation: spin 1s linear infinite;
  margin: 0 auto 15px;
}

/* 錯誤狀態樣式 */
.error-state {
  text-align: center;
  padding: 30px;
  color: #dc3545;
}

.retry-button {
  margin-top: 12px;
  padding: 6px 12px;
  background-color: #dc3545;
  color: white;
  border: none;
  border-radius: 3px;
  cursor: pointer;
  font-size: 14px;
}

.retry-button:hover {
  background-color: #c82333;
}

/* 輪播樣式 */
.carousel {
  position: relative;
  height: 100%;
  width: 100%;
}

.carousel img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: opacity 0.3s ease;
}

.carousel-controls {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 10px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.carousel:hover .carousel-controls {
  opacity: 1;
}

.carousel-btn {
  background-color: rgba(0, 0, 0, 0.5);
  color: white;
  border: none;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.carousel-btn:hover {
  background-color: rgba(0, 0, 0, 0.7);
}

.carousel-indicators {
  position: absolute;
  bottom: 10px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 6px;
}

.indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  transition: all 0.3s ease;
}

.indicator.active {
  background-color: white;
  transform: scale(1.2);
}

@keyframes pulse-soft {

  0%,
  100% {
    transform: scale(1);
  }

  50% {
    transform: scale(1.05);
  }
}

.animate-pulse-soft {
  animation: pulse-soft 2s ease-in-out infinite;
}
</style>

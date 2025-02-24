<script>
import axios from 'axios';

export default {
  name: 'ActivityList',
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
      usedImageIndexes: new Set(), // 追蹤已使用的圖片索引
      currentImageIndexes: {}, // 儲存每個活動當前顯示的圖片索引
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
        return '待定';
      return new Date(dateString).toLocaleDateString('zh-TW', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      });
    },

    getRandomUniqueImageIndex() {
      let availableIndexes = Array.from(
        { length: this.defaultImages.length },
        (_, i) => i,
      ).filter(i => !this.usedImageIndexes.has(i));

      // 如果所有圖片都被使用過，重置追蹤器
      if (availableIndexes.length === 0) {
        this.usedImageIndexes.clear();
        availableIndexes = Array.from(
          { length: this.defaultImages.length },
          (_, i) => i,
        );
      }

      const randomIndex = availableIndexes[
        Math.floor(Math.random() * availableIndexes.length)
      ];
      this.usedImageIndexes.add(randomIndex);

      // 保持追蹤器大小在合理範圍
      if (this.usedImageIndexes.size > this.itemsPerPage) {
        const firstUsed = Array.from(this.usedImageIndexes)[0];
        this.usedImageIndexes.delete(firstUsed);
      }

      return randomIndex;
    },

    getImageUrl(activity) {
      if (Array.isArray(activity.image_url) && activity.image_url.length > 0)
        return activity.image_url[0]; // 返回第一張圖片

      if (activity.image_url)
        return activity.image_url;

      const index = this.getRandomUniqueImageIndex();
      return this.defaultImages[index];
    },

    handleImageError(e) {
      const index = this.getRandomUniqueImageIndex();
      e.target.src = this.defaultImages[index];
      e.target.onerror = null;
    },

    getStatusText(activity) {
      const now = new Date();
      const startDate = new Date(activity.start_date);
      const endDate = new Date(activity.end_date);

      if (now < startDate)
        return '即將開始';
      if (now > endDate)
        return '已結束';
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
        this.usedImageIndexes.clear(); // 重置已使用的圖片記錄
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    },

    viewDetails(activity) {
      this.$router.push(`/activity/${activity.id}`);
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
      <div class="activities-container">
        <div v-for="activity in paginatedActivities" :key="activity.id" class="activity-card">
          <div class="activity-image">
            <div v-if="Array.isArray(activity.image_url) && activity.image_url.length > 0" class="carousel">
              <img
                :src="activity.image_url[currentImageIndexes[activity.id] || 0]" :alt="activity.activity_name"
                loading="lazy" @error="handleImageError"
              >
              <div v-if="activity.image_url.length > 1" class="carousel-controls">
                <button class="carousel-btn prev" @click="prevImage(activity.id)">
                  <i class="fas fa-chevron-left" />
                </button>
                <button class="carousel-btn next" @click="nextImage(activity.id)">
                  <i class="fas fa-chevron-right" />
                </button>
                <div class="carousel-indicators">
                  <span
                    v-for="(_, index) in activity.image_url" :key="index"
                    class="indicator" :class="[{ active: (currentImageIndexes[activity.id] || 0) === index }]"
                    @click="setImage(activity.id, index)"
                  />
                </div>
              </div>
            </div>
            <img
              v-else :src="getImageUrl(activity)" :alt="activity.activity_name" loading="lazy"
              @error="handleImageError"
            >
          </div>
          <div class="activity-content">
            <h2 class="activity-title">
              {{ activity.activity_name }}
            </h2>
            <div class="activity-details">
              <p class="activity-date">
                <i class="fas fa-calendar-alt" />
                {{ formatDate(activity.start_date) }} - {{ formatDate(activity.end_date) }}
              </p>
              <p class="activity-location">
                <i class="fas fa-map-marker-alt" />
                {{ activity.location }}
              </p>
            </div>
            <div class="content-divider" />
            <p class="activity-description">
              {{ activity.description }}
            </p>
            <div class="activity-status" :class="getStatusClass(activity)">
              {{ getStatusText(activity) }}
            </div>
            <div class="activity-footer">
              <button class="detail-button" @click="viewDetails(activity)">
                <i class="fas fa-info-circle" />
                活動詳情
              </button>
            </div>
          </div>
        </div>
      </div>

      <div v-if="totalPages > 1" class="pagination">
        <button :disabled="currentPage === 1" class="page-button" title="第一頁" @click="changePage(1)">
          <i class="fas fa-angle-double-left" />
        </button>

        <button :disabled="currentPage === 1" class="page-button" title="上一頁" @click="changePage(currentPage - 1)">
          <i class="fas fa-angle-left" />
        </button>

        <button
          v-for="page in displayedPages" :key="page" class="page-button" :class="[{ active: currentPage === page }]"
          @click="changePage(page)"
        >
          {{ page }}
        </button>

        <button
          :disabled="currentPage === totalPages" class="page-button" title="下一頁"
          @click="changePage(currentPage + 1)"
        >
          <i class="fas fa-angle-right" />
        </button>

        <button :disabled="currentPage === totalPages" class="page-button" title="最後一頁" @click="changePage(totalPages)">
          <i class="fas fa-angle-double-right" />
        </button>
      </div>
    </template>
  </div>
</template>

<style scoped>
/* 主要容器樣式 */
.activity-list {
  min-height: 100vh;
  background-color: #f8f9fa;
  padding: 20px;
}

/* 搜尋區塊樣式 */
.search-container {
  width: 100%;
  padding: 15px;
  background: #fff;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
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

/* 活動卡片容器樣式 */
.activities-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
  margin: 0 auto;
  padding: 15px;
}

/* 活動卡片樣式 */
.activity-card {
  background: white;
  border-radius: 4px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;
  border: 1px solid #dee2e6;
  position: relative;
}

.activity-card:hover {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.activity-image {
  height: 200px;
  overflow: hidden;
  position: relative;
  border-bottom: 1px solid #dee2e6;
  background-color: #f8f9fa;
}

.activity-image::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 40%;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.2), transparent);
}

.activity-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
  background-color: #f8f9fa;
}

.activity-card:hover .activity-image img {
  transform: scale(1.05);
}

.activity-content {
  padding: 20px;
  text-align: left;
}

.activity-title {
  font-size: 18px;
  font-weight: 600;
  color: #212529;
  margin-bottom: 12px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  line-clamp: 2;
  overflow: hidden;
}

.activity-details {
  margin: 12px 0;
  color: #495057;
}

.activity-details p {
  display: flex;
  align-items: center;
  margin: 8px 0;
  font-size: 14px;
}

.activity-details i {
  width: 20px;
  margin-right: 10px;
  color: #6c757d;
  font-size: 15px;
  text-align: center;
}

.content-divider {
  height: 1px;
  background-color: #dee2e6;
  margin: 12px 0;
}

.activity-description {
  margin: 12px 0;
  color: #6c757d;
  line-height: 1.6;
  font-size: 14px;
  text-align: left;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  line-clamp: 2;
  overflow: hidden;
  max-height: 44px;
  position: relative;
  word-break: break-word;
}

.activity-description::after {
  content: '';
  position: absolute;
  bottom: 0;
  right: 0;
  width: 40px;
  height: 22px;
  background: linear-gradient(to right, transparent, white);
}

/* 活動狀態樣式 */
.activity-status {
  display: inline-block;
  padding: 6px 12px;
  border-radius: 3px;
  font-size: 12px;
  font-weight: 500;
  position: absolute;
  top: 12px;
  right: 12px;
  backdrop-filter: blur(4px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  min-width: 72px;
  /* 根據「即將開始」的寬度設置 */
  text-align: center;
}

.status-upcoming {
  background-color: rgba(52, 58, 64, 0.6);
  /* 提高透明度 */
  color: #ffffff;
  border: 1px solid rgba(255, 255, 255, 0.15);
  /* 調整邊框透明度 */
}

.status-ongoing {
  background-color: rgba(40, 167, 69, 0.6);
  /* 保持一致的透明度 */
  color: #ffffff;
  border: 1px solid rgba(255, 255, 255, 0.15);
}

.status-ended {
  background-color: rgba(108, 117, 125, 0.6);
  /* 保持一致的透明度 */
  color: #ffffff;
  border: 1px solid rgba(255, 255, 255, 0.15);
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

/* 響應式設計 */
@media (max-width: 768px) {
  .activities-container {
    grid-template-columns: 1fr;
    padding: 10px;
  }

  .activity-card {
    margin-bottom: 15px;
  }
}

/* 分頁樣式 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  margin: 30px 0;
  padding: 15px;
}

.page-button {
  min-width: 36px;
  height: 36px;
  padding: 0 12px;
  border: 1px solid #dee2e6;
  background-color: #fff;
  color: #495057;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  margin: 0 2px;
}

.page-button i {
  font-size: 12px;
}

.page-button:first-child,
.page-button:last-child {
  font-size: 12px;
}

.page-button:hover:not(:disabled) {
  background-color: #e9ecef;
  border-color: #dee2e6;
  color: #007bff;
}

.page-button.active {
  background-color: #007bff;
  border-color: #007bff;
  color: #fff;
}

.page-button:disabled {
  background-color: #f8f9fa;
  border-color: #dee2e6;
  color: #6c757d;
  cursor: not-allowed;
}

/* 響應式設計補充 */
@media (max-width: 768px) {
  .pagination {
    gap: 4px;
  }

  .page-button {
    min-width: 32px;
    height: 32px;
    padding: 0 8px;
  }

  /* 在移動端隱藏部分頁碼 */
  .page-button:not(:first-child):not(:last-child):not(.active) {
    display: none;
  }
}

/* 活動卡片底部樣式 */
.activity-footer {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #dee2e6;
  text-align: right;
}

.detail-button {
  padding: 6px 12px;
  background-color: #343a40;
  /* 改用深色系 */
  color: #fff;
  border: none;
  border-radius: 3px;
  font-size: 13px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  transition: all 0.2s;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.detail-button:hover {
  background-color: #23272b;
  /* 深色系的 hover 狀態 */
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
}

.detail-button i {
  font-size: 12px;
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
</style>

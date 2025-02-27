<script>
import axios from 'axios';
import { NButton, NCard, NIcon, NPagination, NSelect } from 'naive-ui';
import { CalendarOutline, LocationOutline, TicketOutline } from '@vicons/ionicons5';

// 導出預設圖片陣列
export const defaultActivityImages = [
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
];

export default {
  name: 'ActivityList',
  components: {
    NCard,
    NButton,
    NPagination,
    NIcon,
    NSelect,
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
      defaultImages: defaultActivityImages, // 使用導出的預設圖片
      hasMultipleImages: {}, // 標記每個活動是否有多張圖片
      currentImageIndexes: {}, // 儲存每個活動的當前圖片索引
      topPagination: true, // 控制上方分頁的顯示
      pageSizeOptions: [12, 24, 36, 48], // 將頁面大小選項提取為變數
      selectedStatus: '', // 新增：用於儲存選擇的活動狀態
      statusOptions: [
        { label: '全部活動', value: '' },
        { label: '只限今日', value: '只限今日' },
        { label: '即將結束', value: '即將結束' },
        { label: '進行中', value: '進行中' },
        { label: '即將開始', value: '即將開始' },
        { label: '未開始', value: '未開始' },
        { label: '已結束', value: '已結束' },
        { label: '未知', value: '未知' },
      ],
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
    itemsPerPage: {
      handler(newVal) {
        /* eslint-disable no-console */
        console.log('每頁顯示數量改變為:', newVal);
      },
      immediate: false,
    },
    selectedStatus: {
      handler() {
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

    // 從 localStorage 讀取之前保存的設置
    const savedPageSize = localStorage.getItem('preferredPageSize');
    if (savedPageSize) {
      const size = Number.parseInt(savedPageSize);
      if (this.pageSizeOptions.includes(size))
        this.itemsPerPage = size;
    }
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
      const today = new Date(now);
      today.setHours(0, 0, 0, 0);

      const threeDays = 3 * 24 * 60 * 60 * 1000;

      // 初始化分類容器
      const categorizedActivities = {
        todayOnly: [], // (1) 只限今日
        endingSoon: [], // (2) 即將結束
        ongoing: [], // (3) 進行中
        upcoming: [], // (4) 即將開始
        notStarted: [], // (5) 未開始
        ended: [], // (6) 已結束
        unknown: [], // (7) 未知
      };

      // 按照指定順序進行分類
      activities.forEach((activity) => {
        // 檢查日期是否完整
        if (!activity.start_date || !activity.end_date
          || activity.start_date === 'null' || activity.end_date === 'null'
          || activity.start_date === '' || activity.end_date === '') {
          // (7) 未知
          categorizedActivities.unknown.push({
            ...activity,
            sortTime: 0,
          });
          return;
        }

        try {
          const startDate = new Date(activity.start_date);
          const endDate = new Date(activity.end_date);

          // 檢查日期是否有效
          if (Number.isNaN(startDate.getTime()) || Number.isNaN(endDate.getTime())) {
            categorizedActivities.unknown.push({
              ...activity,
              sortTime: 0,
            });
            return;
          }

          const startDiff = startDate.getTime() - now.getTime();
          const endDiff = endDate.getTime() - now.getTime();
          const isSameDay = startDate.toDateString() === endDate.toDateString();

          // 按照指定順序進行分類判斷
          if (endDate < now) {
            // (6) 已結束
            categorizedActivities.ended.push({
              ...activity,
              sortTime: endDate.getTime(),
            });
          }
          else if (isSameDay && startDate.toDateString() === now.toDateString()) {
            // (1) 只限今日
            categorizedActivities.todayOnly.push({
              ...activity,
              sortTime: startDate.getTime(),
            });
          }
          else if (endDiff <= threeDays && endDiff > 0) {
            // (2) 即將結束
            categorizedActivities.endingSoon.push({
              ...activity,
              sortTime: endDiff,
            });
          }
          else if (now >= startDate && startDiff <= -threeDays) {
            // (3) 進行中
            categorizedActivities.ongoing.push({
              ...activity,
              sortTime: startDate.getTime(),
            });
          }
          else if (startDiff > 0 && startDiff <= threeDays) {
            // (4) 即將開始
            categorizedActivities.upcoming.push({
              ...activity,
              sortTime: startDiff,
            });
          }
          else if (startDiff > threeDays) {
            // (5) 未開始
            categorizedActivities.notStarted.push({
              ...activity,
              sortTime: startDiff,
            });
          }
        }
        catch (error) {
          // 如果日期解析出錯，歸類為未知
          console.error('Date parsing error:', error);
          categorizedActivities.unknown.push({
            ...activity,
            sortTime: 0,
          });
        }
      });

      // 對各類別進行排序
      categorizedActivities.todayOnly.sort((a, b) => a.sortTime - b.sortTime);
      categorizedActivities.endingSoon.sort((a, b) => a.sortTime - b.sortTime);
      categorizedActivities.ongoing.sort((a, b) => b.sortTime - a.sortTime);
      categorizedActivities.upcoming.sort((a, b) => a.sortTime - b.sortTime);
      categorizedActivities.notStarted.sort((a, b) => a.sortTime - b.sortTime);
      categorizedActivities.ended.sort((a, b) => b.sortTime - a.sortTime);
      // 未知類別按照活動名稱排序
      categorizedActivities.unknown.sort((a, b) =>
        (a.activity_name || '').localeCompare(b.activity_name || '', 'zh-TW'),
      );

      // 按照指定順序合併所有活動
      return [
        ...categorizedActivities.todayOnly, // (1)
        ...categorizedActivities.endingSoon, // (2)
        ...categorizedActivities.ongoing, // (3)
        ...categorizedActivities.upcoming, // (4)
        ...categorizedActivities.notStarted, // (5)
        ...categorizedActivities.ended, // (6)
        ...categorizedActivities.unknown, // (7)
      ];
    },

    handleSearch() {
      const query = this.searchQuery.trim();
      const searchDate = this.searchDate ? new Date(this.searchDate) : null;
      const status = this.selectedStatus;

      if (!query && !searchDate && !status) {
        this.activities = [...this.allActivities];
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

          const matchesStatus = !status || this.getStatusText(activity) === status;

          return matchesQuery && matchesDate && matchesStatus;
        });

        this.activities = filteredActivities;
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
      if (!activity)
        return '';

      const imageUrls = this.getActivityImageUrls(activity);

      // 如果活動有自己的圖片
      if (imageUrls.length > 0) {
        // 更新是否有多張圖片的狀態
        this.hasMultipleImages[activity.id] = imageUrls.length > 1;

        // 確保當前圖片索引存在且有效
        if (typeof this.currentImageIndexes[activity.id] === 'undefined')
          this.currentImageIndexes[activity.id] = 0;

        // 返回當前索引的圖片
        const currentIndex = this.currentImageIndexes[activity.id];
        return imageUrls[currentIndex % imageUrls.length];
      }

      // 如果沒有圖片，使用活動ID生成固定的預設圖片索引
      const idString = String(activity.id || '') + String(activity.activity_name || '');
      let hash = 0;
      for (let i = 0; i < idString.length; i++) {
        hash = ((hash << 5) - hash) + idString.charCodeAt(i);
        hash = hash & hash;
      }
      // 確保hash值為正數
      hash = Math.abs(hash);

      // 計算當前頁面上已使用的預設圖片索引
      const usedIndexes = new Set();
      this.paginatedActivities.forEach((a) => {
        if (a.id !== activity.id && !this.getActivityImageUrls(a).length) {
          const aHash = this.calculateHash(a);
          usedIndexes.add(aHash % this.defaultImages.length);
        }
      });

      // 如果當前計算出的索引已被使用，則尋找下一個可用的索引
      let defaultIndex = hash % this.defaultImages.length;
      while (usedIndexes.has(defaultIndex))
        defaultIndex = (defaultIndex + 1) % this.defaultImages.length;

      return this.defaultImages[defaultIndex];
    },

    // 新增：計算活動的雜湊值
    calculateHash(activity) {
      const idString = String(activity.id || '') + String(activity.activity_name || '');
      let hash = 0;
      for (let i = 0; i < idString.length; i++) {
        hash = ((hash << 5) - hash) + idString.charCodeAt(i);
        hash = hash & hash;
      }
      return Math.abs(hash);
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
      if (!activity.start_date || !activity.end_date)
        return '未知';

      const now = new Date();
      const today = new Date(now);
      today.setHours(0, 0, 0, 0);

      const threeDays = 3 * 24 * 60 * 60 * 1000;

      const startDate = new Date(activity.start_date);
      const endDate = new Date(activity.end_date);
      const startDiff = startDate.getTime() - now.getTime();
      const endDiff = endDate.getTime() - now.getTime();

      // 檢查是否為當日活動
      const isSameDay = startDate.toDateString() === endDate.toDateString();

      if (endDate < now)
        return '已結束';
      if (isSameDay && startDate.toDateString() === now.toDateString())
        return '只限今日';
      if (endDiff <= threeDays && endDiff > 0)
        return '即將結束';
      if (now >= startDate && startDiff <= -threeDays)
        return '進行中';
      if (startDiff > 0 && startDiff <= threeDays)
        return '即將開始';
      if (startDiff > threeDays)
        return '未開始';

      return '未知';
    },

    getStatusClass(activity) {
      const status = this.getStatusText(activity);
      return {
        'bg-orange-500/80 animate-pulse-soft': status === '即將結束',
        'bg-red-500/80 animate-pulse-urgent': status === '只限今日',
        'bg-green-500/80': status === '進行中',
        'bg-yellow-500/80': status === '即將開始',
        'bg-gray-700/80': status === '未開始',
        'bg-gray-400/80': status === '已結束',
        'bg-purple-400/80': status === '未知',
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

    prevImage(activity, event) {
      if (event)
        event.stopPropagation();

      const imageUrls = this.getActivityImageUrls(activity);
      if (imageUrls.length > 1) {
        if (typeof this.currentImageIndexes[activity.id] === 'undefined')
          this.currentImageIndexes[activity.id] = 0;

        const currentIndex = this.currentImageIndexes[activity.id];
        this.currentImageIndexes[activity.id] = (currentIndex - 1 + imageUrls.length) % imageUrls.length;
      }
    },

    nextImage(activity, event) {
      if (event)
        event.stopPropagation();

      const imageUrls = this.getActivityImageUrls(activity);
      if (imageUrls.length > 1) {
        if (typeof this.currentImageIndexes[activity.id] === 'undefined')
          this.currentImageIndexes[activity.id] = 0;

        const currentIndex = this.currentImageIndexes[activity.id];
        this.currentImageIndexes[activity.id] = (currentIndex + 1) % imageUrls.length;
      }
    },

    getActivityImageUrls(activity) {
      if (!activity?.image_url)
        return [];

      try {
        let imageUrls = [];
        if (typeof activity.image_url === 'string') {
          try {
            imageUrls = JSON.parse(activity.image_url);
          }
          catch {
            if (activity.image_url.includes('|'))
              imageUrls = activity.image_url.split('|');
            else if (activity.image_url.includes(','))
              imageUrls = activity.image_url.split(',');
            else
              imageUrls = [activity.image_url];
          }
        }
        else if (Array.isArray(activity.image_url)) {
          imageUrls = activity.image_url;
        }

        return imageUrls
          .filter(url => url && url.trim())
          .map(url => url.trim());
      }
      catch (e) {
        console.error('取得圖片 URL 列表錯誤:', e);
        return [];
      }
    },

    handlePageSizeChange(pageSize) {
      // 保存到 localStorage
      localStorage.setItem('preferredPageSize', pageSize);

      this.itemsPerPage = pageSize;
      // 確保當前頁碼有效
      const maxPage = Math.ceil(this.activities.length / this.itemsPerPage);
      if (this.currentPage > maxPage)
        this.currentPage = maxPage;

      // 強制更新兩個分頁組件
      this.$nextTick(() => {
        // 觸發重新渲染
        this.$forceUpdate();
      });

      // 滾動到頁面頂部
      window.scrollTo({ top: 0, behavior: 'smooth' });
    },
  },
};
</script>

<template>
  <div class="activity-list">
    <div class="search-container bg-white rounded-lg shadow-md p-6 mb-8">
      <div class="flex flex-col md:flex-row gap-4">
        <!-- 搜尋輸入框 -->
        <div class="flex-1 relative">
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <i class="fas fa-search text-gray-400" />
          </div>
          <input
            v-model="searchQuery" type="text" placeholder="搜尋活動名稱、地點..."
            class="w-full pl-10 pr-4 py-3 rounded-lg border border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all duration-200 bg-gray-50 hover:bg-white"
          >
        </div>

        <!-- 日期選擇器 -->
        <div class="relative">
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <NIcon class="text-gray-400">
              <CalendarOutline />
            </NIcon>
          </div>
          <input
            v-model="searchDate" type="date"
            class="w-full md:w-48 pl-10 pr-4 py-3 rounded-lg border border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all duration-200 bg-gray-50 hover:bg-white"
            :min="minDate" :max="maxDate"
          >
        </div>

        <!-- 新增：活動分類選單 -->
        <div class="relative">
          <NSelect
            v-model:value="selectedStatus" :options="statusOptions" placeholder="選擇活動狀態"
            class="w-full md:w-48 status-select" :consistent-menu-width="false" size="large"
          >
            <template #prefix>
              <NIcon class="text-gray-400">
                <i class="fas fa-filter" />
              </NIcon>
            </template>
          </NSelect>
        </div>

        <!-- 搜尋按鈕 -->
        <NButton
          type="primary"
          class="search-button py-3 px-8 rounded-lg transition-all duration-200 hover:shadow-lg flex items-center gap-2"
          size="large" @click="handleSearch"
        >
          <NIcon>
            <i class="fas fa-search" />
          </NIcon>
          <span>搜尋活動</span>
        </NButton>
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
      <!-- 上方分頁 -->
      <div class="flex justify-center mb-8">
        <NPagination
          v-model:page="currentPage" v-model:page-size="itemsPerPage" :page-count="totalPages"
          :page-sizes="pageSizeOptions" :page-slot="7" show-size-picker @update:page="changePage"
          @update:page-size="handlePageSizeChange"
        />
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-4">
        <template v-for="activity in paginatedActivities" :key="activity.id">
          <NCard
            class="activity-card transform transition-all duration-300 hover:-translate-y-1" :bordered="false"
            size="medium" :segmented="{ content: true }" :hoverable="true"
            style="box-shadow: 0 2px 8px rgba(0,0,0,0.08);"
          >
            <!-- 圖片容器 -->
            <div class="relative aspect-[16/9] overflow-hidden rounded-t-lg" @click.stop>
              <img
                :src="getImageUrl(activity)" :alt="activity.activity_name"
                class="w-full h-full object-cover transition-opacity duration-300" @error="handleImageError"
              >

              <!-- 輪播控制按鈕 - 只在多張圖片時顯示 -->
              <div
                v-if="hasMultipleImages[activity.id]"
                class="absolute inset-0 flex items-center justify-between px-4 opacity-0 hover:opacity-100 transition-opacity duration-300"
                @click.stop
              >
                <button
                  class="carousel-button transform hover:scale-110 transition-transform"
                  @click.stop="prevImage(activity, $event)"
                >
                  <i class="fas fa-chevron-left" />
                </button>
                <button
                  class="carousel-button transform hover:scale-110 transition-transform"
                  @click.stop="nextImage(activity, $event)"
                >
                  <i class="fas fa-chevron-right" />
                </button>
              </div>

              <!-- 圖片指示器 - 只在多張圖片時顯示 -->
              <div
                v-if="hasMultipleImages[activity.id]"
                class="absolute bottom-4 left-1/2 transform -translate-x-1/2 flex space-x-2 z-10" @click.stop
              >
                <button
                  v-for="(_, index) in getActivityImageUrls(activity)" :key="index"
                  class="w-2 h-2 rounded-full transition-all duration-300 bg-white/50 hover:bg-white/80" :class="[
                    index === (currentImageIndexes[activity.id] || 0) ? 'bg-white scale-125' : '',
                  ]" @click.stop="currentImageIndexes[activity.id] = index"
                />
              </div>

              <!-- 活動狀態標籤 -->
              <div
                class="absolute top-3 right-3 px-4 py-1.5 min-w-[80px] text-center rounded-md text-sm font-medium text-white transition-transform duration-300"
                :class="getStatusClass(activity)"
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

      <!-- 下方分頁 -->
      <div class="flex justify-center mt-8 mb-12">
        <NPagination
          v-model:page="currentPage" v-model:page-size="itemsPerPage" :page-count="totalPages"
          :page-sizes="pageSizeOptions" :page-slot="7" show-size-picker @update:page="changePage"
          @update:page-size="handlePageSizeChange"
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

/* 搜尋區塊的新樣式 */
.search-container {
  background: linear-gradient(to right, #ffffff, #f8f9fa);
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

/* 輸入框焦點效果 */
input:focus {
  outline: none;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
}

/* 日期選擇器自定義樣式 */
input[type="date"] {
  appearance: none;
  -webkit-appearance: none;
  position: relative;
  cursor: pointer;
}

input[type="date"]::-webkit-calendar-picker-indicator {
  background: transparent;
  bottom: 0;
  color: transparent;
  cursor: pointer;
  height: auto;
  left: 0;
  position: absolute;
  right: 0;
  top: 0;
  width: auto;
}

/* 搜尋按鈕懸停效果 */
.n-button:hover {
  transform: translateY(-1px);
}

/* 響應式調整 */
@media (max-width: 768px) {
  .search-container {
    padding: 1rem;
  }

  input[type="date"] {
    width: 100%;
  }
}

/* 添加漸變背景效果 */
.search-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, #3b82f6, #60a5fa, #93c5fd);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.search-container:hover::before {
  opacity: 1;
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

/* 新增一個專門用於"只限今日"的快速跳動動畫 */
@keyframes pulse-urgent {

  0%,
  100% {
    transform: scale(1);
  }

  50% {
    transform: scale(1.1);
  }
}

.animate-pulse-soft {
  animation: pulse-soft 2s ease-in-out infinite;
}

/* 新增一個用於"只限今日"的動畫類別 */
.animate-pulse-urgent {
  animation: pulse-urgent 1s ease-in-out infinite;
}

/* 添加分頁相關樣式 */
.n-pagination {
  @apply bg-white rounded-lg shadow-sm p-2;
}

/* 確保上下分頁的一致性 */
.n-pagination :deep(.n-pagination-item) {
  @apply min-w-[32px] h-8 leading-8 mx-1;
}

.n-pagination :deep(.n-pagination-item--active) {
  @apply bg-blue-500 text-white;
}

.n-pagination :deep(.n-pagination-item:hover:not(.n-pagination-item--active)) {
  @apply bg-gray-100;
}

/* 確保分頁選擇器的樣式一致 */
.n-pagination :deep(.n-pagination-size-picker) {
  @apply min-w-[80px];
}

.n-pagination :deep(.n-base-selection) {
  @apply bg-white border border-gray-200;
}

/* 活動分類選單樣式 */
.status-select :deep(.n-base-selection) {
  background-color: #f8f9fa;
  border-color: #e2e8f0;
  transition: all 0.2s ease;
  height: 48px;
  /* 確保與其他輸入框高度一致 */
}

.status-select :deep(.n-base-selection:hover) {
  background-color: white;
  border-color: #93c5fd;
}

.status-select :deep(.n-base-selection-label) {
  height: 48px;
  line-height: 48px;
  padding-left: 36px;
  /* 為圖標留出空間 */
}

.status-select :deep(.n-base-selection-prefix) {
  margin-left: 12px;
  color: #6b7280;
}

.status-select :deep(.n-base-selection-placeholder) {
  color: #9ca3af;
}

/* 下拉選單樣式 */
.status-select :deep(.n-select-menu) {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  padding: 4px;
}

.status-select :deep(.n-select-option) {
  padding: 8px 12px;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.status-select :deep(.n-select-option:hover) {
  background-color: #f0f9ff;
}

/* 搜尋按鈕樣式 */
.search-button {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  border: none;
  height: 48px;
  /* 確保與其他輸入框高度一致 */
  font-weight: 500;
  letter-spacing: 0.5px;
}

.search-button:hover {
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
}

.search-button:active {
  transform: translateY(0);
}

/* 確保在移動設備上的響應式設計 */
@media (max-width: 768px) {
  .status-select {
    width: 100%;
  }

  .search-button {
    width: 100%;
    justify-content: center;
  }
}

/* 輪播按鈕樣式 */
.carousel-button {
  @apply bg-black/50 text-white p-2 rounded-full hover:bg-black/70 transition-colors cursor-pointer;
}

/* 確保按鈕在觸控設備上可見 */
@media (hover: none) {
  .carousel-controls {
    opacity: 1 !important;
  }
}

/* 添加按鈕懸停效果 */
.carousel-button:hover {
  transform: scale(1.1);
}

/* 指示器樣式 */
.carousel-indicator {
  @apply w-2 h-2 rounded-full transition-all cursor-pointer;
}
</style>

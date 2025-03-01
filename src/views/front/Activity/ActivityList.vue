<script lang="ts">
import axios from 'axios';
import { defineComponent } from 'vue';
import { NButton, NCard, NPagination, NSelect, NTooltip } from 'naive-ui';

// import { CalendarOutline, LocationOutline, TicketOutline } from '@vicons/ionicons5';

// 定義活動介面
interface Activity {
  id: number
  uid: string
  activity_name: string
  description: string
  location: string
  start_date: string
  end_date: string
  ticket_price: string
  image_url: string | string[]
  sortTime?: number
}

// 定義分類活動介面
interface CategorizedActivities {
  todayOnly: Activity[]
  endingSoon: Activity[]
  ongoing: Activity[]
  upcoming: Activity[]
  notStarted: Activity[]
  ended: Activity[]
  unknown: Activity[]
}

// 定義錯誤型別
type ErrorType = string | null;

// 匯出預設活動圖片陣列
export const defaultActivityImages = [
  // 露營活動
  'https://images.unsplash.com/photo-1504280390367-361c6d9f38f4?w=800&fm=jpg&fit=crop&q=80',
  // 攀岩活動
  'https://images.unsplash.com/photo-1522163182402-834f871fd851?w=800&fm=jpg&fit=crop&q=80',
  // 衝浪活動
  'https://images.unsplash.com/photo-1502680390469-be75c86b636f?w=800&fm=jpg&fit=crop&q=80',
  // 健行活動
  'https://images.unsplash.com/photo-1551632811-561732d1e306?w=800&fm=jpg&fit=crop&q=80',
  // 單車活動
  'https://images.unsplash.com/photo-1534787238916-9ba6764efd4f?w=800&fm=jpg&fit=crop&q=80',
  // 游泳活動
  'https://images.unsplash.com/photo-1530549387789-4c1017266635?w=800&fm=jpg&fit=crop&q=80',
  // 瑜珈活動
  'https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=800&fm=jpg&fit=crop&q=80',
  // 路跑活動
  'https://images.unsplash.com/photo-1552674605-db6ffd4facb5?w=800&fm=jpg&fit=crop&q=80',
  // 滑板活動
  'https://images.unsplash.com/photo-1520045892732-304bc3ac5d8e?w=800&fm=jpg&fit=crop&q=80',
  // 籃球活動
  'https://images.unsplash.com/photo-1546519638-68e109498ffc?w=800&fm=jpg&fit=crop&q=80',
  // 網球活動
  'https://images.unsplash.com/photo-1595435934249-5df7ed86e1c0?w=800&fm=jpg&fit=crop&q=80',
  // 高爾夫活動
  'https://images.unsplash.com/photo-1535131749006-b7f58c99034b?w=800&fm=jpg&fit=crop&q=80',
  // 舞蹈活動
  'https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?w=800&fm=jpg&fit=crop&q=80',
  // 攝影活動
  'https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=800&fm=jpg&fit=crop&q=80',
  // 繪畫活動
  'https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=800&fm=jpg&fit=crop&q=100',
  // 烹飪活動
  'https://images.unsplash.com/photo-1556911220-bff31c812dba?w=800&fm=jpg&fit=crop&q=80',
  // 園藝活動
  'https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=800&fm=jpg&fit=crop&q=80',
  // 手作活動
  'https://images.unsplash.com/photo-1452860606245-08befc0ff44b?w=800&fm=jpg&fit=crop&q=80',
  // 音樂活動
  'https://images.unsplash.com/photo-1511379938547-c1f69419868d?w=800&fm=jpg&fit=crop&q=80',
  // 靜心活動
  'https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=800&fm=jpg&fit=crop&q=80',
  // 寵物活動
  'https://images.unsplash.com/photo-1450778869180-41d0601e046e?w=800&fm=jpg&fit=crop&q=80',
  // 閱讀活動
  'https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?w=800&fm=jpg&fit=crop&q=80',
  // 電競活動
  'https://images.unsplash.com/photo-1538481199705-c710c4e965fc?w=800&fm=jpg&fit=crop&q=80',
  // 旅遊活動
  'https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=800&fm=jpg&fit=crop&q=80',
  // 露營車活動
  'https://images.unsplash.com/photo-1523987355523-c7b5b0dd90a7?w=800&fm=jpg&fit=crop&q=80',
];

// 常數定義
const STATUS_OPTIONS = [
  { label: '全部活動', value: '' },
  { label: '只限今日', value: '只限今日' },
  { label: '即將結束', value: '即將結束' },
  { label: '進行中', value: '進行中' },
  { label: '即將開始', value: '即將開始' },
  { label: '未開始', value: '未開始' },
  { label: '已結束', value: '已結束' },
  { label: '未知', value: '未知' },
];

const PAGE_SIZE_OPTIONS = [12, 24, 36, 48];

export default defineComponent({
  name: 'ActivityList',
  components: {
    NCard, // 卡片容器元件
    NButton, // 按鈕元件
    NPagination, // 分頁元件
    // NIcon, // 圖示元件
    NSelect, // 下拉選單元件
    NTooltip,
    // LocationOutline, // 地點圖示
    // CalendarOutline, // 行事曆圖示
    // TicketOutline, // 票券圖示
  },
  data() {
    return {
      activities: [] as Activity[], // 活動清單
      allActivities: [] as Activity[], // 儲存所有活動的原始資料
      loading: false, // 讀取狀態
      error: null as ErrorType, // 錯誤訊息
      searchQuery: '', // 搜尋關鍵字
      baseURL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000', // API 基礎網址
      currentPage: 1, // 目前頁碼
      itemsPerPage: 12, // 每頁顯示筆數
      maxDisplayPages: 5, // 最大顯示頁數
      searchDate: '', // 搜尋日期
      minDate: '', // 最小日期
      maxDate: '', // 最大日期
      defaultImages: defaultActivityImages, // 使用匯出的預設圖片
      hasMultipleImages: {} as Record<number, boolean>, // 標記每個活動是否有多張圖片
      currentImageIndexes: {} as Record<number, number>, // 儲存每個活動目前的圖片索引
      topPagination: true, // 控制上方分頁的顯示
      pageSizeOptions: PAGE_SIZE_OPTIONS, // 頁面大小選項
      selectedStatus: '', // 選擇的活動狀態
      statusOptions: STATUS_OPTIONS, // 活動狀態選項
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
    this.initializeComponent();
  },
  methods: {
    initializeComponent() {
      this.fetchActivities();
      this.loadSavedPageSize();
    },

    loadSavedPageSize() {
      const savedPageSize = localStorage.getItem('preferredPageSize');
      if (savedPageSize) {
        const size = Number.parseInt(savedPageSize);
        if (this.pageSizeOptions.includes(size))
          this.itemsPerPage = size;
      }
    },

    getMinDate() {
      const today = new Date();
      return new Date(today.getFullYear() - 1, today.getMonth(), today.getDate())
        .toISOString().split('T')[0];
    },

    getMaxDate() {
      const today = new Date();
      return new Date(today.getFullYear() + 1, today.getMonth(), today.getDate())
        .toISOString().split('T')[0];
    },

    async fetchActivities() {
      this.loading = true;
      this.error = null;

      try {
        const data = await this.fetchActivityData();
        this.processActivityData(data);
      }
      catch (error) {
        console.error('Error fetching activities:', error);
        this.error = '無法載入活動資料，請稍後再試';
      }
      finally {
        this.loading = false;
      }
    },

    async fetchActivityData() {
      try {
        const localData = await import('@/assets/theme_entertainment/events_data.json');
        return localData.default;
      }
      catch (localError) {
        console.error('Local data error:', localError);
        const response = await axios.get('/theme_entertainment/activities/api/list/');
        return response.data;
      }
    },

    processActivityData(data: any) {
      let activities: Activity[];
      if (Array.isArray(data))
        activities = data;

      else if (data.status === 'success' && Array.isArray(data.data))
        activities = data.data;

      else
        throw new Error('API 返回的數據格式無效');

      this.allActivities = this.sortActivities(activities);
      this.activities = [...this.allActivities];
    },

    sortActivities(activities: Activity[]) {
      const now = new Date();
      const today = new Date(now);
      today.setHours(0, 0, 0, 0);

      const threeDays = 3 * 24 * 60 * 60 * 1000;

      // 初始化分類容器
      const categorizedActivities: CategorizedActivities = {
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
      categorizedActivities.todayOnly.sort((a, b) => (a.sortTime ?? 0) - (b.sortTime ?? 0));
      categorizedActivities.endingSoon.sort((a, b) => (a.sortTime ?? 0) - (b.sortTime ?? 0));
      categorizedActivities.ongoing.sort((a, b) => (b.sortTime ?? 0) - (a.sortTime ?? 0));
      categorizedActivities.upcoming.sort((a, b) => (a.sortTime ?? 0) - (b.sortTime ?? 0));
      categorizedActivities.notStarted.sort((a, b) => (a.sortTime ?? 0) - (b.sortTime ?? 0));
      categorizedActivities.ended.sort((a, b) => (b.sortTime ?? 0) - (a.sortTime ?? 0));
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

    formatDate(dateString: string | null): string {
      if (!dateString)
        return '時間未定';
      return new Date(dateString).toLocaleDateString('zh-TW', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      });
    },

    getImageUrl(activity: Activity): string {
      if (!activity)
        return '';

      const imageUrls = this.getActivityImageUrls(activity);

      // 如果活動有自己的圖片且不是 ["None"]
      if (imageUrls.length > 0 && !(imageUrls.length === 1 && imageUrls[0] === 'None')) {
        // 更新是否有多張圖片的狀態
        this.hasMultipleImages[activity.id] = imageUrls.length > 1;

        // 確保當前圖片索引存在且有效
        if (typeof this.currentImageIndexes[activity.id] === 'undefined')
          this.currentImageIndexes[activity.id] = 0;

        // 返回當前索引的圖片
        const currentIndex = this.currentImageIndexes[activity.id];
        return imageUrls[currentIndex % imageUrls.length];
      }

      // 如果沒有圖片或圖片為 ["None"]，使用活動ID生成固定的預設圖片索引
      const idString = String(activity.id || '') + String(activity.activity_name || '');
      let hash = 0;
      for (let i = 0; i < idString.length; i++) {
        hash = ((hash << 5) - hash) + idString.charCodeAt(i);
        hash = hash & hash;
      }
      // 確保hash值為正數
      hash = Math.abs(hash);

      // 計算當前頁面上已使用的預設圖片索引
      const usedIndexes = new Set<number>();
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
    calculateHash(activity: Activity) {
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
      const usedIndexes = new Set<number>();
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key && key.startsWith('activity_image_')) {
          const value = localStorage.getItem(key);
          if (value)
            usedIndexes.add(Number.parseInt(value));
        }
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

    handleImageError(e: Event) {
      const target = e.target as HTMLImageElement;
      const activityId = target.dataset.activityId;
      const activity = this.paginatedActivities.find(
        (a: Activity) => a.id === Number(activityId),
      );

      if (activity) {
        const storageKey = `activity_image_${activity.id}`;
        const newIndex = this.getRandomUniqueImageIndex();
        localStorage.setItem(storageKey, String(newIndex));
        target.src = this.defaultImages[newIndex];
      }
      target.onerror = null;
    },

    getStatusText(activity: Activity): string {
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

    getStatusClass(activity: Activity): Record<string, boolean> {
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

    changePage(page: number) {
      if (page >= 1 && page <= this.totalPages) {
        this.currentPage = page;
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    },

    viewDetails(activity: Activity) {
      this.$router.push({
        name: 'ActivityDetail',
        params: { id: activity.uid },
      });
    },

    prevImage(activity: Activity, event?: Event) {
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

    nextImage(activity: Activity, event?: Event) {
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

    getActivityImageUrls(activity: Activity): string[] {
      if (!activity?.image_url)
        return [];

      try {
        let imageUrls: string[] = [];
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
          .filter((url: string) => url && url.trim())
          .map((url: string) => url.trim());
      }
      catch (e) {
        console.error('取得圖片 URL 列表錯誤:', e);
        return [];
      }
    },

    handlePageSizeChange(pageSize: number) {
      localStorage.setItem('preferredPageSize', String(pageSize));
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
});
</script>

<template>
  <div class="activity-list">
    <div class="search-container bg-white rounded-lg shadow-md p-6 mb-8">
      <div class="flex flex-col md:flex-row gap-4">
        <!-- 搜尋輸入框 -->
        <div class="flex-1 relative">
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <i class="fas fa-search text-[#0F4BB4]" />
          </div>
          <input
            v-model="searchQuery" type="text" placeholder="搜尋活動名稱、地點..."
            class="w-full h-[44px] pl-10 pr-4 rounded-lg border border-gray-200 focus:border-[#0F4BB4] focus:ring-2 focus:ring-[#0F4BB4]/20 transition-all duration-200 bg-white text-base font-normal"
          >
        </div>

        <!-- 日期選擇器 -->
        <div class="relative">
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <i class="far fa-calendar text-[#0F4BB4]" />
          </div>
          <input
            v-model="searchDate" type="date"
            class="w-full md:w-48 h-[44px] pl-10 pr-4 rounded-lg border border-gray-200 focus:border-[#0F4BB4] focus:ring-2 focus:ring-[#0F4BB4]/20 transition-all duration-200 bg-white text-base font-normal"
            :min="minDate" :max="maxDate"
          >
        </div>

        <!-- 活動分類選單 -->
        <div class="relative h-[44px]">
          <NSelect
            v-model:value="selectedStatus" :options="statusOptions" placeholder="選擇活動狀態"
            class="w-full md:w-48 status-select text-base font-normal" :consistent-menu-width="false"
          />
          <i class="fas fa-filter text-[#0F4BB4] absolute left-4 top-1/2 -translate-y-1/2 z-10 text-md" />
        </div>

        <!-- 搜尋按鈕 -->
        <NButton
          type="primary"
          class="search-button h-[44px] px-8 rounded-lg transition-all duration-200 hover:shadow-lg flex items-center justify-center gap-3 w-full md:w-auto bg-[#0F4BB4] text-base font-normal"
          @click="handleSearch"
        >
          <i class="fas fa-search text-base" />
          <span class="ml-1">搜尋活動</span>
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
          :page-sizes="pageSizeOptions" :page-slot="7" show-size-picker class="pagination-custom"
          @update:page="changePage" @update:page-size="handlePageSizeChange"
        />
      </div>

      <div class="container mx-auto px-2 sm:px-4 lg:px-0">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <template v-for="activity in paginatedActivities" :key="activity.id">
            <NCard
              class="activity-card transform transition-all duration-300 hover:-translate-y-1" :bordered="false"
              size="medium" :segmented="{ content: true }" :hoverable="true"
              style="box-shadow: 0 2px 8px rgba(0,0,0,0.08);"
            >
              <!-- 圖片容器 -->
              <div class="relative aspect-[16/9] overflow-hidden rounded-t-lg mt-0" @click.stop>
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
              <div class="pt-1 px-5 pb-5">
                <!-- 活動標題 -->
                <NTooltip v-if="activity.activity_name?.length > 20" trigger="hover" placement="top">
                  <template #trigger>
                    <h3
                      class="text-xl font-semibold text-gray-900 mb-4 whitespace-nowrap overflow-hidden text-ellipsis"
                    >
                      {{ activity.activity_name }}
                    </h3>
                  </template>
                  {{ activity.activity_name }}
                </NTooltip>
                <h3
                  v-else
                  class="text-xl font-semibold text-gray-900 mb-4 whitespace-nowrap overflow-hidden text-ellipsis"
                >
                  {{ activity.activity_name }}
                </h3>

                <!-- 活動資訊 -->
                <div class="space-y-2 text-sm text-gray-600">
                  <div class="flex items-center whitespace-nowrap overflow-hidden">
                    <div class="w-6 flex justify-center flex-shrink-0">
                      <i class="fas fa-map-marker-alt mr-2" />
                    </div>
                    <NTooltip v-if="activity.location?.length > 25" trigger="hover" placement="top">
                      <template #trigger>
                        <span class="overflow-hidden text-ellipsis">{{ activity.location || '地點未定' }}</span>
                      </template>
                      {{ activity.location || '地點未定' }}
                    </NTooltip>
                    <span v-else class="overflow-hidden text-ellipsis">{{ activity.location || '地點未定' }}</span>
                  </div>
                  <div class="flex items-center whitespace-nowrap overflow-hidden">
                    <div class="w-6 flex justify-center flex-shrink-0">
                      <i class="far fa-calendar mr-2" />
                    </div>
                    <span class="overflow-hidden text-ellipsis">{{ (activity.start_date === '無資料' || activity.end_date
                      === '無資料')
                      ? '起訖時間無相關資訊'
                      : `${formatDate(activity.start_date)} ~ ${formatDate(activity.end_date)}` }}</span>
                  </div>
                  <div class="flex items-center whitespace-nowrap overflow-hidden">
                    <div class="w-6 flex justify-center flex-shrink-0">
                      <i class="fas fa-ticket-alt mr-2" />
                    </div>
                    <NTooltip v-if="(activity.ticket_price || '無售票資訊').length > 25" trigger="hover" placement="top">
                      <template #trigger>
                        <span class="overflow-hidden text-ellipsis">{{ activity.ticket_price === '無資料' ? '無售票資訊'
                          : (activity.ticket_price || '無售票資訊') }}</span>
                      </template>
                      {{ activity.ticket_price === '無資料' ? '無售票資訊' : (activity.ticket_price || '無售票資訊') }}
                    </NTooltip>
                    <span v-else class="overflow-hidden text-ellipsis">{{ activity.ticket_price === '無資料' ? '無售票資訊'
                      : (activity.ticket_price || '無售票資訊') }}</span>
                  </div>
                </div>

                <!-- 分隔線 -->
                <div class="my-4 border-t border-gray-200" />

                <!-- 活動描述 -->
                <p class="text-sm text-gray-500 line-clamp-3" style="text-indent: 2em !important;">
                  {{ activity.description === '無資料' ? '無活動相關簡介及說明' : (activity.description || '無活動相關簡介及說明') }}
                </p>

                <!-- 按鈕區域 -->
                <div class="mt-4 flex justify-end">
                  <NButton
                    type="success" size="small"
                    class="hover:shadow-md transition-shadow bg-[#417690] hover:bg-[#205067] text-white font-medium"
                    @click="viewDetails(activity)"
                  >
                    查看詳情
                  </NButton>
                </div>
              </div>
            </NCard>
          </template>
        </div>
      </div>

      <!-- 下方分頁 -->
      <div class="flex justify-center mt-8 mb-12">
        <NPagination
          v-model:page="currentPage" v-model:page-size="itemsPerPage" :page-count="totalPages"
          :page-sizes="pageSizeOptions" :page-slot="7" show-size-picker class="pagination-custom"
          @update:page="changePage" @update:page-size="handlePageSizeChange"
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
  background: #ffffff;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

/* 輸入框焦點效果 */
input:focus {
  outline: none;
  box-shadow: 0 0 0 2px rgba(15, 75, 180, 0.2);
}

/* 日期選擇器自定義樣式 */
input[type="date"] {
  appearance: none;
  -webkit-appearance: none;
  position: relative;
  cursor: pointer;
}

/* 日期選擇器圖標樣式 */
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

/* 輪播容器樣式 */
.carousel {
  position: relative;
  height: 100%;
  width: 100%;
}

/* 輪播圖片樣式 */
.carousel img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: opacity 0.3s ease;
}

/* 輪播控制區域樣式 */
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

/* 輪播控制區域懸停效果 */
.carousel:hover .carousel-controls {
  opacity: 1;
}

/* 輪播按鈕基礎樣式 */
.carousel-button {
  background-color: rgba(0, 0, 0, 0.5);
  color: white;
  padding: 8px;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.3s ease;
}

/* 輪播按鈕懸停效果 */
.carousel-button:hover {
  background-color: rgba(0, 0, 0, 0.7);
  transform: scale(1.1);
}

/* 輪播指示器容器 */
.carousel-indicators {
  position: absolute;
  bottom: 10px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 6px;
}

/* 輪播指示器基礎樣式 */
.carousel-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  transition: all 0.3s ease;
}

/* 輪播指示器啟動狀態 */
.carousel-indicator.active {
  background-color: white;
  transform: scale(1.2);
}

/* 分頁組件樣式 */
.pagination-custom {
  background-color: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  padding: 0.5rem;
}

/* 分頁項目樣式 */
.pagination-custom :deep(.n-pagination-item) {
  min-width: 36px;
  height: 36px;
  line-height: 36px;
  margin: 0 4px;
  border-radius: 6px;
  color: #666;
  font-weight: 500;
  transition: all 0.2s ease;
}

/* 分頁目前項目樣式 */
.pagination-custom :deep(.n-pagination-item--active) {
  background-color: #0F4BB4;
  color: white;
  font-weight: 600;
}

/* 分頁項目懸停效果 */
.pagination-custom :deep(.n-pagination-item:hover:not(.n-pagination-item--active)) {
  background-color: #e9f2ff;
  color: #0F4BB4;
}

/* 分頁選擇器樣式 */
.pagination-custom :deep(.n-pagination-size-picker) {
  min-width: 110px;
}

/* 分頁選擇器基礎樣式 */
.pagination-custom :deep(.n-base-selection) {
  background-color: white;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  height: 36px;
  transition: all 0.2s ease;
}

/* 分頁選擇器懸停效果 */
.pagination-custom :deep(.n-base-selection:hover) {
  border-color: #0F4BB4;
}

/* 分頁選擇器聚焦效果 */
.pagination-custom :deep(.n-base-selection--active) {
  border-color: #0F4BB4;
  box-shadow: 0 0 0 2px rgba(15, 75, 180, 0.2);
}

/* 分頁選擇器下拉菜單樣式 */
.pagination-custom :deep(.n-base-selection-menu) {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  padding: 4px;
}

/* 分頁選擇器選項樣式 */
.pagination-custom :deep(.n-base-select-option) {
  padding: 8px 12px;
  border-radius: 6px;
  transition: all 0.2s ease;
}

/* 分頁選擇器選項懸停效果 */
.pagination-custom :deep(.n-base-select-option:hover) {
  background-color: #e9f2ff;
  color: #0F4BB4;
}

/* 分頁按鈕樣式 */
.pagination-custom :deep(.n-pagination-item.n-pagination-item--button) {
  background-color: white;
  border: 1px solid #e2e8f0;
}

/* 分頁按鈕懸停效果 */
.pagination-custom :deep(.n-pagination-item.n-pagination-item--button:hover:not(:disabled)) {
  background-color: #e9f2ff;
  border-color: #0F4BB4;
  color: #0F4BB4;
}

/* 分頁按鈕禁用效果 */
.pagination-custom :deep(.n-pagination-item.n-pagination-item--button:disabled) {
  background-color: #f8f9fa;
  border-color: #e2e8f0;
  color: #9ca3af;
  cursor: not-allowed;
}

/* 響應式設計 */
@media (max-width: 768px) {
  .pagination-custom :deep(.n-pagination-item) {
    min-width: 32px;
    height: 32px;
    line-height: 32px;
    margin: 0 2px;
  }

  .pagination-custom :deep(.n-pagination-size-picker) {
    min-width: 90px;
  }
}

/* 動畫效果定義 */
@keyframes pulse-soft {

  0%,
  100% {
    transform: scale(1);
  }

  50% {
    transform: scale(1.05);
  }
}

@keyframes pulse-urgent {

  0%,
  100% {
    transform: scale(1);
  }

  50% {
    transform: scale(1.1);
  }
}

/* 動畫類名定義 */
.animate-pulse-soft {
  animation: pulse-soft 2s ease-in-out infinite;
}

.animate-pulse-urgent {
  animation: pulse-urgent 1s ease-in-out infinite;
}

/* 響應式設計 */
@media (max-width: 768px) {

  /* 搜索容器響應式調整 */
  .search-container {
    padding: 1rem;
  }

  /* 日期選擇器響應式調整 */
  input[type="date"] {
    width: 100%;
  }

  /* 狀態選擇器響應式調整 */
  .status-select {
    width: 100%;
  }

  /* 搜索按鈕響應式調整 */
  .search-button {
    width: 100%;
    justify-content: center;
  }
}

/* 觸控設備適配 */
@media (hover: none) {
  .carousel-controls {
    opacity: 1 !important;
  }
}

/* 卡片內容區域樣式 */
:deep(.n-card__content) {
  padding: 0rem 0rem;
  /* 上下，左右 */
  margin: 0;
  background-color: white;
  border-radius: 0 0 0.5rem 0.5rem;
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  transition: all 0.3s ease;
}

:deep(.n-card) {
  overflow: hidden;
}

:deep(.n-card-header) {
  padding: 0;
  margin: 0;
  border: none;
}

:deep(.n-card__content:first-child) {
  padding: 0;
  margin: 0;
}

/* 響應式調整 */
@media (max-width: 768px) {
  :deep(.n-card__content) {
    padding: 0rem 0rem;
    /* 手機版縮小內邊距 */
  }
}

/* 確保內容區域的間距 */
.card-content>* {
  margin-bottom: 0.75rem;
  /* 內容元素間距 */
}

.card-content>*:last-child {
  margin-bottom: 0;
  /* 最後一個元素不要底部間距 */
}

/* Tooltip 相關樣式 */
:deep(.n-tooltip) {
  max-width: 300px;
  white-space: normal;
  word-wrap: break-word;
}

:deep(.n-tooltip-content) {
  font-size: 14px;
  padding: 8px 12px;
}

/* 狀態選擇器樣式 */
.status-select :deep(.n-base-selection) {
  height: 44px !important;
  line-height: 44px;
  background-color: white;
  border: 1px solid #e2e8f0;
  transition: all 0.2s ease;
  font-size: 1rem !important;
}

/* 狀態選擇器標籤樣式 */
.status-select :deep(.n-base-selection-label) {
  height: 44px;
  line-height: 44px;
  padding-left: 36px;
  font-size: 1rem !important;
}

/* 狀態選擇器觸發器樣式 */
.status-select :deep(.n-base-selection-placeholder) {
  height: 44px;
  line-height: 44px;
  padding-left: 36px;
  font-size: 1rem !important;
}

/* 狀態選擇器下拉選項樣式 */
.status-select :deep(.n-base-select-option__content) {
  font-size: 1rem !important;
}

/* 搜尋按鈕樣式 */
.search-button {
  height: 44px;
  font-weight: normal;
  letter-spacing: 0.5px;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 120px;
  font-size: 1rem !important;
  gap: 0.75rem !important;
}

.search-button i {
  font-size: 1rem;
}

.search-button span {
  position: relative;
  top: 1px;
}

/* 搜尋按鈕懸停效果 */
.search-button:hover {
  background: #0d3d91;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(15, 75, 180, 0.2);
}

/* 搜尋按鈕點擊效果 */
.search-button:active {
  transform: translateY(0);
}
</style>

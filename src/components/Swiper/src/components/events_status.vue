<script setup lang="ts">
// 基本組件和函式庫導入
import { Navigation } from 'swiper';
import { Swiper, SwiperSlide } from 'swiper/vue';
import { v4 } from 'uuid';
import { computed, ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';

// 類型和自定義組件導入
import type { SwiperOptions } from 'swiper/types';
import { useSwiper } from '../hooks/useSwiper';
import SwiperLayout from '../Layout.vue';
import CustomNavigation from './CustomNavigation.vue';
import Title from '@/components/Title.vue';
import { defaultActivityImages } from '@/views/front/Activity/ActivityList.vue';

/**
 * 活動介面定義
 */
interface Activity {
    id: number;
    activity_name: string;
    image_url: string | string[];
    start_date: string;
    end_date: string;
    uid?: string;
}

/**
 * 活動狀態分類介面
 */
interface StatusCategory {
    name: string;        // 狀態名稱
    category: string;    // 分類標識
    image: string;       // 預設圖片
    color: string;       // 背景顏色
    description: string; // 描述文字
}

/**
 * 活動分類結果介面
 */
interface CategorizedActivities {
    todayOnly: Activity[];   // 只限今日
    endingSoon: Activity[];  // 即將結束
    ongoing: Activity[];     // 進行中
    upcoming: Activity[];    // 即將開始
    notStarted: Activity[];  // 未開始
    ended: Activity[];       // 已結束
}

/**
 * 活動狀態分類定義
 */
const statusCategories: StatusCategory[] = [
    {
        name: '只限今日',
        category: 'todayOnly',
        image: '/images/event_status/today_only.jpg',
        color: 'bg-red-500/60',
        description: '今天開始且今天結束的活動'
    },
    {
        name: '即將結束',
        category: 'endingSoon',
        image: '/images/event_status/ending_soon.jpg',
        color: 'bg-orange-500/60',
        description: '3天內即將結束的活動'
    },
    {
        name: '進行中',
        category: 'ongoing',
        image: '/images/event_status/ongoing.jpg',
        color: 'bg-green-500/60',
        description: '已開始且距今超過3天的活動'
    },
    {
        name: '即將開始',
        category: 'upcoming',
        image: '/images/event_status/upcoming.jpg',
        color: 'bg-yellow-500/60',
        description: '3天內即將開始的活動'
    },
    {
        name: '未開始',
        category: 'notStarted',
        image: '/images/event_status/not_started.jpg',
        color: 'bg-gray-700/60',
        description: '距離開始還有超過3天的活動'
    },
    {
        name: '已結束',
        category: 'ended',
        image: '/images/event_status/ended.jpg',
        color: 'bg-gray-400/60',
        description: '已經結束的活動'
    }
];

// 狀態對應表 - 用於路由導航
const statusNameMap: Record<string, string> = {
    todayOnly: '只限今日',
    endingSoon: '即將結束',
    ongoing: '進行中',
    upcoming: '即將開始',
    notStarted: '未開始',
    ended: '已結束'
};

// 存儲所有分類的活動
const categorizedActivities = ref<CategorizedActivities>({
    todayOnly: [],
    endingSoon: [],
    ongoing: [],
    upcoming: [],
    notStarted: [],
    ended: []
});

// 當前顯示的活動索引 (所有類別)
const currentActivityIndices = ref<Record<string, number>>({
    todayOnly: 0,
    endingSoon: 0,
    ongoing: 0,
    upcoming: 0,
    notStarted: 0,
    ended: 0
});

// 預設圖片使用記錄
const usedDefaultImages = ref<Record<string, number>>({});

// 輪播計時器
let carouselTimers: Record<string, number | null> = {
    todayOnly: null,
    endingSoon: null,
    ongoing: null,
    upcoming: null,
    notStarted: null,
    ended: null
};

// 定義組件屬性
const {
    slidesPerView = 6,
    slidesPerGroup = 6,
    spaceBetween = 16,
    speed = 1200,
    title,
    secTitle,
    btn = { text: '', pathName: '' },
} = defineProps<SwiperOptions & {
    title: string
    secTitle?: string
    btn?: {
        text: string
        pathName: string
    }
}>();

const router = useRouter();
const { isBeginning, isEnd, onSwiper, onSlideChange } = useSwiper();

const btnUUID = v4();

/**
 * 計算輪播組件設定值
 */
const getBindValues = computed(() => {
    return {
        slidesPerView,
        slidesPerGroup,
        spaceBetween,
        speed,
        modules: [Navigation],
        navigation: {
            prevEl: `.swiper-${btnUUID}-custom-prev`,
            nextEl: `.swiper-${btnUUID}-custom-next`,
        },
        breakpoints: {
            '@0.00': {
                slidesPerView: 3,
                spaceBetween: 12,
                speed: 300,
            },
            '@0.75': {
                slidesPerView: 4,
                spaceBetween: 12,
                speed: 800,
            },
            '@1.00': {
                slidesPerView: 5,
                speed: 1000,
            },
            '@1.50': {
                slidesPerView,
                noSwiping: true,
            },
        },
    };
});

/**
 * 計算活動的雜湊值
 * @param activity 活動資料
 * @returns 雜湊值
 */
const calculateHash = (activity: Activity): number => {
    const idString = String(activity.id || '') + String(activity.activity_name || '');
    let hash = 0;
    for (let i = 0; i < idString.length; i++) {
        hash = ((hash << 5) - hash) + idString.charCodeAt(i);
        hash = hash & hash;
    }
    return Math.abs(hash);
};

/**
 * 獲取預設圖片索引
 * @param activity 活動資料
 * @param category 分類
 * @returns 圖片索引
 */
const getDefaultImageIndex = (activity: Activity, category: string): number => {
    const hash = calculateHash(activity);
    const baseIndex = hash % defaultActivityImages.length;

    // 檢查該索引是否已被使用
    const categoryKey = `${category}_${baseIndex}`;
    if (usedDefaultImages.value[categoryKey]) {
        // 尋找下一個未使用的索引
        for (let i = 0; i < defaultActivityImages.length; i++) {
            const nextIndex = (baseIndex + i) % defaultActivityImages.length;
            const nextKey = `${category}_${nextIndex}`;
            if (!usedDefaultImages.value[nextKey]) {
                usedDefaultImages.value[nextKey] = 1;
                return nextIndex;
            }
        }
        // 如果所有索引都被使用，重置並使用第一個
        return baseIndex;
    }

    // 標記為已使用
    usedDefaultImages.value[categoryKey] = 1;
    return baseIndex;
};

/**
 * 獲取活動圖片URL
 * @param activity 活動資料
 * @param category 分類
 * @returns 圖片URL
 */
const getActivityImageUrl = (activity: Activity, category: string): string => {
    if (!activity.image_url) {
        // 若無圖片使用預設圖片
        const index = getDefaultImageIndex(activity, category);
        return defaultActivityImages[index];
    }

    try {
        let imageUrls: string[] = [];

        // 處理字串或陣列型態的圖片URL
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

        // 過濾並取得第一個有效URL
        const validUrls = imageUrls
            .filter((url: string) => url && url.trim() && url !== 'None')
            .map((url: string) => url.trim());

        if (validUrls.length > 0) {
            return validUrls[0];
        } else {
            // 若無有效圖片使用預設圖片
            const index = getDefaultImageIndex(activity, category);
            return defaultActivityImages[index];
        }
    }
    catch (e) {
        console.error('獲取圖片URL錯誤:', e);
        // 發生錯誤時使用預設圖片
        const index = getDefaultImageIndex(activity, category);
        return defaultActivityImages[index];
    }
};

/**
 * 切換到下一個特定類別的活動
 * @param category 分類
 */
const nextActivity = (category: string): void => {
    const activities = categorizedActivities.value[category as keyof CategorizedActivities];
    if (activities && activities.length > 0) {
        currentActivityIndices.value[category] = (currentActivityIndices.value[category] + 1) % activities.length;
    }
};

/**
 * 獲取所有活動並進行分類
 */
const fetchAndCategorizeActivities = async (): Promise<void> => {
    try {
        // 直接從API或本地JSON檔案獲取活動數據
        const activities = await fetchActivitiesData();

        // 對活動進行分類
        const categorized = categorizeActivities(activities);
        categorizedActivities.value = categorized;

        // 將分類結果存入localStorage
        localStorage.setItem('categorizedActivities', JSON.stringify(categorized));
        localStorage.setItem('categorizedActivitiesTimestamp', new Date().getTime().toString());
    } catch (error) {
        console.error('分類活動時發生錯誤:', error);
    }
};

/**
 * 從本地JSON或API獲取活動數據
 * @returns 活動陣列
 */
const fetchActivitiesData = async (): Promise<Activity[]> => {
    try {
        // 優先嘗試從API獲取
        const apiResponse = await axios.get('/theme_entertainment/activities/api/list/');
        const apiActivities = apiResponse.data.data || apiResponse.data;
        console.log('成功從API獲取活動資料');
        return apiActivities;
    } catch (apiError) {
        console.error('從API獲取活動錯誤:', apiError);

        // API獲取失敗時，嘗試從本地JSON獲取
        try {
            const response = await import('@/assets/theme_entertainment/events_data.json');
            const activities = response.default;
            console.log('成功從本地JSON獲取活動資料');
            return activities;
        } catch (jsonError) {
            console.error('從本地JSON獲取活動錯誤:', jsonError);
            return [];
        }
    }
};

/**
 * 對活動數據進行分類
 * @param activities 活動陣列
 * @returns 分類後的活動
 */
const categorizeActivities = (activities: Activity[]): CategorizedActivities => {
    const now = new Date();
    const today = new Date(now);
    today.setHours(0, 0, 0, 0);

    const threeDays = 3 * 24 * 60 * 60 * 1000;

    // 初始化分類容器
    const categorized: CategorizedActivities = {
        todayOnly: [],
        endingSoon: [],
        ongoing: [],
        upcoming: [],
        notStarted: [],
        ended: []
    };

    // 分類活動
    activities.forEach((activity) => {
        // 檢查日期是否完整有效
        if (!activity.start_date || !activity.end_date) return;

        try {
            const startDate = new Date(activity.start_date);
            const endDate = new Date(activity.end_date);

            // 檢查日期是否有效
            if (isNaN(startDate.getTime()) || isNaN(endDate.getTime())) return;

            const startDiff = startDate.getTime() - now.getTime();
            const endDiff = endDate.getTime() - now.getTime();
            const isSameDay = startDate.toDateString() === endDate.toDateString();

            // 依照分類邏輯分類活動
            if (endDate < now) {
                // 已結束
                categorized.ended.push(activity);
            } else if (isSameDay && startDate.toDateString() === now.toDateString()) {
                // 只限今日
                categorized.todayOnly.push(activity);
            } else if (endDiff <= threeDays && endDiff > 0) {
                // 即將結束
                categorized.endingSoon.push(activity);
            } else if (now >= startDate && startDiff <= -threeDays) {
                // 進行中
                categorized.ongoing.push(activity);
            } else if (startDiff > 0 && startDiff <= threeDays) {
                // 即將開始
                categorized.upcoming.push(activity);
            } else if (startDiff > threeDays) {
                // 未開始
                categorized.notStarted.push(activity);
            }
        } catch (e) {
            console.error('處理活動日期時發生錯誤:', e);
        }
    });

    return categorized;
};

/**
 * 獲取特定分類的當前活動
 * @param category 分類
 * @returns 活動物件或null
 */
const getCurrentActivity = (category: string): Activity | null => {
    const activities = categorizedActivities.value[category as keyof CategorizedActivities];
    if (!activities || activities.length === 0) return null;

    const index = currentActivityIndices.value[category] || 0;
    return activities[index];
};

/**
 * 獲取特定分類的活動圖片URL
 * @param category 分類
 * @returns 圖片URL
 */
const getActivityImageForCategory = (category: string): string => {
    const activity = getCurrentActivity(category);
    if (!activity) {
        // 如果沒有活動，使用預設圖片
        const categoryData = statusCategories.find(s => s.category === category);
        return categoryData ? categoryData.image : '';
    }
    return getActivityImageUrl(activity, category);
};

/**
 * 獲取特定分類的活動名稱
 * @param category 分類
 * @returns 活動名稱
 */
const getActivityNameForCategory = (category: string): string => {
    const activity = getCurrentActivity(category);
    return activity ? activity.activity_name : '';
};

/**
 * 獲取特定分類的活動數量
 * @param category 分類
 * @returns 活動數量
 */
const getActivityCountForCategory = (category: string): number => {
    return categorizedActivities.value[category as keyof CategorizedActivities]?.length || 0;
};

/**
 * 獲取特定分類的當前活動索引
 * @param category 分類
 * @returns 當前索引
 */
const getCurrentActivityIndex = (category: string): number => {
    return currentActivityIndices.value[category] || 0;
};

/**
 * 點擊活動狀態卡片時的處理函數
 * @param category 分類
 */
const handleStatusCardClick = (category: string): void => {
    const statusName = statusNameMap[category] || category;
    router.push({
        name: 'ActivityList',
        query: { status: statusName }
    });
};

/**
 * 啟動所有類別的輪播計時器
 */
const startCarouselTimers = (): void => {
    // 為每個類別設置輪播計時器
    Object.keys(categorizedActivities.value).forEach((category) => {
        if (carouselTimers[category]) {
            clearInterval(carouselTimers[category]!);
        }

        // 只有當該類別有多個活動時才設置輪播
        if ((categorizedActivities.value[category as keyof CategorizedActivities]?.length || 0) > 1) {
            carouselTimers[category] = window.setInterval(() => nextActivity(category), 5000);
        }
    });
};

/**
 * 清除所有輪播計時器
 */
const clearAllCarouselTimers = (): void => {
    Object.keys(carouselTimers).forEach((category) => {
        if (carouselTimers[category]) {
            clearInterval(carouselTimers[category]!);
            carouselTimers[category] = null;
        }
    });
};

/**
 * 處理圖片載入錯誤
 * @param e 錯誤事件
 * @param category 分類
 */
const handleImageError = (e: Event, category: string) => {
    const target = e.target as HTMLImageElement;
    const activity = getCurrentActivity(category);

    if (activity) {
        // 若圖片載入失敗，使用另一個預設圖片
        const randomIndex = Math.floor(Math.random() * defaultActivityImages.length);
        target.src = defaultActivityImages[randomIndex];
    } else {
        // 若無活動，使用類別預設圖片
        const categoryData = statusCategories.find(s => s.category === category);
        if (categoryData) target.src = categoryData.image;
    }

    // 防止重複觸發錯誤
    target.onerror = null;
};

// 生命週期掛載完成時獲取活動並啟動輪播
onMounted(async () => {
    await fetchAndCategorizeActivities();
    startCarouselTimers();
});

// 組件卸載時清除所有輪播計時器
onUnmounted(() => {
    clearAllCarouselTimers();
});
</script>

<template>
    <SwiperLayout>
        <template #title>
            <Title :title="title" :sec-title="secTitle" />
        </template>
        <template #swiper>
            <Swiper :no-swiping="true" v-bind="getBindValues" @swiper="onSwiper" @slide-change="onSlideChange">
                <SwiperSlide v-for="status in statusCategories" :key="status.category" class="lg:swiper-no-swiping">
                    <div class="status-card" @click="handleStatusCardClick(status.category)">
                        <div class="status-image-container">
                            <img :src="getActivityImageForCategory(status.category)" :alt="status.name"
                                class="status-image" @error="(e) => handleImageError(e, status.category)"
                                :data-category="status.category">
                            <div class="status-overlay"></div>
                            <div v-if="getActivityNameForCategory(status.category)" class="activity-name">
                                {{ getActivityNameForCategory(status.category) }}
                            </div>
                        </div>
                        <div class="status-content" :class="status.color">
                            <div class="status-content-inner">
                                <h3 class="status-title text-white">{{ status.name }}</h3>
                            </div>
                        </div>
                    </div>
                </SwiperSlide>
            </Swiper>
            <CustomNavigation :classkey="btnUUID" :is-beginning="isBeginning" :is-end="isEnd" />
        </template>
        <template #btn>
            <div v-if="btn.text" class="mt-6 text-center md:mb-6 md:mt-12">
                <button type="button" class="btn">
                    {{ btn.text }}
                </button>
            </div>
        </template>
    </SwiperLayout>
</template>

<style scoped>
.status-card {
    cursor: pointer;
    height: 200px;
    width: 100%;
    border-radius: 5px;
    overflow: hidden;
    box-shadow: none;
    transition: all 0.3s ease;
    background-color: white;
    display: flex;
    flex-direction: column;
    position: relative;
    @apply md:h-60;
}

.status-card:hover {
    transform: none;
    box-shadow: none;
}

.status-image-container {
    position: relative;
    height: 100%;
    width: 100%;
    overflow: hidden;
}

.status-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.5s ease;
}

.status-card:hover .status-image {
    transform: scale(1.08);
}

.status-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(to bottom, rgba(0, 0, 0, 0.1) 0%, rgba(0, 0, 0, 0.5) 100%);
}

.activity-name {
    position: absolute;
    bottom: 50px;
    left: 10px;
    right: 10px;
    color: white;
    padding: 4px 8px;
    font-size: 14px;
    font-weight: 600;
    text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.9);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    background-color: transparent;
    border-radius: 4px;
}

.status-content {
    position: absolute;
    bottom: 0;
    left: 0;
    height: 40px;
    width: 100%;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    backdrop-filter: blur(1px);
}

.status-content-inner {
    width: 100%;
    text-align: center;
    padding: 0 8px;
}

.status-title {
    font-size: 15px;
    font-weight: 600;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    letter-spacing: 0.5px;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
    @apply md:text-xl;
}

@keyframes fadein {
    from {
        opacity: 0;
    }

    to {
        opacity: 1;
    }
}

.status-image {
    animation: fadein 0.5s;
}
</style>
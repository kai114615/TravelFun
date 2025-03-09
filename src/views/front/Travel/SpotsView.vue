<script setup>
import CategoriesComponent from '@/components/travelComponents/src/CategoriesComponent.vue';
import PageSizeComponent from '@/components/travelComponents/src/PageSizeComponent.vue';
import PagingComponent from '@/components/travelComponents/src/PagingComponent.vue';
import SearchComponent from '@/components/travelComponents/src/SearchComponent.vue';
import SortingComponent from '@/components/travelComponents/src/SortingComponent.vue';
import { ref, watchEffect, onMounted } from 'vue';
import Nav from '@/components/travelComponents/src/Nav.vue';
import axios from 'axios';


import { computed } from 'vue';
import { useRoute } from 'vue-router';

import Banner from '@/components/Banner.vue';
import Container from '@/layout/Container.vue';
import SpotPreviewModal from '@/components/travelComponents/src/SpotPreviewModal.vue';
import { useUserStore } from '@/stores/user';
import { useMessage } from 'naive-ui';
import { useRouter } from 'vue-router';
const Taiwenimg = new URL('@/assets/台灣圖片/台灣風景圖片.png', import.meta.url).href;
const imageUrl = '/旅遊圖片.png';

//資料的搜尋、分頁、排序
const ITEM = ref({
  "class1": 0,
  "search": "",
  "ordering": "spotid",
  "page": 1,
  "page_size": 20
})

//將ITEM資料轉成QueryString
const toQueryString = params => {
  return Object.keys(params)
    .filter(key => params[key] !== 0 && params[key] !== "")
    .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`)
    .join('&');
}

const SPOTS = ref([]) //接收API回傳的結果
const API_URL = 'http://127.0.0.1:8000/travel/api/travelfilter/'

//?categoryid=3&search=山&page=2&page_size=5&ordering=-spotid
watchEffect(async () => {

  const URL_PARAMS = `${API_URL}?${toQueryString(ITEM.value)}`
  const response = await fetch(URL_PARAMS)
  const datas = await response.json()
  SPOTS.value = datas
  
})

//page 會由子組件傳過來
//分頁功能
const pagingHandler = page => {
  window.scrollTo({
    top: 0, // 滾動到頂部
    behavior: "smooth", // 平滑滾動
  });
  ITEM.value.page = page
}

//關鍵字搜尋
//keyword 就是子組件傳過來的資料
const searchHandler = keyword => {
  ITEM.value.search = keyword
}

//排序
const sortingHandler = value => {
  ITEM.value.ordering = value
}

//一頁幾筆資料
const pageSizeHandler = value => {
  ITEM.value.page_size = +value
  ITEM.value.page = 1
}

//根據分類編號讀取景點
const CategoryHandler = id => {
  console.log(ITEM.value)
  ITEM.value.class1 = id
  ITEM.value.page = 1
}

const showPreview = ref(false);
const selectedSpot = ref(null);
const selectedTravelId = ref(null);

const openPreview = (spot) => {
  selectedSpot.value = spot;
  selectedTravelId.value = spot.travel_id;
  showPreview.value = true;
};

const closePreview = () => {
  showPreview.value = false;
  selectedSpot.value = null;
  selectedTravelId.value = null;
};

// 檢查景點是否已加入我的景點
const isSpotAdded = (spotId) => {
  const key = `mySpots_${userStore.userInfo?.id}`;
  const mySpots = JSON.parse(localStorage.getItem(key) || '[]');
  return mySpots.some(spot => spot.travel_id === spotId);
};

const userStore = useUserStore();
const message = useMessage();
const router = useRouter();

// 加入/移除景點
const addToMySpots = (spot) => {
  if (!userStore.loginStatus) {
    message.warning('請先登入才能加入景點');
    router.push({
      name: 'Login',
      query: { redirect: router.currentRoute.value.fullPath }
    });
    return;
  }

  const key = `mySpots_${userStore.userInfo?.id}`;
  const mySpots = JSON.parse(localStorage.getItem(key) || '[]');
  if (!isSpotAdded(spot.travel_id)) {
    // 加入景點
    mySpots.push(spot);
    localStorage.setItem(key, JSON.stringify(mySpots));
    // 強制更新組件
    SPOTS.value = { ...SPOTS.value };
    message.success('已加入景點');
  } else {
    // 移除景點
    const updatedSpots = mySpots.filter(s => s.travel_id !== spot.travel_id);
    localStorage.setItem(key, JSON.stringify(updatedSpots));
    // 強制更新組件
    SPOTS.value = { ...SPOTS.value };
    message.success('已移除景點');
  }
};

// 處理 SpotPreviewModal 更新事件
const handleSpotsUpdate = () => {
  // 強制更新組件
  SPOTS.value = { ...SPOTS.value };
};

</script>

<template>

<Banner bg-url="/images/banner.jpg">
    <template #title>
      景點搜尋
    </template>
    <template #sec-title>
      探索台灣各地的風俗名情
    </template>
  </Banner>
  <Nav class="mb-6" />
  <div class="spots-container">
    <!-- 頂部橫幅圖片 -->
    <!-- 標題和功能區 -->
    <div class="function-area">
      <div class="title-controls">
        <h2 class="main-title">台灣景點</h2>
        <div class="flex-spacer"></div>
        <div class="control-group">
          <div class="control-item">
            <PageSizeComponent @PageSizeChange="pageSizeHandler" />
          </div>
          <div class="control-item">
            <SortingComponent @sortChange="sortingHandler" />
          </div>
        </div>
      </div>
    </div>

    <!-- 主要內容區 -->
    <div class="main-content">
      <div class="content-wrapper">
        <!-- 搜尋和分類區 -->
        <div class="filter-section">
          <div class="search-area">
            <SearchComponent @searchInput="searchHandler" />
          </div>
          <div class="category-area">
            <CategoriesComponent @categoryClick="CategoryHandler" />
          </div>
        </div>

        <!-- 景點卡片列表 -->
        <div class="spots-grid">
          <div v-for="spot in SPOTS.results" 
               :key="spot.travel_id" 
               class="spot-card">
            <div class="card-inner">
              <div class="card-actions">
                <button class="preview-button" @click="openPreview(spot)">
                  <i class="fas fa-eye"></i>
                  <span>預覽</span>
                </button>
                <button 
                  :class="['add-button', { 'added': userStore.loginStatus && isSpotAdded(spot.travel_id) }]"
                  @click="addToMySpots(spot)"
                >
                  <i :class="['fas', !userStore.loginStatus ? 'fa-plus' : (isSpotAdded(spot.travel_id) ? 'fa-trash' : 'fa-plus')]"></i>
                  <span>{{ !userStore.loginStatus ? '加入景點' : (isSpotAdded(spot.travel_id) ? '移除景點' : '加入景點') }}</span>
                </button>
              </div>
              <div class="card-image">
                <img v-if="spot.image1" :src="spot.image1" :alt="spot.travel_name">
                <img v-else :src="imageUrl" :alt="spot.travel_name">
              </div>
              <div class="card-content">
                <h3 class="spot-title">{{ spot.travel_name }}</h3>
                <p class="spot-description">{{ spot.travel_txt }}</p>
              </div>
              <div class="card-footer">
                <template v-if="spot.travel_address">
                  <strong>地址:</strong>
                  <span class="address">{{ spot.travel_address }}</span>
                </template>
                <template v-else>
                  <strong>縣市:</strong>
                  <span>{{ spot.region }} {{ spot.town }}</span>
                </template>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 分頁控制 -->
    <div class="pagination-wrapper">
      <PagingComponent 
        @goPaging="pagingHandler" 
        :thePage="SPOTS.current_page" 
        :totalPages="SPOTS.total_page"
      />
    </div>
  </div>
  
  <SpotPreviewModal 
    :is-open="showPreview"
    :spot="selectedSpot"
    :travel_id="selectedTravelId"
    @close="closePreview"
    @update-spots="handleSpotsUpdate"
  />
</template>

<style lang="scss" scoped>
.spots-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.banner-image {
  margin-bottom: 2rem;
  
  .taiwan-img {
    width: 100%;
    height: 300px;
    object-fit: cover;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  }
}

.function-area {
  margin-bottom: 2rem;
  position: relative;

  .title-controls {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1rem;
    position: relative;
    padding-bottom: 1rem;

    &::after {
      content: '';
      position: absolute;
      bottom: 0;
      left: 0;
      width: 100%;
      height: 1px;
      background: linear-gradient(to right, #2c3e50 30%, transparent);
    }

    .main-title {
      font-size: 2rem;
      color: #2c3e50;
      margin: 0;
      white-space: nowrap;
    }

    .flex-spacer {
      flex: 1;
    }

    .control-group {
      display: flex;
      gap: 1rem;
      align-items: center;

      .control-item {
        width: 200px;
      }
    }
  }

  .search-wrapper {
    width: 100%;
    
    .control-item.search {
      width: 100%;
    }
  }
}

.main-content {
  display: flex;
  flex-direction: column;
  margin-bottom: 2rem;
  align-items: center;
}

.content-wrapper {
  width: 90%;
  max-width: 1200px;
  margin: 0 auto;
}

.filter-section {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  padding: 1.5rem;
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;

  .search-area {
    flex: 2;
  }

  .category-area {
    flex: 1;
  }
}

.spots-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
  margin-top: 2rem;
}

.spot-card {
  .card-inner {
    background: white;
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    transition: all 0.3s ease;
    position: relative;
    height: 100%;
    display: flex;
    flex-direction: column;

    &:hover {
      transform: translateY(-5px);
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);

      .card-image img {
        transform: scale(1.05);
      }
    }

    .card-image {
      height: 220px;
      overflow: hidden;
      position: relative;

      &::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(to bottom, transparent 60%, rgba(0, 0, 0, 0.1));
      }

      img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        transition: transform 0.3s ease;
      }
    }

    .card-content {
      padding: 1.25rem;
      flex-grow: 1;
      display: flex;
      flex-direction: column;
      gap: 0.75rem;

      .spot-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #2c3e50;
        line-height: 1.4;
        margin: 0;
      }

      .spot-description {
        color: #666;
        font-size: 0.9rem;
        line-height: 1.5;
        display: -webkit-box;
        -webkit-line-clamp: 3;
        -webkit-box-orient: vertical;
        line-clamp: 3;
        overflow: hidden;
      }
    }

    .card-footer {
      padding: 1.25rem;
      background: #f8f9fa;
      border-top: 1px solid #eee;

      strong {
        color: #2c3e50;
        font-weight: 600;
        margin-right: 0.5rem;
      }

      span {
        color: #666;
        font-size: 0.95rem;
      }
    }
  }
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  padding: 2rem 0;
}

@media (max-width: 1400px) {
  .spots-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

@media (max-width: 1100px) {
  .spots-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .content-wrapper {
    width: 95%;
  }

  .spots-grid {
    grid-template-columns: repeat(1, 1fr);
    gap: 16px;
  }

  .spot-card .card-inner {
    .card-image {
      height: 200px;
    }

    .card-content {
      padding: 1rem;
      
      .spot-title {
        font-size: 1.2rem;
      }
    }

    .card-footer {
      padding: 1rem;
    }
  }

  .preview-button,
  .add-button {
    min-width: 72px;
    height: 32px;
    font-size: 12px;
    padding: 0 12px;
    
    i {
      font-size: 12px;
    }
  }
}

.card-actions {
  position: absolute;
  top: 12px;
  right: 12px;
  display: flex;
  gap: 8px;
  z-index: 2;
}

.preview-button,
.add-button {
  min-width: 80px;
  height: 36px;
  padding: 0 16px;
  border: none;
  border-radius: 50px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-size: 13px;
  backdrop-filter: blur(4px);
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  
  i {
    font-size: 13px;
  }
  
  span {
    font-weight: 500;
  }
}

.preview-button {
  background: rgba(15, 75, 180, 0.9);
  color: white;
  
  &:hover {
    background: rgba(13, 61, 145, 0.95);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  }
}

.add-button {
  background: rgba(40, 167, 69, 0.9);
  color: white;
  
  &:hover:not(:disabled) {
    background: rgba(34, 139, 58, 0.95);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  }
  
  &.added {
    background: rgba(220, 53, 69, 0.9);
    cursor: not-allowed;
    
    &:hover {
      transform: none;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    }
  }
  
  &:disabled {
    cursor: not-allowed;
  }
}

.address {
  text-align: left;
  color: #666;
  font-size: 14px;
  margin-top: 4px;
}
</style>
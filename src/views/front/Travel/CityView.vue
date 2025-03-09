<script setup>
import { useRoute } from 'vue-router';
import { ref,  computed , watchEffect } from 'vue';
import Nav from '@/components/travelComponents/src/Nav.vue';
import Banner from '@/components/Banner.vue';
import Container from '@/layout/Container.vue';
import SpotPreviewModal from '@/components/travelComponents/src/SpotPreviewModal.vue';
import { useUserStore } from '@/stores/user';
import { useMessage } from 'naive-ui';
import { useRouter } from 'vue-router';

// Props 定義
defineProps({
  city: String,
});
const place_data=[
  {
   tag: "taipei_city",
   place: "臺北市",
   presentation: "台灣首都，融合現代與歷史，擁有台北101與故宮博物院。",
   route: "/api/city/臺北市",
   picture:new URL('@/assets/台灣圖片/台北市.jpg', import.meta.url).href
  },
  {
   tag: "new_taipei_city",
   place: "新北市",
   presentation: "環繞台北市，擁有美麗的海岸線與山脈，是都市與自然的結合。",
   route: "/api/city/新北市",
   picture:new URL('@/assets/台灣圖片/新北市.jpg', import.meta.url).href
  },

  {
   tag: "taichung_city",
   place: "臺中市",
   presentation: "文化藝術之都，擁有許多博物館與自然景點。",
   route: "/api/city/臺中市",
   picture:new URL('@/assets/台灣圖片/台中市.jpg', import.meta.url).href

   
  },

  {
   tag: "tainan_city",
   place: "臺南市",
   presentation: "台灣歷史悠久的城市，擁有古老的廟宇與美食。",
   route: "/api/city/臺南市",
   picture:new URL('@/assets/台灣圖片/台南市.jpg', import.meta.url).href

  },

  {
   tag: "kaohsiung_city",
   place: "高雄市",
   presentation: "南部大城市，擁有台灣最大的港口及繁華的夜市。",
   route: "/api/city/高雄市",
   picture:new URL('@/assets/台灣圖片/高雄市.jpg', import.meta.url).href

  },

  {
   tag: "keelung_city",
   place: "基隆市",
   presentation: "位於台灣北端，擁有繁忙的港口及美麗的海景。",
   route: "/api/city/基隆市",
   picture:new URL('@/assets/台灣圖片/基隆市.jpg', import.meta.url).href

  },

  {
   tag: "taoyuan_country",
   place: "桃園市",
   presentation: "擁有台灣主要國際機場，是重要的交通樞紐。",
   route: "/api/city/桃園市",
   picture:new URL('@/assets/台灣圖片/桃園市.jpg', import.meta.url).href

  },

  {
   tag: "hsinchu_city",
   place: "新竹市",
   presentation: "科技重鎮，擁有新竹科學園區及豐富的歷史景點。",
   route: "/api/city/新竹市",
   picture:new URL('@/assets/台灣圖片/新竹市.jpg', import.meta.url).href

  },

  {
   tag: "hsinchu_country",
   place: "新竹縣",
   presentation: "科技園區與古老文化相結合，擁有豐富的歷史景點。",
   route: "/api/city/新竹縣",
   picture:new URL('@/assets/台灣圖片/新竹縣.jpg', import.meta.url).href

  },

  {
   tag: "miaoli_country",
   place: "苗栗縣",
   presentation: "擁有美麗的山區風光與豐富的客家文化",
   route: "/api/city/苗栗縣",
   picture:new URL('@/assets/台灣圖片/苗栗縣.jpg', import.meta.url).href

  },

  {
   tag: "changhua_country",
   place: "彰化縣",
   presentation: "以傳統工藝和文化著名，擁有古老的廟宇。",
   route: "/api/city/彰化縣",
   picture:new URL('@/assets/台灣圖片/彰化縣.jpg', import.meta.url).href

  },

  {
   tag: "nantou_country",
   place: "南投縣",
   presentation: "以日月潭為代表的美麗湖泊與山區風景。",
   route: "/api/city/南投縣",
   picture:new URL('@/assets/台灣圖片/南投縣.jpg', import.meta.url).href

  },

  {
   tag: "yunlin_country",
   place: "雲林縣",
   presentation: "農業重鎮，擁有豐富的自然資源與文化遺產。",
   route: "/api/city/雲林縣",
   picture:new URL('@/assets/台灣圖片/雲林縣.jpg', import.meta.url).href

  },

  {
   tag: "chiayi_city",
   place: "嘉義市",
   presentation: "擁有阿里山、茶園與文化遺產的知名旅遊城市。",
   route: "/api/city/嘉義市",
   picture:new URL('@/assets/台灣圖片/嘉義市.jpg', import.meta.url).href

  },

  {
   tag: "chiayi_country",
   place: "嘉義縣",
   presentation: "擁有美麗的山脈與豐富的農業資源。",
   route: "/city/嘉義縣",
   picture:new URL('@/assets/台灣圖片/嘉義縣.jpg', import.meta.url).href

  },

  {
   tag: "pingtung_country",
   place: "屏東縣",
   presentation: "台灣最南端，擁有美麗的海灘與自然景點。",
   route: "/api/city/屏東縣",
   picture:new URL('@/assets/台灣圖片/屏東縣.jpg', import.meta.url).href

  },

  {
   tag: "yilan_country",
   place: "宜蘭縣",
   presentation: "風景如畫，擁有美麗的海岸線與溫泉。",
   route: "/api/city/宜蘭縣",
   picture:new URL('@/assets/台灣圖片/宜蘭縣.jpg', import.meta.url).href

  },

  {
   tag: "hualien_country",
   place: "花蓮縣",
   presentation: "擁有壯麗的太魯閣峽谷與美麗的海岸。",
   route: "/api/city/花蓮縣",
   picture:new URL('@/assets/台灣圖片/花蓮縣.jpg', import.meta.url).href

  },

  {
   tag: "taitung_country",
   place: "臺東縣",
   presentation: "自然景觀豐富，是台灣東部的度假天堂。",
   route: "/api/city/臺東縣",
   picture:new URL('@/assets/台灣圖片/台東縣.jpg', import.meta.url).href

  },

  {
   tag: "penghu_country",
   place: "澎湖縣",
   presentation: "由多個小島組成，擁有美麗的沙灘與海洋生態",
   route: "/api/city/澎湖縣",
   picture:new URL('@/assets/台灣圖片/澎湖縣.jpg', import.meta.url).href

  },

  {
   tag: "kinmen_country",
   place: "金門縣",
   presentation: "具有豐富歷史背景，擁有古老的軍事遺跡與美麗的海景。",
   route: "/api/city/金門縣"
  },

  {
   tag: "lienchiang_country",
   place: "連江縣",
   presentation: "位於台灣海峽，擁有傳統的閩南文化與風光明媚的海島景致。",
   route: "/city/連江縣"
   
  },
];
const route = useRoute();
const city = ref(route.params.city);
const filteredData = computed(() => {
  return place_data.filter(item => item.place.includes(city.value));
});
const imageUrl = '/旅遊圖片.png';
const country = ref([]);
const showPreview = ref(false);
const selectedSpot = ref(null);
const selectedTravelId = ref(null);

const currentPage = ref(1); // 當前頁碼
const pageSize = ref(15); // 每頁顯示的數據數量

const BASE_URL = 'http://127.0.0.1:8000/travel/api';

const class_id = ref([]);
const loadClass = async () => {
  const API_URL = `${BASE_URL}/travelclass/`;
  try {
    const response = await fetch(API_URL);
    const datas = await response.json();
    if (Array.isArray(datas)) {
      class_id.value = datas;
    } else {
      console.error('類別資料格式錯誤:', datas);
      class_id.value = [];
    }
  } catch (error) {
    console.error('載入類別資料失敗:', error);
    class_id.value = [];
  }
};
loadClass();

// 加載景點數據
const spots = ref([]);
const loadCategories = async () => {
  const API_URL = `${BASE_URL}/travel/`;
  try {
    const response = await fetch(API_URL);
    const datas = await response.json();
    if (Array.isArray(datas)) {
      spots.value = datas.filter((data) => data.region === route.params.city);
      filtereTown.value = [...spots.value]; // 初始化完整數據
    } else {
      console.error('景點資料格式錯誤:', datas);
      spots.value = [];
      filtereTown.value = [];
    }
  } catch (error) {
    console.error('載入景點資料失敗:', error);
    spots.value = [];
    filtereTown.value = [];
  }
};
loadCategories();

// 加載城鎮數據
const towns = ref([]);
const loadTowns = async () => {
  const API_URL_town = `${BASE_URL}/taiwan/`;
  try {
    const response = await fetch(API_URL_town);
    const datas = await response.json();
    if (Array.isArray(datas)) {
      towns.value = [];
      datas.forEach((item) => {
        if (
          item.region === route.params.city ||
          (route.params.city.startsWith('臺') &&
            item.region.startsWith('台') &&
            item.region.slice(1, 3) === route.params.city.slice(1, 3))
        ) {
          towns.value.push(item.town);
        }
      });
    } else {
      console.error('城鎮資料格式錯誤:', datas);
      towns.value = [];
    }
  } catch (error) {
    console.error('載入城鎮資料失敗:', error);
    towns.value = [];
  }
};
loadTowns();


const callClass= (classId) => {
    for(let id=0;id<class_id.value.length;id++){
      if(classId==class_id.value[id].class_id){
        console.log(class_id.value[id].class_name)
        return class_id.value[id].class_name;
      }     
    }
};


const filtereTown = ref([]);
const filterData = (town) => {
  if (town !== 1) {
    if (country.value.includes(town)) {
      country.value = country.value.filter(t => t !== town);
      if (country.value.length === 0) {
        spots.value = [...filtereTown.value];
      } else {
        spots.value = filtereTown.value.filter((item) => 
          country.value.includes(item.town)
        );
      }
    } else {
      if (country.value.length < 3) {
        country.value.push(town);
        spots.value = filtereTown.value.filter((item) => 
          country.value.includes(item.town)
        );
      }
    }
  } else {
    country.value = [];
    spots.value = [...filtereTown.value];
  }
  currentPage.value = 1; // 重置到第 1 頁
};

// 分頁邏輯
const totalPages = computed(() => Math.ceil(spots.value.length / pageSize.value));
const paginatedSpots = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  const end = start + pageSize.value;
  return spots.value.slice(start, end);
});

// 顯示的頁碼範圍
const pageRange = computed(() => {
  const maxPagesToShow = 10;
  const total = totalPages.value;
  const current = currentPage.value;
  const start = Math.max(1, current - Math.floor(maxPagesToShow / 2));
  const end = Math.min(total, start + maxPagesToShow - 1);
  return Array.from({ length: end - start + 1 }, (_, i) => start + i);
});

// 切換頁面
const goToPage = (page) => {
  window.scrollTo({
    top: 0, // 滾動到頂部
    behavior: "smooth", // 平滑滾動
  });
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page;
  }
};

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
    spots.value = [...spots.value];
    message.success('已加入景點');
  } else {
    // 移除景點
    const updatedSpots = mySpots.filter(s => s.travel_id !== spot.travel_id);
    localStorage.setItem(key, JSON.stringify(updatedSpots));
    // 強制更新組件
    spots.value = [...spots.value];
    message.success('已移除景點');
  }
};

// 過濾數據

</script>

<template>
  <Banner :bg-url="filteredData[0].picture">
    <template #title>
      {{route.params.city}}
    </template>
  </Banner>
  <Nav class="mb-6" />
  
  <div class="spots-container">
    <!-- 標題和功能區 -->
    <div class="function-area">
      <div class="title-controls">
        <h2 class="main-title">城市: <span v-if="country.length > 0" class="text-cc-primary">{{ country.join('、') }}</span></h2>
        <div class="flex-spacer"></div>
        <div class="control-group">
          <div class="control-item">
            <select v-model="pageSize" class="form-select">
              <option value="15">每頁 15 筆</option>
              <option value="30">每頁 30 筆</option>
              <option value="50">每頁 50 筆</option>
            </select>
          </div>
        </div>
      </div>
    </div>
    
    <div class="main-content">
      <div class="content-wrapper">
        <!-- 資料顯示區域 -->
        <div class="stats-section">
          <div class="stats-grid">
            <div class="stat-card">
              <div class="stat-icon">
                <i class="fas fa-map-marker-alt"></i>
              </div>
              <div class="stat-content">
                <h4>總景點數</h4>
                <p class="stat-value">{{ spots.length }}</p>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon">
                <i class="fas fa-city"></i>
              </div>
              <div class="stat-content">
                <h4>區域數量</h4>
                <p class="stat-value">{{ towns.length }}</p>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon">
                <i class="fas fa-location-arrow"></i>
              </div>
              <div class="stat-content">
                <h4>當前區域</h4>
                <p class="stat-value">{{ country.length ? country.join('、') : '全部' }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- 側邊欄改為頂部過濾區 -->
        <div class="filter-section">
          <div class="selection-info">
            <span class="selection-count">
              已選取: {{ country.length }}/3
            </span>
          </div>
          <div class="town-filter">
            <button 
              @click="filterData(1)"
              class="filter-btn"
              :class="{ active: country.length === 0 }"
            >
              全部地區
            </button>
            <button
              v-for="town in towns"
              :key="town"
              @click="filterData(town)"
              class="filter-btn"
              :disabled="country.length >= 3 && !country.includes(town)"
              :class="{ 
                active: country.includes(town),
                'disabled': country.length >= 3 && !country.includes(town)
              }"
            >
              {{ town }}
            </button>
          </div>
        </div>

        <!-- 景點列表 -->
        <div v-if="paginatedSpots.length" class="spots-grid">
          <div v-for="spot in paginatedSpots" 
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
                <img 
                  :src="spot.image1 || imageUrl" 
                  :alt="spot.travel_name"
                >
              </div>
              <div class="card-content">
                <h3 class="spot-title">{{ spot.travel_name }}</h3>
                <p class="spot-description">{{ spot.travel_txt }}</p>
                <div class="spot-tags">
                  <span v-if="spot.class1" class="tag">{{ callClass(spot.class1) }}</span>
                  <span v-if="spot.class2" class="tag">{{ callClass(spot.class2) }}</span>
                  <span v-if="spot.class3" class="tag">{{ callClass(spot.class3) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div v-else class="no-data">
          目前尚未有景點資料
    </div>

        <!-- 分頁控制 -->
        <div class="pagination-wrapper">
          <div class="pagination">
            <button 
              @click="goToPage(currentPage - 1)" 
              :disabled="currentPage === 1"
              class="page-btn"
            >
              上一頁
            </button>
            <button
              v-for="page in pageRange"
              :key="page"
              @click="goToPage(page)"
              class="page-btn"
              :class="{ active: currentPage === page }"
            >
          {{ page }}
        </button>
            <button 
              @click="goToPage(currentPage + 1)"
              :disabled="currentPage === totalPages"
              class="page-btn"
            >
              下一頁
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
  <SpotPreviewModal 
    :is-open="showPreview"
    :spot="selectedSpot"
    :travel_id="selectedTravelId"
    @close="closePreview"
  />
</template>

<style lang="scss" scoped>
.spots-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.function-area {
  margin-bottom: 2rem;

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
    }

    .flex-spacer {
      flex: 1;
    }
  }
}

.filter-section {
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);

  .selection-info {
    margin-bottom: 1rem;
    
    .selection-count {
      display: inline-block;
      padding: 0.25rem 0.75rem;
      background: #e9f2ff;
      color: #0F4BB4;
      border-radius: 20px;
      font-size: 0.875rem;
    }
  }

  .town-filter {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .filter-btn {
    padding: 0.5rem 1rem;
    border-radius: 20px;
    border: 1px solid #ddd;
    background: white;
    color: #666;
    transition: all 0.3s ease;

    &:hover {
      background: #f8f9fa;
    }

    &.active {
      background: #0F4BB4;
      color: white;
      border-color: #0F4BB4;
    }

    &.disabled {
      opacity: 0.5;
      cursor: not-allowed;
      
      &:hover {
        background: white;
        color: #666;
        border-color: #ddd;
      }
    }
  }
}

.spots-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

@media (max-width: 1200px) {
  .spots-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 992px) {
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
  }

  .filter-section {
    padding: 1rem;
  }

  .stats-grid {
    grid-template-columns: repeat(1, 1fr) !important;
  }
}

.spot-card {
  .card-inner {
    background: white;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    transition: transform 0.2s ease;
    position: relative;

    &:hover {
      transform: translateY(-5px);
    }

    .card-image {
  height: 200px;
      overflow: hidden;

      img {
        width: 100%;
        height: 100%;
        object-fit: cover;
      }
    }

    .card-content {
      padding: 1rem;

      .spot-title {
        font-size: 1.2rem;
        color: #2c3e50;
        margin-bottom: 0.5rem;
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

      .spot-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-top: 1rem;

        .tag {
          padding: 0.25rem 0.75rem;
          background: #e9f2ff;
          color: #0F4BB4;
          border-radius: 20px;
          font-size: 0.875rem;
        }
      }
    }
  }
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  padding: 2rem 0;

  .pagination {
    display: flex;
    gap: 0.5rem;

    .page-btn {
      padding: 0.5rem 1rem;
      border: 1px solid #ddd;
      border-radius: 6px;
      background: white;
      color: #666;
      transition: all 0.3s ease;

      &:hover:not(:disabled) {
        background: #f8f9fa;
      }

      &.active {
        background: #0F4BB4;
        color: white;
        border-color: #0F4BB4;
      }

      &:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }
    }
  }
}

.no-data {
  text-align: center;
  padding: 3rem;
  color: #666;
}

.stats-section {
  margin-bottom: 2rem;
  
  .stats-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
  }

  .stat-card {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    display: flex;
    align-items: center;
    gap: 1rem;
    transition: transform 0.2s ease;

    &:hover {
      transform: translateY(-2px);
    }

    .stat-icon {
      width: 48px;
      height: 48px;
      background: #e9f2ff;
      border-radius: 12px;
      display: flex;
      align-items: center;
  justify-content: center; 
      color: #0F4BB4;
      font-size: 1.5rem;
    }

    .stat-content {
      flex: 1;

      h4 {
        color: #666;
        font-size: 0.875rem;
        margin-bottom: 0.25rem;
      }

      .stat-value {
        color: #0F4BB4;
        font-size: 1.5rem;
        font-weight: bold;
      }
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

@media (max-width: 768px) {
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
</style>

<script setup>
import { ref, onMounted, computed } from 'vue';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import axios from 'axios';
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';
import { watchEffect } from 'vue';

import Nav from '@/components/travelComponents/src/Nav.vue';
import { NBreadcrumb, NBreadcrumbItem } from 'naive-ui';

import { useRoute, useRouter } from 'vue-router';

import Banner from '@/components/Banner.vue';
import Container from '@/layout/Container.vue';
import SpotPreviewModal from '@/components/travelComponents/src/SpotPreviewModal.vue';
import { useUserStore } from '@/stores/user';
import { useMessage } from 'naive-ui';

let DefaultIcon = L.icon({
  iconUrl: icon,
  shadowUrl: iconShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
});

let ActiveIcon = L.icon({
  iconUrl: icon,
  shadowUrl: iconShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  className: 'red-marker'
});

L.Marker.prototype.options.icon = DefaultIcon;

const place_data=[
  {
   tag: "taipei_city",
   place: "臺北市",
   presentation: "台灣首都，融合現代與歷史，擁有台北101與故宮博物院。",
   route: "/臺北市",
   picture:new URL('@/assets/台灣圖片/台北市.jpg', import.meta.url).href
  },
  {
   tag: "new_taipei_city",
   place: "新北市",
   presentation: "環繞台北市，擁有美麗的海岸線與山脈，是都市與自然的結合。",
   route: "/新北市",
   picture:new URL('@/assets/台灣圖片/新北市.jpg', import.meta.url).href
  },

  {
   tag: "taichung_city",
   place: "臺中市",
   presentation: "文化藝術之都，擁有許多博物館與自然景點。",
   route: "/臺中市",
   picture:new URL('@/assets/台灣圖片/台中市.jpg', import.meta.url).href

   
  },

  {
   tag: "tainan_city",
   place: "臺南市",
   presentation: "台灣歷史悠久的城市，擁有古老的廟宇與美食。",
   route: "/臺南市",
   picture:new URL('@/assets/台灣圖片/台南市.jpg', import.meta.url).href

  },

  {
   tag: "kaohsiung_city",
   place: "高雄市",
   presentation: "南部大城市，擁有台灣最大的港口及繁華的夜市。",
   route: "/高雄市",
   picture:new URL('@/assets/台灣圖片/高雄市.jpg', import.meta.url).href

  },

  {
   tag: "keelung_city",
   place: "基隆市",
   presentation: "位於台灣北端，擁有繁忙的港口及美麗的海景。",
   route: "/基隆市",
   picture:new URL('@/assets/台灣圖片/基隆市.jpg', import.meta.url).href

  },

  {
   tag: "taoyuan_country",
   place: "桃園市",
   presentation: "擁有台灣主要國際機場，是重要的交通樞紐。",
   route: "/桃園市",
   picture:new URL('@/assets/台灣圖片/桃園市.jpg', import.meta.url).href

  },

  {
   tag: "hsinchu_city",
   place: "新竹市",
   presentation: "科技重鎮，擁有新竹科學園區及豐富的歷史景點。",
   route: "/新竹市",
   picture:new URL('@/assets/台灣圖片/新竹市.jpg', import.meta.url).href

  },

  {
   tag: "hsinchu_country",
   place: "新竹縣",
   presentation: "科技園區與古老文化相結合，擁有豐富的歷史景點。",
   route: "/新竹縣",
   picture:new URL('@/assets/台灣圖片/新竹縣.jpg', import.meta.url).href

  },

  {
   tag: "miaoli_country",
   place: "苗栗縣",
   presentation: "擁有美麗的山區風光與豐富的客家文化",
   route: "/苗栗縣",
   picture:new URL('@/assets/台灣圖片/苗栗縣.jpg', import.meta.url).href

  },

  {
   tag: "changhua_country",
   place: "彰化縣",
   presentation: "以傳統工藝和文化著名，擁有古老的廟宇。",
   route: "/彰化縣",
   picture:new URL('@/assets/台灣圖片/彰化縣.jpg', import.meta.url).href

  },

  {
   tag: "nantou_country",
   place: "南投縣",
   presentation: "以日月潭為代表的美麗湖泊與山區風景。",
   route: "/南投縣",
   picture:new URL('@/assets/台灣圖片/南投縣.jpg', import.meta.url).href

  },

  {
   tag: "yunlin_country",
   place: "雲林縣",
   presentation: "農業重鎮，擁有豐富的自然資源與文化遺產。",
   route: "/雲林縣",
   picture:new URL('@/assets/台灣圖片/雲林縣.jpg', import.meta.url).href

  },

  {
   tag: "chiayi_city",
   place: "嘉義市",
   presentation: "擁有阿里山、茶園與文化遺產的知名旅遊城市。",
   route: "/嘉義市",
   picture:new URL('@/assets/台灣圖片/嘉義市.jpg', import.meta.url).href

  },

  {
   tag: "chiayi_country",
   place: "嘉義縣",
   presentation: "擁有美麗的山脈與豐富的農業資源。",
   route: "/嘉義縣",
   picture:new URL('@/assets/台灣圖片/嘉義縣.jpg', import.meta.url).href

  },

  {
   tag: "pingtung_country",
   place: "屏東縣",
   presentation: "台灣最南端，擁有美麗的海灘與自然景點。",
   route: "/屏東縣",
   picture:new URL('@/assets/台灣圖片/屏東縣.jpg', import.meta.url).href

  },

  {
   tag: "yilan_country",
   place: "宜蘭縣",
   presentation: "風景如畫，擁有美麗的海岸線與溫泉。",
   route: "/宜蘭縣",
   picture:new URL('@/assets/台灣圖片/宜蘭縣.jpg', import.meta.url).href

  },

  {
   tag: "hualien_country",
   place: "花蓮縣",
   presentation: "擁有壯麗的太魯閣峽谷與美麗的海岸。",
   route: "/花蓮縣",
   picture:new URL('@/assets/台灣圖片/花蓮縣.jpg', import.meta.url).href

  },

  {
   tag: "taitung_country",
   place: "臺東縣",
   presentation: "自然景觀豐富，是台灣東部的度假天堂。",
   route: "/臺東縣",
   picture:new URL('@/assets/台灣圖片/台東縣.jpg', import.meta.url).href

  },

  {
   tag: "penghu_country",
   place: "澎湖縣",
   presentation: "由多個小島組成，擁有美麗的沙灘與海洋生態",
   route: "/澎湖縣",
   picture:new URL('@/assets/台灣圖片/澎湖縣.jpg', import.meta.url).href

  },

  {
   tag: "kinmen_country",
   place: "金門縣",
   presentation: "具有豐富歷史背景，擁有古老的軍事遺跡與美麗的海景。",
   route: "/金門縣"
  },

  {
   tag: "lienchiang_country",
   place: "連江縣",
   presentation: "位於台灣海峽，擁有傳統的閩南文化與風光明媚的海島景致。",
   route: "/連江縣"
   
  },
];

const BASE_URL = 'http://127.0.0.1:8000/travel/api';

const allLocations = ref([]);
const filteredLocations = ref([]);
const selectedCity = ref([]);
const cityOptions = ref([]);
const map = ref(null);
const markers = ref([]);
const searchKeyword = ref(""); // 1. 新增一個反應式變數用於存儲搜尋的關鍵字
const imageUrl = '/旅遊圖片.png';
const selectedSpot = ref(null);
const showPreview = ref(false);
const selectedSpotForPreview = ref(null);
const selectedTravelId = ref(null);

const userStore = useUserStore();
const message = useMessage();
const router = useRouter();

onMounted(async () => {
  initMap();
  await fetchLocations();
  await fetchCityOptions();
});

function initMap() {
  if (!map.value) {
    map.value = L.map("map", {
      center: [23.6978, 120.9605],
      zoom: 7,
      zoomControl: false,
      minZoom: 7,
      maxZoom: 16
    });
    
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: '&copy; OpenStreetMap contributors',
    }).addTo(map.value);

    // 添加自定義縮放控制
    L.control.zoom({
      position: 'bottomright'
    }).addTo(map.value);
  }
}

async function fetchLocations() {
  try {
    const response = await axios.get(`${BASE_URL}/travel/`);
    allLocations.value = response.data;
  } catch (error) {
    console.error("無法獲取景點數據：", error);
  }
}

async function fetchCityOptions() {
  try {
    const response = await axios.get(`${BASE_URL}/travel/`);
    cityOptions.value = response.data;
  } catch (error) {
    console.error("無法獲取縣市資料：", error);
  }
}

function addMarkers(locations) {
  clearMarkers();
  locations.forEach((loc) => {
    const marker = L.marker([loc.py, loc.px], {
      icon: DefaultIcon
    })
      .addTo(map.value)
      .on('click', () => {
        markers.value.forEach(m => m.setIcon(DefaultIcon));
        marker.setIcon(ActiveIcon);
        selectedSpot.value = loc;
      });
    markers.value.push(marker);
  });
}

function clearMarkers() {
  markers.value.forEach((marker) => {
    marker.setIcon(DefaultIcon);
    map.value.removeLayer(marker);
  });
  markers.value = [];
  selectedSpot.value = null;
}

function applyFilter() {
  let filtered = allLocations.value;

  // 根據選擇的縣市進行篩選
  if (selectedCity.value.length > 0) {
    filtered = filtered.filter((loc) => selectedCity.value.includes(loc.region));
  }

  // 根據搜尋關鍵字進行篩選
  if (searchKeyword.value) {
    filtered = filtered.filter((loc) =>
      loc.travel_name.toLowerCase().includes(searchKeyword.value.toLowerCase())
    );
  }

  filteredLocations.value = filtered;
  addMarkers(filteredLocations.value); // 更新地圖上的標記
}

const handleCityClick = (cityPlace) => {
  if (selectedCity.value.includes(cityPlace)) {
    // 如果已經選中，則移除
    selectedCity.value = selectedCity.value.filter(city => city !== cityPlace);
  } else {
    // 如果未選中且選中數量小於3，則添加
    if (selectedCity.value.length < 3) {
      selectedCity.value.push(cityPlace);
    }
  }
};

function clearSelection() {
  markers.value.forEach(marker => marker.setIcon(DefaultIcon));
  selectedSpot.value = null;
}

const openPreview = (spot) => {
  selectedSpotForPreview.value = spot;
  selectedTravelId.value = spot.travel_id;
  showPreview.value = true;
};

const closePreview = () => {
  showPreview.value = false;
  selectedSpotForPreview.value = null;
  selectedTravelId.value = null;
};

// 檢查景點是否已加入我的景點
const isSpotAdded = (spotId) => {
  const key = `mySpots_${userStore.userInfo?.id}`;
  const mySpots = JSON.parse(localStorage.getItem(key) || '[]');
  return mySpots.some(spot => spot.travel_id === spotId);
};

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
  const isAdded = isSpotAdded(spot.travel_id);
  
  if (!isAdded) {
    // 加入景點
    mySpots.push(spot);
    localStorage.setItem(key, JSON.stringify(mySpots));
    message.success('已加入景點');
  } else {
    // 移除景點
    const updatedSpots = mySpots.filter(s => s.travel_id !== spot.travel_id);
    localStorage.setItem(key, JSON.stringify(updatedSpots));
    message.success('已移除景點');
  }
  
  // 強制更新當前景點的狀態
  if (selectedSpot.value && selectedSpot.value.travel_id === spot.travel_id) {
    selectedSpot.value = { ...spot };
  }
  
  // 強制更新過濾後的景點列表
  if (filteredLocations.value.length > 0) {
    const index = filteredLocations.value.findIndex(s => s.travel_id === spot.travel_id);
    if (index !== -1) {
      filteredLocations.value[index] = { ...spot };
      filteredLocations.value = [...filteredLocations.value];
    }
  }
};

// 處理 SpotPreviewModal 更新事件
const handleSpotsUpdate = () => {
  // 強制更新組件
  filteredLocations.value = [...filteredLocations.value];
};

</script>


<template>
  <Banner bg-url="/images/banner.jpg">
    <template #title>
      旅遊地圖
    </template>
    <template #sec-title>
      尋找台灣特色文化風景
    </template>
  </Banner>
  <Nav class="mb-6" />
  <div class="title-controls">
        <h2 class="main-title">景點地圖</h2>

      </div>
  <div class="map-container">
    <div class="filter-section">
      <div class="search-group">
        <input
          v-model="searchKeyword"
          type="text"
          placeholder="輸入景點名稱搜尋..."
          class="search-input"
        />
        <button @click="applyFilter" class="filter-button">
          <i class="fas fa-search"></i> 搜尋
        </button>
      </div>
      <div class="selected-info">
        城市: {{ selectedCity.length }}/3
      </div>
      <div class="city-buttons">
        <button 
          v-for="city in place_data" 
          :key="city.tag"
          :class="['city-button', { active: selectedCity.includes(city.place) }]"
          @click="handleCityClick(city.place)"
          :disabled="!selectedCity.includes(city.place) && selectedCity.length >= 3"
        >
          {{ city.place }}
        </button>
      </div>
    </div>
    <div class="map-content">
      <div id="map" class="map-view"></div>
      <div class="spot-info" v-if="selectedSpot">
        <div class="spot-header">
          <button class="close-button" @click="clearSelection">×</button>
        </div>
        <div class="spot-image">
          <img :src="selectedSpot.image1 || imageUrl" :alt="selectedSpot.travel_name">
        </div>
        <div class="spot-details">
          <h3>{{ selectedSpot.travel_name }}</h3>
          <p class="address">{{ selectedSpot.travel_address || `${selectedSpot.region}${selectedSpot.town || ''}` }}</p>
          <div class="spot-actions">
            <button class="preview-button" @click="openPreview(selectedSpot)">
              <i class="fas fa-eye"></i> 預覽
            </button>
            <button 
              :class="['add-button', { 'added': userStore.loginStatus && isSpotAdded(selectedSpot.travel_id) }]"
              @click="addToMySpots(selectedSpot)"
            >
              <i :class="['fas', !userStore.loginStatus ? 'fa-plus' : (isSpotAdded(selectedSpot.travel_id) ? 'fa-trash' : 'fa-plus')]"></i>
              {{ !userStore.loginStatus ? '加入景點' : (isSpotAdded(selectedSpot.travel_id) ? '移除景點' : '加入景點') }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
  <SpotPreviewModal 
    :is-open="showPreview"
    :spot="selectedSpotForPreview"
    :travel_id="selectedTravelId"
    @close="closePreview"
    @update-spots="handleSpotsUpdate"
  />
</template>



<style lang="scss" scoped>
.title-controls {
  width: 90%;
  max-width: 1600px;
  margin: 0 auto;
  padding: 0 20px;

  .main-title {
    font-size: 24px;
    font-weight: 500;
    color: #333;
    margin: 24px 0 16px;
  }
}

.map-container {
  padding: 0 20px 20px;
  width: 90%;
  max-width: 1600px;
  margin: 0 auto;
}

.filter-section {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  margin-bottom: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.search-group {
  display: flex;
  gap: 12px;
  width: 100%;
}

.search-input {
  flex: 1;
  padding: 8px 16px;
  border: 2px solid #eee;
  border-radius: 6px;
  font-size: 14px;
  transition: all 0.3s ease;
  
  &:focus {
    outline: none;
    border-color: #007bff;
    box-shadow: 0 0 0 3px rgba(0,123,255,0.15);
  }
}

.selected-info {
  color: #666;
  font-size: 13px;
  padding: 0 4px;
}

.city-buttons {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(85px, 1fr));
  gap: 8px;
  width: 100%;
}

.city-button {
  padding: 6px 12px;
  border: 1px solid #eee;
  border-radius: 6px;
  background-color: white;
  color: #555;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  
  &:hover:not(:disabled) {
    background-color: #f8f9fa;
    border-color: #007bff;
    transform: translateY(-1px);
  }
  
  &.active {
    background-color: #007bff;
    color: white;
    border-color: #007bff;
    font-weight: 500;
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    background-color: #f8f9fa;
  }
}

.filter-button {
  padding: 8px 20px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  font-weight: 500;
  
  &:hover {
    background-color: #0056b3;
    transform: translateY(-1px);
  }
  
  i {
    font-size: 14px;
  }
}

.map-content {
  display: flex;
  gap: 20px;
  height: calc(100vh - 180px);
}

.map-view {
  flex: 1;
  height: 100%;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  overflow: hidden;
  position: relative;
  z-index: 1;
}

.spot-info {
  width: 300px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  overflow: hidden;
  position: relative;
  
  .spot-header {
    position: absolute;
    top: 0;
    right: 0;
    padding: 8px;
    z-index: 2;
    
    .close-button {
      width: 28px;
      height: 28px;
      border-radius: 50%;
      background: rgba(0, 0, 0, 0.5);
      color: white;
      border: none;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 20px;
      transition: all 0.3s ease;
      
      &:hover {
        background: rgba(0, 0, 0, 0.7);
      }
    }
  }
  
  .spot-image {
    width: 100%;
    height: 200px;
    overflow: hidden;
    
    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
  }
  
  .spot-details {
    padding: 16px;
    
    h3 {
      font-size: 18px;
      font-weight: 500;
      color: #333;
      margin-bottom: 8px;
    }
    
    .address {
      color: #666;
      font-size: 14px;
    }
  }
}

.spot-actions {
  display: flex;
  gap: 8px;
  margin-top: 12px;
}

.preview-button {
  position: absolute;
  top: 12px;
  left: 12px;
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
  background: rgba(15, 75, 180, 0.9);
  color: white;
  z-index: 2;
  
  i {
    font-size: 13px;
  }
  
  span {
    font-weight: 500;
  }
  
  &:hover {
    background: rgba(13, 61, 145, 0.95);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  }
}

.add-button {
  position: absolute;
  top: 12px;
  left: 100px;
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
  background: rgba(40, 167, 69, 0.9);
  color: white;
  z-index: 2;
  
  &:hover:not(:disabled) {
    background: rgba(34, 139, 58, 0.95);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  }
  
  &.added {
    background: rgba(220, 53, 69, 0.9);
    
    &:hover {
      background: rgba(189, 45, 59, 0.95);
    }
  }
  
  &:disabled {
    cursor: not-allowed;
    opacity: 0.7;
  }
  
  i {
    font-size: 13px;
  }
  
  span {
    font-weight: 500;
  }
}

@media (max-width: 768px) {
  .title-controls {
    width: 95%;
    padding: 0 10px;
    
    .main-title {
      font-size: 20px;
      margin: 16px 0 12px;
    }
  }

  .map-container {
    width: 95%;
    padding: 0 10px 10px;
  }

  .filter-section {
    padding: 16px;
    gap: 12px;
  }

  .search-group {
    flex-direction: column;
  }

  .city-buttons {
    grid-template-columns: repeat(auto-fill, minmax(70px, 1fr));
    gap: 6px;
  }

  .city-button {
    padding: 4px 8px;
    font-size: 13px;
    height: 28px;
  }

  .filter-button {
    width: 100%;
    justify-content: center;
    padding: 8px 16px;
  }

  .map-content {
    flex-direction: column;
  }
  
  .spot-info {
    width: 100%;
    height: auto;
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
  
  .add-button {
    left: 90px;
  }
}

:deep(.red-marker) {
  filter: hue-rotate(140deg) saturate(120%);
}
</style>

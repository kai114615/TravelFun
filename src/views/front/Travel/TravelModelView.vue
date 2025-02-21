<script setup >
import { ref } from 'vue';
import axios from 'axios'; 

import { useRouter } from "vue-router";
import { NBreadcrumb, NBreadcrumbItem } from 'naive-ui';

import Nav from '@/components/travelComponents/src/Nav.vue';

import Banner from '@/components/Banner.vue';
import Container from '@/layout/Container.vue';
import SpotPreviewModal from '@/components/travelComponents/src/SpotPreviewModal.vue';

const query = ref(''); // 用於綁定查詢輸入
const results = ref([]); // 用於存儲 API 返回的結果
const spots = ref([]);
const travel_model= ref([]);
const imageUrl = '/旅遊圖片.png';

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

const updateQuery = (event) => {
  query.value = event.target.value;
};


const fetchApi = async () => {
  try {
    const response = await axios.post('http://127.0.0.1:8000/travel/api/query/', {
      queries: query.value.split('\n'), // 將輸入按行分割為數組
    });
    
    if(query.value){
      results.value = response.data.results;
      console.log(results.value)
      spotfilter();
    }
    else{
      return;
    }
    
  } catch (error) {
    console.error('API 調用失敗：', error);
    alert('API 調用失敗，請檢查後端服務！');
  }
};



const loadCategories = async () => {
  const API_URL = `http://127.0.0.1:8000/travel/api/travel/`;
  const response = await fetch(API_URL);
  const datas = await response.json();
  spots.value = datas;
};
loadCategories();
const spotfilter =()=>{
  const resultIds = [];
  for (let i = 0; i < results.value.length; i++) {
    const similarities = results.value[i].similarities; 
    const documentIds = results.value[i].document_ids; 
    for (let j = 0; j < similarities.length; j++) {
      if (parseFloat(similarities[j]) > 0.3) {
        resultIds.push(documentIds[j]); // 添加符合条件的 document_id
      }
    }
  }
  travel_model.value = spots.value.filter((spot) =>
    resultIds.includes(spot.travel_id)
  );
  console.log(travel_model.value)
}

// 檢查景點是否已加入我的景點
const isSpotAdded = (spotId) => {
  const mySpots = JSON.parse(localStorage.getItem('mySpots') || '[]');
  return mySpots.some(spot => spot.travel_id === spotId);
};

// 加入/移除景點
const addToMySpots = (spot) => {
  const mySpots = JSON.parse(localStorage.getItem('mySpots') || '[]');
  const isAdded = isSpotAdded(spot.travel_id);
  
  if (!isAdded) {
    // 加入景點
    mySpots.push(spot);
    localStorage.setItem('mySpots', JSON.stringify(mySpots));
  } else {
    // 移除景點
    const updatedSpots = mySpots.filter(s => s.travel_id !== spot.travel_id);
    localStorage.setItem('mySpots', JSON.stringify(updatedSpots));
  }
  
  // 強制更新當前景點的狀態
  const index = travel_model.value.findIndex(s => s.travel_id === spot.travel_id);
  if (index !== -1) {
    travel_model.value[index] = { ...spot };
  }
};

</script>


<template>


  <Banner bg-url="/images/banner.jpg">
    <template #title>
      <span class="text-cc-primary">AI</span> 景點推薦
    </template>
    <template #sec-title>
      讓人工智慧為您量身打造最適合的旅遊行程
    </template>
  </Banner>

  <Nav class="mb-6" />
  
  <div class="container">
    <div class="search-section">
      <div class="search-input-wrapper">
        <textarea 
          :value="query" 
          @input="updateQuery" 
          placeholder="請描述您想要的旅遊體驗，例如：&#10;我想去有山有海的地方&#10;適合全家大小一起遊玩的景點&#10;有特色小吃的觀光景點"
          class="search-textarea"
        ></textarea>
        <button @click="fetchApi" class="search-button">
          <i class="fas fa-search mr-2"></i>
          開始搜尋
        </button>
      </div>
    </div>

    <div v-if="query" class="results-section">
      <div v-if="travel_model.length > 0" class="spots-grid">
        <div v-for="(travel, index) in travel_model" :key="index" class="spot-card">
          <div class="card-inner">
            <button class="preview-button" @click="openPreview(travel)">
              <i class="fas fa-eye"></i>
              <span>預覽</span>
            </button>
            <button 
              :class="['add-button', { 'added': isSpotAdded(travel.travel_id) }]"
              @click="addToMySpots(travel)"
            >
              <i :class="['fas', isSpotAdded(travel.travel_id) ? 'fa-trash' : 'fa-plus']"></i>
              <span>{{ isSpotAdded(travel.travel_id) ? '移除景點' : '加入景點' }}</span>
            </button>
            <div class="card-image">
              <img v-if="travel.image1" :src="travel.image1" :alt="travel.travel_name">
              <img v-else :src="imageUrl" :alt="travel.travel_name">
            </div>
            <div class="card-content">
              <h3 class="spot-title">{{ travel.travel_name }}</h3>
              <p class="spot-description">{{ travel.travel_txt.length <= 100 ? travel.travel_txt : travel.travel_txt.substring(0, 100) + '...' }}</p>
              <div class="spot-tags">
                <span class="tag">{{ travel.region }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="no-results">
        <i class="fas fa-search"></i>
        <p>請輸入景點有關的資料</p>
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
.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
}

.search-section {
  margin-bottom: 2rem;
  
  .search-input-wrapper {
    position: relative;
    max-width: 800px;
    margin: 0 auto;
  }
  
  .search-textarea {
    width: 100%;
    height: 150px;
    padding: 1rem;
    padding-right: 140px;
    border: 1px solid #ddd;
    border-radius: 12px;
    resize: vertical;
    font-size: 1rem;
    transition: border-color 0.3s ease;
    
    &:focus {
      outline: none;
      border-color: #0F4BB4;
    }
  }

  .search-button {
    position: absolute;
    bottom: 1rem;
    right: 1rem;
    display: flex;
    align-items: center;
    padding: 0.75rem 1.5rem;
    background: #0F4BB4;
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 0.9rem;
    cursor: pointer;
    transition: all 0.3s ease;
    
    &:hover {
      background: #0d3d91;
      transform: translateY(-1px);
    }
  }
}

.results-section {
  .spots-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1.5rem;
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
      height: 160px;
      overflow: hidden;
      position: relative;

      img {
        width: 100%;
        height: 100%;
        object-fit: cover;
      }
    }

    .card-content {
      padding: 1rem;

      .spot-title {
        font-size: 1.1rem;
        line-height: 1.4;
        margin-bottom: 0.5rem;
        font-weight: 600;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }

      .spot-description {
        font-size: 0.875rem;
        line-height: 1.5;
        margin-bottom: 0.75rem;
        display: -webkit-box;
        -webkit-line-clamp: 3;
        line-clamp: 3;
        -webkit-box-orient: vertical;
        overflow: hidden;
      }
    }
  }
}

.no-results {
  text-align: center;
  padding: 4rem 0;
  color: #666;

  i {
    font-size: 3rem;
    margin-bottom: 1rem;
    color: #ddd;
  }

  p {
    font-size: 1.1rem;
  }
}

@media (max-width: 1400px) {
  .spots-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 1024px) {
  .spots-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .spots-grid {
    grid-template-columns: 1fr;
  }
  
  .search-button {
    position: static;
    width: 100%;
    margin-top: 1rem;
    justify-content: center;
  }
  
  .search-textarea {
    padding-right: 1rem;
  }
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
  right: 12px;
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

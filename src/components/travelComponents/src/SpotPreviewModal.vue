<script setup>
import { ref, onMounted, watch } from 'vue';

const props = defineProps({
  isOpen: Boolean,
  spot: Object,
  travel_id: Number,
});

const emit = defineEmits(['close']);
const classNames = ref({});
const spots = ref([]);
const filteredSpots = ref([]);

const closeModal = () => {
  emit('close');
};

// 加載分類資料
const loadCategories = async () => {
  const API_URL = `http://127.0.0.1:8000/travel/api/travel/`;
  try {
    const response = await fetch(API_URL);
    const datas = await response.json();
    spots.value = datas;
    
    // 根據 travel_id 過濾相關景點
    if (props.travel_id) {
      const currentSpot = spots.value.find(spot => spot.travel_id === props.travel_id);
      if (currentSpot) {
        // 過濾同一區域的景點
        filteredSpots.value = spots.value.filter(spot => 
          spot.travel_id !== props.travel_id && 
          spot.region === currentSpot.region &&
          spot.town === currentSpot.town
        ).slice(0, 3); // 只顯示最多3個相關景點
      }
    }
  } catch (error) {
    console.error('載入景點資料失敗:', error);
    spots.value = [];
    filteredSpots.value = [];
  }
};

// 監聽 travel_id 的變化
watch(() => props.travel_id, () => {
  loadCategories();
});

const loadClassNames = async () => {
  try {
    const response = await fetch('http://127.0.0.1:8000/travel/api/travelclass/');
    const data = await response.json();
    // 建立 ID 到 class_name 的映射
    const mapping = {};
    data.forEach(item => {
      mapping[item.class_id] = item.class_name;
    });
    classNames.value = mapping;
  } catch (error) {
    console.error('載入分類資料失敗:', error);
  }
};

onMounted(() => {
  loadClassNames();
});

// 根據 class_id 獲取 class_name
const getClassName = (classId) => {
  return classNames.value[classId] || classId;
};
</script>

<template>
  <div v-if="isOpen" class="modal-overlay" @click.self="closeModal">
    <div class="modal-content">
      <button class="close-button" @click="closeModal">×</button>
      
      <div class="spot-preview" v-if="spot">
        <div class="spot-image">
          <img :src="spot.image1 || '/旅遊圖片.png'" :alt="spot.travel_name">
        </div>
        
        <div class="spot-details">
          <h2 class="spot-title">{{ spot.travel_name }}</h2>
          
          <div class="spot-description">
            <h3 class="section-title">景點介紹:</h3>
            <p>{{ spot.travel_txt }}</p>
          </div>
          
          <div class="spot-location">
            <div class="location-header">
              <h3 class="location-title" style="color: #09c45a;">地址資訊:</h3>
            </div>
            <div class="location-content">
              {{ spot.travel_address || `${spot.region}${spot.town || ''}` }}
            </div>
          </div>
          
          <div class="spot-location">
            <div class="location-header">
              <h3 class="location-title" style="color: #09c45a;">電話:</h3>
            </div>
            <div class="location-content">
              <span v-if="spot.tel" class="tag">{{ spot.tel }}</span>
              <span v-if="!spot.tel" class="tag">尚未有資料</span>
            </div>
          </div>

          <div class="spot-location">
            <div class="location-header">
              <h3 class="location-title" style="color: #09c45a;">票價:</h3>
            </div>
            <div class="location-content">
              <span v-if="spot.ticketinfo" class="tag">{{ ticketinfo }}</span>
              <span v-if="!spot.tticketinfoel" class="tag">尚未有資料</span>
            </div>
          </div>

          <div class="spot-location">
            <div class="location-header">
              <h3 class="location-title" style="color: #09c45a;">營業時間:</h3>
            </div>
            <div class="location-content">
              <span v-if="spot.opentime" class="tag">{{ spot.opentime }}</span>
              <span v-if="!spot.opentime" class="tag">尚未提供</span>
            </div>
          </div>
          <div class="spot-tags" v-if="spot.class1 || spot.class2 || spot.class3">
            <h3 class="section-title">景點類型:</h3>
            <div class="tags-container">
              <span v-if="spot.class1" class="tag">{{ getClassName(spot.class1) }}</span>
              <span v-if="spot.class2" class="tag">{{ getClassName(spot.class2) }}</span>
              <span v-if="spot.class3" class="tag">{{ getClassName(spot.class3) }}</span>
            </div>
          </div>
          
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 100%;
  max-width: 900px;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
}

.close-button {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: none;
  background: rgba(0, 0, 0, 0.5);
  color: white;
  font-size: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2;
  
  &:hover {
    background: rgba(0, 0, 0, 0.7);
  }
}

.spot-preview {
  .spot-image {
    width: 100%;
    max-height: 400px;
    display: flex;
    justify-content: center;
    align-items: center;
    background: #f8f9fa;
    overflow: hidden;
    position: relative;
    
    img {
      max-width: 100%;
      max-height: 400px;
      height: auto;
      width: auto;
      object-fit: contain;
    }
  }
  
  .spot-details {
    padding: 24px;
    
    .spot-title {
      font-size: 24px;
      font-weight: 600;
      color: #2c3e50;
      margin-bottom: 16px;
    }
    
    .spot-location {
      margin-bottom: 24px;
      
      .location-header {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 12px;
        
        i {
          color: #0F4BB4;
          font-size: 18px;
        }
        
        .location-title {
          font-size: 18px;
          font-weight: 500;
          color: #2c3e50;
          margin: 0;
        }
      }
      
      .location-content {
        font-size: 14px;
        padding-left: 0;
        text-align: left;
        word-break: break-all;
        margin-top: 4px;
      }
    }
    
    .spot-description {
      margin-bottom: 24px;
      
      h3 {
        font-size: 18px;
        font-weight: 500;
        color: #09c45a;
        margin-bottom: 12px;
      }
      
      p {
        color: #666;
        line-height: 1.6;
      }
    }
    
    .spot-tags {
      h3 {
        font-size: 18px;
        font-weight: 500;
        color: #09c45a;
        margin-bottom: 12px;
      }
      
      .tags-container {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        
        .tag {
          padding: 6px 12px;
          background: #e9f2ff;
          color: #0F4BB4;
          border-radius: 20px;
          font-size: 14px;
        }
      }
    }
  }
}

@media (max-width: 768px) {
  .modal-content {
    max-height: 95vh;
  }
  
  .spot-preview {
    .spot-image {
      max-height: 300px;
      
      img {
        max-height: 300px;
      }
    }
    
    .spot-details {
      padding: 16px;
      
      .spot-title {
        font-size: 20px;
      }
      
      .spot-location {
        padding: 12px;
        
        .location-header {
          margin-bottom: 8px;
          
          i {
            font-size: 16px;
          }
          
          .location-title {
            font-size: 16px;
          }
        }
        
        .location-content {
          font-size: 14px;
          padding-left: 0;
        }
      }
    }
  }
}

.section-title {
  font-size: 18px;
  font-weight: 500;
  color: #0F4BB4;
  margin-bottom: 12px;
}
</style> 
<script setup>
import { ref, onMounted, computed } from 'vue';
import Nav from '@/components/travelComponents/src/Nav.vue';
import Banner from '@/components/Banner.vue';
import SpotPreviewModal from '@/components/travelComponents/src/SpotPreviewModal.vue';

const mySpots = ref([]);
const showPreview = ref(false);
const selectedSpot = ref(null);
const selectedTravelId = ref(null);
const currentGroup = ref(0); // 當前顯示的組別

// 行事曆相關
const currentYear = ref(new Date().getFullYear());
const selectedMonth = ref(new Date().getMonth());
const years = computed(() => {
  const currentYear = new Date().getFullYear();
  return Array.from({ length: 3 }, (_, i) => currentYear + i);
});

const months = [
  "一月", "二月", "三月", "四月", "五月", "六月",
  "七月", "八月", "九月", "十月", "十一月", "十二月"
];

// 計算每個月的天數
const getDaysInMonth = (year, month) => {
  return new Date(year, month + 1, 0).getDate();
};

// 計算每個月第一天是星期幾
const getFirstDayOfMonth = (year, month) => {
  return new Date(year, month, 1).getDay();
};

// 拖放相關
const draggedSpot = ref(null);

// 更新行程數據結構
const scheduleData = ref({});

// 處理開始拖動
const handleDragStart = (spot) => {
  draggedSpot.value = spot;
};

// 處理拖動結束
const handleDragEnd = () => {
  draggedSpot.value = null;
};

// 處理拖動進入日期格子
const handleDragOver = (event, isCurrentMonth) => {
  event.preventDefault();
  if (isCurrentMonth) {
    event.currentTarget.classList.add('drag-over');
  }
};

// 處理拖動離開日期格子
const handleDragLeave = (event, isCurrentMonth) => {
  if (isCurrentMonth) {
    event.currentTarget.classList.remove('drag-over');
  }
};

// 處理放下景點
const handleDrop = (year, month, day, event, isCurrentMonth) => {
  event.preventDefault();
  event.currentTarget.classList.remove('drag-over');
  
  // 如果不是當月日期，則不允許放置
  if (!isCurrentMonth) {
    alert('只能在當月的日期中安排行程！');
    return;
  }
  
  if (!draggedSpot.value) return;
  
  const dateKey = `${year}-${month + 1}-${day}`;
  if (!scheduleData.value[dateKey]) {
    scheduleData.value[dateKey] = [];
  }
  
  // 檢查是否已經存在
  const exists = scheduleData.value[dateKey].some(
    spot => spot.travel_id === draggedSpot.value.travel_id
  );
  
  if (!exists) {
    scheduleData.value[dateKey].push({
      ...draggedSpot.value,
      time: new Date().toISOString()
    });
    // 保存到 localStorage
    localStorage.setItem('travelSchedule', JSON.stringify(scheduleData.value));
    alert(`已將 ${draggedSpot.value.travel_name} 加入到 ${year}年${month + 1}月${day}日的行程中`);
  } else {
    alert('此景點已在該日期的行程中！');
  }
  
  draggedSpot.value = null;
};

// 從行程中移除景點
const removeFromSchedule = (dateKey, spotId) => {
  if (scheduleData.value[dateKey]) {
    const spotToRemove = scheduleData.value[dateKey].find(spot => spot.travel_id === spotId);
    if (spotToRemove) {
      const confirmDelete = confirm(`確定要從行程中移除 ${spotToRemove.travel_name} 嗎？`);
      if (confirmDelete) {
        scheduleData.value[dateKey] = scheduleData.value[dateKey].filter(
          spot => spot.travel_id !== spotId
        );
        localStorage.setItem('travelSchedule', JSON.stringify(scheduleData.value));
      }
    }
  }
};

// 在 script setup 部分更新特殊節日的資料
const holidays = {
  '1-1': '元旦',
  '1-2': '補假',
  '1-20': '小年夜',
  '1-21': '除夕',
  '1-22': '春節',
  '1-23': '春節',
  '1-24': '春節',
  '1-25': '春節',
  '1-26': '春節',
  '2-28': '和平紀念日',
  '3-8': '婦女節',
  '4-4': '兒童節',
  '4-5': '清明節',
  '5-1': '勞動節',
  '6-3': '端午節',
  '6-23': '國際奧林匹克日',
  '8-8': '父親節',
  '9-28': '教師節',
  '9-29': '中秋節',
  '10-10': '國慶日',
  '10-25': '光復節',
  '10-31': '萬聖節',
  '11-12': '國父誕辰紀念日',
  '12-25': '聖誕節',
  '12-31': '跨年夜'
};

// 修改 calendarDays computed 函數
const calendarDays = computed(() => {
  const days = [];
  const daysInMonth = getDaysInMonth(currentYear.value, selectedMonth.value);
  const firstDay = getFirstDayOfMonth(currentYear.value, selectedMonth.value);

  // 添加上個月的天數
  const prevMonthDays = getDaysInMonth(currentYear.value, selectedMonth.value - 1);
  for (let i = firstDay - 1; i >= 0; i--) {
    const day = prevMonthDays - i;
    const dateKey = `${currentYear.value}-${selectedMonth.value}-${day}`;
    const holidayKey = `${selectedMonth.value}-${day}`;
    days.push({
      day,
      isCurrentMonth: false,
      events: scheduleData.value[dateKey] || [],
      holiday: holidays[holidayKey]
    });
  }

  // 添加當前月的天數
  for (let i = 1; i <= daysInMonth; i++) {
    const dateKey = `${currentYear.value}-${selectedMonth.value + 1}-${i}`;
    const holidayKey = `${selectedMonth.value + 1}-${i}`;
    days.push({
      day: i,
      isCurrentMonth: true,
      events: scheduleData.value[dateKey] || [],
      holiday: holidays[holidayKey]
    });
  }

  // 添加下個月的天數
  const remainingDays = 42 - days.length;
  for (let i = 1; i <= remainingDays; i++) {
    const dateKey = `${currentYear.value}-${selectedMonth.value + 2}-${i}`;
    const holidayKey = `${selectedMonth.value + 2}-${i}`;
    days.push({
      day: i,
      isCurrentMonth: false,
      events: scheduleData.value[dateKey] || [],
      holiday: holidays[holidayKey]
    });
  }

  return days;
});

// 切換月份
const changeMonth = (delta) => {
  let newMonth = selectedMonth.value + delta;
  if (newMonth > 11) {
    newMonth = 0;
    currentYear.value++;
  } else if (newMonth < 0) {
    newMonth = 11;
    currentYear.value--;
  }
  selectedMonth.value = newMonth;
};

// 切換年份
const changeYear = (event) => {
  currentYear.value = parseInt(event.target.value);
};

onMounted(() => {
  loadMySpots();
  // 從 localStorage 加載行程數據
  const savedSchedule = localStorage.getItem('travelSchedule');
  if (savedSchedule) {
    scheduleData.value = JSON.parse(savedSchedule);
  }
});

const loadMySpots = () => {
  const spots = JSON.parse(localStorage.getItem('mySpots') || '[]');
  mySpots.value = spots;
};

const removeSpot = (spotId) => {
  const spotToRemove = mySpots.value.find(spot => spot.travel_id === spotId);
  if (spotToRemove && window.confirm(`確定要移除 ${spotToRemove.travel_name} 嗎？`)) {
    const spots = mySpots.value.filter(spot => spot.travel_id !== spotId);
    mySpots.value = spots;
    localStorage.setItem('mySpots', JSON.stringify(spots));
    
    // 更新當前組別
    if (currentGroup.value >= totalGroups.value) {
      currentGroup.value = Math.max(0, totalGroups.value - 1);
    }
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
  const mySpots = JSON.parse(localStorage.getItem('mySpots') || '[]');
  return mySpots.some(spot => spot.travel_id === spotId);
};

// 加入/移除景點
const addToMySpots = (spot) => {
  const storedSpots = JSON.parse(localStorage.getItem('mySpots') || '[]');
  const isAdded = isSpotAdded(spot.travel_id);
  
  if (!isAdded) {
    // 加入景點
    storedSpots.push(spot);
    localStorage.setItem('mySpots', JSON.stringify(storedSpots));
    mySpots.value = storedSpots;
  } else {
    // 移除景點
    const updatedSpots = storedSpots.filter(s => s.travel_id !== spot.travel_id);
    localStorage.setItem('mySpots', JSON.stringify(updatedSpots));
    mySpots.value = updatedSpots;
    
    // 更新當前組別
    if (currentGroup.value >= Math.ceil(updatedSpots.length / 5)) {
      currentGroup.value = Math.max(0, Math.ceil(updatedSpots.length / 5) - 1);
    }
  }
};

// 計算分組後的景點
const groupedSpots = computed(() => {
  const groups = [];
  for (let i = 0; i < mySpots.value.length; i += 5) {
    groups.push(mySpots.value.slice(i, i + 5));
  }
  return groups;
});

// 計算總組數
const totalGroups = computed(() => {
  return Math.ceil(mySpots.value.length / 5);
});

// 當前顯示的景點
const currentSpots = computed(() => {
  return groupedSpots.value[currentGroup.value] || [];
});

// 切換到下一組
const nextGroup = () => {
  if (currentGroup.value < totalGroups.value - 1) {
    currentGroup.value++;
  }
};

// 切換到上一組
const prevGroup = () => {
  if (currentGroup.value > 0) {
    currentGroup.value--;
  }
};
</script>

<template>
  <Banner bg-url="/images/banner.jpg">
    <template #title>
      我的景點
    </template>
    <template #sec-title>
      規劃您的完美旅程
    </template>
  </Banner>
  
  <Nav class="mb-6" />
  
  <div class="my-spots-container">
    <div class="schedule-layout">
      <!-- 左側收藏景點列表 -->
      <div class="spots-sidebar">
        <div class="sidebar-header">
          <h3>我的收藏景點</h3>
          <p>已收藏 {{ mySpots.length }} 個景點</p>
          <div v-if="mySpots.length === 0" class="no-spots-hint">
            <i class="fas fa-map-marked-alt"></i>
            <p>您還沒有收藏任何景點</p>
            <router-link to="/spots" class="browse-button">
              瀏覽景點
            </router-link>
          </div>
          <div v-if="mySpots.length > 0" class="group-navigation">
            <button 
              class="nav-button" 
              @click="prevGroup" 
              :disabled="currentGroup === 0"
            >
              <i class="fas fa-chevron-left"></i>
            </button>
            <span class="group-info">第 {{ currentGroup + 1 }}/{{ totalGroups }} 組</span>
            <button 
              class="nav-button" 
              @click="nextGroup" 
              :disabled="currentGroup === totalGroups - 1"
            >
              <i class="fas fa-chevron-right"></i>
            </button>
          </div>
        </div>
        <div class="spots-list" v-if="mySpots.length > 0">
          <div v-for="spot in currentSpots" 
               :key="spot.travel_id" 
               class="spot-item"
               draggable="true"
               @dragstart="handleDragStart(spot)"
               @dragend="handleDragEnd">
            <div class="spot-info">
              <div class="spot-name">{{ spot.travel_name }}</div>
              <div class="spot-address">{{ spot.travel_address || `${spot.region}${spot.town}` }}</div>
              <div class="card-actions">
                <button class="preview-button" @click="openPreview(spot)">
                  <i class="fas fa-eye"></i>
                  <span>預覽</span>
                </button>
                <button 
                  :class="['add-button', { 'added': isSpotAdded(spot.travel_id) }]"
                  @click="addToMySpots(spot)"
                >
                  <i :class="['fas', isSpotAdded(spot.travel_id) ? 'fa-trash' : 'fa-plus']"></i>
                  <span>{{ isSpotAdded(spot.travel_id) ? '移除景點' : '加入景點' }}</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右側行事曆部分 -->
      <div class="calendar-section">
        <div class="calendar-header">
          <div class="year-selector">
            <select :value="currentYear" @change="changeYear" class="year-select">
              <option v-for="year in years" :key="year" :value="year">
                {{ year }} 年
              </option>
            </select>
          </div>
          <div class="month-navigation">
            <button @click="changeMonth(-1)" class="month-nav-btn">
              <i class="fas fa-chevron-left"></i>
            </button>
            <span class="current-month">{{ months[selectedMonth] }}</span>
            <button @click="changeMonth(1)" class="month-nav-btn">
              <i class="fas fa-chevron-right"></i>
            </button>
          </div>
        </div>
        
        <div class="calendar-grid">
          <div class="weekday-header">
            <div class="weekday">日</div>
            <div class="weekday">一</div>
            <div class="weekday">二</div>
            <div class="weekday">三</div>
            <div class="weekday">四</div>
            <div class="weekday">五</div>
            <div class="weekday">六</div>
          </div>
          <div class="days-grid">
            <div 
              v-for="(day, index) in calendarDays" 
              :key="index"
              :class="[
                'day-cell',
                { 'current-month': day.isCurrentMonth },
                { 'other-month': !day.isCurrentMonth },
                { 'has-events': day.events.length > 0 },
                { 'has-holiday': day.holiday }
              ]"
              @dragover="(e) => handleDragOver(e, day.isCurrentMonth)"
              @dragleave="(e) => handleDragLeave(e, day.isCurrentMonth)"
              @drop="(e) => handleDrop(currentYear, selectedMonth, day.day, e, day.isCurrentMonth)"
            >
              <span class="day-number" :class="{ 'other-month-text': !day.isCurrentMonth }">{{ day.day }}</span>
              <span v-if="day.holiday" class="holiday-tag" :class="{ 'other-month-text': !day.isCurrentMonth }">{{ day.holiday }}</span>
              <div class="day-events">
                <div v-for="event in day.events" 
                     :key="event.travel_id" 
                     class="event-item"
                     @click="day.isCurrentMonth && openPreview(event)">
                  <span class="event-title">{{ event.travel_name }}</span>
                  <button v-if="day.isCurrentMonth"
                          class="remove-event" 
                          @click.stop="removeFromSchedule(`${currentYear}-${selectedMonth + 1}-${day.day}`, event.travel_id)">
                    ×
                  </button>
                </div>
              </div>
            </div>
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
.my-spots-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.schedule-layout {
  display: flex;
  gap: 20px;
  margin-bottom: 2rem;
}

.spots-sidebar {
  width: 300px;
  flex-shrink: 0;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  
  .sidebar-header {
    padding: 16px;
    border-bottom: 1px solid #eee;
    
    h3 {
      font-size: 1.2rem;
      color: #2c3e50;
      margin-bottom: 8px;
    }
    
    p {
      color: #666;
      font-size: 0.9rem;
    }
  }
}

.spots-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.spot-item {
  display: flex;
  flex-direction: column;
  padding: 12px;
  border-radius: 8px;
  background: #f8f9fa;
  margin-bottom: 8px;
  cursor: grab;
  transition: all 0.2s ease;
  
  &:active {
    cursor: grabbing;
  }
  
  &:hover {
    background: #e9ecef;
    transform: translateY(-1px);
  }
  
  .spot-info {
    flex: 1;
    min-width: 0;
    
    .spot-name {
      font-weight: 500;
      color: #2c3e50;
      margin-bottom: 4px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    
    .spot-address {
      font-size: 0.8rem;
      color: #666;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      margin-bottom: 8px;
    }
  }
  
  .card-actions {
    display: flex;
    gap: 8px;
    margin-top: 8px;
  }
}

.action-button {
  min-width: 80px;
  height: 32px;
  border: none;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  gap: 4px;
  padding: 0 12px;
  font-size: 0.9rem;
  
  i {
    font-size: 0.9rem;
  }
  
  span {
    font-weight: 500;
  }
  
  &.preview {
    background: rgba(15, 75, 180, 0.1);
    color: #0F4BB4;
    
    &:hover {
      background: rgba(15, 75, 180, 0.2);
    }
  }
  
  &.remove {
    background: rgba(220, 53, 69, 0.1);
    color: #dc3545;
    
    &:hover {
      background: rgba(220, 53, 69, 0.2);
    }
  }
}

.calendar-section {
  flex: 1;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.no-spots-hint {
  text-align: center;
  padding: 24px 16px;
  
  i {
    font-size: 2rem;
    color: #ddd;
    margin-bottom: 12px;
  }
  
  p {
    color: #666;
    margin-bottom: 16px;
  }
  
  .browse-button {
    display: inline-block;
    padding: 8px 16px;
    background: #0F4BB4;
    color: white;
    text-decoration: none;
    border-radius: 6px;
    font-size: 0.9rem;
    transition: all 0.3s ease;
    
    &:hover {
      background: #0d3d91;
      transform: translateY(-1px);
    }
  }
}

.calendar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.year-selector {
  .year-select {
    padding: 8px 16px;
    border: 1px solid #ddd;
    border-radius: 6px;
    font-size: 16px;
    color: #333;
    background: white;
    cursor: pointer;
    
    &:focus {
      outline: none;
      border-color: #0F4BB4;
    }
  }
}

.month-navigation {
  display: flex;
  align-items: center;
  gap: 16px;
  
  .month-nav-btn {
    width: 32px;
    height: 32px;
    border: none;
    border-radius: 50%;
    background: #f8f9fa;
    color: #333;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
    
    &:hover {
      background: #e9ecef;
    }
  }
  
  .current-month {
    font-size: 18px;
    font-weight: 500;
    color: #333;
    min-width: 80px;
    text-align: center;
  }
}

.calendar-grid {
  border: 1px solid #eee;
  border-radius: 8px;
  overflow: hidden;
}

.weekday-header {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  background: #f8f9fa;
  border-bottom: 1px solid #eee;
  
  .weekday {
    padding: 12px;
    text-align: center;
    font-weight: 500;
    color: #666;
  }
}

.days-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 1px;
  background: #eee;
}

.day-cell {
  position: relative;
  min-height: 120px;
  padding: 8px;
  background: white;
  transition: all 0.2s ease;
  
  &.other-month {
    background: #f5f5f5;
    cursor: not-allowed;
    
    .day-events {
      opacity: 0.6;
      pointer-events: none;
    }
    
    .event-item {
      cursor: not-allowed;
    }
  }
  
  &.other-month-text {
    color: #999;
  }
  
  &.drag-over {
    background: #e3f2fd;
    box-shadow: inset 0 0 0 2px #0F4BB4;
  }
  
  &.has-events {
    background: #f8f9fa;
    
    &.other-month {
      background: #f0f0f0;
    }
  }
  
  &:hover:not(.other-month) {
    background: #f0f4f8;
  }
  
  &.has-holiday {
    background: #fff8e1;
    
    &.other-month {
      background: #fff8e1;
      opacity: 0.7;
    }
  }
  
  .day-number {
    font-size: 14px;
    font-weight: 500;
    margin-bottom: 4px;
    color: #333;
    display: flex;
    align-items: center;
    gap: 4px;
    
    &.other-month-text {
      color: #999;
    }
  }
  
  .holiday-tag {
    display: inline-block;
    padding: 2px 6px;
    background: #ffebee;
    color: #f44336;
    border-radius: 4px;
    font-size: 12px;
    margin-left: 4px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: calc(100% - 30px);
    
    &.other-month-text {
      opacity: 0.7;
      background: #ffebee99;
    }
  }
  
  .day-events {
    margin-top: 4px;
    display: flex;
    flex-direction: column;
    gap: 4px;
    max-height: calc(100% - 24px);
    overflow-y: auto;
  }
  
  .event-item {
    background: #e3f2fd;
    padding: 6px 8px;
    border-radius: 4px;
    font-size: 12px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    cursor: pointer;
    transition: all 0.2s ease;
    
    &:hover {
      background: #bbdefb;
      transform: translateY(-1px);
      
      .remove-event {
        opacity: 1;
      }
    }
    
    .event-title {
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      flex: 1;
      color: #0F4BB4;
      font-weight: 500;
    }
    
    .remove-event {
      background: none;
      border: none;
      color: #dc3545;
      cursor: pointer;
      padding: 0 4px;
      font-size: 14px;
      opacity: 0;
      transition: opacity 0.2s ease;
      
      &:hover {
        color: #c82333;
      }
    }
  }
}

@media (max-width: 768px) {
  .schedule-layout {
    flex-direction: column;
  }
  
  .spots-sidebar {
    width: 100%;
  }
  
  .calendar-header {
    flex-direction: column;
    gap: 12px;
  }
  
  .day-cell {
    min-height: 60px;
    padding: 4px;
  }
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
    
    &:hover {
      background: rgba(189, 45, 59, 0.95);
    }
  }
  
  &:disabled {
    cursor: not-allowed;
    opacity: 0.7;
  }
}

.group-navigation {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-top: 12px;
  padding: 8px;
  background: #f8f9fa;
  border-radius: 8px;
  
  .nav-button {
    width: 32px;
    height: 32px;
    border: none;
    border-radius: 6px;
    background: white;
    color: #666;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    
    &:hover:not(:disabled) {
      background: #007bff;
      color: white;
      transform: translateY(-1px);
    }
    
    &:disabled {
      opacity: 0.5;
      cursor: not-allowed;
      background: #eee;
    }
    
    i {
      font-size: 14px;
    }
  }
  
  .group-info {
    font-size: 14px;
    color: #666;
    min-width: 80px;
    text-align: center;
  }
}

@media (max-width: 768px) {
  .group-navigation {
    padding: 6px;
    gap: 8px;
    
    .nav-button {
      width: 28px;
      height: 28px;
      
      i {
        font-size: 12px;
      }
    }
    
    .group-info {
      font-size: 13px;
      min-width: 70px;
    }
  }
}
</style>
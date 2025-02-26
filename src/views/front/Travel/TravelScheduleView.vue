<script setup>
import { ref, onMounted, computed, onUnmounted } from 'vue';
import Nav from '@/components/travelComponents/src/Nav.vue';
import Banner from '@/components/Banner.vue';
import SpotPreviewModal from '@/components/travelComponents/src/SpotPreviewModal.vue';

const mySpots = ref([]);
const showPreview = ref(false);
const selectedSpot = ref(null);
const selectedTravelId = ref(null);
const currentGroup = ref(0); // 當前顯示的組別
const spotsPerGroup = 3;

// 新增最佳路徑相關的響應式變數
const optimizedPath = ref(null);
const totalDistance = ref(null);
const isCalculating = ref(false);
const showPathResult = ref(false);
const selectedSpots = ref([]); // 新增：用於追蹤選中的景點
const startPoint = ref(null); // 新增：起點
const endPoint = ref(null); // 新增：終點

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

// 在 script setup 部分添加新的變數和函數
const autoScrollSpeed = ref(0);
const autoScrollInterval = ref(null);
const scrollThreshold = 150; // 距離邊緣多少像素開始自動滾動

// 事件拖曳相關變數
const draggedEvent = ref(null);
const draggedEventDate = ref(null);
const draggedEventIndex = ref(null);

// 修改 handleDragStart 函數
const handleDragStart = (spot, event) => {
  draggedSpot.value = spot;
  startAutoScroll();
};

// 修改 handleDragEnd 函數
const handleDragEnd = () => {
  draggedSpot.value = null;
  stopAutoScroll();
};

// 添加自動滾動相關函數
const startAutoScroll = () => {
  if (autoScrollInterval.value) return;
  
  autoScrollInterval.value = setInterval(() => {
    if (autoScrollSpeed.value !== 0) {
      window.scrollBy(0, autoScrollSpeed.value);
    }
  }, 16); // 約60fps
};

const stopAutoScroll = () => {
  if (autoScrollInterval.value) {
    clearInterval(autoScrollInterval.value);
    autoScrollInterval.value = null;
  }
  autoScrollSpeed.value = 0;
};

// 添加滾動檢查函數
const checkScrollBoundary = (event) => {
  const { clientY } = event;
  const windowHeight = window.innerHeight;
  
  if (clientY < scrollThreshold) {
    // 靠近頂部，向上滾動
    autoScrollSpeed.value = -10;
  } else if (clientY > windowHeight - scrollThreshold) {
    // 靠近底部，向下滾動
    autoScrollSpeed.value = 10;
  } else {
    // 在中間區域，停止滾動
    autoScrollSpeed.value = 0;
  }
};

// 修改 handleDragOver 函數
const handleDragOver = (event, isCurrentMonth) => {
  event.preventDefault();
  if (isCurrentMonth) {
    event.currentTarget.classList.add('drag-over');
  }
  checkScrollBoundary(event);
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
  }
  
  draggedSpot.value = null;
};

// 從行程中移除景點
const removeFromSchedule = (dateKey, spotId) => {
  if (scheduleData.value[dateKey]) {
    scheduleData.value[dateKey] = scheduleData.value[dateKey].filter(
      spot => spot.travel_id !== spotId
    );
    localStorage.setItem('travelSchedule', JSON.stringify(scheduleData.value));
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

  // 填充當月第一天之前的空白
  for (let i = 0; i < firstDay; i++) {
    days.push({
      day: '',
      isCurrentMonth: false,
      events: [],
      holiday: null
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

  // 填充當月最後一天之後的空白
  const remainingDays = 42 - days.length;
  for (let i = 0; i < remainingDays; i++) {
    days.push({
      day: '',
      isCurrentMonth: false,
      events: [],
      holiday: null
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
    // 從我的景點列表中移除
    const spots = mySpots.value.filter(spot => spot.travel_id !== spotId);
    mySpots.value = spots;
    localStorage.setItem('mySpots', JSON.stringify(spots));
    
    // 從已選擇的景點中移除
    selectedSpots.value = selectedSpots.value.filter(spot => spot.travel_id !== spotId);
    
    // 如果是起點，清除起點
    if (startPoint.value && startPoint.value.travel_id === spotId) {
      startPoint.value = null;
    }
    
    // 如果是終點，清除終點
    if (endPoint.value && endPoint.value.travel_id === spotId) {
      endPoint.value = null;
    }
    
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

// 新增：設置起點
const setStartPoint = (spot) => {
  // 如果這個點已經是終點，不允許設為起點
  if (endPoint.value && endPoint.value.travel_id === spot.travel_id) {
    return;
  }
  
  // 如果點擊的是當前起點，則取消設置
  if (startPoint.value && startPoint.value.travel_id === spot.travel_id) {
    startPoint.value = null;
  } else {
    startPoint.value = spot;
  }
};

// 新增：設置終點
const setEndPoint = (spot) => {
  // 如果這個點已經是起點，不允許設為終點
  if (startPoint.value && startPoint.value.travel_id === spot.travel_id) {
    return;
  }
  
  // 如果點擊的是當前終點，則取消設置
  if (endPoint.value && endPoint.value.travel_id === spot.travel_id) {
    endPoint.value = null;
  } else {
    endPoint.value = spot;
  }
};

// 修改：檢查景點是否被選中
const isSpotSelected = (spotId) => {
  return selectedSpots.value.some(spot => spot.travel_id === spotId) ||
         (startPoint.value && startPoint.value.travel_id === spotId) ||
         (endPoint.value && endPoint.value.travel_id === spotId);
};

// 修改：選擇/取消選擇景點的函數
const toggleSpotSelection = (spot) => {
  const index = selectedSpots.value.findIndex(s => s.travel_id === spot.travel_id);
  if (index === -1) {
    selectedSpots.value.push(spot);
  } else {
    selectedSpots.value.splice(index, 1);
    // 如果移除的景點是起點或終點，清除相應的設置
    if (startPoint.value && startPoint.value.travel_id === spot.travel_id) {
      startPoint.value = null;
    }
    if (endPoint.value && endPoint.value.travel_id === spot.travel_id) {
      endPoint.value = null;
    }
  }
};

// 修改：計算最佳路徑函數
const calculateOptimalPath = async () => {
  if (selectedSpots.value.length < 1 && !startPoint.value && !endPoint.value) {
    alert('請至少選擇一個景點以計算最佳路徑');
    return;
  }

  try {
    isCalculating.value = true;
    showPathResult.value = true;

    // 準備路徑點數據，排除已經是起點或終點的景點
    const intermediateSpots = selectedSpots.value.filter(spot => 
      (!startPoint.value || spot.travel_id !== startPoint.value.travel_id) && 
      (!endPoint.value || spot.travel_id !== endPoint.value.travel_id)
    );

    const pathPoints = [
      ...(startPoint.value ? [[parseFloat(startPoint.value.py), parseFloat(startPoint.value.px)]] : []),
      ...intermediateSpots.map(spot => [parseFloat(spot.py), parseFloat(spot.px)]),
      ...(endPoint.value ? [[parseFloat(endPoint.value.py), parseFloat(endPoint.value.px)]] : [])
    ];

    // 準備API請求數據
    const requestData = {
      path: pathPoints
    };

    // 如果有設置起點和終點，加入請求數據
    if (startPoint.value) {
      requestData.start_point = [parseFloat(startPoint.value.py), parseFloat(startPoint.value.px)];
    }
    if (endPoint.value) {
      requestData.end_point = [parseFloat(endPoint.value.py), parseFloat(endPoint.value.px)];
    }

    // 呼叫 API 計算最佳路徑
    const response = await fetch('http://127.0.0.1:8000/travel/api/find-path/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestData)
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || '計算最佳路徑時發生錯誤');
    }

    const data = await response.json();
    
    if (data.success) {
      // 將最佳路徑的座標對應回景點資訊
      optimizedPath.value = data.path.map(point => {
        const [lat, lon] = point;
        return [startPoint.value, ...intermediateSpots, endPoint.value].find(spot => 
          spot && Math.abs(parseFloat(spot.py) - lat) < 0.0001 && 
          Math.abs(parseFloat(spot.px) - lon) < 0.0001
        );
      });
      
      totalDistance.value = data.total_distance;
    } else {
      throw new Error('無法計算最佳路徑');
    }
  } catch (error) {
    alert(`計算最佳路徑時發生錯誤: ${error.message}`);
    showPathResult.value = false;
  } finally {
    isCalculating.value = false;
  }
};

// 修改：關閉路徑結果時清空選中的景點和起終點
const closePathResult = () => {
  showPathResult.value = false;
  optimizedPath.value = null;
  totalDistance.value = null;
  selectedSpots.value = [];
  startPoint.value = null;
  endPoint.value = null;
};

// 開始拖曳事件
const handleEventDragStart = (event, draggedItem, year, month, day, index) => {
  draggedEvent.value = draggedItem;
  draggedEventDate.value = `${year}-${month + 1}-${day}`;
  draggedEventIndex.value = index;
  event.target.classList.add('dragging');
};

// 拖曳結束
const handleEventDragEnd = (event) => {
  event.target.classList.remove('dragging');
  draggedEvent.value = null;
  draggedEventDate.value = null;
  draggedEventIndex.value = null;
  
  // 移除所有拖曳效果
  document.querySelectorAll('.event-item').forEach(item => {
    item.classList.remove('drag-over');
  });
};

// 拖曳經過其他事件時
const handleEventDragOver = (event, year, month, day) => {
  event.preventDefault();
  const currentDateKey = `${year}-${month + 1}-${day}`;
  
  // 只有在同一天時才允許拖曳
  if (draggedEventDate.value === currentDateKey) {
    // 移除其他項目的拖曳效果
    document.querySelectorAll('.event-item').forEach(item => {
      item.classList.remove('drag-over');
    });
    // 添加當前項目的拖曳效果
    event.target.closest('.event-item')?.classList.add('drag-over');
  }
};

// 放下事件
const handleEventDrop = (event, year, month, day, dropIndex) => {
  event.preventDefault();
  
  if (!draggedEvent.value) return;
  
  const newDateKey = `${year}-${month + 1}-${day}`;
  
  // 只允許在同一天內移動
  if (newDateKey !== draggedEventDate.value) {
    return;
  }
  
  // 同一天的重新排序
  const events = scheduleData.value[newDateKey];
  const [movedEvent] = events.splice(draggedEventIndex.value, 1);
  events.splice(dropIndex, 0, movedEvent);
  
  // 保存更新後的數據
  localStorage.setItem('travelSchedule', JSON.stringify(scheduleData.value));
  
  // 清除拖曳狀態
  draggedEvent.value = null;
  draggedEventDate.value = null;
  draggedEventIndex.value = null;
  
  // 移除所有拖曳效果
  document.querySelectorAll('.event-item').forEach(item => {
    item.classList.remove('drag-over');
  });
};

// 在組件卸載時清理
onUnmounted(() => {
  stopAutoScroll();
});
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
               :class="{ 
                 'selected': isSpotSelected(spot.travel_id),
                 'dragging': draggedSpot && draggedSpot.travel_id === spot.travel_id 
               }"
               draggable="true"
               @dragstart="(e) => handleDragStart(spot, e)"
               @dragend="handleDragEnd"
               @click="toggleSpotSelection(spot)">
            <div class="spot-info">
              <div class="spot-header">
                <div class="spot-checkbox">
                  <i :class="['fas', isSpotSelected(spot.travel_id) ? 'fa-check-circle' : 'fa-circle']"></i>
                </div>
                <div class="spot-name">{{ spot.travel_name }}</div>
              </div>
              <div class="spot-address">{{ spot.travel_address || `${spot.region}${spot.town}` }}</div>
              <div class="card-actions">
                <button class="preview-button" @click.stop="openPreview(spot)">
                  <i class="fas fa-eye"></i>
                  <span>預覽</span>
                </button>
                <button class="remove-button" @click.stop="removeSpot(spot.travel_id)">
                  <i class="fas fa-trash"></i>
                  <span>移除</span>
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
              @dragover="(e) => handleDragOver(e, currentYear, selectedMonth, day.day)"
              @dragleave="(e) => handleDragLeave(e, day.isCurrentMonth)"
              @drop="(e) => handleDrop(currentYear, selectedMonth, day.day, e, day.isCurrentMonth)"
            >
              <span class="day-number" :class="{ 'other-month-text': !day.isCurrentMonth }">{{ day.day }}</span>
              <span v-if="day.holiday" class="holiday-tag" :class="{ 'other-month-text': !day.isCurrentMonth }">{{ day.holiday }}</span>
              <div class="day-events">
                <div v-for="(event, eventIndex) in day.events" 
                     :key="event.travel_id" 
                     class="event-item"
                     :class="{ 'dragging': draggedEvent && draggedEvent.travel_id === event.travel_id }"
                     draggable="true"
                     @dragstart="(e) => handleEventDragStart(e, event, currentYear, selectedMonth, day.day, eventIndex)"
                     @dragover.prevent="(e) => handleEventDragOver(e, currentYear, selectedMonth, day.day)"
                     @drop="(e) => handleEventDrop(e, currentYear, selectedMonth, day.day, eventIndex)"
                     @dragend="handleEventDragEnd"
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

    <!-- 最佳路徑區域 -->
    <div class="spots-panel">
      <div class="panel-header">
        <h2>已選擇的景點</h2>
        <div class="header-actions">
          <button 
            v-if="selectedSpots.length >= 2" 
            class="optimal-path-button"
            :class="{ 'calculating': isCalculating }"
            @click="calculateOptimalPath"
            :disabled="isCalculating"
          >
            <i class="fas fa-route"></i>
            {{ isCalculating ? '計算中...' : '計算最佳路徑' }}
          </button>
        </div>
      </div>

      <!-- 顯示已選擇的景點列表 -->
      <div class="selected-spots-list" v-if="selectedSpots.length > 0">
        <div v-for="(spot, index) in selectedSpots" 
             :key="spot.travel_id" 
             class="selected-spot-item"
             :class="{
               'start-point': startPoint && startPoint.travel_id === spot.travel_id,
               'end-point': endPoint && endPoint.travel_id === spot.travel_id
             }">
          <span class="spot-number">{{ index + 1 }}</span>
          <div class="spot-info">
            <div class="spot-name">{{ spot.travel_name }}</div>
            <div class="spot-address">{{ spot.travel_address || `${spot.region}${spot.town}` }}</div>
          </div>
          <div class="spot-actions">
            <button class="point-button start-point" 
                    @click.stop="setStartPoint(spot)"
                    :class="{ 'active': startPoint && startPoint.travel_id === spot.travel_id }">
              <i class="fas fa-flag"></i>
              <span>起點</span>
            </button>
            <button class="point-button end-point" 
                    @click.stop="setEndPoint(spot)"
                    :class="{ 'active': endPoint && endPoint.travel_id === spot.travel_id }">
              <i class="fas fa-flag-checkered"></i>
              <span>終點</span>
            </button>
            <button class="remove-spot" @click="toggleSpotSelection(spot)">
              <i class="fas fa-times"></i>
            </button>
          </div>
        </div>
      </div>
      <div v-else class="no-spots-selected">
        <i class="fas fa-map-marker-alt"></i>
        <p>尚未選擇任何景點</p>
        <p class="hint">點擊左側景點以選擇</p>
      </div>

      <!-- 顯示最佳路徑結果 -->
      <div v-if="showPathResult" class="optimal-path-result">
        <div class="result-header">
          <h3>最佳路徑結果</h3>
          <button class="close-result" @click="closePathResult">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="path-info">
          <p class="total-distance">總距離: {{ totalDistance }} 公里</p>
          <div class="path-sequence">
            <div v-for="(spot, index) in optimizedPath" :key="index" class="path-point">
              <span class="point-number">{{ index + 1 }}</span>
              <div class="point-details">
                <span class="point-name">{{ spot.travel_name }}</span>
                <span class="point-address">{{ spot.travel_address || `${spot.region}${spot.town}` }}</span>
              </div>
              <i v-if="index < optimizedPath.length - 1" class="fas fa-arrow-right"></i>
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
  border: 2px solid transparent;
  user-select: none;
  touch-action: none; // 防止觸控設備的默認行為
  
  &.selected {
    border-color: #0F4BB4;
    background: #e3f2fd;
  }
  
  &.dragging {
    opacity: 0.7;
    transform: scale(1.02);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  }
  
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
    
    .spot-header {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 4px;
      
      .spot-checkbox {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 24px;
        height: 24px;
        
        i {
          font-size: 18px;
          color: #666;
          transition: color 0.2s ease;
        }
      }
      
      .spot-name {
        font-weight: 500;
        color: #2c3e50;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }
    }
    
    .spot-address {
      font-size: 0.8rem;
      color: #666;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      margin-bottom: 8px;
      padding-left: 32px;
    }
  }
  
  .card-actions {
    display: flex;
    gap: 8px;
    margin-top: 8px;
    padding-left: 32px;
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
  position: relative;
  z-index: 1;
  min-width: 800px;
  max-height: 800px;
  overflow: auto;
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
  min-width: 760px;
}

.weekday-header {
  display: grid;
  grid-template-columns: repeat(7, minmax(100px, 1fr));
  background: #f8f9fa;
  border-bottom: 1px solid #eee;
  position: sticky;
  top: 0;
  z-index: 2;
  
  .weekday {
    padding: 12px;
    text-align: center;
    font-weight: 500;
    color: #666;
  }
}

.days-grid {
  display: grid;
  grid-template-columns: repeat(7, minmax(100px, 1fr));
  gap: 1px;
  background: #eee;
}

.day-cell {
  position: relative;
  height: 120px;
  padding: 8px;
  background: white;
  transition: all 0.2s ease;
  overflow-y: auto;
  
  &.other-month {
    background: transparent;
    pointer-events: none;
    
    .day-number, 
    .holiday-tag,
    .day-events {
      display: none;
    }
  }
  
  &.drag-over {
    background: #e3f2fd;
    box-shadow: inset 0 0 0 2px #0F4BB4;
    transition: all 0.2s ease;
  }
  
  &.has-events {
    background: #f8f9fa;
  }
  
  &:hover:not(.other-month) {
    background: #f0f4f8;
  }
  
  &.has-holiday {
    background: #fff8e1;
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
    cursor: move;
    transition: all 0.2s ease;
    user-select: none;
    
    &.dragging {
      opacity: 0.5;
      transform: scale(0.95);
    }
    
    &.drag-over {
      border: 2px dashed #0F4BB4;
      padding: 4px 6px;
    }
    
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
    overflow-x: auto;
  }
  
  .spots-sidebar {
    width: 100%;
  }
  
  .calendar-section {
    min-width: 760px;
  }
  
  .calendar-header {
    position: sticky;
    top: 0;
    background: white;
    z-index: 2;
  }
  
  .day-cell {
    min-height: 60px;
    padding: 4px;
  }
}

.preview-button,
.add-button,
.remove-button {
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

.remove-button {
  background: rgba(220, 53, 69, 0.9);
  color: white;
  
  &:hover {
    background: rgba(189, 45, 59, 0.95);
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

.optimal-path-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background-color: #0F4BB4;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;

  &:hover:not(:disabled) {
    background-color: #0d3d91;
    transform: translateY(-1px);
  }

  &.calculating {
    background-color: #666;
    cursor: wait;
  }

  &:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }

  i {
    font-size: 14px;
  }
}

.optimal-path-result {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 16px;
  margin: 16px 0;
  border: 1px solid #dee2e6;

  .result-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;

    h3 {
      margin: 0;
      color: #2c3e50;
      font-size: 16px;
    }

    .close-result {
      background: none;
      border: none;
      color: #666;
      cursor: pointer;
      padding: 4px;
      
      &:hover {
        color: #dc3545;
      }
    }
  }

  .path-info {
    .total-distance {
      margin: 0 0 16px 0;
      color: #0F4BB4;
      font-weight: 500;
      font-size: 18px;
    }
  }

  .path-sequence {
    display: flex;
    flex-direction: column;
    gap: 12px;

    .path-point {
      display: flex;
      align-items: center;
      gap: 12px;
      background: white;
      padding: 12px;
      border-radius: 8px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.1);

      .point-number {
        background: #0F4BB4;
        color: white;
        width: 28px;
        height: 28px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 14px;
        font-weight: 500;
      }

      .point-details {
        flex: 1;
        min-width: 0;

        .point-name {
          display: block;
          color: #2c3e50;
          font-weight: 500;
          margin-bottom: 4px;
        }

        .point-address {
          display: block;
          color: #666;
          font-size: 14px;
        }
      }

      .fa-arrow-right {
        color: #0F4BB4;
        font-size: 16px;
      }
    }
  }
}

.spots-panel {
  margin-top: 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 20px;

  .panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;

    h2 {
      font-size: 1.2rem;
      color: #2c3e50;
      margin: 0;
    }
  }

  .selected-spots-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
    margin-bottom: 20px;
  }

  .selected-spot-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px;
    background: #f8f9fa;
    border-radius: 8px;
    transition: all 0.2s ease;

    &:hover {
      background: #e9ecef;
    }

    .spot-number {
      width: 24px;
      height: 24px;
      background: #0F4BB4;
      color: white;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 14px;
      font-weight: 500;
    }

    .spot-info {
      flex: 1;
      min-width: 0;

      .spot-name {
        font-weight: 500;
        color: #2c3e50;
        margin-bottom: 4px;
      }

      .spot-address {
        font-size: 0.9rem;
        color: #666;
      }
    }

    .spot-actions {
      display: flex;
      gap: 8px;
    }

    .point-button {
      min-width: 70px;
      height: 36px;
      padding: 0 12px;
      border: none;
      border-radius: 50px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      font-size: 13px;
      transition: all 0.3s ease;
      background: rgba(255, 255, 255, 0.9);
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
      
      i {
        font-size: 13px;
      }
      
      span {
        font-weight: 500;
      }
      
      &.start-point {
        color: #28a745;
        border: 1px solid #28a745;
        
        &:hover, &.active {
          background: #28a745;
          color: white;
        }
      }
      
      &.end-point {
        color: #dc3545;
        border: 1px solid #dc3545;
        
        &:hover, &.active {
          background: #dc3545;
          color: white;
        }
      }
    }

    .remove-spot {
      width: 32px;
      height: 32px;
      border: none;
      border-radius: 50%;
      background: rgba(220, 53, 69, 0.1);
      color: #dc3545;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.2s ease;

      &:hover {
        background: #dc3545;
        color: white;
        transform: translateY(-1px);
        box-shadow: 0 2px 4px rgba(220, 53, 69, 0.3);
      }

      i {
        font-size: 16px;
      }
    }
  }

  .no-spots-selected {
    text-align: center;
    padding: 40px 20px;
    color: #666;

    i {
      font-size: 2rem;
      color: #ddd;
      margin-bottom: 12px;
    }

    p {
      margin: 8px 0;

      &.hint {
        font-size: 0.9rem;
        color: #999;
      }
    }
  }
}

.point-button {
  min-width: 70px;
  height: 36px;
  padding: 0 12px;
  border: none;
  border-radius: 50px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-size: 13px;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  
  i {
    font-size: 13px;
  }
  
  span {
    font-weight: 500;
  }
  
  &.start-point {
    color: #28a745;
    border: 1px solid #28a745;
    
    &:hover, &.active {
      background: #28a745;
      color: white;
    }
  }
  
  &.end-point {
    color: #dc3545;
    border: 1px solid #dc3545;
    
    &:hover, &.active {
      background: #dc3545;
      color: white;
    }
  }
}
</style>
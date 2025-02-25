<script>
import axios from 'axios';

export default {
  name: 'EventList',
  data() {
    return {
      events: [],
      loading: true,
      error: null,
    };
  },
  async created() {
    try {
      this.loading = true;
      this.error = null;
      const response = await axios.get('/api/theme_entertainment/api/simple-events/');
      if (response.data.status === 'success') {
        this.events = response.data.data;
        console.log('獲取到的活動數據：', this.events);
      }
      else {
        this.error = response.data.message || '獲取數據失敗';
        console.error('獲取數據失敗：', response.data);
      }
    }
    catch (error) {
      this.error = '獲取活動資料失敗，請稍後再試';
      console.error('獲取活動資料失敗：', error.response || error);
    }
    finally {
      this.loading = false;
    }
  },
};
</script>

<template>
  <div class="events-container">
    <h2>活動列表</h2>
    <div v-if="loading" class="loading">
      載入中...
    </div>
    <div v-else-if="error" class="error">
      {{ error }}
    </div>
    <div v-else-if="events.length === 0" class="no-events">
      目前沒有活動
    </div>
    <div v-else class="events-grid">
      <div v-for="event in events" :key="event.id" class="event-card">
        <h3>{{ event.title }}</h3>
        <p class="description">
          {{ event.description }}
        </p>
        <div class="event-details">
          <p><strong>地點：</strong>{{ event.location }}</p>
          <p><strong>開始日期：</strong>{{ event.start_date }}</p>
          <p><strong>結束日期：</strong>{{ event.end_date }}</p>
          <span class="status" :class="event.status">{{ event.status }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.events-container {
  padding: 20px;
}

.loading, .error, .no-events {
  text-align: center;
  padding: 20px;
  font-size: 1.2em;
}

.error {
  color: #dc3545;
}

.events-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.event-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 15px;
  background: #fff;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.event-details {
  margin-top: 10px;
}

.status {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.9em;
}

.status.active {
  background-color: #4CAF50;
  color: white;
}

.description {
  color: #666;
  margin: 10px 0;
}
</style>

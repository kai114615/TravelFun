<script lang="ts">
import axios from 'axios';

interface Event {
  id: number
  title: string
  description: string | null
  start_date: string | null
  end_date: string | null
  location: string | null
  image_url: string | undefined
}

export default {
  name: 'EventsList',
  data() {
    return {
      events: [] as Event[],
      loading: false,
      error: null as string | null,
    };
  },
  mounted() {
    this.fetchEvents();
  },
  methods: {
    async fetchEvents(): Promise<void> {
      this.loading = true;
      this.error = null;
      try {
        console.log('Fetching events...');
        const response = await axios.get('/theme_entertainment/activities/api/list/');
        console.log('API Response:', response.data);

        if (!response.data) {
          this.error = '伺服器無回應';
          return;
        }

        if (response.data.data && Array.isArray(response.data.data)) {
          if (response.data.data.length === 0) {
            this.error = '目前尚無活動資料';
            return;
          }

          this.events = response.data.data.map((event: any) => ({
            id: event.id,
            title: event.activity_name || event.title || '',
            description: event.description || '',
            start_date: event.start_date || null,
            end_date: event.end_date || null,
            location: event.location || '',
            image_url: event.image_url || undefined,
          }));
        }
        else {
          throw new Error('Invalid response format');
        }
      }
      catch (error) {
        const axiosError = error as any;
        console.error('API Error details:', axiosError.response || axiosError);
        this.error = axiosError.response?.data?.message
          || '無法載入活動資料，請稍後再試';
      }
      finally {
        this.loading = false;
      }
    },
    formatDate(dateString: string | null): string {
      if (!dateString)
        return '日期未定';
      try {
        return new Date(dateString).toLocaleDateString('zh-TW', {
          year: 'numeric',
          month: 'long',
          day: 'numeric',
        });
      }
      catch (e) {
        return dateString;
      }
    },
    handleImageError(e: { target: HTMLImageElement }): void {
      const { target } = e;
      target.src = '/default-event-image.jpg';
    },
  },
};
</script>

<template>
  <div class="events-container">
    <h2 class="events-title">活動列表</h2>
    <div v-if="loading" class="loading">
      載入中...
    </div>
    <div v-if="error" class="error-message">
      {{ error }}
    </div>
    <div v-if="!loading && !error" class="events-grid">
      <div v-for="event in events" :key="event.id" class="event-card">
        <img :src="event.image_url" :alt="event.title" class="event-image" @error="handleImageError">
        <div class="event-content">
          <h3>{{ event.title }}</h3>
          <p class="event-date">{{ formatDate(event.start_date) }} - {{ formatDate(event.end_date) }}</p>
          <p class="event-location">{{ event.location }}</p>
          <p class="event-description">{{ event.description }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.events-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.loading {
  text-align: center;
  padding: 20px;
  font-size: 1.2em;
  color: #666;
}

.error-message {
  text-align: center;
  padding: 20px;
  color: #dc3545;
  background-color: #f8d7da;
  border-radius: 4px;
  margin: 10px 0;
}

.events-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 25px;
  margin-top: 20px;
}

.event-card {
  border: 1px solid #ddd;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease;
  background: #fff;
}

.event-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}

.event-image {
  width: 100%;
  height: 200px;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.event-card:hover .event-image {
  transform: scale(1.05);
}

.event-content {
  padding: 20px;
}

.event-date,
.event-location {
  color: #666;
  margin: 5px 0;
}

.event-description {
  font-size: 0.9em;
  line-height: 1.4;
  margin-top: 10px;
}

h2 {
  color: #2c3e50;
  text-align: center;
  font-size: 2em;
  margin-bottom: 30px;
}

h3 {
  margin: 0 0 10px 0;
  color: #2c3e50;
  font-size: 1.4em;
}

@media (max-width: 768px) {
  .events-grid {
    grid-template-columns: 1fr;
  }

  .event-card {
    margin: 0 10px;
  }
}
</style>

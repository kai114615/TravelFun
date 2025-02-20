<script lang="ts">
import axios from 'axios';

interface Event {
  id: number
  title: string
  description: string | null
  start_date: string | null
  end_date: string | null
  location: string | null
  image_url: string | null
  source: string
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
        const response = await axios.get('http://localhost:8000/theme_entertainment/api/events/');
        console.log('API Response:', response.data);

        if (!response.data) {
          this.error = '伺服器無回應';
          return;
        }

        if (response.data.results && Array.isArray(response.data.results)) {
          if (response.data.results.length === 0) {
            this.error = '目前尚無活動資料';
            return;
          }

          this.events = response.data.results.map((event: any) => ({
            id: event.id,
            title: event.activity_name,
            description: event.description || '',
            start_date: event.start_date || null,
            end_date: event.end_date || null,
            location: event.location || '',
            image_url: event.image_url || null,
            source: event.source || '主題育樂',
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
    handleImageError(e: ErrorEvent): void {
      const target = e.target as HTMLImageElement;
      target.src = '/default-event-image.jpg';
    },
  },
};
</script>

<template>
  <div class="events-container">
    <h2>活動列表</h2>
    <div v-if="loading" class="loading">
      載入中...
    </div>
    <div v-if="error" class="error-message">
      {{ error }}
    </div>
    <div v-if="!loading && !error" class="events-grid">
      <div v-for="event in events" :key="event.id" class="event-card">
        <img v-if="event.image_url" :src="event.image_url" :alt="event.title" @error="handleImageError">
        <div class="event-content">
          <h3>{{ event.title }}</h3>
          <p class="description">
            {{ event.description }}
          </p>
          <div class="event-details">
            <p><i class="fas fa-map-marker-alt" /> {{ event.location }}</p>
            <p>
              <i class="fas fa-calendar-alt" /> {{ formatDate(event.start_date) }} - {{
                formatDate(event.end_date) }}
            </p>
          </div>
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

.event-card img {
    width: 100%;
    height: 200px;
    object-fit: cover;
    transition: transform 0.3s ease;
}

.event-card:hover img {
    transform: scale(1.05);
}

.event-content {
    padding: 20px;
}

.description {
    color: #666;
    margin: 10px 0;
    line-height: 1.5;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.event-details {
    margin-top: 15px;
    color: #666;
    font-size: 0.9em;
}

.event-details p {
    margin: 5px 0;
}

.event-details i {
    margin-right: 8px;
    color: #4a90e2;
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

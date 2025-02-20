<script>
import EventsList from '@/components/EventsList.vue';

export default {
  name: 'ThemeEntertainment',
  components: {
    EventsList,
  },
};
</script>

<template>
  <div class="theme-entertainment">
    <div class="theme-header">
      <h1>主題育樂活動</h1>
      <p class="subtitle">
        探索精彩活動，豐富您的生活
      </p>
    </div>
    <EventsList />
  </div>
</template>

<style scoped>
.theme-entertainment {
    min-height: 100vh;
    background-color: #f5f7fa;
}

.theme-header {
    text-align: center;
    padding: 40px 20px;
    background: linear-gradient(to right, #4a90e2, #67b26f);
    color: white;
    margin-bottom: 30px;
}

.theme-header h1 {
    font-size: 2.5em;
    margin: 0;
    padding: 0;
}

.subtitle {
    font-size: 1.2em;
    margin-top: 10px;
    opacity: 0.9;
}

@media (max-width: 768px) {
    .theme-header {
        padding: 30px 15px;
    }

    .theme-header h1 {
        font-size: 2em;
    }
}
</style>

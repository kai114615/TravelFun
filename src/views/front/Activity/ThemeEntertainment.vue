<script>
import ActivityList from '@/views/front/Activity/ActivityList.vue';

export default {
  name: 'ThemeEntertainment',
  components: {
    ActivityList,
  },
};
</script>

<template>
  <div class="theme-entertainment">
    <ActivityList />
  </div>
</template>

<style scoped>
.theme-entertainment {
  min-height: 100vh;
  background-color: #f5f7fa;
}
</style>

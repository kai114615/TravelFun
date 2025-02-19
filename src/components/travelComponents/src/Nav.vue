<template>
  <div class="travel-nav">
    <div class="container">
      <div class="nav-buttons">
        <router-link 
          :to="{ name: 'Travel' }" 
          class="nav-btn"
          :class="{ active: $route.name === 'Travel' }"
        >
          全台旅遊
        </router-link>
        <router-link 
          :to="{ name: 'TravelModel' }" 
          class="nav-btn"
          :class="{ active: $route.name === 'TravelModel' }"
        >
          推薦系統
        </router-link>
        <router-link 
          :to="{ name: 'Spots' }" 
          class="nav-btn"
          :class="{ active: $route.name === 'Spots' }"
        >
          景點
        </router-link>
        
        <router-link 
          :to="{ name: 'TravelMap' }" 
          class="nav-btn"
          :class="{ active: $route.name === 'TravelMap' }"
        >
          景點地圖
        </router-link>
      </div>
    </div>
  </div>
</template>

<script >
export default {
  name: 'TravelNav'
}
</script>

<style scoped>
.travel-nav {
  padding: 1rem 0;
  background-color: #f8f9fa;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.nav-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.nav-btn {
  padding: 0.5rem 1.5rem;
  border-radius: 4px;
  text-decoration: none;
  color: #333;
  background-color: #fff;
  border: 1px solid #ddd;
  transition: all 0.3s ease;
}

.nav-btn:hover {
  background-color: #e9ecef;
}

.nav-btn.active {
  background-color: #0d6efd;
  color: #fff;
  border-color: #0d6efd;
}
</style> 
<template >
  <div class="category-select-container">
    <select 
      class="form-select" 
      v-model="class_id" 
      @change="clickHandler(class_id)"
    >
      <option value="0">全部</option>
      <option 
        v-for="TC in travel_class" 
        :key="TC.class_id" 
        :value="TC.class_id"
      >
        {{ TC.class_name }}
      </option>
    </select>
  </div>
</template>

<script setup >
import { ref, watchEffect } from 'vue'
const BASE_URL = import.meta.env.VITE_APIURL
const API_URL = 'http://127.0.0.1:8000/travel/api/travelclass/'

const travel_class = ref([])
const class_id = ref(0)
const emit = defineEmits(["categoryClick"])

const clickHandler = id => {
  emit("categoryClick", id)
}

watchEffect(async () => {
  const response = await fetch(API_URL)
  const datas = await response.json();
  travel_class.value = datas
})
</script>

<style lang="scss" scoped>
.category-select-container {
  margin-bottom: 1rem;
  
  h5 {
    margin-bottom: 0.5rem;
    color: #2c3e50;
  }

  .form-select {
    width: 100%;
    padding: 0.5rem;
    border: none;
    border-bottom: 1px solid #ddd;
    border-radius: 0;
    background-color: white;
    font-size: 1rem;
    color: #2c3e50;
    cursor: pointer;
    transition: border-color 0.2s ease;

    &:focus {
      outline: none;
      border-bottom-color: #007bff;
      box-shadow: none;
    }

    &:hover {
      border-bottom-color: #007bff;
    }

    option {
      padding: 0.5rem;
    }
  }
}
</style>
  
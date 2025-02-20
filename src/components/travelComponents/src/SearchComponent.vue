<script setup >
import { ref } from 'vue';

const emit = defineEmits(['searchInput'])
    const keyword = ref('')
    const inputHandler = ()=>{
emit('searchInput', keyword.value)
    }
</script>

<template>
    <div>
      <div class="search-container d-flex gap-2">
    <input @keyup.enter="inputHandler" type="text" v-model="keyword" placeholder="關鍵字搜尋" class="form-control">
    <button @click="inputHandler" class="btn btn-primary">搜尋
    </button>
  </div>

    </div>
</template>

<style lang="scss" scoped>
.search-container {
  display: flex;
  align-items: center;
  
  input {
    flex: 1;
    border: none;
    border-bottom: 1px solid #ddd;
    border-radius: 0;
    padding: 0.5rem 0;
    
    &:focus {
      outline: none;
      border-bottom-color: #007bff;
      box-shadow: none;
    }
  }
  
  button {
    min-width: 80px;
    border-radius: 20px;
  }
}
</style>
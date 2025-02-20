<script setup >
import { computed } from 'vue';

const props = defineProps({
  totalPages: Number,
  thePage: Number,
});
const emit = defineEmits(['goPaging']);

const clickHandler = (page) => {
  if (page >= 1 && page <= props.totalPages) {
    emit('goPaging', page);
  }
};

// 計算顯示的頁碼範圍
const visiblePages = computed(() => {
  const maxPagesToShow = 10; // 總共顯示的最大頁碼數量（包括頭尾）
  const range = []; // 存放顯示的頁碼
  const start = 1; // 第一頁
  const end = props.totalPages; // 最後一頁

  if (props.totalPages <= maxPagesToShow) {
    // 如果總頁數小於最大顯示頁碼，直接顯示所有頁碼
    return Array.from({ length: props.totalPages }, (_, i) => i + 1);
  }

  const halfRange = Math.floor(maxPagesToShow / 2);
  const lowerBound = Math.max(start, props.thePage - halfRange);
  const upperBound = Math.min(end, props.thePage + halfRange);

  if (lowerBound > start + 1) {
    range.push(start, '...');
  } else {
    range.push(...Array.from({ length: lowerBound - start }, (_, i) => start + i));
  }

  range.push(...Array.from({ length: upperBound - lowerBound + 1 }, (_, i) => lowerBound + i));

  if (upperBound < end - 1) {
    range.push('...', end);
  } else {
    range.push(...Array.from({ length: end - upperBound }, (_, i) => upperBound + i + 1));
  }

  return range;
});
</script>

<template>
  <div class="pagination">
    <div class="page-info">
      共 {{ totalPages }} 頁
    </div>
    <button 
      @click="clickHandler(thePage - 1)" 
      :disabled="thePage === 1"
      class="page-btn prev-next-btn"
    >
      上一頁
    </button>
    <button 
      v-for="page in visiblePages" 
      :key="page"
      @click="clickHandler(page)"
      class="page-btn"
      :class="{
        'active': thePage === page,
        'dots': page === '...'
      }"
      :disabled="page === '...'"
    >
      {{ page }}
    </button>
    <button 
      @click="clickHandler(thePage + 1)" 
      :disabled="thePage === totalPages"
      class="page-btn prev-next-btn"
    >
      下一頁
    </button>
  </div>
</template>

<style lang="scss" scoped>
.pagination {
  display: flex;
  gap: 0.5rem;
  justify-content: center;
  align-items: center;
  margin-top: 2rem;
}

.page-info {
  margin-right: 1rem;
  color: #666;
  font-size: 0.9rem;
  padding: 0.5rem;
  background: #f8f9fa;
  border-radius: 20px;
  border: 1px solid #dee2e6;
}

.page-btn {
  min-width: 40px;
  height: 40px;
  padding: 0 0.8rem;
  border: none;
  background: transparent;
  color: #666;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;

  &:hover:not(:disabled) {
    background: #f0f0f0;
    color: #007bff;
  }

  &.active {
    background: #007bff;
    color: white;
    font-weight: 500;
  }

  &.dots {
    cursor: default;
    pointer-events: none;
    padding: 0 0.4rem;
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  &.prev-next-btn {
    min-width: 80px;
    background: #f8f9fa;
    border: 1px solid #dee2e6;

    &:hover:not(:disabled) {
      background: #e9ecef;
      color: #0056b3;
    }
  }
}

@media (max-width: 768px) {
  .page-info {
    font-size: 0.8rem;
    padding: 0.4rem;
  }

  .page-btn {
    min-width: 35px;
    height: 35px;
    font-size: 0.8rem;

    &.prev-next-btn {
      min-width: 70px;
    }
  }
}
</style>


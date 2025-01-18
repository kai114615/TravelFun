<template>
  <div class="min-h-screen bg-gray-50">
    <Header />
    <!-- 主要內容區域 -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- 主要內容 -->
      <div class="bg-white rounded-lg shadow-sm p-6">
        <router-view v-slot="{ Component }">
          <transition
            enter-active-class="transition-opacity duration-300"
            enter-from-class="opacity-0"
            enter-to-class="opacity-100"
            leave-active-class="transition-opacity duration-300"
            leave-from-class="opacity-100"
            leave-to-class="opacity-0"
          >
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import Header from '@/components/Header';
</script>

<style scoped>
.router-link-active {
  @apply text-blue-600;
}
</style> 
<script setup lang="ts">
import LogoImage from '@/assets/logoImg.svg';
</script>

<template>
  <footer class="flex flex-col items-center bg-cc-other-2 p-4">
    <div class="mt-6 mb-10 flex items-center">
      <router-link to="/" class="cursor-pointer hover:opacity-80 transition-opacity">
        <img class="h-10 object-cover" :src="LogoImage" alt="logo">
      </router-link>
    </div>
    <p class="text-center text-sm text-cc-other-3">
      © 2024-2025 By OJTP01
    </p>
  </footer>
</template>

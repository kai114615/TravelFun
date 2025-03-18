<script setup lang="ts">
import { ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import AiChat from './AiChat.vue';

// 定義在哪些頁面顯示聊天組件
const validPaths = [
    '/', // 首頁
    '/theme', // 主題育樂頁面
    '/activities', // 活動頁面
    '/shop', // 商城頁面
    '/products', // 產品頁面
];

const route = useRoute();
const showChat = ref(true);

// 監聽路由變化，決定是否顯示聊天組件
watch(() => route.path, (newPath) => {
    // 檢查當前路徑是否在允許顯示的路徑列表中
    // 使用 startsWith 來匹配路徑前綴，這樣子路徑也能匹配
    showChat.value = validPaths.some(path => newPath.startsWith(path));
}, { immediate: true });
</script>

<template>
    <!-- 只在特定頁面顯示聊天組件 -->
    <AiChat v-if="showChat" />
</template>
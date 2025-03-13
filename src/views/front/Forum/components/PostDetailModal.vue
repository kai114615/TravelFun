<script setup lang="ts">
import { defineEmits, defineProps, ref, watch, nextTick } from 'vue';
import { NButton, NIcon, NInput, NModal, useMessage } from 'naive-ui';
import {
  ChatBubbleOutlined,
  FavoriteBorderOutlined,
  FavoriteOutlined,
  VisibilityOutlined,
} from '@vicons/material';
import { useUserStore } from '@/stores';
import { apiForumAddComment, apiForumToggleLike } from '@/utils/api';
import CommentSection from './CommentSection.vue';

const props = defineProps({
  show: {
    type: Boolean,
    required: true,
  },
  post: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(['update:show', 'like', 'comment', 'comment-count-update']);

const userStore = useUserStore();
const message = useMessage();

const isLiked = ref(false);
const likeCount = ref(0);
const commentCount = ref(0);
const viewCount = ref(0);
const isViewUpdated = ref(false);

// 監聽 post 變化
watch(() => props.post, (newPost) => {
  if (newPost) {
    console.log('Post data updated:', newPost);
    
    // 檢查觀看數是否更新
    const oldViewCount = viewCount.value;
    const newViewCount = newPost.views || 0;
    
    // 更新各項數據
    isLiked.value = newPost.is_liked || false;
    likeCount.value = newPost.like_count || 0;
    commentCount.value = newPost.comment_count || 0;
    viewCount.value = newViewCount;
    
    // 如果觀看數增加了，標記為已更新以觸發動畫
    if (oldViewCount > 0 && newViewCount > oldViewCount) {
      console.log('觀看數已更新:', oldViewCount, '->', newViewCount);
      isViewUpdated.value = true;
      
      // 短暫延遲後重置標記，以便下次更新也能觸發動畫
      setTimeout(() => {
        isViewUpdated.value = false;
      }, 2500); // 略長於動畫時間，確保動畫完成
    }
  }
}, { immediate: true, deep: true });

// 處理評論數量更新
const handleCommentUpdate = (count: number) => {
  console.log('評論數量更新:', count, '文章ID:', props.post?.id);
  // 始終使用最新值更新本地狀態
  commentCount.value = count;
  
  // 確保事件始終正確發送到父組件
  setTimeout(() => {
    emit('comment-count-update', count);
    console.log('已發送評論數量更新事件:', count);
  }, 0);
};

// 格式化日期
function formatDate(date: string) {
  if (!date)
    return '';
  return new Date(date).toLocaleString('zh-TW');
}

// 處理按讚
async function handleLike() {
  if (!userStore.loginStatus) {
    message.warning('請先登入後才能點讚');
    return;
  }

  try {
    console.log('文章詳情中點讚 - 文章ID:', props.post.id, '當前狀態:', isLiked.value, '點讚數:', likeCount.value);
    
    // 保存原始狀態以便恢復
    const wasLiked = isLiked.value;
    const originalCount = likeCount.value;
    
    // 立即在UI中更新狀態（樂觀更新）
    isLiked.value = !wasLiked;
    likeCount.value += wasLiked ? -1 : 1;
    
    console.log('UI已樂觀更新 - 新狀態:', isLiked.value, '新點讚數:', likeCount.value);
    
    // 立即通知父組件更新
    emit('like', {
      post_id: props.post.id,
      is_liked: isLiked.value,
      like_count: likeCount.value
    });
    
    // 強制Vue更新視圖
    await nextTick();
    
    // 調用API
    const response = await apiForumToggleLike(props.post.id);
    console.log('點讚API響應:', response.data);
    
    if (response.data.status === 'success') {
      // 使用後端返回的實際數據更新
      isLiked.value = response.data.data.is_liked;
      likeCount.value = response.data.data.like_count;
      
      console.log('API更新完成 - 最終狀態:', isLiked.value, '最終點讚數:', likeCount.value);
      
      // 再次發送事件，確保父組件同步更新
      emit('like', {
        post_id: props.post.id,
        is_liked: isLiked.value,
        like_count: likeCount.value
      });
      
      // 強制多次更新，確保視圖刷新
      await nextTick();
      setTimeout(() => {
        // 再次觸發動畫效果
        isLiked.value = isLiked.value;
        console.log('UI延遲強制刷新完成');
      }, 50);
      
      // 顯示成功消息
      message.success(response.data.message || (isLiked.value ? '已點讚！' : '已取消點讚'));
    } else {
      // 如果請求失敗，恢復原始狀態
      isLiked.value = wasLiked;
      likeCount.value = originalCount;
      
      console.log('恢復原狀 - 恢復狀態:', wasLiked, '恢復點讚數:', originalCount);
      
      // 通知父組件恢復原狀
      emit('like', {
        post_id: props.post.id,
        is_liked: wasLiked,
        like_count: originalCount
      });
      
      // 強制視圖更新
      await nextTick();
      
      // 顯示錯誤消息
      message.error(response.data.message || '操作失敗，請稍後重試');
    }
  } catch (error) {
    console.error('按讚失敗:', error);
    // 恢復UI中的原始狀態
    isLiked.value = wasLiked;
    likeCount.value = originalCount;
    
    // 通知父組件恢復原狀
    emit('like', {
      post_id: props.post.id,
      is_liked: wasLiked,
      like_count: originalCount
    });
    
    // 強制視圖更新
    await nextTick();
    
    message.error('按讚失敗，請稍後重試');
  }
}
</script>

<template>
  <NModal
    :show="show"
    preset="card"
    style="width: 1000px; max-width: 95vw;"
    @update:show="(value) => emit('update:show', value)"
  >
    <div class="post-detail-modal">
      <!-- 文章標題區域 -->
      <div class="border-b border-gray-200 pb-6 mb-6">
        <div class="flex items-center justify-between mb-3">
          <div class="flex items-center gap-3">
            <span class="px-3 py-1.5 bg-indigo-50 text-indigo-600 rounded-md text-sm font-medium">{{ post?.category?.name || '旅遊討論' }}</span>
            <span class="text-gray-500 text-sm">•</span>
            <span class="text-sm text-gray-500">發表於 {{ formatDate(post?.created_at) }}</span>
          </div>
          <div class="flex items-center gap-4 text-gray-500 text-sm">
            <span class="flex items-center gap-1.5 px-3 py-1 bg-blue-50 text-blue-600 rounded-md transition-all duration-500" :class="{'view-highlight': isViewUpdated}">
              <NIcon size="18"><VisibilityOutlined /></NIcon>
              {{ viewCount }} 觀看
            </span>
            <div class="flex items-center text-gray-700">
              <button @click="handleLike" 
                class="flex items-center space-x-1 px-3 py-1.5 rounded-md transition-colors focus:outline-none"
                :class="[
                  isLiked 
                    ? 'text-green-600 bg-green-50 hover:bg-green-100 border border-green-200' 
                    : 'text-gray-500 hover:text-green-600 hover:bg-green-50 hover:border-green-200 border border-gray-200'
                ]"
              >
                <NIcon>
                  <component :is="isLiked ? FavoriteOutlined : FavoriteBorderOutlined" 
                             :class="['like-icon', { 'like-animation': isLiked }]" />
                </NIcon>
                <span class="font-medium" :key="`likes-${likeCount}-${isLiked}`">{{ likeCount }}</span>
              </button>
            </div>
            <span class="flex items-center gap-1.5">
              <NIcon size="18"><ChatBubbleOutlined /></NIcon>
              {{ commentCount }}
            </span>
          </div>
        </div>
        <h1 class="text-2xl font-bold text-gray-900 mb-4">
          {{ post?.title }}
        </h1>
        <div class="flex flex-wrap gap-2">
          <span
            v-for="tag in post?.tags"
            :key="tag.id"
            class="px-3 py-1 bg-gray-100 text-gray-600 rounded-full text-xs border border-gray-200"
          >
            # {{ tag.name }}
          </span>
        </div>
      </div>

      <!-- 作者資訊與內容 -->
      <div class="flex mb-6 gap-6">
        <div class="flex-shrink-0">
          <div class="flex flex-col items-center text-center w-32">
            <img
              :src="post?.author?.avatar || 'https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y'"
              :alt="post?.author?.username"
              class="w-16 h-16 rounded-full object-cover ring-1 ring-gray-200 shadow-sm mb-3"
            >
            <div class="text-sm font-medium text-gray-900">
              {{ post?.author?.username }}
            </div>
            <div class="text-xs px-2 py-0.5 bg-indigo-50 text-indigo-600 rounded-full mt-1.5">
              {{ post?.author?.title || '旅遊愛好者' }}
            </div>
          </div>
        </div>
        
        <!-- 文章內容 -->
        <div class="flex-1 bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
          <div class="prose prose-lg max-w-none text-gray-700" v-html="post?.content" />
          
          <!-- 文章底部可能的旅遊相關資訊 -->
          <div v-if="post?.meta" class="mt-8 pt-5 border-t border-gray-100">
            <div v-if="post?.meta.location" class="flex items-center text-sm text-gray-600 mb-2.5">
              <span class="font-medium mr-3">旅遊地點:</span>
              <span>{{ post?.meta.location }}</span>
            </div>
            <div v-if="post?.meta.travel_date" class="flex items-center text-sm text-gray-600 mb-2.5">
              <span class="font-medium mr-3">旅遊日期:</span>
              <span>{{ post?.meta.travel_date }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 互動按鈕 -->
      <div class="flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-200 mb-6">
        <div class="text-sm text-gray-500">
          發表於 {{ formatDate(post?.created_at) }}
        </div>
        <NButton
          :type="isLiked ? 'error' : 'default'"
          class="flex items-center gap-2"
          @click="handleLike"
        >
          <NIcon>
            <component :is="isLiked ? FavoriteOutlined : FavoriteBorderOutlined" />
          </NIcon>
          {{ isLiked ? '已讚 ' + likeCount : '讚 ' + likeCount }}
        </NButton>
      </div>

      <!-- 評論區域 -->
      <div class="bg-white rounded-lg border border-gray-200 overflow-hidden shadow-sm">
        <!-- 評論列表組件 -->
        <div class="p-5">
          <CommentSection 
            :post-id="post.id" 
            @comment-count-update="handleCommentUpdate"
          />
        </div>
      </div>
    </div>
  </NModal>
</template>

<style scoped>
.post-detail-modal {
  max-height: 85vh;
  overflow-y: auto;
  background-color: #f9fafb;
  padding: 1.75rem;
  position: relative;
  border-radius: 0.5rem;
}

.prose {
  font-size: 1.05rem;
  line-height: 1.8;
  color: #374151;
}

.prose p {
  margin-bottom: 1.25rem;
}

.prose img {
  max-width: 100%;
  height: auto;
  border-radius: 0.375rem;
  margin: 1.5rem 0;
  border: 1px solid #f0f0f0;
  box-shadow: 0 3px 8px rgba(0,0,0,0.08);
}

/* 添加滾動條樣式 */
.post-detail-modal::-webkit-scrollbar {
  width: 8px;
}

.post-detail-modal::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.post-detail-modal::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 4px;
}

.post-detail-modal::-webkit-scrollbar-thumb:hover {
  background: #a5b4fc;
}

/* 增加文章內容區域的排版 */
.prose h1, .prose h2, .prose h3 {
  margin-top: 2rem;
  margin-bottom: 1rem;
  font-weight: 600;
  color: #1f2937;
}

.prose h1 {
  font-size: 1.5rem;
}

.prose h2 {
  font-size: 1.3rem;
}

.prose h3 {
  font-size: 1.15rem;
}

.prose ul, .prose ol {
  padding-left: 1.5rem;
  margin-bottom: 1.25rem;
}

.prose li {
  margin-bottom: 0.5rem;
}

.prose a {
  color: #4f46e5;
  text-decoration: underline;
}

.prose blockquote {
  border-left: 4px solid #d1d5db;
  padding-left: 1rem;
  font-style: italic;
  color: #6b7280;
  margin: 1.5rem 0;
}

.view-highlight {
  animation: pulse 2s ease-in-out;
}

@keyframes pulse {
  0% {
    transform: scale(1);
    background-color: rgba(191, 219, 254, 0.5);
  }
  50% {
    transform: scale(1.05);
    background-color: rgba(147, 197, 253, 0.8);
  }
  100% {
    transform: scale(1);
    background-color: rgba(219, 234, 254, 0.5);
  }
}

/* 更強的點讚按鈕動畫效果 */
.like-icon {
  transition: transform 0.3s ease;
}

.like-icon:hover {
  transform: scale(1.2);
}

.like-animation {
  animation: heartBeat 0.6s ease-in-out;
}

@keyframes heartBeat {
  0% {
    transform: scale(1);
  }
  14% {
    transform: scale(1.3);
  }
  28% {
    transform: scale(1);
  }
  42% {
    transform: scale(1.3);
  }
  70% {
    transform: scale(1);
  }
}

/* 原有的 scale 動畫 */
.animate-scale {
  animation: scale 0.3s ease-in-out;
}

@keyframes scale {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.3);
  }
  100% {
    transform: scale(1);
  }
}
</style>

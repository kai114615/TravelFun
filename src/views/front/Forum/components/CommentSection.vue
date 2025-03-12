<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { NAvatar, NSpace, NCard, NMessageProvider, useMessage, NButton, NInput } from 'naive-ui';
import { storeToRefs } from 'pinia';
import { useUserStore } from '@/stores';
import { FORUM_API } from '@/utils/api';
import { request } from '@/utils/request';

const props = defineProps<{
  postId: number;
}>();

const emit = defineEmits(['comment-count-update', 'commentAdded']);

const userStore = useUserStore();
const { userInfo, loginStatus } = storeToRefs(userStore);
const message = useMessage();

const comments = ref<any[]>([]);
const newComment = ref('');
const isSubmitting = ref(false);

// 處理頭像URL
const getAvatarUrl = (avatarPath: string) => {
  if (!avatarPath) return '/images/member.jpg';
  if (avatarPath.startsWith('http')) return avatarPath;
  return `http://127.0.0.1:8000${avatarPath}`;
};

// 獲取評論列表
const fetchComments = async () => {
  try {
    console.log('正在獲取文章ID:', props.postId, '的評論列表');
    const response = await FORUM_API.getComments(props.postId);
    
    if (response.data.status === 'success') {
      // 保存舊的評論數量用於比較
      const oldCommentCount = comments.value?.length || 0;
      
      // 更新評論列表
      comments.value = response.data.data || [];
      const newCommentCount = comments.value.length;
      
      console.log('評論列表獲取成功 - 文章ID:', props.postId, '舊評論數:', oldCommentCount, '新評論數:', newCommentCount);
      
      // 只有在評論數量發生變化時才發送事件
      if (oldCommentCount !== newCommentCount) {
        console.log('評論數量已變更，發送更新事件...');
        // 使用 setTimeout 確保事件在微任務隊列中執行，避免可能的同步問題
        setTimeout(() => {
          emit('comment-count-update', newCommentCount);
          console.log('評論數量更新事件已發送:', newCommentCount);
        }, 0);
      }
    } else {
      throw new Error(response.data.message || '獲取評論失敗');
    }
  }
  catch (error: any) {
    console.error('獲取評論失敗:', error);
    message.error(error.message || '獲取評論失敗，請稍後再試');
  }
};

// 提交評論
const submitComment = async () => {
  if (!userInfo.value) {
    message.error('請先登入後再發表評論');
    return;
  }

  if (!newComment.value.trim()) {
    message.error('評論內容不能為空');
    return;
  }

  isSubmitting.value = true;

  try {
    const token = localStorage.getItem('access_token');
    if (!token) {
      throw new Error('未登入或登入已過期');
    }

    console.log('正在提交評論到文章ID:', props.postId);
    
    const response = await request({
      method: 'post',
      url: `/api/forum/posts/${props.postId}/add_comment/`,
      data: { content: newComment.value.trim() },
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });

    if (response.status === 201) {
      message.success('評論發表成功');
      newComment.value = '';
      console.log('評論添加成功，正在重新獲取評論列表...');
      
      // 重新獲取評論列表
      await fetchComments();
      
      // 強制發送一次評論更新事件以確保UI刷新
      const currentCount = comments.value.length;
      console.log('強制發送評論數更新事件:', currentCount);
      
      setTimeout(() => {
        emit('commentAdded');
        emit('comment-count-update', currentCount);
        console.log('評論添加和數量更新事件已發送');
      }, 0);
    } else {
      throw new Error(response.data.message || '發表評論失敗');
    }
  } catch (error: any) {
    console.error('發表評論失敗:', error);
    if (error.response?.status === 401) {
      message.error('登入已過期，請重新登入');
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    } else if (error.response?.status === 403) {
      message.error('您沒有權限執行此操作');
    } else {
      message.error(error.response?.data?.message || error.message || '發表評論失敗，請稍後再試');
    }
  } finally {
    isSubmitting.value = false;
  }
};

// 刪除評論
const deleteComment = async (commentId: number) => {
  try {
    console.log('正在刪除評論ID:', commentId, '從文章ID:', props.postId);
    
    const response = await FORUM_API.deleteComment(commentId);
    if (response.data.status === 'success') {
      message.success('評論刪除成功');
      console.log('評論刪除成功，正在重新獲取評論列表...');
      
      // 記錄當前評論數用於比較
      const oldCommentCount = comments.value.length;
      
      // 重新獲取評論列表
      await fetchComments();
      
      // 獲取最新的評論數
      const newCommentCount = comments.value.length;
      console.log('刪除評論後 - 舊評論數:', oldCommentCount, '新評論數:', newCommentCount);
      
      // 強制發送一次評論更新事件以確保UI刷新
      if (oldCommentCount !== newCommentCount) {
        setTimeout(() => {
          emit('comment-count-update', newCommentCount);
          console.log('評論刪除後數量更新事件已發送:', newCommentCount);
        }, 0);
      }
    } else {
      throw new Error(response.data.message || '刪除評論失敗');
    }
  }
  catch (error: any) {
    console.error('刪除評論失敗:', error);
    message.error(error.message || '刪除評論失敗，請稍後再試');
  }
};

// 格式化時間
const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  return date.toLocaleString('zh-TW', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
};

// 檢查是否可以刪除評論
const canDeleteComment = (comment: any) => {
  return userInfo.value && (
    userInfo.value.id === comment.author.id || // 評論作者
    userInfo.value.level === 'admin' // 管理員
  );
};

// 監聽重新載入事件
const handleReload = () => {
  fetchComments();
};

onMounted(() => {
  fetchComments();
  // 添加事件監聽
  const commentSection = document.querySelector('.comments-section');
  if (commentSection) {
    commentSection.addEventListener('reload-comments', handleReload);
  }
});
</script>

<template>
  <NMessageProvider>
    <div class="comments-section">
      <!-- 評論列表 -->
      <div class="bg-white rounded-md border border-gray-200 overflow-hidden mb-4">
        <div class="border-b border-gray-200 px-4 py-3 bg-gray-50 flex justify-between items-center">
          <h3 class="font-medium text-gray-700">評論列表 ({{ comments.length }})</h3>
          <span class="text-xs text-gray-500">按時間排序</span>
        </div>
        
        <div class="p-4">
          <template v-if="comments.length">
            <div 
              v-for="(comment, index) in comments" 
              :key="comment.id" 
              class="comment-item py-3 px-2"
              :class="{'border-b border-gray-100': index !== comments.length - 1}"
            >
              <div class="flex">
                <NAvatar
                  :src="getAvatarUrl(comment.author.avatar)"
                  :fallback-src="'/images/member.jpg'"
                  size="small"
                  class="mr-3 flex-shrink-0"
                />
                <div class="flex-grow">
                  <div class="flex justify-between items-start">
                    <div>
                      <span class="font-medium text-gray-800 text-sm">{{ comment.author.username }}</span>
                      <span class="text-gray-500 text-xs ml-2">{{ formatDate(comment.created_at) }}</span>
                    </div>
                    <NButton
                      v-if="canDeleteComment(comment)"
                      text
                      type="error"
                      size="small"
                      class="text-xs px-2"
                      @click="deleteComment(comment.id)"
                    >
                      刪除
                    </NButton>
                  </div>
                  <p class="mt-2 text-gray-700 text-sm">{{ comment.content }}</p>
                </div>
              </div>
            </div>
          </template>
          <template v-else>
            <div class="text-center text-gray-500 py-6 px-4">
              <svg class="w-10 h-10 mx-auto text-gray-300 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>
              </svg>
              <p class="text-sm font-medium">暫無評論</p>
              <p class="mt-1 text-xs">成為第一個發表評論的人！</p>
            </div>
          </template>
        </div>
      </div>

      <!-- 評論輸入框 -->
      <div class="bg-white rounded-md border border-gray-200 p-4">
        <h4 class="text-gray-700 font-medium mb-3 pb-2 border-b border-gray-100">
          發表新評論
        </h4>
        <NInput
          v-model:value="newComment"
          type="textarea"
          placeholder="寫下你的評論..."
          :rows="3"
          :autofocus="true"
          class="comment-input"
        />
        <div class="flex justify-end mt-3">
          <NButton
            type="primary"
            :disabled="!newComment.trim()"
            :loading="isSubmitting"
            class="rounded-md"
            @click="submitComment"
          >
            發表評論
          </NButton>
        </div>
      </div>
    </div>
  </NMessageProvider>
</template>

<style scoped>
.comments-section {
  position: relative;
}

.comment-item {
  transition: background-color 0.2s ease;
}

.comment-item:hover {
  background-color: #f9fafb;
}
</style> 
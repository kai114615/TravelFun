<script setup lang="ts">
import { defineEmits, defineProps, ref, watch } from 'vue';
import { NButton, NIcon, NInput, NModal, useMessage } from 'naive-ui';
import {
  ChatBubbleOutlined,
  FavoriteBorderOutlined,
  FavoriteOutlined,
  VisibilityOutlined,
} from '@vicons/material';
import { useUserStore } from '@/stores';
import { apiForumAddComment, apiForumToggleLike } from '@/utils/api';

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

const emit = defineEmits(['update:show', 'like', 'comment']);

const userStore = useUserStore();
const message = useMessage();

const showComments = ref(false);
const newComment = ref('');
const isSubmitting = ref(false);
const isLiked = ref(false);
const likeCount = ref(0);

// 監聽 post 變化
watch(() => props.post, (newPost) => {
  if (newPost) {
    console.log('Post data updated:', newPost);
    isLiked.value = newPost.is_liked || false;
    likeCount.value = newPost.like_count || 0;
  }
}, { immediate: true, deep: true });

// 格式化日期
function formatDate(date: string) {
  if (!date)
    return '';
  return new Date(date).toLocaleString('zh-TW');
}

// 處理按讚
async function handleLike() {
  if (!userStore.loginStatus) {
    message.warning('請先登入');
    return;
  }

  try {
    // 先更新本地狀態
    const currentIsLiked = isLiked.value;
    const currentLikeCount = likeCount.value;
    
    // 樂觀更新
    isLiked.value = !currentIsLiked;
    likeCount.value = currentLikeCount + (currentIsLiked ? -1 : 1);

    // 發送請求到後端
    const response = await apiForumToggleLike(props.post.id);
    console.log('Like API response:', response);

    if (response.data.status === 'success') {
      // 使用後端返回的實際數據更新
      const { is_liked, like_count } = response.data.data;
      isLiked.value = is_liked;
      likeCount.value = like_count;
      
      // 發送事件到父組件
      emit('like', { is_liked, like_count });
      message.success(response.data.message);
    }
    else {
      // 如果請求失敗，恢復原始狀態
      isLiked.value = currentIsLiked;
      likeCount.value = currentLikeCount;
      throw new Error(response.data.message);
    }
  }
  catch (error: any) {
    console.error('按讚失敗:', error);
    message.error('操作失敗，請稍後重試');
  }
}

// 處理評論按鈕點擊
function handleComment() {
  if (!userStore.loginStatus) {
    message.warning('請先登入');
    return;
  }
  showComments.value = !showComments.value;
}

// 提交評論
async function submitComment() {
  if (!userStore.loginStatus) {
    message.warning('請先登入');
    return;
  }

  if (!newComment.value.trim()) {
    message.warning('請輸入評論內容');
    return;
  }

  try {
    isSubmitting.value = true;
    const response = await apiForumAddComment(props.post.id, newComment.value);
    if (response.data.status === 'success') {
      emit('comment', response.data.data);
      newComment.value = '';
      message.success('評論發表成功');
    }
  }
  catch (error) {
    console.error('發表評論失敗:', error);
    message.error('發表失敗，請稍後再試');
  }
  finally {
    isSubmitting.value = false;
  }
}
</script>

<template>
  <NModal
    :show="show"
    preset="card"
    style="width: 800px; max-width: 90vw;"
    @update:show="(value) => emit('update:show', value)"
  >
    <div class="post-detail-modal">
      <!-- 文章標題區域 -->
      <div class="border-b border-gray-200 pb-4 mb-6">
        <div class="flex items-center gap-2 mb-2">
          <span class="px-2 py-1 bg-primary/10 text-primary rounded text-sm">{{ post?.category?.name || '未分類' }}</span>
          <span class="text-gray-400">•</span>
          <span class="text-sm text-gray-500">發表於 {{ formatDate(post?.created_at) }}</span>
        </div>
        <h1 class="text-2xl font-bold text-gray-900 mb-2">
          {{ post?.title }}
        </h1>
        <div class="flex flex-wrap gap-2">
          <span
            v-for="tag in post?.tags"
            :key="tag.id"
            class="px-2 py-1 bg-gray-100 text-gray-600 rounded-full text-xs"
          >
            # {{ tag.name }}
          </span>
        </div>
      </div>

      <div class="flex gap-6">
        <!-- 左側作者資訊 -->
        <div class="w-48 flex-shrink-0">
          <div class="bg-gray-50 rounded-lg p-4 sticky top-4">
            <div class="flex flex-col items-center text-center">
              <img
                :src="post?.author?.avatar || 'https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y'"
                :alt="post?.author?.username"
                class="w-20 h-20 rounded-full object-cover mb-3 ring-2 ring-primary/20"
              >
              <div class="mb-4">
                <div class="font-medium text-gray-900 mb-1">
                  {{ post?.author?.username }}
                </div>
                <div class="text-xs px-2 py-1 bg-primary/10 text-primary rounded-full">
                  {{ post?.author?.title || '一般會員' }}
                </div>
              </div>
              <!-- 互動統計 -->
              <div class="w-full space-y-3 text-sm text-gray-500">
                <div class="flex items-center justify-center gap-2 p-2 rounded bg-gray-100/50">
                  <NIcon size="18">
                    <VisibilityOutlined />
                  </NIcon>
                  <span class="font-medium">{{ post?.views || 0 }}</span>
                  <span class="text-xs">瀏覽</span>
                </div>
                <div class="flex items-center justify-center gap-2 p-2 rounded bg-gray-100/50">
                  <NIcon size="18">
                    <component :is="isLiked ? FavoriteOutlined : FavoriteBorderOutlined" />
                  </NIcon>
                  <span class="font-medium">{{ likeCount }}</span>
                  <span class="text-xs">讚</span>
                </div>
                <div class="flex items-center justify-center gap-2 p-2 rounded bg-gray-100/50">
                  <NIcon size="18">
                    <ChatBubbleOutlined />
                  </NIcon>
                  <span class="font-medium">{{ post?.comment_count || 0 }}</span>
                  <span class="text-xs">評論</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 右側文章內容 -->
        <div class="flex-1">
          <!-- 文章內容 -->
          <div class="bg-white rounded-lg p-6 mb-6 shadow-sm border border-gray-100">
            <div class="prose max-w-none" v-html="post?.content" />
          </div>

          <!-- 互動按鈕 -->
          <div class="flex items-center gap-4 bg-white rounded-lg p-4 shadow-sm border border-gray-100 mb-6">
            <NButton
              :type="isLiked ? 'error' : 'default'"
              ghost
              class="flex items-center gap-2 flex-1"
              size="large"
              @click="handleLike"
            >
              <NIcon>
                <component :is="isLiked ? FavoriteOutlined : FavoriteBorderOutlined" />
              </NIcon>
              {{ isLiked ? '取消讚' : '按讚' }}
            </NButton>
            <NButton
              type="primary"
              ghost
              class="flex items-center gap-2 flex-1"
              :class="{ 'n-button--active-color': showComments }"
              size="large"
              @click="handleComment"
            >
              <NIcon><ChatBubbleOutlined /></NIcon>
              {{ showComments ? '收起評論' : '評論' }}
            </NButton>
          </div>

          <!-- 評論區域 -->
          <div v-if="showComments" class="bg-white rounded-lg p-6 shadow-sm border border-gray-100">
            <h3 class="font-bold mb-4 flex items-center gap-2">
              <NIcon><ChatBubbleOutlined /></NIcon>
              評論區
            </h3>
            <!-- 評論輸入框 -->
            <div class="mb-6">
              <NInput
                v-model:value="newComment"
                type="textarea"
                placeholder="寫下你的評論..."
                :rows="3"
                :autofocus="true"
              />
              <div class="flex justify-end mt-2">
                <NButton
                  type="primary"
                  :disabled="!newComment.trim()"
                  :loading="isSubmitting"
                  size="large"
                  @click="submitComment"
                >
                  發表評論
                </NButton>
              </div>
            </div>
            <!-- 評論列表 -->
            <div class="space-y-6">
              <div v-for="comment in post?.comments" :key="comment.id" class="bg-gray-50/50 rounded-lg p-4">
                <div class="flex items-start gap-3">
                  <img
                    :src="comment.author?.avatar || 'https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y'"
                    :alt="comment.author?.username"
                    class="w-10 h-10 rounded-full ring-2 ring-primary/10"
                  >
                  <div class="flex-1">
                    <div class="flex items-center gap-2 mb-2">
                      <span class="font-medium text-gray-900">{{ comment.author?.username }}</span>
                      <span class="text-xs px-2 py-0.5 bg-gray-100 text-gray-600 rounded-full">{{ comment.author?.title || '一般會員' }}</span>
                      <span class="text-xs text-gray-500">{{ formatDate(comment.created_at) }}</span>
                    </div>
                    <p class="text-gray-700">
                      {{ comment.content }}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </NModal>
</template>

<style scoped>
.post-detail-modal {
  max-height: 80vh;
  overflow-y: auto;
  background-color: #f9fafb;
}

.prose {
  font-size: 1rem;
  line-height: 1.75;
  color: #374151;
}

.prose p {
  margin-bottom: 1rem;
}

.prose img {
  max-width: 100%;
  height: auto;
  border-radius: 0.5rem;
  margin: 1.5rem 0;
}

.prose h1, .prose h2, .prose h3 {
  color: #111827;
  font-weight: 600;
  margin: 2rem 0 1rem;
}

.prose h1 {
  font-size: 2rem;
}

.prose h2 {
  font-size: 1.5rem;
}

.prose h3 {
  font-size: 1.25rem;
}

.prose ul, .prose ol {
  margin: 1rem 0;
  padding-left: 1.5rem;
}

.prose li {
  margin: 0.5rem 0;
}

.prose blockquote {
  border-left: 4px solid #e5e7eb;
  padding-left: 1rem;
  color: #6b7280;
  font-style: italic;
  margin: 1.5rem 0;
}

.prose code {
  background-color: #f3f4f6;
  padding: 0.2rem 0.4rem;
  border-radius: 0.25rem;
  font-size: 0.875em;
}

.prose pre {
  background-color: #1f2937;
  color: #f3f4f6;
  padding: 1rem;
  border-radius: 0.5rem;
  overflow-x: auto;
  margin: 1.5rem 0;
}
</style>

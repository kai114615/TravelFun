<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { NAvatar, NSpace, NCard, NMessageProvider, useMessage, NButton, NInput } from 'naive-ui';
import { storeToRefs } from 'pinia';
import { useUserStore } from '@/stores';
import { FORUM_API } from '@/utils/api';

const props = defineProps<{
  postId: number;
}>();

const emit = defineEmits(['comment-count-update']);

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
    const response = await FORUM_API.getComments(props.postId);
    if (response.data.status === 'success') {
      comments.value = response.data.data || [];
      // 發送評論數量更新事件
      emit('comment-count-update', comments.value.length);
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
  if (!loginStatus.value) {
    message.warning('請先登入後再發表評論');
    return;
  }

  if (!newComment.value.trim()) {
    message.warning('評論內容不能為空');
    return;
  }

  isSubmitting.value = true;
  try {
    const response = await FORUM_API.addComment(props.postId, newComment.value);
    if (response.data.status === 'success') {
      message.success('評論發表成功');
      newComment.value = '';
      await fetchComments(); // 重新獲取評論列表並更新數量
    } else {
      throw new Error(response.data.message || '發表評論失敗');
    }
  }
  catch (error: any) {
    console.error('發表評論失敗:', error);
    message.error(error.message || '發表評論失敗，請稍後再試');
  }
  finally {
    isSubmitting.value = false;
  }
};

// 刪除評論
const deleteComment = async (commentId: number) => {
  try {
    const response = await FORUM_API.deleteComment(commentId);
    if (response.data.status === 'success') {
      message.success('評論刪除成功');
      await fetchComments(); // 重新獲取評論列表並更新數量
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
      <NCard title="評論列表">
        <template v-if="comments.length">
          <div v-for="comment in comments" :key="comment.id" class="comment-item mb-4">
            <NSpace align="start">
              <NAvatar
                :src="getAvatarUrl(comment.author.avatar)"
                :fallback-src="'/images/member.jpg'"
                size="medium"
              />
              <div class="flex-grow">
                <div class="flex justify-between items-start">
                  <div>
                    <span class="font-bold">{{ comment.author.username }}</span>
                    <span class="text-gray-500 text-sm ml-2">{{ formatDate(comment.created_at) }}</span>
                  </div>
                  <NButton
                    v-if="canDeleteComment(comment)"
                    text
                    type="error"
                    @click="deleteComment(comment.id)"
                  >
                    刪除
                  </NButton>
                </div>
                <p class="mt-2 text-gray-700">{{ comment.content }}</p>
              </div>
            </NSpace>
          </div>
        </template>
        <template v-else>
          <div class="text-center text-gray-500 py-4">
            暫無評論，來發表第一條評論吧！
          </div>
        </template>
      </NCard>
    </div>
  </NMessageProvider>
</template>

<style scoped>
.comments-section {
  margin-top: 2rem;
}

.comment-item {
  padding: 1rem;
  border-bottom: 1px solid #eee;
}

.comment-item:last-child {
  border-bottom: none;
}
</style> 
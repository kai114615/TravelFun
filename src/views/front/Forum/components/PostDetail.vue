<script setup lang="ts">
import { ref, computed } from 'vue';
import { NButton, NInput, NModal, NCard, NIcon, useMessage } from 'naive-ui';
import { 
  FavoriteOutlined,
  FavoriteBorderOutlined,
  ShareOutlined,
  VisibilityOutlined,
  ChatBubbleOutlined,
  ThumbUpOutlined,
  ReplyOutlined,
  AccessTimeOutlined,
  ArrowBackOutlined
} from '@vicons/material';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores';
import { apiForumToggleLike, apiForumAddComment, apiForumDeleteComment } from '@/utils/api';

const router = useRouter();
const userStore = useUserStore();
const message = useMessage();

// 添加評論區域的 ref
const commentSection = ref(null);

// 判斷是否登入
const isLoggedIn = computed(() => userStore.loginStatus);

// 模擬文章數據
const post = ref({
  id: 1,
  type: '遊記',
  title: '【台北三天兩夜】跟著在地人吃喝玩樂，精華景點全攻略',
  content: `
    ## Day 1 - 台北車站周邊
    早上從台北車站出發，先到附近的早餐店吃個道地的蛋餅和豆漿。接著步行到二二八和平公園散步，欣賞公園內的歷史建築和紀念碑。

    ### 午餐推薦
    - 阜杭豆漿：必吃的燒餅油條
    - 老張牛肉麵：在地人推薦的好味道

    ## Day 2 - 信義區購物行程
    上午前往台北101，除了觀景台外，底下的食品街也很推薦。下午可以逛逛附近的新光三越和統一時代百貨。

    ### 晚餐推薦
    - 鼎泰豐：必吃的小籠包
    - 心齋橋：平價美食街

    ## Day 3 - 文青之旅
    早上到永康街散步，品嚐知名的芒果冰。下午前往華山1914文創園區，體驗台北的文創能量。

    ### 交通建議
    - 建議購買悠遊卡
    - 大眾運輸非常方便
    - 景點間可以步行或搭乘捷運
  `,
  postDate: '2024-01-10 10:45',
  views: 1239,
  likes: 156,
  author: {
    name: '背包客阿明',
    title: '旅遊達人',
    avatar: 'https://picsum.photos/201'
  },
  comments: [
    {
      id: 1,
      author: {
        name: '小茹看世界',
        title: '精選作者',
        avatar: 'https://picsum.photos/202'
      },
      content: '推薦的餐廳都很棒！特別是鼎泰豐，一定要先訂位才不會等太久。',
      postDate: '2024-01-10 11:30',
      likes: 25
    },
    {
      id: 2,
      author: {
        name: '老王遊台灣',
        title: '在地嚮導',
        avatar: 'https://picsum.photos/203'
      },
      content: '補充一下交通資訊：如果要去台北101，建議搭乘捷運信義線到台北101/世貿站下車，出站後走路約3分鐘就到了。',
      postDate: '2024-01-10 12:15',
      likes: 18
    }
  ]
});

// 新增評論相關功能
const newComment = ref('');
const isSubmitting = ref(false);
const showLoginModal = ref(false);

// 處理發表評論
const handleComment = async () => {
  if (!isLoggedIn.value) {
    showLoginModal.value = true;
    return;
  }

  if (!newComment.value.trim()) {
    message.warning('請輸入評論內容');
    return;
  }

  try {
    isSubmitting.value = true;
    const response = await apiForumAddComment(post.value.id, newComment.value);
    
    if (response.data.status === 'success') {
      // 將新評論添加到列表
      post.value.comments.unshift({
        id: response.data.data.id,
        content: newComment.value,
        author: {
          name: userStore.displayName,
          title: '會員',
          avatar: userStore.userInfo?.avatar || 'https://picsum.photos/205'
        },
        postDate: new Date().toLocaleString(),
        likes: 0
      });
      
      // 清空輸入框
      newComment.value = '';
      message.success('評論發表成功');
    }
  } catch (error) {
    console.error('發表評論失敗:', error);
  } finally {
    isSubmitting.value = false;
  }
};

// 處理刪除評論
const handleDeleteComment = async (commentId: number) => {
  try {
    const response = await apiForumDeleteComment(commentId);
    if (response.data.status === 'success') {
      // 從列表中移除該評論
      post.value.comments = post.value.comments.filter(comment => comment.id !== commentId);
    }
  } catch (error) {
    console.error('刪除評論失敗:', error);
  }
};

// 跳轉到登入頁面
const goToLogin = () => {
  router.push('/login');
  showLoginModal.value = false;
};

// 返回上一頁
const goBack = () => {
  router.back();
};

// 處理按讚
const handleLike = async () => {
  if (!isLoggedIn.value) {
    message.warning('請先登入後再按讚');
    return;
  }

  try {
    const response = await apiForumToggleLike(post.value.id);
    
    if (response.data.status === 'success') {
      // 使用後端返回的數據更新狀態
      post.value.is_liked = response.data.data.is_liked;
      post.value.likes = response.data.data.like_count;
      message.success(response.data.message);
    }
  } catch (error) {
    console.error('按讚失敗:', error);
    // 不需要顯示錯誤消息，因為 API 函數已經處理了
  }
};

// 添加跳轉到評論區域的方法
const scrollToComments = () => {
  const commentSection = document.getElementById('comment-section');
  if (commentSection) {
    commentSection.scrollIntoView({ 
      behavior: 'smooth',
      block: 'start'
    });
  }
};
</script>

<template>
  <div class="max-w-4xl mx-auto px-4 py-8">
    <!-- 返回按鈕 -->
    <div class="mb-6">
      <NButton
        secondary
        class="rounded-full !flex !items-center !gap-1 hover:bg-primary/5 transition-colors"
        @click="goBack"
      >
        <template #icon>
          <NIcon><ArrowBackOutlined /></NIcon>
        </template>
        返回討論區
      </NButton>
    </div>

    <!-- 文章內容 -->
    <div class="bg-white rounded-xl shadow-sm p-6 mb-8">
      <!-- 作者信息 -->
      <div class="flex items-center gap-4 mb-6">
        <img :src="post.author.avatar" :alt="post.author.name" class="w-12 h-12 rounded-full ring-2 ring-primary/20">
        <div>
          <div class="flex items-center gap-2">
            <span class="font-medium text-gray-800">{{ post.author.name }}</span>
            <span class="px-2 py-0.5 bg-primary/5 text-primary rounded-full text-xs">{{ post.author.title }}</span>
          </div>
          <div class="text-sm text-gray-500 mt-1">發表於 {{ post.postDate }}</div>
        </div>
      </div>

      <!-- 文章標題 -->
      <h1 class="text-2xl font-bold text-gray-800 mb-4">
        <span class="text-primary bg-primary/5 px-2 py-1 rounded-md text-lg mr-2">[{{ post.type }}]</span>
        {{ post.title }}
      </h1>

      <!-- 文章統計 -->
      <div class="flex items-center gap-4 text-sm text-gray-500 mb-6">
        <span class="flex items-center gap-1">
          <NIcon size="16"><VisibilityOutlined /></NIcon>
          {{ post.views }} 瀏覽
        </span>
        <span class="flex items-center gap-1">
          <NIcon size="16">
            <component :is="post.is_liked ? FavoriteOutlined : FavoriteBorderOutlined" />
          </NIcon>
          {{ post.likes }} 喜歡
        </span>
        <button 
          class="flex items-center gap-1 hover:text-primary transition-colors cursor-pointer"
          @click="scrollToComments"
        >
          <NIcon size="16"><ChatBubbleOutlined /></NIcon>
          {{ post.comments?.length || 0 }} 留言
        </button>
      </div>

      <!-- 文章內容 -->
      <div class="prose prose-lg max-w-none mb-8">
        <div class="markdown-body" v-html="post.content"></div>
      </div>

      <!-- 互動按鈕 -->
      <div class="flex items-center gap-4 border-t border-gray-100 pt-6">
        <NButton 
          :type="post.is_liked ? 'error' : 'default'" 
          ghost 
          class="rounded-full"
          @click="handleLike"
        >
          <template #icon>
            <NIcon>
              <component :is="post.is_liked ? FavoriteOutlined : FavoriteBorderOutlined" />
            </NIcon>
          </template>
          {{ post.is_liked ? '已喜歡' : '喜歡' }}
        </NButton>
        <NButton class="rounded-full">
          <template #icon>
            <NIcon><ShareOutlined /></NIcon>
          </template>
          分享
        </NButton>
      </div>
    </div>

    <!-- 留言區 -->
    <div ref="commentSection" id="comment-section" class="bg-white rounded-xl shadow-sm p-6">
      <h2 class="text-xl font-bold text-gray-800 mb-6">留言區 ({{ post.comments.length }})</h2>

      <!-- 發表留言 -->
      <div class="mb-8">
        <NInput
          v-model:value="newComment"
          type="textarea"
          placeholder="分享您的想法..."
          :rows="3"
          class="mb-4"
          :disabled="isSubmitting"
        />
        <NButton 
          type="primary" 
          @click="handleComment" 
          class="rounded-full"
          :loading="isSubmitting"
          :disabled="isSubmitting || !newComment.trim()"
        >
          {{ isLoggedIn ? '發表留言' : '請先登入' }}
        </NButton>
      </div>

      <!-- 留言列表 -->
      <div class="space-y-6">
        <div v-for="comment in post.comments" :key="comment.id" class="border-b border-gray-100 pb-6 last:border-0">
          <div class="flex items-start gap-4">
            <img :src="comment.author.avatar" :alt="comment.author.name" class="w-10 h-10 rounded-full">
            <div class="flex-1">
              <div class="flex items-center gap-2 mb-1">
                <span class="font-medium text-gray-800">{{ comment.author.name }}</span>
                <span class="px-2 py-0.5 bg-gray-100 text-gray-600 rounded-full text-xs">{{ comment.author.title }}</span>
              </div>
              <div class="text-gray-600 mb-2">{{ comment.content }}</div>
              <div class="flex items-center gap-4 text-sm text-gray-500">
                <span class="flex items-center gap-1">
                  <NIcon size="16"><AccessTimeOutlined /></NIcon>
                  {{ comment.postDate }}
                </span>
                <button class="flex items-center gap-1 hover:text-primary transition-colors">
                  <NIcon size="16"><ThumbUpOutlined /></NIcon>
                  {{ comment.likes }}
                </button>
                <button 
                  v-if="userStore.userInfo?.id === comment.author.id"
                  class="text-red-500 hover:text-red-600 transition-colors flex items-center gap-1"
                  @click="handleDeleteComment(comment.id)"
                >
                  <i class="fas fa-trash-alt"></i>
                  刪除
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 登入提示彈窗 -->
    <NModal v-model:show="showLoginModal">
      <NCard
        style="width: 400px"
        title="需要登入"
        :bordered="false"
        size="huge"
        role="dialog"
        aria-modal="true"
      >
        <div class="text-center">
          <p class="mb-6">請先登入後再發表留言</p>
          <div class="flex justify-center gap-4">
            <NButton type="primary" @click="goToLogin">
              前往登入
            </NButton>
            <NButton @click="showLoginModal = false">
              取消
            </NButton>
          </div>
        </div>
      </NCard>
    </NModal>
  </div>
</template>

<style scoped>
.markdown-body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial,
    'Noto Sans', sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol',
    'Noto Color Emoji';
}

.markdown-body h2 {
  font-size: 1.5em;
  margin-top: 1.5em;
  margin-bottom: 0.5em;
  font-weight: 600;
  color: #2d3748;
}

.markdown-body h3 {
  font-size: 1.25em;
  margin-top: 1.5em;
  margin-bottom: 0.5em;
  font-weight: 600;
  color: #2d3748;
}

.markdown-body ul {
  margin-top: 0.5em;
  margin-bottom: 1em;
  padding-left: 1.5em;
  list-style-type: disc;
}

.markdown-body li {
  margin: 0.25em 0;
  color: #4a5568;
}
</style> 
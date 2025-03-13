<script setup lang="ts">
import { computed, ref } from 'vue';
import { NButton, NCard, NIcon, NInput, NModal, useMessage } from 'naive-ui';
import {
  AccessTimeOutlined,
  ArrowBackOutlined,
  ChatBubbleOutlined,
  FavoriteBorderOutlined,
  FavoriteOutlined,
  ShareOutlined,
  ThumbUpOutlined,
  VisibilityOutlined,
} from '@vicons/material';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores';
import { apiForumAddComment, apiForumDeleteComment, apiForumToggleLike } from '@/utils/api';
import { marked } from 'marked';

// 設置marked選項
marked.setOptions({
  breaks: true,
  headerIds: true,
  gfm: true,
});

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
    avatar: 'https://picsum.photos/201',
  },
  comments: [
    {
      id: 1,
      author: {
        name: '小茹看世界',
        title: '精選作者',
        avatar: 'https://picsum.photos/202',
      },
      content: '推薦的餐廳都很棒！特別是鼎泰豐，一定要先訂位才不會等太久。',
      postDate: '2024-01-10 11:30',
      likes: 25,
    },
    {
      id: 2,
      author: {
        name: '老王遊台灣',
        title: '在地嚮導',
        avatar: 'https://picsum.photos/203',
      },
      content: '補充一下交通資訊：如果要去台北101，建議搭乘捷運信義線到台北101/世貿站下車，出站後走路約3分鐘就到了。',
      postDate: '2024-01-10 12:15',
      likes: 18,
    },
  ],
});

// 新增評論相關功能
const newComment = ref('');
const isSubmitting = ref(false);
const showLoginModal = ref(false);

// 將Markdown轉換為HTML的方法
function renderMarkdown(content: string) {
  if (!content) return '';
  
  // 預處理：處理非標準Markdown文本 (確保換行生效)
  let processedContent = content
    // 基本清理 - 移除多餘的空格，確保首尾沒有多餘空行
    .trim()
    // 將連續的空格替換為單個空格
    .replace(/ {2,}/g, ' ')
    // 處理帶有emoji(•)的Day格式
    .replace(/•\s*Day\s*(\d+)\s*[:：]\s*([^•\n]+)/g, '\n\n## Day $1：$2')
    // 將 "Day N:" 或 "Day N :" 格式轉換為Markdown標題
    .replace(/Day\s*(\d+)\s*[:：]/g, '\n\n## Day $1：')
    // 處理其他常見的行程標題格式
    .replace(/([^a-zA-Z0-9\s]*)(\d+)\s*[:：]\s*([^a-zA-Z0-9\s]*)/g, '\n\n## $1$2：$3')
    // 處理純文本段落 - 將以中文句號、英文句號結尾的句子視為段落結尾
    .replace(/([。.!！?？])\s*/g, '$1\n\n')
    // 確保圓點符號前後有空格，被識別為列表項
    .replace(/([^-])•\s*/g, '$1\n- ')
    // 將含有emoji的內容轉換為列表項
    .replace(/([^-])([\u{1F300}-\u{1F6FF}|[\u{2600}-\u{26FF}|\u2022])\s+([^\n]+)/gu, '$1\n- $2 $3')
    // 尋找類似"台北 - 高雄"這樣的格式，將其視為子標題
    .replace(/([a-zA-Z\u4e00-\u9fa5]+)\s*[-－]\s*([a-zA-Z\u4e00-\u9fa5]+)/g, function(match) {
      // 避免處理已經是標題的內容
      if (match.startsWith('#')) return match;
      return `\n\n### ${match}`;
    })
    // 識別emoji作為列表項
    .replace(/\n([\u{1F300}-\u{1F6FF}|[\u{2600}-\u{26FF}])\s*/gu, '\n\n- $1 ')
    // 識別行程亮點部分（如"行程亮點："）作為項目
    .replace(/([^\n]+)[:：]\s*([^\n]*)/g, function(match, p1, p2) {
      // 避免過度匹配Day 1：這樣的格式
      if (p1.match(/Day \d+/i)) return match;
      
      // 處理旅遊行程常見標籤
      const travelLabels = ['行程亮點', '交通方式', '美食推薦', '住宿推薦', '完美收尾', '特色體驗', '注意事項'];
      
      // 檢查是否為旅遊行程標籤
      const isLabel = travelLabels.some(label => p1.includes(label));
      
      // 如果是旅遊行程標籤
      if (isLabel) {
        // 處理有逗號或頓號分隔的項目清單
        if (p2.includes('、') || p2.includes('，') || p2.includes(',')) {
          const items = p2.split(/[、，,]/);
          const listItems = items.map(item => `- ${item.trim()}`).join('\n');
          return `\n\n**${p1}**：\n${listItems}`;
        }
        return `\n\n**${p1}**：${p2}`;
      }
      
      // 如果第一部分看起來像標題
      if (p1.length < 20 && !p1.includes('http')) {
        return `\n\n### ${p1}：\n${p2}`;
      }
      return match;
    })
    // 處理交通方式、行程建議等特定格式
    .replace(/交通方式\s*[:：]\s*/g, '\n\n**交通方式**：')
    .replace(/住宿推薦\s*[:：]\s*/g, '\n\n**住宿推薦**：')
    .replace(/美食推薦\s*[:：]\s*/g, '\n\n**美食推薦**：')
    .replace(/行程亮點\s*[:：]\s*/g, '\n\n**行程亮點**：')
    .replace(/特色體驗\s*[:：]\s*/g, '\n\n**特色體驗**：')
    .replace(/完美收尾\s*[:：]\s*/g, '\n\n**完美收尾**：')
    // 先將所有單個換行符替換為br標記佔位符
    .replace(/\n(?!\n)/g, '\n<br-placeholder>\n')
    // 兩個連續換行符表示段落
    .replace(/\n\n+/g, '\n\n')
    // 最後處理 - 移除重複的換行和空格
    .replace(/\n{3,}/g, '\n\n');
  
  // 使用marked轉換為HTML
  let html = marked(processedContent);
  
  // 後處理：將佔位符替換為實際的<br>標籤
  html = html.replace(/<br-placeholder>/g, '<br>');
  
  // 如果沒有任何HTML標籤，表示可能是純文本，添加段落標籤
  if (!html.includes('<h') && !html.includes('<p') && !html.includes('<ul')) {
    html = '<p>' + html.replace(/\n\n/g, '</p><p>').replace(/\n/g, '<br>') + '</p>';
  }
  
  return html;
}

// 將Markdown內容轉換為HTML
const renderedContent = computed(() => {
  return renderMarkdown(post.value.content);
});

// 處理發表評論
async function handleComment() {
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
          avatar: userStore.userInfo?.avatar || 'https://picsum.photos/205',
        },
        postDate: new Date().toLocaleString(),
        likes: 0,
      });

      // 清空輸入框
      newComment.value = '';
      message.success('評論發表成功');
    }
  }
  catch (error) {
    console.error('發表評論失敗:', error);
  }
  finally {
    isSubmitting.value = false;
  }
}

// 處理刪除評論
async function handleDeleteComment(commentId: number) {
  try {
    const response = await apiForumDeleteComment(commentId);
    if (response.data.status === 'success') {
      // 從列表中移除該評論
      post.value.comments = post.value.comments.filter(comment => comment.id !== commentId);
    }
  }
  catch (error) {
    console.error('刪除評論失敗:', error);
  }
}

// 跳轉到登入頁面
function goToLogin() {
  router.push('/login');
  showLoginModal.value = false;
}

// 返回上一頁
function goBack() {
  router.back();
}

// 處理按讚
async function handleLike() {
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
  }
  catch (error) {
    console.error('按讚失敗:', error);
    // 不需要顯示錯誤消息，因為 API 函數已經處理了
  }
}

// 添加跳轉到評論區域的方法
function scrollToComments() {
  const commentSection = document.getElementById('comment-section');
  if (commentSection) {
    commentSection.scrollIntoView({
      behavior: 'smooth',
      block: 'start',
    });
  }
}
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
          <div class="text-sm text-gray-500 mt-1">
            發表於 {{ post.postDate }}
          </div>
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
          <NIcon size="16">
            <ChatBubbleOutlined />
          </NIcon>
          {{ post.comments?.length || 0 }} 留言
        </button>
      </div>

      <!-- 文章內容 -->
      <div class="prose prose-lg max-w-none mb-8">
        <div class="markdown-body" v-html="renderedContent" />
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
    <div id="comment-section" ref="commentSection" class="bg-white rounded-xl shadow-sm p-6">
      <h2 class="text-xl font-bold text-gray-800 mb-6">
        留言區 ({{ post.comments.length }})
      </h2>

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
          class="rounded-full"
          :loading="isSubmitting"
          :disabled="isSubmitting || !newComment.trim()"
          @click="handleComment"
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
              <div class="text-gray-600 mb-2">
                {{ comment.content }}
              </div>
              <div class="flex items-center gap-4 text-sm text-gray-500">
                <span class="flex items-center gap-1">
                  <NIcon size="16"><AccessTimeOutlined /></NIcon>
                  {{ comment.postDate }}
                </span>
                <button class="flex items-center gap-1 hover:text-primary transition-colors">
                  <NIcon size="16">
                    <ThumbUpOutlined />
                  </NIcon>
                  {{ comment.likes }}
                </button>
                <button
                  v-if="userStore.userInfo?.id === comment.author.id"
                  class="text-red-500 hover:text-red-600 transition-colors flex items-center gap-1"
                  @click="handleDeleteComment(comment.id)"
                >
                  <i class="fas fa-trash-alt" />
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
          <p class="mb-6">
            請先登入後再發表留言
          </p>
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

/* 自定義樣式處理行程格式 */
:deep(.custom-markdown strong) {
  font-weight: 600;
  color: #1a202c;
  background-color: rgba(254, 215, 170, 0.2);
  padding: 0.1em 0.3em;
  border-radius: 3px;
}

/* 為旅遊行程的關鍵字標記（如交通方式、行程亮點等）添加特殊樣式 */
:deep(.custom-markdown) strong:first-child {
  display: inline-block;
  color: #0369a1;
  background-color: #f0f9ff;
  padding: 0.2em 0.5em;
  border-radius: 4px;
  margin-bottom: 0.5em;
  border-left: 3px solid #0284c7;
}

/* Day標題樣式增強 */
:deep(.custom-markdown h2) {
  position: relative;
  font-size: 1.6em;
  margin-top: 2.5em;
  margin-bottom: 1em;
  font-weight: 600;
  color: #1e40af; /* 深藍色 */
  padding: 0.5em 0;
  border-bottom: 2px solid #dbeafe;
  text-align: left;
  background-color: #f8fafc;
  padding-left: 0.8em;
  border-radius: 6px 6px 0 0;
}
</style>

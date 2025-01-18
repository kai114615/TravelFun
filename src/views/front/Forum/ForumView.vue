<script setup lang="ts">
import { ref, computed } from 'vue';
import Banner from '@/components/Banner.vue';
import { NButton, NIcon, NCarousel, NInput, NSelect, NDatePicker, NModal, NForm, NFormItem, NCard } from 'naive-ui';
import { 
  PersonOutlined,
  EditOutlined,
  StarOutlined,
  NewReleasesOutlined,
  LocalFireDepartmentOutlined,
  VisibilityOutlined,
  ChatBubbleOutlined,
  CategoryOutlined,
  NavigateNextOutlined,
  GroupsOutlined,
  LocalOfferOutlined,
  SearchOutlined,
  SortOutlined,
  FilterAltOutlined,
  AddOutlined
} from '@vicons/material';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores';

const router = useRouter();
const userStore = useUserStore();
const isLoggedIn = computed(() => userStore.loginStatus);

const title = ref('討論區');
const activeCategory = ref('國內旅遊');

// 分類列表
const categories = [
  { name: '國內旅遊', count: 328 },
  { name: '旅遊規劃', count: 156 },
  { name: '行程分享', count: 245 },
  { name: '閒聊中心', count: 89 }
];

// 頂部按鈕列表
const topButtons = [
  '國內旅遊',
  '旅遊規劃',
  '行程分享',
  '閒聊中心'
];

// 文章列表
const posts = ref([
  {
    type: '遊記',
    title: '【台北三天兩夜】跟著在地人吃喝玩樂，精華景點全攻略',
    isNew: true,
    postDate: '2024-01-10 10:45',
    lastReply: '12分鐘前',
    views: 1239,
    replies: 124,
    author: {
      name: '背包客阿明',
      title: '旅遊達人',
      avatar: 'https://picsum.photos/201'
    }
  },
  {
    type: '規劃',
    title: '新手規劃環島行程，需要注意什麼？',
    isNew: true,
    postDate: '2024-01-10 09:30',
    lastReply: '25分鐘前',
    views: 856,
    replies: 67,
    author: {
      name: '小茹看世界',
      title: '精選作者',
      avatar: 'https://picsum.photos/202'
    }
  },
  {
    type: '分享',
    title: '2024春節花蓮行程分享，包含訂房及交通建議',
    isNew: false,
    postDate: '2024-01-09 15:20',
    lastReply: '1小時前',
    views: 723,
    replies: 45,
    author: {
      name: '老王遊台灣',
      title: '在地嚮導',
      avatar: 'https://picsum.photos/203'
    }
  },
  {
    type: '閒聊',
    title: '大家最喜歡的台灣小吃是什麼？來分享一下！',
    isNew: false,
    postDate: '2024-01-09 14:15',
    lastReply: '2小時前',
    views: 512,
    replies: 93,
    author: {
      name: '美食探險家',
      title: '美食專家',
      avatar: 'https://picsum.photos/204'
    }
  }
]);

// 版務人員
const moderator = {
  avatar: 'https://picsum.photos/200',
  name: '旅遊顧問',
  status: '線上'
};

// 活躍作者
const activeAuthors = [
  {
    avatar: 'https://picsum.photos/201',
    name: '背包客阿明',
    title: '旅遊達人'
  },
  {
    avatar: 'https://picsum.photos/202',
    name: '小茹看世界',
    title: '精選作者'
  },
  {
    avatar: 'https://picsum.photos/203',
    name: '老王遊台灣',
    title: '在地嚮導'
  }
];

// 輪播圖片列表
const carouselImages = [
  {
    url: 'https://images.pexels.com/photos/5059013/pexels-photo-5059013.jpeg',
    title: '阿里山日出',
    description: '雲海、森林鐵路與晨曦，令人嚮往的日出勝地'
  },
  {
    url: 'https://images.pexels.com/photos/2478248/pexels-photo-2478248.jpeg',
    title: '台北101',
    description: '台灣地標性建築，象徵經濟繁榮與進步'
  },
  {
    url: 'https://images.pexels.com/photos/5824901/pexels-photo-5824901.jpeg',
    title: '太魯閣國家公園',
    description: '壯麗的峽谷與清澈溪流，台灣最著名的國家公園'
  },
  {
    url: 'https://images.pexels.com/photos/5827881/pexels-photo-5827881.jpeg',
    title: '日月潭風光',
    description: '台灣最大的天然湖泊，山水相映的自然美景'
  },
  {
    url: 'https://images.pexels.com/photos/5827896/pexels-photo-5827896.jpeg',
    title: '九份老街',
    description: '充滿懷舊氛圍的山城，展現台灣傳統文化'
  },
  {
    url: 'https://images.pexels.com/photos/1835927/pexels-photo-1835927.jpeg',
    title: '墾丁海灘',
    description: '陽光、沙灘與碧海，台灣最南端的度假天堂'
  },
  {
    url: 'https://images.pexels.com/photos/5827912/pexels-photo-5827912.jpeg',
    title: '陽明山國家公園',
    description: '溫泉與花季的天堂，台北後花園'
  },
  {
    url: 'https://images.pexels.com/photos/5827920/pexels-photo-5827920.jpeg',
    title: '清境農場',
    description: '青青草原與綿羊群，台灣的小瑞士'
  }
];

// 跳轉到文章詳情頁
const goToPostDetail = (postId: number) => {
  router.push(`/forum/post/${postId}`);
};

// 搜尋關鍵字
const searchKeyword = ref('');

// 排序選項
const sortOptions = [
  { label: '最新發布', value: 'newest' },
  { label: '最多觀看', value: 'most-viewed' },
  { label: '最多回覆', value: 'most-replied' },
  { label: '最多喜歡', value: 'most-liked' }
];
const currentSort = ref('newest');

// 篩選選項
const filterOptions = ref({
  dateRange: null,
  category: null,
  author: null
});

// 發文表單
const showPostModal = ref(false);
const newPost = ref({
  title: '',
  content: '',
  type: '',
  tags: []
});

// 處理搜尋
const handleSearch = () => {
  // TODO: 實作搜尋邏輯
  console.log('搜尋關鍵字:', searchKeyword.value);
};

// 處理排序
const handleSort = (value: string) => {
  currentSort.value = value;
  // TODO: 實作排序邏輯
};

// 處理篩選
const handleFilter = () => {
  // TODO: 實作篩選邏輯
  console.log('篩選條件:', filterOptions.value);
};

// 處理發文
const handlePost = () => {
  // TODO: 實作發文邏輯
  console.log('新文章:', newPost.value);
  showPostModal.value = false;
};

// 處理發文按鈕點擊
const handlePostButtonClick = () => {
  if (!isLoggedIn.value) {
    showLoginModal.value = true;
    return;
  }
  showPostModal.value = true;
};

// 登入提示彈窗
const showLoginModal = ref(false);

// 跳轉到註冊頁面
const goToRegister = () => {
  router.push('/register');
  showLoginModal.value = false;
};
</script>

<template>
  <main class="bg-gradient-to-b from-gray-50 to-white min-h-screen">
    <!-- 輪播Banner -->
    <div class="relative h-[400px]">
      <NCarousel
        autoplay
        :interval="5000"
        dot-type="line"
        effect="fade"
        class="h-full"
      >
        <div
          v-for="(image, index) in carouselImages"
          :key="index"
          class="h-full relative"
        >
          <img
            :src="image.url"
            :alt="image.title"
            class="w-full h-full object-cover"
          >
          <div class="absolute inset-0 bg-black/30 flex items-center justify-center">
            <div class="text-center text-white">
              <h1 class="text-4xl font-bold mb-4">{{ title }}</h1>
              <p class="text-xl opacity-90">分享您的旅遊經驗</p>
            </div>
          </div>
        </div>
      </NCarousel>
    </div>

    <div class="max-w-7xl mx-auto px-4 py-8">
      <!-- 頂部分類按鈕 -->
      <div class="flex flex-wrap gap-3 mb-8">
        <NButton
          v-for="btn in topButtons"
          :key="btn"
          :type="activeCategory === btn ? 'primary' : 'default'"
          secondary
          class="!rounded-full px-6 transition-all duration-300 hover:transform hover:scale-105"
          :class="{ 'shadow-md': activeCategory === btn }"
          @click="activeCategory = btn"
        >
          {{ btn }}
        </NButton>
      </div>

      <div class="flex flex-col lg:flex-row gap-6">
        <!-- 左側分類列表 -->
        <div class="w-full lg:w-64 flex-shrink-0">
          <div class="bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow duration-300 p-5">
            <h3 class="font-semibold text-gray-800 mb-4 text-lg flex items-center gap-2">
              <NIcon size="20"><CategoryOutlined /></NIcon>
              討論分類
            </h3>
            <ul class="space-y-2.5">
              <li v-for="category in categories" :key="category.name">
                <a
                  href="#"
                  class="flex items-center justify-between p-3 rounded-lg transition-all duration-300"
                  :class="{ 
                    'bg-primary/5 text-primary font-medium': category.name === activeCategory,
                    'text-gray-600 hover:bg-gray-50': category.name !== activeCategory
                  }"
                >
                  <span>{{ category.name }}</span>
                  <span class="px-2.5 py-1 rounded-full text-xs" :class="{
                    'bg-primary/10 text-primary': category.name === activeCategory,
                    'bg-gray-100 text-gray-500': category.name !== activeCategory
                  }">{{ category.count }}</span>
                </a>
              </li>
            </ul>
          </div>

          <!-- 快速導覽 -->
          <div class="bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow duration-300 p-5 mt-6">
            <h3 class="font-semibold text-gray-800 mb-4 text-lg flex items-center gap-2">
              <NIcon size="20"><NavigateNextOutlined /></NIcon>
              快速導覽
            </h3>
            <div class="space-y-2 text-sm text-gray-600">
              <div class="flex items-center gap-2">
                <span class="w-2 h-2 rounded-full bg-green-500"></span>
                <span>【遊記】分享旅遊體驗</span>
              </div>
              <div class="flex items-center gap-2">
                <span class="w-2 h-2 rounded-full bg-blue-500"></span>
                <span>【規劃】行程規劃討論</span>
              </div>
              <div class="flex items-center gap-2">
                <span class="w-2 h-2 rounded-full bg-yellow-500"></span>
                <span>【分享】景點美食推薦</span>
              </div>
              <div class="flex items-center gap-2">
                <span class="w-2 h-2 rounded-full bg-purple-500"></span>
                <span>【閒聊】輕鬆話題交流</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 中間主要內容區 -->
        <div class="flex-1">
          <div class="bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow duration-300">
            <!-- 功能按鈕區 -->
            <div class="border-b border-gray-100 p-5">
              <div class="flex flex-col gap-4">
                <!-- 搜尋和排序區 -->
                <div class="flex items-center justify-between">
                  <div class="flex gap-3 flex-1">
                    <NInput
                      v-model:value="searchKeyword"
                      placeholder="搜尋文章..."
                      class="max-w-xs"
                    >
                      <template #prefix>
                        <NIcon><SearchOutlined /></NIcon>
                      </template>
                    </NInput>
                    <NSelect
                      v-model:value="currentSort"
                      :options="sortOptions"
                      class="w-32"
                    >
                      <template #prefix>
                        <NIcon><SortOutlined /></NIcon>
                      </template>
                    </NSelect>
                  </div>
                  <NButton type="primary" secondary class="rounded-full px-6" strong @click="handlePostButtonClick">
                    <div class="flex items-center gap-2">
                      <NIcon><AddOutlined /></NIcon>
                      發表新主題
                    </div>
                  </NButton>
                </div>
                
                <!-- 篩選區 -->
                <div class="flex items-center gap-4">
                  <NDatePicker
                    v-model:value="filterOptions.dateRange"
                    type="daterange"
                    clearable
                    class="w-64"
                    placeholder="選擇日期範圍"
                  />
                  <NSelect
                    v-model:value="filterOptions.category"
                    :options="categories.map(c => ({ label: c.name, value: c.name }))"
                    placeholder="選擇分類"
                    clearable
                    class="w-32"
                  />
                  <NButton size="small" class="rounded-full px-5" @click="handleFilter">
                    <template #icon>
                      <NIcon><FilterAltOutlined /></NIcon>
                    </template>
                    篩選
                  </NButton>
                </div>
              </div>
            </div>

            <!-- 文章列表 -->
            <div class="divide-y divide-gray-100">
              <div
                v-for="(post, index) in posts"
                :key="index"
                class="p-5 hover:bg-gray-50/70 transition-colors duration-300"
              >
                <div class="flex items-start justify-between">
                  <div class="flex-1">
                    <div class="flex items-center gap-3 mb-2">
                      <img :src="post.author.avatar" :alt="post.author.name" class="w-8 h-8 rounded-full ring-1 ring-gray-200">
                      <div>
                        <div class="flex items-center gap-2">
                          <span class="font-medium text-gray-800">{{ post.author.name }}</span>
                          <span class="px-2 py-0.5 bg-gray-100 text-gray-600 rounded text-xs">{{ post.author.title }}</span>
                        </div>
                      </div>
                    </div>
                    <h3 class="text-lg font-medium mb-2 flex items-center gap-2">
                      <span class="text-primary bg-primary/5 px-2 py-0.5 rounded-md text-sm">[{{ post.type }}]</span>
                      <a 
                        href="#" 
                        class="text-gray-800 hover:text-primary transition-colors duration-300"
                        @click.prevent="goToPostDetail(index + 1)"
                      >
                        {{ post.title }}
                      </a>
                      <span v-if="post.isNew" class="bg-red-50 text-red-500 text-xs px-2 py-0.5 rounded-full">NEW</span>
                    </h3>
                    <div class="text-sm text-gray-500 flex items-center gap-2">
                      <span>發表於 {{ post.postDate }}</span>
                      <span class="w-1 h-1 rounded-full bg-gray-300"></span>
                      <span>最後回覆 {{ post.lastReply }}</span>
                    </div>
                  </div>
                  <div class="text-right space-y-1">
                    <div class="text-sm text-gray-500 flex items-center justify-end gap-1">
                      <NIcon size="16"><VisibilityOutlined /></NIcon>
                      {{ post.views }}
                    </div>
                    <div class="text-sm text-gray-500 flex items-center justify-end gap-1">
                      <NIcon size="16"><ChatBubbleOutlined /></NIcon>
                      {{ post.replies }}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 分頁 -->
            <div class="p-5 border-t border-gray-100">
              <div class="flex justify-between items-center">
                <div class="flex gap-2">
                  <NButton size="small" type="primary" class="rounded-lg min-w-[32px]">1</NButton>
                  <NButton size="small" class="rounded-lg min-w-[32px]">2</NButton>
                  <NButton size="small" class="rounded-lg min-w-[32px]">3</NButton>
                  <NButton size="small" class="rounded-lg min-w-[32px]">4</NButton>
                  <span class="w-8 h-8 flex items-center justify-center text-gray-400">...</span>
                  <NButton size="small" class="rounded-lg min-w-[32px]">42</NButton>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 右側信息欄 -->
        <div class="w-full lg:w-80 flex-shrink-0 space-y-6">
          <!-- 版務人員 -->
          <div class="bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow duration-300 p-5">
            <h3 class="font-semibold text-gray-800 mb-4 text-lg flex items-center gap-2">
              <NIcon size="20"><PersonOutlined /></NIcon>
              版務人員
            </h3>
            <div class="flex items-center gap-4">
              <img :src="moderator.avatar" :alt="moderator.name" class="w-12 h-12 rounded-full ring-2 ring-primary/20">
              <div>
                <div class="font-medium text-gray-800">{{ moderator.name }}</div>
                <div class="text-sm mt-1">
                  <span class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-primary bg-primary/5">
                    <span class="w-1.5 h-1.5 rounded-full bg-primary"></span>
                    {{ moderator.status }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- 活躍作者 -->
          <div class="bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow duration-300 p-5">
            <h3 class="font-semibold text-gray-800 mb-4 text-lg flex items-center gap-2">
              <NIcon size="20"><GroupsOutlined /></NIcon>
              本版近期活躍作者
            </h3>
            <div class="space-y-5">
              <div v-for="author in activeAuthors" :key="author.name" class="flex items-center gap-4 p-2 rounded-lg hover:bg-gray-50 transition-colors duration-300">
                <img :src="author.avatar" :alt="author.name" class="w-12 h-12 rounded-full ring-2 ring-gray-100">
                <div>
                  <div class="font-medium text-gray-800">{{ author.name }}</div>
                  <div class="text-sm text-gray-500 mt-0.5">{{ author.title }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- 熱門標籤 -->
          <div class="bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow duration-300 p-5">
            <h3 class="font-semibold text-gray-800 mb-4 text-lg flex items-center gap-2">
              <NIcon size="20"><LocalOfferOutlined /></NIcon>
              熱門標籤
            </h3>
            <div class="flex flex-wrap gap-2">
              <span class="px-3 py-1 bg-gray-100 text-gray-600 rounded-full text-sm hover:bg-gray-200 cursor-pointer transition-colors duration-300">#台北美食</span>
              <span class="px-3 py-1 bg-gray-100 text-gray-600 rounded-full text-sm hover:bg-gray-200 cursor-pointer transition-colors duration-300">#環島旅行</span>
              <span class="px-3 py-1 bg-gray-100 text-gray-600 rounded-full text-sm hover:bg-gray-200 cursor-pointer transition-colors duration-300">#花蓮景點</span>
              <span class="px-3 py-1 bg-gray-100 text-gray-600 rounded-full text-sm hover:bg-gray-200 cursor-pointer transition-colors duration-300">#親子遊</span>
              <span class="px-3 py-1 bg-gray-100 text-gray-600 rounded-full text-sm hover:bg-gray-200 cursor-pointer transition-colors duration-300">#自由行</span>
              <span class="px-3 py-1 bg-gray-100 text-gray-600 rounded-full text-sm hover:bg-gray-200 cursor-pointer transition-colors duration-300">#住宿推薦</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </main>

  <!-- 發文彈窗 -->
  <NModal v-model:show="showPostModal" style="width: 600px">
    <NCard
      title="發表新主題"
      :bordered="false"
      size="huge"
      role="dialog"
      aria-modal="true"
    >
      <NForm>
        <NFormItem label="文章分類">
          <NSelect
            v-model:value="newPost.type"
            :options="categories.map(c => ({ label: c.name, value: c.name }))"
            placeholder="請選擇分類"
          />
        </NFormItem>
        <NFormItem label="文章標題">
          <NInput v-model:value="newPost.title" placeholder="請輸入標題" />
        </NFormItem>
        <NFormItem label="文章內容">
          <NInput
            v-model:value="newPost.content"
            type="textarea"
            placeholder="請輸入內容"
            :rows="6"
          />
        </NFormItem>
        <NFormItem label="標籤">
          <NSelect
            v-model:value="newPost.tags"
            multiple
            placeholder="請選擇標籤"
            :options="[
              { label: '台北美食', value: 'taipei-food' },
              { label: '環島旅行', value: 'round-island' },
              { label: '花蓮景點', value: 'hualien' },
              { label: '親子遊', value: 'family' },
              { label: '自由行', value: 'free-travel' },
              { label: '住宿推薦', value: 'accommodation' }
            ]"
          />
        </NFormItem>
      </NForm>
      <template #footer>
        <div class="flex justify-end gap-4">
          <NButton @click="showPostModal = false">取消</NButton>
          <NButton type="primary" @click="handlePost">發表</NButton>
        </div>
      </template>
    </NCard>
  </NModal>

  <!-- 登入提示彈窗 -->
  <NModal v-model:show="showLoginModal" style="width: 400px">
    <NCard
      title="需要註冊"
      :bordered="false"
      size="huge"
      role="dialog"
      aria-modal="true"
    >
      <div class="text-center">
        <p class="mb-6">發表文章需要先註冊成為會員</p>
        <div class="flex justify-center gap-4">
          <NButton type="primary" @click="goToRegister">
            立即註冊
          </NButton>
          <NButton @click="showLoginModal = false">
            取消
          </NButton>
        </div>
      </div>
    </NCard>
  </NModal>
</template>

<style scoped>
.text-primary {
  color: var(--primary-color);
}

.bg-primary {
  background-color: var(--primary-color);
}

.border-primary {
  border-color: var(--primary-color);
}

.hover\:text-primary:hover {
  color: var(--primary-color);
}

.hover\:bg-primary:hover {
  background-color: var(--primary-color);
}

.ring-primary {
  --tw-ring-color: var(--primary-color);
}

/* 自定義漸變背景 */
.bg-primary\/5 {
  background-color: rgba(var(--primary-color-rgb), 0.05);
}

.bg-primary\/10 {
  background-color: rgba(var(--primary-color-rgb), 0.1);
}

/* 添加平滑過渡效果 */
.transition-all {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 300ms;
}

/* 卡片懸浮效果 */
.hover\:shadow-md {
  --tw-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  box-shadow: var(--tw-ring-offset-shadow, 0 0 #0000), var(--tw-ring-shadow, 0 0 #0000), var(--tw-shadow);
}

/* 圓角按鈕樣式 */
.rounded-full {
  border-radius: 9999px;
}

/* 標籤樣式 */
.rounded-lg {
  border-radius: 0.5rem;
}
</style> 
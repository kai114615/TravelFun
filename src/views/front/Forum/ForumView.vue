<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores';
import Banner from '@/components/Banner.vue';
import { 
  AddOutlined,
  CategoryOutlined,
  ChatBubbleOutlined,
  EditOutlined,
  FilterAltOutlined,
  GroupsOutlined,
  LocalFireDepartmentOutlined,
  LocalOfferOutlined,
  NavigateNextOutlined,
  NewReleasesOutlined,
  PersonOutlined,
  SearchOutlined,
  SortOutlined,
  StarOutlined,
  VisibilityOutlined,
} from '@vicons/material';
import { 
  NButton, 
  NCard, 
  NCarousel, 
  NDatePicker, 
  NForm, 
  NFormItem, 
  NIcon, 
  NInput, 
  NModal, 
  NSelect, 
  NSwitch, 
  useMessage,
} from 'naive-ui';

const router = useRouter();
const userStore = useUserStore();
const isLoggedIn = computed(() => userStore.loginStatus);
const message = useMessage();

const title = ref('討論區');
const activeCategory = ref('國內旅遊');

// 分類列表
const categories = ref([]);

// 頂部按鈕列表
const topButtons = ref([]);

// 文章列表
const posts = ref([]);
const isLoading = ref(false);

// 版務人員
const moderator = ref({
  avatar: '',
  name: '',
  status: ''
});

// 活躍作者
const activeAuthors = ref([]);

// 分類選項
const categoryOptions = ref([]);

// 標籤列表
const tags = ref([]);
const selectedTags = ref([]);

// 加載分類列表
const loadCategories = async () => {
  try {
    console.log('開始載入分類列表...');
    const response = await axios.get('http://localhost:8000/api/public/categories/', {
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    console.log('分類列表響應:', response.data);
    
    if (response.data && response.data.status === 'success' && Array.isArray(response.data.data)) {
      // 確保每個分類都有必要的欄位
      const validCategories = response.data.data.filter(category => 
        category && typeof category.id === 'number' && typeof category.name === 'string'
      );
      
      if (validCategories.length === 0) {
        console.error('沒有有效的分類數據');
        message.error('無法載入分類列表');
        return;
      }

      categoryOptions.value = validCategories.map(category => ({
        label: category.name,
        value: category.id,
        description: category.description || '',
        post_count: category.post_count || 0
      }));
      
      categories.value = categoryOptions.value;
      topButtons.value = categories.value.map(c => c.label);
      
      console.log('分類列表已更新:', categoryOptions.value);
    } else {
      console.error('無效的分類資料格式:', response.data);
      message.error('分類資料格式錯誤');
      categoryOptions.value = [];
      categories.value = [];
      topButtons.value = [];
    }
  } catch (error) {
    console.error('載入分類列表失敗:', error);
    console.error('錯誤詳情:', {
      message: error.message,
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data
    });
    message.error('載入分類列表失敗');
    categoryOptions.value = [];
    categories.value = [];
    topButtons.value = [];
  }
};

// 加載文章列表
const loadPosts = async () => {
  try {
    console.log('開始加載文章列表...');
    isLoading.value = true;
    
    const headers = {
      'Content-Type': 'application/json'
    };
    
    const token = localStorage.getItem('access_token');
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    const response = await axios.get('http://localhost:8000/api/public/posts/', { headers });
    
    console.log('文章列表響應:', response.data);
    
    if (Array.isArray(response.data)) {
      posts.value = response.data.map((post: any) => ({
        id: post.id || 0,
        title: post.title || '',
        content: post.content || '',
        category_id: post.category?.id || null,
        category: {
          id: post.category?.id || null,
          name: post.category?.name || '未知分類'
        },
        author: {
          id: post.author?.id || 0,
          username: post.author?.username || '匿名用戶'
        },
        created_at: post.created_at || new Date().toISOString(),
        views: post.views || 0,
        likes_count: post.like_count || 0,
        comments_count: post.comment_count || 0,
        tags: Array.isArray(post.tags) ? post.tags.map(tag => ({
          id: tag.id,
          name: tag.name,
          description: tag.description || ''
        })) : []
      }));
      console.log('更新後的文章列表:', posts.value);
    } else {
      console.error('無效的響應格式:', response.data);
      posts.value = [];
    }
  } catch (error: any) {
    console.error('加載文章列表失敗:', error);
    posts.value = [];
    message.error(error.response?.data?.message || '加載文章列表失敗，請稍後重試');
  } finally {
    isLoading.value = false;
  }
};

// 加載標籤列表
const loadTags = async () => {
  try {
    console.log('開始載入標籤列表...');
    const response = await axios.get('http://localhost:8000/api/public/tags/', {
      headers: {
        'Content-Type': 'application/json'
      }
    });

    console.log('標籤API響應:', response.data);

    if (Array.isArray(response.data)) {
      tags.value = response.data.map(tag => ({
        label: tag.name,
        value: tag.id,
        description: tag.description || ''
      }));
      console.log('處理後的標籤數據:', tags.value);
    } else {
      console.error('標籤數據格式不正確:', response.data);
      tags.value = [];
    }
  } catch (error) {
    console.error('載入標籤列表失敗:', error);
    message.error('載入標籤列表失敗');
    tags.value = [];
  }
};

// 判斷是否為新文章（24小時內）
const isNewPost = (created_at) => {
  const postDate = new Date(created_at);
  const now = new Date();
  return (now - postDate) < 24 * 60 * 60 * 1000;
};

// 格式化日期
const formatDate = (date) => {
  return new Date(date).toLocaleString('zh-TW', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
};

// 發文表單
const showPostModal = ref(false);
const postForm = ref({
  category_id: null,
  title: '',
  content: '',
  tags: [],
  is_public: true,
  allow_comments: true
});

// 重置表單
const resetForm = () => {
  postForm.value = {
    category_id: null,
    title: '',
    content: '',
    tags: [],
    is_public: true,
    allow_comments: true
  };
  selectedTags.value = [];
};

// 表單驗證規則
const rules = {
  category_id: {
    required: true,
    type: 'number',
    message: '請選擇文章分類',
    trigger: ['blur', 'change', 'input']
  },
  title: {
    required: true,
    message: '請輸入文章標題',
    trigger: ['blur', 'input'],
    min: 2,
    max: 100
  },
  content: {
    required: true,
    message: '請輸入文章內容',
    trigger: ['blur', 'input'],
    min: 10
  }
};

// 狀態
const isSubmitting = ref(false);
const showLoginModal = ref(false);

// 獲取分類名稱
const getCategoryName = (categoryId) => {
  const category = categoryOptions.value.find(c => c.value === categoryId);
  return category ? category.label : '未知分類';
}

// 監聽登入狀態變化
watch(isLoggedIn, async (newValue) => {
  if (!newValue) {
    try {
      // 呼叫後端登出 API
      const token = localStorage.getItem('access_token');
      if (token) {
        await axios.post('http://localhost:8000/api/auth/logout/', null, {
          headers: {
            'Authorization': `Bearer ${token}`,
          }
        });
      }
      
      // 清除本地存儲和狀態
      localStorage.clear();
      userStore.setLoginStatus(false);
      userStore.clearUserInfo();
      message.success('已登出系統');
      
      // 重新加載文章列表（不需要認證）
      await loadPosts();
      
      router.push('/login');
    } catch (error) {
      console.error('登出錯誤:', error);
      // 即使後端 API 呼叫失敗，仍然清除本地數據
      localStorage.clear();
      userStore.setLoginStatus(false);
      userStore.clearUserInfo();
      message.warning('登出時發生錯誤，但已清除本地登入狀態');
      
      // 重新加載文章列表（不需要認證）
      await loadPosts();
      
      router.push('/login');
    }
  } else {
    // 重新加載數據
    await loadCategories();
    await loadPosts();
    await loadTags();
  }
});

// 提交表單
const handleSubmit = async () => {
  try {
    isSubmitting.value = true;
    
    // 檢查登入狀態
    if (!isLoggedIn.value) {
      message.error('請先登入');
      showLoginModal.value = true;
      isSubmitting.value = false;
      return;
    }

    // 獲取 token
    const token = localStorage.getItem('access_token');
    if (!token) {
      message.error('登入已過期，請重新登入');
      showLoginModal.value = true;
      isSubmitting.value = false;
      return;
    }

    // 準備發送的數據
    const response = await axios.post(
      'http://localhost:8000/api/public/posts/',
      {
        title: postForm.value.title.trim(),
        content: postForm.value.content.trim(),
        category_id: Number(postForm.value.category_id),
        tags_ids: selectedTags.value,  // 修改欄位名稱
      },
      {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        }
      }
    );

    console.log('API 響應:', response.data);

    if (response.data && response.data.data) {
      message.success('發文成功');
      showPostModal.value = false;
      resetForm();
      // 延遲一下再重新加載文章列表
      setTimeout(async () => {
        await loadPosts();
      }, 500);
    } else {
      throw new Error(response.data.message || '發文失敗');
    }
  } catch (error) {
    console.error('發文錯誤:', error);
    if (error.response) {
      const errorMessage = error.response.data.message || error.response.data.detail || '發文失敗';
      message.error(errorMessage);
      console.error('API 錯誤詳情:', error.response.data);
    } else {
      message.error(error.message || '發文失敗，請稍後重試');
    }
  } finally {
    isSubmitting.value = false;
  }
};

// 在組件掛載時加載數據
onMounted(async () => {
  await loadCategories();
  await loadPosts();
  await loadTags();  // 添加載入標籤
});

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

// 處理發文按鈕點擊
const handlePostButtonClick = () => {
  if (!isLoggedIn.value) {
    showLoginModal.value = true;
    return;
  }
  showPostModal.value = true;
};

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
              <li v-for="category in categoryOptions" :key="category.value">
                <a
                  href="#"
                  class="flex items-center justify-between p-3 rounded-lg transition-all duration-300"
                  :class="{ 
                    'bg-primary/5 text-primary font-medium': category.value === postForm.category_id,
                    'text-gray-600 hover:bg-gray-50': category.value !== postForm.category_id
                  }"
                  @click.prevent="postForm.category_id = category.value"
                >
                  <span>{{ category.label }}</span>
                  <span class="px-2.5 py-1 rounded-full text-xs" :class="{
                    'bg-primary/10 text-primary': category.value === postForm.category_id,
                    'bg-gray-100 text-gray-500': category.value !== postForm.category_id
                  }">{{ category.post_count }}</span>
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
            <div class="bg-white rounded-lg shadow-md p-6 mt-4">
              <h2 class="text-2xl font-bold mb-4">文章列表</h2>
              <div v-if="!posts || posts.length === 0" class="text-gray-500 text-center py-4">
                暫無文章
              </div>
              <div v-else class="space-y-4">
                <div v-for="post in posts" :key="post.id" 
                  class="border-b pb-4 hover:bg-gray-50 p-4 rounded-lg transition-all duration-300">
                  <div class="flex justify-between items-start mb-2">
                    <h3 class="text-xl font-semibold text-gray-800 hover:text-primary cursor-pointer"
                      @click="goToPostDetail(post.id)">
                      {{ post.title }}
                    </h3>
                    <span class="text-sm text-gray-500">
                      {{ formatDate(post.created_at) }}
                    </span>
                  </div>
                  <p class="text-gray-600 mt-2 line-clamp-3">{{ post.content }}</p>
                  <div class="flex items-center justify-between mt-3">
                    <div class="flex items-center gap-4">
                      <div class="flex items-center text-gray-500 text-sm">
                        <NIcon size="16" class="mr-1"><PersonOutlined /></NIcon>
                        {{ post.author?.username || '匿名用戶' }}
                      </div>
                      <div class="flex items-center text-gray-500 text-sm">
                        <NIcon size="16" class="mr-1"><CategoryOutlined /></NIcon>
                        {{ getCategoryName(post.category_id) }}
                      </div>
                      <div class="flex items-center text-gray-500 text-sm">
                        <NIcon size="16" class="mr-1"><LocalOfferOutlined /></NIcon>
                        <template v-if="post.tags && post.tags.length > 0">
                          <span v-for="(tag, index) in post.tags" :key="tag.id">
                            {{ tag.name }}{{ index < post.tags.length - 1 ? ', ' : '' }}
                          </span>
                        </template>
                        <template v-else>無標籤</template>
                      </div>
                    </div>
                    <div class="flex items-center gap-4">
                      <div class="flex items-center text-gray-500 text-sm">
                        <NIcon size="16" class="mr-1"><VisibilityOutlined /></NIcon>
                        {{ post.views || 0 }}
                      </div>
                      <div class="flex items-center text-gray-500 text-sm">
                        <NIcon size="16" class="mr-1"><ChatBubbleOutlined /></NIcon>
                        {{ post.comments_count || 0 }}
                      </div>
                      <div class="flex items-center text-gray-500 text-sm">
                        <NIcon size="16" class="mr-1"><StarOutlined /></NIcon>
                        {{ post.likes_count || 0 }}
                      </div>
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
  <NModal v-model:show="showPostModal" style="width: 800px">
    <NCard
      title="發表新主題"
      :bordered="false"
      size="huge"
      role="dialog"
      aria-modal="true"
    >
      <NForm ref="formRef" :model="postForm" :rules="rules">
        <NFormItem label="文章分類" path="category_id" required>
          <NSelect
            v-model:value="postForm.category_id"
            :options="categoryOptions"
            placeholder="請選擇分類"
            :disabled="isSubmitting"
            @update:value="(val) => {
              console.log('選擇的分類值:', val);
              if (!val) {
                postForm.category_id = null;
                message.warning('請選擇文章分類');
                return;
              }
              const selectedCategory = categoryOptions.value.find(cat => cat.value === val);
              if (selectedCategory) {
                postForm.category_id = val;
                message.success(`已選擇分類: ${selectedCategory.label}`);
              } else {
                postForm.category_id = null;
                message.error('無效的分類選擇');
              }
            }"
          />
        </NFormItem>
        <NFormItem label="文章標題" path="title" required>
          <NInput 
            v-model:value="postForm.title" 
            placeholder="請輸入標題（2-100字）"
            :maxlength="100"
            show-count
          />
        </NFormItem>
        <NFormItem label="文章內容" path="content" required>
          <NInput
            v-model:value="postForm.content"
            type="textarea"
            placeholder="請輸入內容（至少10字）"
            :rows="10"
            show-count
          />
        </NFormItem>
        <NFormItem label="標籤" path="tags">
          <NSelect
            v-model:value="selectedTags"
            :options="tags"
            multiple
            placeholder="請選擇標籤"
            :disabled="isSubmitting"
            @update:value="(val) => {
              console.log('選擇的標籤:', val);
              selectedTags.value = val;
            }"
          />
        </NFormItem>
        <NFormItem label="文章設定">
          <div class="space-y-2">
            <NSwitch v-model:value="postForm.is_public">
              <template #checked>公開</template>
              <template #unchecked>私密</template>
            </NSwitch>
            <NSwitch v-model:value="postForm.allow_comments">
              <template #checked>允許評論</template>
              <template #unchecked>禁止評論</template>
            </NSwitch>
          </div>
        </NFormItem>
      </NForm>
      <template #footer>
        <div class="flex justify-end gap-4">
          <NButton @click="showPostModal = false">取消</NButton>
          <NButton 
            type="primary" 
            @click="handleSubmit"
            :loading="isSubmitting"
            :disabled="!postForm.category_id || !postForm.title.trim() || !postForm.content.trim()"
          >
            發表文章
          </NButton>
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
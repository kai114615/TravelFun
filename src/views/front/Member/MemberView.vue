<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { 
  NTabs, 
  NTabPane, 
  NList, 
  NListItem, 
  NButton, 
  NTag, 
  NBadge,
  NEmpty,
  NCard,
  NSpace,
  NIcon,
  NForm,
  NFormItem,
  NInput,
  NUpload,
  NAvatar,
  NSwitch,
  NDatePicker
} from 'naive-ui';
import { 
  ShoppingCartOutlined,
  MapOutlined,
  ArticleOutlined,
  BookmarkOutlined,
  ThumbUpOutlined,
  NotificationsOutlined,
  VisibilityOutlined,
  ChatBubbleOutlined,
  DeleteOutlined,
  EditOutlined,
  PersonOutlined,
  CameraAltOutlined
} from '@vicons/material';
import { useUserStore } from '@/stores/user';
import { useMessage } from 'naive-ui';
import axios from 'axios';

// 當前選中的標籤頁
const activeTab = ref('orders');

// 訂單列表
const orders = ref([
  {
    id: 'O20240110001',
    date: '2024-01-10',
    items: [
      { name: '台北101觀景台門票', quantity: 2, price: 600 },
      { name: '九份老街導覽行程', quantity: 1, price: 1200 }
    ],
    total: 2400,
    status: '已完成'
  },
  {
    id: 'O20240105002',
    date: '2024-01-05',
    items: [
      { name: '花蓮太魯閣一日遊', quantity: 4, price: 1500 }
    ],
    total: 6000,
    status: '待付款'
  }
]);

// 我的行程
const trips = ref([
  {
    id: 1,
    title: '台北三天兩夜自由行',
    date: '2024-02-15 ~ 2024-02-17',
    status: '規劃中',
    places: ['台北101', '九份老街', '陽明山']
  },
  {
    id: 2,
    title: '花蓮四天三夜親子遊',
    date: '2024-03-20 ~ 2024-03-23',
    status: '已完成',
    places: ['太魯閣', '七星潭', '花蓮夜市']
  }
]);

// 我的文章
const myPosts = ref([
  {
    id: 1,
    title: '【台北】跟著在地人吃喝玩樂，精華景點全攻略',
    date: '2024-01-10',
    views: 1239,
    comments: 124,
    likes: 56
  },
  {
    id: 2,
    title: '花蓮三天兩夜這樣玩最好玩！',
    date: '2024-01-05',
    views: 856,
    comments: 67,
    likes: 34
  }
]);

// 收藏的文章
const savedPosts = ref([
  {
    id: 3,
    title: '2024春節環島攻略',
    author: '旅遊達人小明',
    date: '2024-01-08',
    views: 2341,
    comments: 178
  },
  {
    id: 4,
    title: '台南必吃美食地圖',
    author: '美食專家大胃王',
    date: '2024-01-06',
    views: 1567,
    comments: 143
  }
]);

// 按讚的文章
const likedPosts = ref([
  {
    id: 5,
    title: '新手環島必看攻略',
    author: '單車達人阿德',
    date: '2024-01-09',
    views: 3421,
    comments: 256
  },
  {
    id: 6,
    title: '高雄一日遊推薦路線',
    author: '南部走透透',
    date: '2024-01-07',
    views: 1892,
    comments: 167
  }
]);

// 消息通知
const notifications = ref([
  {
    id: 1,
    type: '文章',
    content: '您的文章「台北三天兩夜」收到新的留言',
    date: '10分鐘前',
    isRead: false
  },
  {
    id: 2,
    type: '訂單',
    content: '您的訂單 O20240110001 已完成付款',
    date: '2小時前',
    isRead: true
  },
  {
    id: 3,
    type: '按讚',
    content: '旅遊達人小明對您的文章按讚',
    date: '昨天',
    isRead: true
  }
]);

// 個人資料
const userProfile = ref({
  name: '',
  email: '',
  phone: '',
  birthday: null,
  address: '',
  avatar: '',
  notifications: {
    email: false,
    push: false
  }
});

// 密碼修改表單
const passwordForm = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
});

// 是否顯示修改密碼表單
const showPasswordForm = ref(false);

const userStore = useUserStore();
const isLoggedIn = computed(() => userStore.loginStatus);
const message = useMessage();

// 頭像 URL 處理
const baseUrl = 'http://localhost:8000';
const avatarUrl = computed(() => {
  if (!userProfile.value.avatar) {
    return 'https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y'
  }
  
  let url = userProfile.value.avatar
  // 移除開頭的斜線（如果存在）
  url = url.replace(/^\/+/, '')
  // 移除重複的 media 前綴
  url = url.replace(/^media\/media\//, 'media/')
  // 確保使用正斜線
  url = url.replace(/\\/g, '/')
  
  // 組合完整 URL
  return `${baseUrl}/${url}`
})

// 修改密碼
const changePassword = async () => {
  try {
    // 驗證新密碼
    if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
      window.$message.error('新密碼與確認密碼不符');
      return;
    }
    
    if (passwordForm.value.newPassword.length < 8) {
      window.$message.error('新密碼長度至少需要8個字元');
      return;
    }

    // TODO: 實作修改密碼邏輯
    console.log('修改密碼:', passwordForm.value);
    
    // 模擬修改成功
    window.$message.success('密碼修改成功');
    // 清空表單
    passwordForm.value = {
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    };
    // 關閉修改密碼表單
    showPasswordForm.value = false;
  } catch (error) {
    console.error('修改密碼失敗:', error);
    window.$message.error('修改密碼失敗');
  }
};

// 模擬從後端獲取用戶資料
const fetchUserProfile = async () => {
  try {
    // 模擬 API 調用
    const mockUserData = {
      name: '王小明',
      email: 'wang@example.com',
      phone: '0912345678',
      birthday: new Date('1990-01-01'),
      address: '台北市信義區信義路五段7號',
      avatar: '',  // 預設為空，將使用 Gravatar 預設頭像
      notifications: {
        email: true,
        push: true
      }
    };
    
    userProfile.value = mockUserData;
  } catch (error) {
    console.error('獲取用戶資料失敗:', error);
  }
};

// 在組件掛載時獲取用戶資料
onMounted(() => {
  fetchUserProfile();
});

// 處理頭像上傳
const handleAvatarUpload = async (options: { file: UploadFileInfo }) => {
  try {
    const formData = new FormData();
    formData.append('avatar', options.file.file as File);

    const token = localStorage.getItem('access_token');
    if (!token) {
      throw new Error('請先登入');
    }

    const response = await axios.post('http://127.0.0.1:8000/api/member/profile/update/', formData, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'multipart/form-data',
        'X-Requested-With': 'XMLHttpRequest'
      },
      withCredentials: true
    });

    if (response.status === 200) {
      message.success('頭像上傳成功');
      // 更新用戶資料
      await userStore.checkLoginStatus();
      // 更新本地頭像顯示
      userProfile.value.avatar = response.data.avatar;
    } else {
      throw new Error(response.data.message || '上傳失敗');
    }
  } catch (error: any) {
    console.error('上傳頭像失敗:', error);
    message.error(error.response?.data?.message || '上傳頭像失敗，請稍後再試');
  }
};

// 保存個人資料
const saveProfile = async () => {
  try {
    const formData = new FormData();
    formData.append('full_name', userProfile.value.full_name);
    formData.append('address', userProfile.value.address);

    const token = localStorage.getItem('access_token');
    if (!token) {
      throw new Error('請先登入');
    }

    const response = await axios.post('http://127.0.0.1:8000/api/member/update-profile/', formData, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'multipart/form-data',
        'X-Requested-With': 'XMLHttpRequest'
      },
      withCredentials: true
    });

    if (response.status === 200) {
      message.success('個人資料更新成功');
      // 更新用戶資料
      await userStore.checkLoginStatus();
      // 更新本地表單數據
      userProfile.value = {
        full_name: response.data.full_name || '',
        address: response.data.address || ''
      };
    } else {
      throw new Error(response.data.message || '更新失敗');
    }
  } catch (error: any) {
    console.error('更新個人資料失敗:', error);
    message.error(error.response?.data?.message || '更新個人資料失敗，請稍後再試');
  }
};

// 刪除文章
const deletePost = (postId: number) => {
  // TODO: 實作刪除文章邏輯
  console.log('刪除文章:', postId);
};

// 編輯文章
const editPost = (postId: number) => {
  // TODO: 實作編輯文章邏輯
  console.log('編輯文章:', postId);
};

// 取消收藏
const removeSaved = (postId: number) => {
  // TODO: 實作取消收藏邏輯
  console.log('取消收藏:', postId);
};

// 取消按讚
const removeLike = (postId: number) => {
  // TODO: 實作取消按讚邏輯
  console.log('取消按讚:', postId);
};

// 標記通知為已讀
const markAsRead = (notificationId: number) => {
  // TODO: 實作標記已讀邏輯
  console.log('標記已讀:', notificationId);
};
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 py-8">
    <h1 class="text-2xl font-bold text-gray-800 mb-8">會員中心</h1>

    <NTabs v-model:value="activeTab" type="line" animated>
      <!-- 1. 我的訂單 -->
      <NTabPane name="orders" tab="我的訂單">
        <template #tab>
          <div class="flex items-center gap-2">
            <NIcon><ShoppingCartOutlined /></NIcon>
            我的訂單
          </div>
        </template>
        <div class="space-y-4">
          <NCard v-for="order in orders" :key="order.id" class="hover:shadow-md transition-shadow">
            <div class="flex justify-between items-start mb-4">
              <div>
                <h3 class="font-medium text-lg">訂單編號：{{ order.id }}</h3>
                <p class="text-gray-500">下單日期：{{ order.date }}</p>
              </div>
              <NTag :type="order.status === '已完成' ? 'success' : 'warning'" round>
                {{ order.status }}
              </NTag>
            </div>
            <NList>
              <NListItem v-for="item in order.items" :key="item.name">
                <div class="flex justify-between items-center">
                  <span>{{ item.name }} x {{ item.quantity }}</span>
                  <span class="text-gray-600">${{ item.price * item.quantity }}</span>
                </div>
              </NListItem>
            </NList>
            <div class="text-right mt-4">
              <span class="font-medium">總計：</span>
              <span class="text-xl text-primary font-bold">${{ order.total }}</span>
            </div>
          </NCard>
        </div>
      </NTabPane>

      <!-- 2. 我的行程 -->
      <NTabPane name="trips" tab="我的行程">
        <template #tab>
          <div class="flex items-center gap-2">
            <NIcon><MapOutlined /></NIcon>
            我的行程
          </div>
        </template>
        <div class="space-y-4">
          <NCard v-for="trip in trips" :key="trip.id" class="hover:shadow-md transition-shadow">
            <div class="flex justify-between items-start">
              <div>
                <h3 class="font-medium text-lg mb-2">{{ trip.title }}</h3>
                <p class="text-gray-500 mb-2">{{ trip.date }}</p>
                <div class="flex flex-wrap gap-2">
                  <NTag v-for="place in trip.places" :key="place" size="small">
                    {{ place }}
                  </NTag>
                </div>
              </div>
              <NTag :type="trip.status === '已完成' ? 'success' : 'info'" round>
                {{ trip.status }}
              </NTag>
            </div>
          </NCard>
        </div>
      </NTabPane>

      <!-- 3. 我的文章 -->
      <NTabPane name="posts" tab="我的文章">
        <template #tab>
          <div class="flex items-center gap-2">
            <NIcon><ArticleOutlined /></NIcon>
            我的文章
          </div>
        </template>
        <div class="space-y-4">
          <NCard v-for="post in myPosts" :key="post.id" class="hover:shadow-md transition-shadow">
            <div class="flex justify-between items-start">
              <div class="flex-1">
                <h3 class="font-medium text-lg mb-2">{{ post.title }}</h3>
                <p class="text-gray-500">發表於 {{ post.date }}</p>
                <div class="flex items-center gap-4 mt-2 text-gray-500">
                  <span class="flex items-center gap-1">
                    <NIcon size="16"><VisibilityOutlined /></NIcon>
                    {{ post.views }}
                  </span>
                  <span class="flex items-center gap-1">
                    <NIcon size="16"><ChatBubbleOutlined /></NIcon>
                    {{ post.comments }}
                  </span>
                  <span class="flex items-center gap-1">
                    <NIcon size="16"><ThumbUpOutlined /></NIcon>
                    {{ post.likes }}
                  </span>
                </div>
              </div>
              <NSpace>
                <NButton size="small" @click="editPost(post.id)">
                  <template #icon>
                    <NIcon><EditOutlined /></NIcon>
                  </template>
                  編輯
                </NButton>
                <NButton size="small" type="error" @click="deletePost(post.id)">
                  <template #icon>
                    <NIcon><DeleteOutlined /></NIcon>
                  </template>
                  刪除
                </NButton>
              </NSpace>
            </div>
          </NCard>
        </div>
      </NTabPane>

      <!-- 4. 收藏的文章 -->
      <NTabPane name="saved" tab="收藏的文章">
        <template #tab>
          <div class="flex items-center gap-2">
            <NIcon><BookmarkOutlined /></NIcon>
            收藏的文章
          </div>
        </template>
        <div class="space-y-4">
          <NCard v-for="post in savedPosts" :key="post.id" class="hover:shadow-md transition-shadow">
            <div class="flex justify-between items-start">
              <div class="flex-1">
                <h3 class="font-medium text-lg mb-2">{{ post.title }}</h3>
                <p class="text-gray-500">{{ post.author }} · {{ post.date }}</p>
                <div class="flex items-center gap-4 mt-2 text-gray-500">
                  <span class="flex items-center gap-1">
                    <NIcon size="16"><VisibilityOutlined /></NIcon>
                    {{ post.views }}
                  </span>
                  <span class="flex items-center gap-1">
                    <NIcon size="16"><ChatBubbleOutlined /></NIcon>
                    {{ post.comments }}
                  </span>
                </div>
              </div>
              <NButton size="small" @click="removeSaved(post.id)">
                <template #icon>
                  <NIcon><BookmarkOutlined /></NIcon>
                </template>
                取消收藏
              </NButton>
            </div>
          </NCard>
        </div>
      </NTabPane>

      <!-- 5. 按讚的文章 -->
      <NTabPane name="liked" tab="按讚的文章">
        <template #tab>
          <div class="flex items-center gap-2">
            <NIcon><ThumbUpOutlined /></NIcon>
            按讚的文章
          </div>
        </template>
        <div class="space-y-4">
          <NCard v-for="post in likedPosts" :key="post.id" class="hover:shadow-md transition-shadow">
            <div class="flex justify-between items-start">
              <div class="flex-1">
                <h3 class="font-medium text-lg mb-2">{{ post.title }}</h3>
                <p class="text-gray-500">{{ post.author }} · {{ post.date }}</p>
                <div class="flex items-center gap-4 mt-2 text-gray-500">
                  <span class="flex items-center gap-1">
                    <NIcon size="16"><VisibilityOutlined /></NIcon>
                    {{ post.views }}
                  </span>
                  <span class="flex items-center gap-1">
                    <NIcon size="16"><ChatBubbleOutlined /></NIcon>
                    {{ post.comments }}
                  </span>
                </div>
              </div>
              <NButton size="small" @click="removeLike(post.id)">
                <template #icon>
                  <NIcon><ThumbUpOutlined /></NIcon>
                </template>
                取消按讚
              </NButton>
            </div>
          </NCard>
        </div>
      </NTabPane>

      <!-- 6. 通知中心 -->
      <NTabPane name="notifications" tab="通知中心">
        <template #tab>
          <div class="flex items-center gap-2">
            <NBadge :value="notifications.filter(n => !n.isRead).length" :max="99">
              <NIcon><NotificationsOutlined /></NIcon>
            </NBadge>
            通知中心
          </div>
        </template>
        <div class="space-y-4">
          <NCard v-for="notification in notifications" :key="notification.id" 
            class="hover:shadow-md transition-shadow"
            :class="{ 'bg-gray-50': !notification.isRead }"
          >
            <div class="flex justify-between items-start">
              <div class="flex-1">
                <div class="flex items-center gap-2 mb-2">
                  <NTag size="small" :type="notification.type === '文章' ? 'info' : notification.type === '訂單' ? 'success' : 'warning'">
                    {{ notification.type }}
                  </NTag>
                  <span class="text-gray-500 text-sm">{{ notification.date }}</span>
                </div>
                <p class="text-gray-800">{{ notification.content }}</p>
              </div>
              <NButton v-if="!notification.isRead" size="tiny" text @click="markAsRead(notification.id)">
                標記已讀
              </NButton>
            </div>
          </NCard>
        </div>
      </NTabPane>

      <!-- 7. 個人資料 -->
      <NTabPane name="profile" tab="個人資料">
        <template #tab>
          <div class="flex items-center gap-2">
            <NIcon><PersonOutlined /></NIcon>
            個人資料
          </div>
        </template>
        
        <NCard class="max-w-2xl mx-auto">
          <div class="flex flex-col items-center mb-8">
            <NAvatar
              :src="avatarUrl"
              :size="100"
              round
              class="mb-4"
            />
            <NUpload
              accept="image/*"
              :max="1"
              :show-file-list="false"
              @change="handleAvatarUpload"
            >
              <NButton secondary>
                <template #icon>
                  <NIcon><CameraAltOutlined /></NIcon>
                </template>
                更換頭像
              </NButton>
            </NUpload>
          </div>

          <NForm>
            <NFormItem label="姓名" required>
              <NInput v-model:value="userProfile.full_name" placeholder="請輸入姓名" />
            </NFormItem>
            
            <NFormItem label="Email" required>
              <NInput v-model:value="userProfile.email" placeholder="請輸入Email" disabled />
            </NFormItem>
            
            <NFormItem label="手機">
              <NInput v-model:value="userProfile.phone" placeholder="請輸入手機號碼" />
            </NFormItem>
            
            <NFormItem label="生日">
              <NDatePicker 
                v-model:value="userProfile.birthday"
                type="date"
                clearable
                :is-date-disabled="(timestamp: number) => timestamp > Date.now()"
              />
            </NFormItem>
            
            <NFormItem label="地址">
              <NInput v-model:value="userProfile.address" placeholder="請輸入地址" />
            </NFormItem>

            <NFormItem label="通知設定">
              <NSpace vertical>
                <div class="flex items-center gap-4">
                  <NSwitch v-model:value="userProfile.notifications.email" />
                  <span>接收Email通知</span>
                </div>
                <div class="flex items-center gap-4">
                  <NSwitch v-model:value="userProfile.notifications.push" />
                  <span>接收推播通知</span>
                </div>
              </NSpace>
            </NFormItem>

            <!-- 修改密碼區塊 -->
            <NFormItem>
              <div class="flex justify-between items-center">
                <span class="font-medium">密碼設定</span>
                <NButton text @click="showPasswordForm = !showPasswordForm">
                  {{ showPasswordForm ? '取消修改' : '修改密碼' }}
                </NButton>
              </div>
              
              <div v-if="showPasswordForm" class="mt-4 space-y-4">
                <NFormItem label="目前密碼">
                  <NInput
                    v-model:value="passwordForm.currentPassword"
                    type="password"
                    placeholder="請輸入目前密碼"
                    show-password-on="click"
                  />
                </NFormItem>
                
                <NFormItem label="新密碼">
                  <NInput
                    v-model:value="passwordForm.newPassword"
                    type="password"
                    placeholder="請輸入新密碼（至少8個字元）"
                    show-password-on="click"
                  />
                </NFormItem>
                
                <NFormItem label="確認新密碼">
                  <NInput
                    v-model:value="passwordForm.confirmPassword"
                    type="password"
                    placeholder="請再次輸入新密碼"
                    show-password-on="click"
                  />
                </NFormItem>

                <div class="flex justify-end">
                  <NButton type="primary" @click="changePassword">
                    確認修改
                  </NButton>
                </div>
              </div>
            </NFormItem>

            <div class="flex justify-end mt-6">
              <NButton type="primary" @click="saveProfile">
                儲存變更
              </NButton>
            </div>
          </NForm>
        </NCard>
      </NTabPane>
    </NTabs>
  </div>
</template>

<style scoped>
.text-primary {
  color: var(--primary-color);
}

.bg-primary {
  background-color: var(--primary-color);
}

.hover\:shadow-md {
  transition: box-shadow 0.3s ease;
}

.hover\:shadow-md:hover {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}
</style> 
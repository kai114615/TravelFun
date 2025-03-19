<script setup lang="ts">
import {
  FavoriteBorderOutlined,
  FavoriteOutlined,
  PersonOutlineFilled,
  AccountCircleOutlined,
} from '@vicons/material';
import { NDialogProvider, NIcon, NMessageProvider, useDialog, useMessage, NAvatar } from 'naive-ui';
import { storeToRefs } from 'pinia';
import { computed, onMounted, ref, watch } from 'vue';
import { RouterLink, useRoute, useRouter } from 'vue-router';
import ShopCart from './ShopCart.vue';
import { createNavList } from './navList.ts';
import { HamburgerMenu } from './Hamburger';
import { websiteConfig } from '@/config/website.config';
import { useCartStore, useDeviceStore, useFavoriteStore, useUserStore } from '@/stores';
import Container from '@/layout/Container.vue';

const route = useRoute();
const router = useRouter();

const cartStore = useCartStore();
const deviceStore = useDeviceStore();
const favoriteStore = useFavoriteStore();
const userStore = useUserStore();

const { totalNum, cartList } = storeToRefs(cartStore);
const { isMobile } = storeToRefs(deviceStore);
const { favoriteList } = storeToRefs(favoriteStore);
const { loginStatus, displayName, userInfo } = storeToRefs(userStore);

const cartRef = ref<InstanceType<typeof ShopCart>>();
const hamBurRef = ref<InstanceType<typeof HamburgerMenu>>();

const dialog = useDialog();
const message = useMessage();

const isFixed = computed(() => new Set(['Home', 'City', 'Country', 'Member']).has(route.name?.toString() || ''));

const navListComponent = computed(() => createNavList().filter(({ component }) => component));

// 計算頭像URL
const avatarUrl = computed(() => {
  if (userInfo.value?.avatar) {
    // 如果是完整URL直接返回
    if (userInfo.value.avatar.startsWith('http://') || userInfo.value.avatar.startsWith('https://')) {
      return userInfo.value.avatar;
    } 
    // 否則需要加上基礎URL
    else {
      // 獲取API基礎URL
      const baseUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
      // 移除頭像路徑前面的斜線（如果有）
      const avatarPath = userInfo.value.avatar.replace(/^\/+/, '');
      // 移除重複的 media 前綴
      const cleanedPath = avatarPath.replace(/^media\/media\//, 'media/');
      return `${baseUrl}/${cleanedPath}`;
    }
  }
  // 返回預設頭像
  return '/avatar-fallback.png';
});

function handleClick(target: string) {
  if (target === 'cart')
    hamBurRef.value?.closeActive();

  cartRef.value?.closeActive();
};

function goToLogin() {
  console.log('跳轉到登入頁面');
  router.push('/login');
}

function goToMemberCenter() {
  router.push('/member/profile');
}

async function handleLogout() {
  dialog.warning({
    title: '登出確認',
    content: '確定要登出嗎？',
    positiveText: '確定',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await userStore.logout();
        cartStore.clearCart();
        message.success('已成功登出');
        router.push('/');
      }
      catch (error) {
        message.error('登出失敗，請稍後再試');
      }
    },
  });
}

// 監聽登入狀態變化
watch(loginStatus, async (newStatus) => {
  if (newStatus)
    await userStore.checkLoginStatus();
}, { immediate: true });

// 監聽路由變化
watch(
  () => route.path,
  async () => {
    await userStore.checkLoginStatus();
  },
);

onMounted(async () => {
  await userStore.checkLoginStatus();
})
</script>

<template>
  <NDialogProvider>
    <NMessageProvider>
      <header
        id="header"
        class="top-0 z-20 flex h-16 justify-center bg-black/30 px-6 py-3 text-white backdrop-blur-[25px]"
        :class="isFixed ? 'fixed left-0 right-0' : 'sticky'"
      >
        <Container class="mx-auto w-full md:px-4 xl:px-0 lg:max-w-cc-width px-3">
          <div class="flex w-full justify-between">
            <HamburgerMenu ref="hamBurRef" :is-mobile="isMobile" @active="handleClick" />
            <div class="flex items-center gap-8 lg:w-[526px]">
              <RouterLink :to="{ name: 'Home' }" class="router-link-active router-link-exact-active">
                <img class="h-10 object-cover" :src="websiteConfig.logoImage" alt="logo">
              </RouterLink>
              <ul class="hidden h-full flex-1 items-center justify-center gap-8 md:flex">
                <template v-for="nav in navListComponent" :key="nav.id">
                  <li class="nav-item">
                    <component
                      :is="nav.component"
                      class="flex items-center gap-2 whitespace-nowrap px-3 py-2 text-sm transition-colors duration-300 hover:text-cc-accent"
                      style="writing-mode: horizontal-tb;"
                    />
                  </li>
                </template>
              </ul>
            </div>
            <div class="flex items-center justify-between lg:w-[256px]" style="pointer-events: auto;">
              <div class="hidden place-content-center md:grid">
                <RouterLink v-if="loginStatus" class="leading-none" :to="{ name: 'WishList' }">
                  <NIcon v-if="favoriteList.length !== 0" size="24" color="#EE5220" class="icon-hover">
                    <FavoriteOutlined />
                  </NIcon>
                  <NIcon v-else class="icon-hover" size="24">
                    <FavoriteBorderOutlined />
                  </NIcon>
                </RouterLink>
              </div>
              <!-- 已登入狀態 -->
              <div v-if="loginStatus" class="flex items-center justify-center text-base gap-2">
                <!-- 用戶頭像和名稱 -->
                <div class="flex items-center cursor-pointer" @click="goToMemberCenter">
                  <!-- 用戶頭像 -->
                  <NAvatar 
                    round 
                    :src="avatarUrl" 
                    size="small"
                    fallback-src="/avatar-fallback.png" 
                    class="user-avatar"
                  />
                  <span class="text-white ml-2 font-medium truncate max-w-[80px] md:max-w-[120px]">{{ displayName || '會員' }}</span>
                </div>
                <!-- 登出按鈕 -->
                <button
                  class="inline-flex items-center px-2 py-1 md:px-3 md:py-1.5 text-xs md:text-sm font-medium text-red-600 hover:text-red-700 transition-colors bg-white/10 hover:bg-white/20 rounded-md"
                  @click="handleLogout"
                >
                  <i class="fas fa-sign-out-alt md:mr-1" />
                  <span class="hidden md:inline">登出</span>
                </button>
              </div>
              <!-- 未登入狀態 -->
              <RouterLink v-else v-slot="{ navigate }" custom :to="{ name: 'Login' }">
                <button
                  type="button"
                  class="hidden w-[144px] items-center justify-center gap-[6px] rounded-[50px] bg-cc-other-8 px-4 py-2 text-sm transition-colors duration-300 hover:bg-cc-accent lg:flex"
                  @click="() => {
                    console.log('點擊登入按鈕');
                    console.log('當前路由：', route.fullPath);
                    navigate();
                  }"
                >
                  <NIcon size="24">
                    <PersonOutlineFilled />
                  </NIcon>
                  登入 / 註冊
                </button>
              </RouterLink>
              <ShopCart
                ref="cartRef"
                :is-mobile="isMobile"
                :total-num="totalNum"
                :cart-list="cartList"
                @active="handleClick"
              />
            </div>
          </div>
        </Container>
      </header>
    </NMessageProvider>
  </NDialogProvider>
</template>

<style scoped>
.nav-item {
  position: relative;
  padding: 0 4px;
}

.nav-item::after {
  content: '';
  position: absolute;
  bottom: -4px;
  left: 0;
  width: 100%;
  height: 2px;
  background-color: #EE5220;
  transform: scaleX(0);
  transition: transform 0.3s;
}

.nav-item:hover::after {
  transform: scaleX(1);
}

.user-avatar {
  border: 2px solid white;
  box-shadow: 0 0 8px rgba(0, 0, 0, 0.2);
}

@media (max-width: 1280px) {
  ul {
    gap: 4px;
  }

  .nav-item {
    padding: 0 2px;
  }
}
</style>

import { createRouter, createWebHashHistory } from 'vue-router';
import MallView from '../views/front/Mall/MallView.vue';
import HomeView from '../views/front/Home/HomeView.vue';
import ThemeEntertainmentView from '@/views/admin/ThemeEntertainmentView.vue';

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomeView,
    meta: {
      title: '首頁',
    },
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/front/Login/LoginView.vue'),
    meta: {
      title: '登入',
    },
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/front/Login/RegisterView.vue'),
    meta: {
      title: '註冊',
    },
  },
  {
    path: '/mall',
    name: 'Mall',
    component: MallView,
    meta: {
      title: '商城中心',
    },
  },
  {
    path: '/mall-products',
    name: 'MallProducts',
    component: () => import('../views/front/Mall/MallProductsView.vue'),
    meta: {
      title: '商城商品 - Travel Fun',
    },
  },
  {
    path: '/activity',
    name: 'Activity',
    component: () => import('../views/front/Activity/ActivityView.vue'),
    meta: {
      title: '主題育樂',
    },
    children: [],
  },
  {
    path: '/travel',
    name: 'Travel',
    component: () => import('../views/front/Travel/TravelView.vue'),
    meta: {
      title: '台灣景點 - Travel Fun',
    },
  },
  {
    path: '/travel/travelmodel',
    name: 'TravelModel',
    component: () => import('../views/front/Travel/TravelModelView.vue'),
    meta: {
      title: '台灣自由行 - Travel Fun',
    },
  },
  {
    path: '/travel/spots',
    name: 'Spots',
    component: () => import('../views/front/Travel/SpotsView.vue'),
    meta: {
      title: '台灣景點 - Travel Fun',
    },
  },
  {
    path: '/travel/TravelMap',
    name: 'TravelMap',
    component: () => import('../views/front/Travel/TravelmapView.vue'),
    meta: {
      title: '旅遊地圖 - Travel Fun',
    },
  },
  {
    path: '/travel/city/:city',
    name: 'TravelCity',
    component: () => import('../views/front/Travel/CityView.vue'),
    meta: {
      title: '全台熱門景點 - Travel Fun',
    },
  },
  {
    path: '/travel/TravelSchedule',
    name: 'TravelSchedule',
    component: () => import('../views/front/Travel/TravelScheduleView.vue'),
    meta: {
      title: '全台熱門景點 - Travel Fun',
    },
  },
  {
    path: '/forum',
    name: 'Forum',
    component: () => import('../views/front/Forum/ForumView.vue'),
    meta: {
      title: '討論區',
    },
  },
  {
    path: '/member/dashboard',
    name: 'MemberDashboard',
    component: () => import('../views/front/Member/DashboardView.vue'),
    meta: {
      title: '會員中心',
      requiresAuth: true,
    },
  },
  {
    path: '/country/:countryName',
    name: 'Country',
    component: () => import('../views/front/Country/CountryView.vue'),
    meta: {
      title: 'AI推薦行程',
    },
  },
  {
    path: '/about',
    name: 'About',
    component: () => import('../views/front/About/AboutView.vue'),
    meta: {
      title: '關於我們',
    },
  },
  {
    path: '/wishlist',
    name: 'WishList',
    component: () => import('../views/front/WishList/WishListView.vue'),
    meta: {
      title: '願望清單',
      requiresAuth: true,
    },
  },
  {
    path: '/admin-dashboard/entertainment/activities',
    name: 'ThemeEntertainmentAdmin',
    component: ThemeEntertainmentView,
    meta: {
      requiresAuth: true,
      title: '主題育樂活動管理',
    },
  },
  {
    path: '/activities',
    name: 'ActivityList',
    component: () => import('../views/front/Activity/ActivityList.vue'),
    meta: {
      title: '主題育樂活動',
    },
  },
];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  document.title = to.meta.title || '商城';
  next();
});

export default router;

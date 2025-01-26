import { createRouter, createWebHashHistory } from 'vue-router';
import MallView from '../views/front/Mall/MallView.vue';
import HomeView from '../views/front/Home/HomeView.vue';

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomeView,
    meta: {
      title: '首頁'
    }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/front/Login/LoginView.vue'),
    meta: {
      title: '登入'
    }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/front/Login/RegisterView.vue'),
    meta: {
      title: '註冊'
    }
  },
  {
    path: '/mall',
    name: 'Mall',
    component: MallView,
    meta: {
      title: '商城中心'
    }
  },
  {
    path: '/activity',
    name: 'Activity',
    component: () => import('../views/front/Activity/ActivityView.vue'),
    meta: {
      title: '主題育樂'
    }
  },
  {
    path: '/forum',
    name: 'Forum',
    component: () => import('../views/front/Forum/ForumView.vue'),
    meta: {
      title: '討論區'
    }
  },
  {
    path: '/member/dashboard',
    name: 'MemberDashboard',
    component: () => import('../views/front/Member/DashboardView.vue'),
    meta: {
      title: '會員中心',
      requiresAuth: true
    }
  },
  {
    path: '/country/:countryName',
    name: 'Country',
    component: () => import('../views/front/Country/CountryView.vue'),
    meta: {
      title: 'AI推薦行程'
    }
  },
  {
    path: '/about',
    name: 'About',
    component: () => import('../views/front/About/AboutView.vue'),
    meta: {
      title: '關於我們'
    }
  },
  {
    path: '/wishlist',
    name: 'WishList',
    component: () => import('../views/front/WishList/WishListView.vue'),
    meta: {
      title: '願望清單',
      requiresAuth: true
    }
  }
];

const router = createRouter({
  history: createWebHashHistory(),
  routes
});

router.beforeEach((to, from, next) => {
  document.title = to.meta.title || '商城';
  next();
});

export default router; 
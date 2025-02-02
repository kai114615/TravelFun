import { createRouter, createWebHashHistory } from 'vue-router';
import { useCartStore, useUserStore } from '@/stores';
import type { RouteRecordRaw } from 'vue-router';
import { createDiscreteApi } from 'naive-ui';

const { message } = createDiscreteApi(['message']);
const { VITE_TITLE } = import.meta.env;

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'Front',
    component: () => import('../layout/FrontLayout.vue'),
    children: [
      {
        path: '',
        name: 'Home',
        component: () => import('../views/front/Home/HomeView.vue'),
        meta: {
          title: VITE_TITLE,
        },
      },
      {
        path: 'mall',
        name: 'Mall',
        component: () => import('../views/front/Mall/MallView.vue'),
        meta: {
          title: '商城中心 - Travel Fun',
        },
      },
      {
        path: 'activity',
        name: 'Activity',
        component: () => import('../views/front/Activity/ActivityView.vue'),
        meta: {
          title: '主題育樂 - Travel Fun',
        },
      },
      {
        path: 'member',
        name: 'Member',
        component: () => import('../views/front/Member/MemberView.vue'),
        meta: {
          title: '會員中心 - Travel Fun',
          requiresAuth: true
        },
      },
      {
        path: 'forum',
        name: 'Forum',
        component: () => import('../views/front/Forum/ForumView.vue'),
        meta: {
          title: '討論區 - Travel Fun',
        },
      },
      {
        path: 'forum/post/:id',
        name: 'PostDetail',
        component: () => import('../views/front/Forum/components/PostDetail.vue'),
        meta: {
          title: '文章詳情 - Travel Fun',
        }
      },
      {
        path: 'login',
        name: 'Login',
        component: () => import('../views/front/Login/LoginView.vue'),
        meta: {
          title: '後台登入 - Travel Fun',
        },
      },
      {
        path: 'register',
        name: 'Register',
        component: () => import('../views/front/Login/components/Register.vue'),
        meta: {
          title: '註冊帳號 - Travel Fun',
        },
      },
      {
        path: 'country/:countryName',
        name: 'Country',
        component: () => import('../views/front/Country/CountryView.vue'),
        meta: {
          title: '台灣自由行 - Travel Fun',
        },
      },
      {
        path: 'city/:cityName',
        name: 'City',
        component: () => import('../views/front/City/CityView.vue'),
        meta: {
          title: '全台熱門景點 - Travel Fun',
        },
      },
      {
        path: 'city/:cityName/products/:category?',
        name: 'CityProducts',
        component: () => import('../views/front/Products/ProductsView.vue'),
        props: route => ({ sort: route.query.sort, mode: 'city' }),
        meta: {
          title: '全台熱門景點 - Travel Fun',
        },
      },
      {
        path: 'country/:countryName/products/:category?',
        name: 'CountryProducts',
        component: () => import('../views/front/Products/ProductsView.vue'),
        props: route => ({ sort: route.query.sort, mode: 'country' }),
        meta: {
          title: '台灣自由行 - Travel Fun',
        },
      },
      {
        path: 'product/:productId',
        name: 'Product',
        component: () => import('../views/front/Product/ProductView.vue'),
        meta: {
          title: '旅遊行程 - Travel Fun',
        },
      },
      {
        path: 'cart',
        name: 'Cart',
        component: () => import('../views/front/Cart/CartView.vue'),
        meta: {
          title: '購物車 - Travel Fun',
        },
        async beforeEnter(_to, _from) {
          const cartStore = useCartStore();
          await cartStore.getCarts();
        },
      },
      {
        path: 'booking',
        name: 'Book',
        component: () => import('../views/front/Book/BookView.vue'),
        children: [
          {
            path: 'order',
            name: 'Order',
            component: () => import('../views/front/Book/components/Order.vue'),
            meta: {
              title: '填寫資料 - Travel Fun',
            },
          },
          {
            path: 'pay/:orderId',
            name: 'Pay',
            component: () => import('../views/front/Book/components/Pay.vue'),
            meta: {
              title: '付款 - Travel Fun',
            },
          },
          {
            path: 'done/:orderId',
            name: 'Done',
            component: () => import('../views/front/Book/components/Done.vue'),
            meta: {
              title: '訂購完成 - Travel Fun',
            },
          },
        ],
      },
      {
        path: 'wishlist',
        name: 'WishList',
        component: () => import('../views/front/WishList/WishListView.vue'),
        meta: {
          title: '我的最愛 - Travel Fun',
        },
      },
      {
        path: 'about',
        name: 'About',
        component: () => import('../views/front/About/AboutView.vue'),
        meta: {
          title: '關於我們 - Travel Fun',
        },
      },
    ],
  },
  {
    path: '/admin',
    name: 'Dashboard',
    component: () => import('../layout/Dashboard.vue'),
    children: [
      {
        path: 'home',
        name: 'AdminHome',
        component: () => import('../views/admin/Home/AdminHomeView.vue'),
        meta: {
          title: 'Dashboard',
          requiresAuth: true,
        },
      },
      {
        path: 'list',
        meta: {
          title: '列表頁面',
          requiresAuth: true,
        },
        children: [
          {
            path: 'products',
            name: 'AdminProducts',
            component: () => import('../views/admin/List/Product/AdminProducts.vue'),
            meta: {
              title: '產品列表',
              requiresAuth: true,
            },
          },
          {
            path: 'orders',
            name: 'AdminOrders',
            component: () => import('../views/admin/List/Order/AdminOrders.vue'),
            meta: {
              title: '訂單列表',
              requiresAuth: true,
            },
          },
          {
            path: 'coupons',
            name: 'AdminCoupons',
            component: () => import('../views/admin/List/Coupon/AdminCoupons.vue'),
            meta: {
              title: '優惠卷列表',
              requiresAuth: true,
            },
          },
        ],
      },
    ],
  },
  {
    path: '/member',
    name: 'MemberLayout',
    component: () => import('@/views/front/Member/MemberLayout.vue'),
    meta: { 
      requiresAuth: true,
      title: '會員中心'
    },
    children: [
      {
        path: 'dashboard',
        name: 'MemberDashboard',
        component: () => import('@/views/front/Member/DashboardView.vue'),
        meta: { 
          requiresAuth: true,
          title: '會員中心' 
        }
      },
      {
        path: 'profile',
        name: 'MemberProfile',
        component: () => import('@/views/front/Member/ProfileView.vue'),
        meta: { 
          requiresAuth: true,
          title: '個人資料' 
        }
      },
      {
        path: 'orders',
        name: 'MemberOrders',
        component: () => import('@/views/front/Member/OrdersView.vue'),
        meta: { 
          requiresAuth: true,
          title: '訂單管理' 
        }
      },
      {
        path: 'messages',
        name: 'MemberMessages',
        component: () => import('@/views/front/Member/MessagesView.vue'),
        meta: { 
          requiresAuth: true,
          title: '訊息中心' 
        }
      },
      {
        path: 'coupons',
        name: 'MemberCoupons',
        component: () => import('@/views/front/Member/CouponsView.vue'),
        meta: { 
          requiresAuth: true,
          title: '優惠券' 
        }
      }
    ]
  }
];

const router = createRouter({
  history: createWebHashHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior() {
    return { top: 0 };
  },
});

// 全局前置守衛
router.beforeEach((to, from, next) => {
  const userStore = useUserStore();
  
  // 檢查路由是否需要認證
  if (to.meta.requiresAuth && !userStore.loginStatus) {
    // 如果需要認證但用戶未登入，重定向到登入頁面
    next({ 
      name: 'Login',
      query: { redirect: to.fullPath }
    });
  } else {
    // 更新頁面標題
    if (to.meta.title) {
      document.title = to.meta.title;
    }
    next();
  }
});

export default router;

import { createRouter, createWebHashHistory } from 'vue-router';
import Mall from '../views/Mall.vue';
import ProductDetail from '../views/ProductDetail.vue';
import Home from '../views/Home.vue';
import Register from '../views/Register.vue';

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: {
      title: '首頁'
    }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: {
      title: '註冊'
    }
  },
  {
    path: '/mall',
    name: 'Mall',
    component: Mall,
    meta: {
      title: '商城中心'
    }
  },
  {
    path: '/mall/product/:id',
    name: 'ProductDetail',
    component: ProductDetail,
    meta: {
      title: '商品詳情'
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
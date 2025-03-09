import { defineStore } from 'pinia';
import { computed, ref } from 'vue';
import type { Cart as CartType } from '@/types';

export interface CartItem {
  id: number;
  name: string;
  price: number;
  quantity: number;
  image_url: string;
  stock: number;
}

export const useCartStore = defineStore('cart', () => {
  const items = ref<CartItem[]>([]);

  // 計算購物車總數量
  const totalNum = computed(() => {
    return items.value.reduce((total, item) => total + item.quantity, 0);
  })

  // 計算購物車總金額
  const totalAmount = computed(() => {
    return items.value.reduce((total, item) => total + item.price * item.quantity, 0);
  })

  // 轉換為 ShopCart 組件需要的格式
  const cartList = computed<CartType[]>(() => {
    return items.value.map(item => ({
      id: String(item.id),
      product_id: String(item.id),
      qty: item.quantity,
      total: item.price * item.quantity,
      final_total: item.price * item.quantity,
      buy_date: Date.now(),
      product: {
        id: item.id,
        title: item.name,
        description: '',
        price: item.price,
        imageUrl: item.image_url
      }
    }));
  })

  // 添加商品到購物車
  const addToCart = (product: CartItem) => {
    const existingItem = items.value.find(item => item.id === product.id);
    if (existingItem) {
      if (existingItem.quantity < existingItem.stock) {
        existingItem.quantity++;
        items.value = [...items.value]; // 強制更新
      }
    } else {
      items.value.push({ ...product, quantity: 1 });
    }
    // 保存到 localStorage
    localStorage.setItem('cart', JSON.stringify(items.value));
  };

  // 從購物車移除商品
  const removeFromCart = (productId: number) => {
    items.value = items.value.filter(item => item.id !== productId);
    // 保存到 localStorage
    localStorage.setItem('cart', JSON.stringify(items.value));
  };

  // 更新商品數量
  const updateQuantity = (productId: number, quantity: number) => {
    const item = items.value.find(item => item.id === productId);
    if (item) {
      if (quantity > 0 && quantity <= item.stock) {
        item.quantity = quantity;
        items.value = [...items.value]; // 強制更新
        // 保存到 localStorage
        localStorage.setItem('cart', JSON.stringify(items.value));
      }
    }
  };

  // 清空購物車
  const clearCart = () => {
    items.value = [];
    // 清空 localStorage 中的購物車數據
    localStorage.removeItem('cart');
  };

  // 初始化購物車
  const initCart = () => {
    const savedCart = localStorage.getItem('cart');
    if (savedCart)
      items.value = JSON.parse(savedCart);
  };

  // 在 store 創建時初始化購物車
  initCart();

  return {
    items,
    totalNum,
    totalAmount,
    cartList,
    addToCart,
    updateQuantity,
    removeFromCart,
    clearCart,
    initCart
  };
})

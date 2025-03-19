import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000/shop/api';

// 獲取授權配置函數
function getAuthConfig() {
  const token = localStorage.getItem('access_token');
  if (!token) {
    console.error('獲取授權配置失敗：未找到訪問令牌');
    return null;
  }
  
  return {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    }
  };
}

// 產品介面定義
export interface Product {
  id: number;
  name: string;
  category: string;
  price: number;
  description: string;
  stock: number;
  image: string;
  is_available: boolean;
  created_at: string;
  updated_at: string;
}

// 訂單項目介面定義
export interface OrderItem {
  id: number;
  product: Product;
  quantity: number;
  subtotal: number;
  order: number;
}

// 訂單介面定義
export interface Order {
  id: number;
  order_number: string;
  user: number;
  user_name?: string;
  status: string;
  payment_status: string;
  shipping_address?: string;
  total_amount: number;
  created_at: string;
  updated_at: string;
  items: OrderItem[];
}

// 訂單回應介面定義
export interface OrdersResponse {
  orders?: Order[];
  success: boolean;
  message?: string;
  pending_orders_count?: number;
  total_orders_count?: number;
}

export const ShoppingAPI = {
  // 獲取所有產品
  getAllProducts: async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/products/`);
      return response.data;
    } catch (error) {
      console.error('獲取所有產品時出錯:', error);
      return { success: false, message: '獲取產品失敗' };
    }
  },
  
  // 獲取單個產品詳情
  getProductDetail: async (productId: number) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/products/${productId}/`);
      return response.data;
    } catch (error) {
      console.error(`獲取產品 ${productId} 詳情時出錯:`, error);
      return { success: false, message: '獲取產品詳情失敗' };
    }
  },
  
  // 獲取產品類別
  getProductCategories: async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/categories/`);
      return response.data;
    } catch (error) {
      console.error('獲取產品類別時出錯:', error);
      return { success: false, message: '獲取產品類別失敗' };
    }
  },
  
  // 獲取用戶訂單
  getUserOrders: async (): Promise<OrdersResponse> => {
    // 檢查授權
    const authConfig = getAuthConfig();
    if (!authConfig) {
      return { success: false, message: '未登入，無法獲取訂單' };
    }
    
    try {
      console.log('嘗試獲取用戶訂單...');
      
      // 嘗試主要API路徑
      try {
        const response = await axios.get(`${API_BASE_URL}/shopping/orders/user/`, authConfig);
        console.log('API訂單響應:', response.data);
        
        if (Array.isArray(response.data)) {
          // 如果返回的是訂單數組
          return {
            success: true,
            orders: response.data,
            total_orders_count: response.data.length,
            pending_orders_count: response.data.filter(order => order.status === 'pending').length
          };
        } else if (response.data.orders) {
          // 如果返回的是包含orders數組的對象
          return {
            success: true,
            orders: response.data.orders,
            total_orders_count: response.data.total_orders_count || response.data.orders.length,
            pending_orders_count: response.data.pending_orders_count || 0
          };
        } else if (response.data.results) {
          // 如果返回的是Django REST分頁格式
          return {
            success: true,
            orders: response.data.results,
            total_orders_count: response.data.count || response.data.results.length,
            pending_orders_count: response.data.results.filter(order => order.status === 'pending').length
          };
        }
        
        // 如果無法識別格式，但有數據，嘗試提取
        return {
          success: true,
          orders: response.data,
          total_orders_count: 0,
          pending_orders_count: 0
        };
      } catch (error) {
        console.error('使用主要API路徑獲取訂單失敗:', error);
        
        // 嘗試備用API路徑
        try {
          const alternativeResponse = await axios.get(`${API_BASE_URL}/orders/user/`, authConfig);
          
          if (Array.isArray(alternativeResponse.data)) {
            return {
              success: true,
              orders: alternativeResponse.data,
              total_orders_count: alternativeResponse.data.length,
              pending_orders_count: alternativeResponse.data.filter(order => order.status === 'pending').length
            };
          } else if (alternativeResponse.data.orders) {
            return {
              success: true,
              orders: alternativeResponse.data.orders,
              total_orders_count: alternativeResponse.data.total_orders_count || alternativeResponse.data.orders.length,
              pending_orders_count: alternativeResponse.data.pending_orders_count || 0
            };
          }
          
          return {
            success: true,
            orders: alternativeResponse.data,
            total_orders_count: 0,
            pending_orders_count: 0
          };
        } catch (alternativeError) {
          console.error('使用備用API路徑獲取訂單也失敗:', alternativeError);
          throw new Error('所有API路徑都獲取訂單失敗');
        }
      }
    } catch (error) {
      console.error('獲取用戶訂單失敗:', error);
      return { 
        success: false, 
        message: '獲取訂單失敗，請稍後再試',
        orders: []
      };
    }
  },
  
  // 獲取訂單詳情
  getOrderDetail: async (orderNumber: string): Promise<{ success: boolean, order?: Order, message?: string }> => {
    // 檢查授權
    const authConfig = getAuthConfig();
    if (!authConfig) {
      return { success: false, message: '未登入，無法獲取訂單詳情' };
    }
    
    try {
      console.log(`嘗試獲取訂單 ${orderNumber} 詳情...`);
      
      // 嘗試主要API路徑
      try {
        const response = await axios.get(`${API_BASE_URL}/shopping/orders/${orderNumber}/`, authConfig);
        console.log('訂單詳情響應:', response.data);
        
        return {
          success: true,
          order: response.data
        };
      } catch (error) {
        console.error('使用主要API路徑獲取訂單詳情失敗:', error);
        
        // 嘗試備用API路徑
        try {
          const alternativeResponse = await axios.get(`${API_BASE_URL}/orders/${orderNumber}/`, authConfig);
          
          return {
            success: true,
            order: alternativeResponse.data
          };
        } catch (alternativeError) {
          console.error('使用備用API路徑獲取訂單詳情也失敗:', alternativeError);
          throw new Error('所有API路徑都獲取訂單詳情失敗');
        }
      }
    } catch (error) {
      console.error(`獲取訂單 ${orderNumber} 詳情失敗:`, error);
      return { 
        success: false, 
        message: '獲取訂單詳情失敗，請稍後再試'
      };
    }
  }
};

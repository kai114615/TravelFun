import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/shop';

export interface Product {
  id: number
  name: string
  category: string
  brand: string
  price: string
  description: string
  stock: number
  is_active: boolean
  image_url: string
  original_price?: string
  discount?: number
}

export const ShoppingAPI = {
  // 獲取所有商品
  getAllProducts: async (): Promise<Product[]> => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/products/`);
      return response.data;
    }
    catch (error) {
      console.error('獲取商品列表失敗:', error);
      throw error;
    }
  },

  // 獲取單個商品詳情
  getProduct: async (id: number): Promise<Product> => {
    try {
      console.log('Calling API with ID:', id);
      const response = await axios.get(`${API_BASE_URL}/api/products/${id}/`);
      console.log('API Response:', response.data);
      if (!response.data)
        throw new Error('商品不存在');

      return response.data;
    }
    catch (error) {
      console.error('獲取商品詳情失敗:', error);
      throw error;
    }
  },

  // 獲取商品分類
  getCategories: async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/categories/`);
      return response.data;
    }
    catch (error) {
      console.error('獲取商品分類失敗:', error);
      throw error;
    }
  },
};

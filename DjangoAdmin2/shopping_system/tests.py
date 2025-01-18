from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Product
import json

class ProductAPITest(APITestCase):
    def setUp(self):
        """測試前的初始化設置"""
        self.client = Client()
        self.products_url = '/admin-dashboard/shop/api/products/'
        # 創建測試商品
        self.test_product = Product.objects.create(
            name='測試商品',
            price=100,
            description='這是一個測試商品',
            stock=10
        )

    def test_get_products_list(self):
        """測試獲取商品列表"""
        response = self.client.get(self.products_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.json()) > 0)

    def test_create_product(self):
        """測試創建新商品"""
        new_product_data = {
            'name': '新測試商品',
            'price': 200,
            'description': '這是一個新的測試商品',
            'stock': 5
        }
        response = self.client.post(
            self.products_url,
            data=json.dumps(new_product_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['name'], new_product_data['name'])

    def test_get_single_product(self):
        """測試獲取單個商品"""
        response = self.client.get(f'{self.products_url}{self.test_product.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['name'], self.test_product.name)

    def test_update_product(self):
        """測試更新商品"""
        updated_data = {
            'name': '更新後的商品',
            'price': 150
        }
        response = self.client.put(
            f'{self.products_url}{self.test_product.id}/',
            data=json.dumps(updated_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['name'], updated_data['name'])

    def test_delete_product(self):
        """測試刪除商品"""
        response = self.client.delete(f'{self.products_url}{self.test_product.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # 確認商品已被刪除
        response = self.client.get(f'{self.products_url}{self.test_product.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND) 
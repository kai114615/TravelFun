from django.urls import path
from . import views

app_name = 'shopping_system'

urlpatterns = [
    # 商品管理
    path('admin-dashboard/shop/layout/', views.shop_layout, name='shop_layout'),
    path('admin-dashboard/shop/products/', views.product_list, name='product_list'),
    path('admin-dashboard/shop/products/create/', views.product_create, name='product_create'),
    path('admin-dashboard/shop/products/<int:pk>/', views.product_detail, name='product_detail'),
    path('admin-dashboard/shop/products/<int:pk>/update/', views.product_update, name='product_update'),
    path('admin-dashboard/shop/products/<int:pk>/delete/', views.product_delete, name='product_delete'),
    path('admin-dashboard/shop/api-test/', views.shop_api_test, name='shop_api_test'),
    
    # API 端點
    path('api/products/', views.product_api, name='product_api_list'),
    path('api/products/<int:product_id>/', views.product_api, name='product_api_detail'),
    path('api/carousels/', views.carousel_api, name='carousel_api_list'),
    path('api/carousels/<int:carousel_id>/', views.carousel_api, name='carousel_api_detail'),
    path('api/categories/', views.category_display_api, name='category_display_api_list'),
    path('api/categories/<int:category_id>/', views.category_display_api, name='category_display_api_detail'),
    path('api/recommended/', views.recommended_product_api, name='recommended_product_api_list'),
    path('api/recommended/<int:recommended_id>/', views.recommended_product_api, name='recommended_product_api_detail'),
    
    # 新增：購物車和訂單相關的API
    path('api/shopping/cart/add/', views.add_to_cart, name='add_to_cart'),
    path('api/shopping/orders/create/', views.create_order, name='create_order'),
    
    # 新增：導出商品資料到JSON檔案的API
    path('api/export-mall-products/', views.export_mall_products_json, name='export_mall_products_json'),
]
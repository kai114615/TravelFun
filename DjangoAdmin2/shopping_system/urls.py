from django.urls import path, include
from . import views
from .image_search.api.views import ImageSearchAPIView

app_name = 'shopping_system'

urlpatterns = [
    # 商品管理
    path('admin-dashboard/shop/products/', views.product_list, name='product_list'),
    path('admin-dashboard/shop/products/create/', views.product_create, name='product_create'),
    path('admin-dashboard/shop/products/<int:pk>/', views.product_detail, name='product_detail'),
    path('admin-dashboard/shop/products/<int:pk>/update/', views.product_update, name='product_update'),
    path('admin-dashboard/shop/products/<int:pk>/delete/', views.product_delete, name='product_delete'),
    
    # 後台其他URL
    path('admin-dashboard/shop/layout/', views.shop_layout, name='shop_layout'),
    path('admin-dashboard/shop/api-test/', views.shop_api_test, name='shop_api_test'),
    
    # 訂單管理 - 使用與商品列表相同的URL結構
    path('admin-dashboard/shop/orders/', views.order_list, name='order_list'),
    path('admin-dashboard/shop/orders/<int:pk>/', views.order_detail, name='order_detail'),
    path('admin-dashboard/shop/orders/<int:pk>/update-status/', views.order_update_status, name='order_update_status'),
    path('admin-dashboard/shop/orders/<int:pk>/delete/', views.order_delete, name='order_delete'),
    
    # API 端點
    path('api/products/', views.product_api, name='product_api_list'),
    path('api/products/<int:product_id>/', views.product_api, name='product_api_detail'),
    path('api/carousels/', views.carousel_api, name='carousel_api_list'),
    path('api/carousels/<int:carousel_id>/', views.carousel_api, name='carousel_api_detail'),
    path('api/categories/', views.category_display_api, name='category_display_api_list'),
    path('api/categories/<int:category_id>/', views.category_display_api, name='category_display_api_detail'),
    path('api/recommended/', views.recommended_product_api, name='recommended_product_api_list'),
    path('api/recommended/<int:recommended_id>/', views.recommended_product_api, name='recommended_product_api_detail'),
    
    # AI圖像搜索API
    path('api/image-search/', ImageSearchAPIView.as_view(), name='image_search_api'),
    
    # 新增：購物車和訂單相關的API
    path('api/shopping/cart/add/', views.add_to_cart, name='add_to_cart'),
    path('api/shopping/orders/', views.all_orders, name='api_all_orders'),
    path('api/shopping/orders/<int:order_id>/', views.order_api_detail, name='api_order_detail'),
    path('api/shopping/orders/<str:order_id>/', views.order_api_detail, name='api_order_detail_str'),
    path('api/shopping/user-orders/', views.user_orders, name='api_user_orders'),
    path('api/shopping/order-detail/<str:order_id>/', views.order_api_detail, name='api_order_detail_alt'),
    
    # 新增：導出商品資料到JSON檔案的API
    path('api/export-mall-products/', views.export_mall_products_json, name='export_mall_products_json'),
    
    # 綠界金流相關的API
    path('api/shopping/ecpay/payment/', views.ecpay_payment, name='ecpay_payment'),
    path('api/ecpay/notify/', views.ecpay_notify, name='ecpay_notify'),
    path('api/ecpay/payment_info/', views.ecpay_payment_info, name='ecpay_payment_info'),

    # 新增物流 API 路由
    path('api/logistics/create/', views.create_shipping_order, name='create_shipping_order'),
    path('api/logistics/callback/', views.logistics_callback, name='logistics_callback'),

    # 訂單創建API (放置在上面路由之前以避免衝突)
    path('api/orders/create/', views.create_order, name='create_order'),
    path('shop/api/shopping/orders/create/', views.create_order, name='api_create_order_shop'),
    path('api/orders/create/', views.create_order, name='api_create_order_alt'),

    # 補充一個額外的路徑，不帶尾部斜線的版本
    path('api/orders/create', views.create_order, name='create_order_no_slash'),

    # 添加額外的訂單創建路由 - 簡單路徑，直接指向視圖函數
    path('', views.create_order),  # 用於匹配從root forwarding過來的請求
]
from django.urls import path
from . import views

urlpatterns = [
    # 用戶認證相關 API
    path('user/signin/', views.signin, name='api-signin'),
    path('user/check-auth/', views.check_auth, name='api-check-auth'),
    path('user/logout/', views.logout, name='api-logout'),
    path('user/register/', views.register, name='api-register'),
    
    # 其他 API 端點
    path('cart/', views.cart_list, name='cart-list'),
    path('products/all/', views.product_list, name='product-list'),
] 
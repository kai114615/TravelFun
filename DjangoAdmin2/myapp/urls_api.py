from django.urls import path
from . import api

urlpatterns = [
    # 產品相關
    path('products/all/', api.product_list_all, name='product-list-all'),
    path('products/', api.product_list, name='product-list'),
    path('product/<int:pk>/', api.product_detail, name='product-detail'),
    
    # 購物車相關
    path('cart/', api.cart_list, name='cart-list'),
    path('cart/<int:pk>/', api.cart_detail, name='cart-detail'),
    path('cart/add/', api.cart_add, name='cart-add'),
    path('cart/remove/<int:pk>/', api.cart_remove, name='cart-remove'),
    path('cart/clear/', api.cart_clear, name='cart-clear'),
] 
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('user-dashboard/', views.user_dashboard, name='user_dashboard'),
    path('profile/update/', views.profile_update, name='profile_update'),
    
    # 會員系統
    path('admin-dashboard/users/list/', views.member_list, name='member_list'),
    path('admin-dashboard/users/list/<int:pk>/', views.member_detail, name='member_detail'),
    path('admin-dashboard/users/list/<int:pk>/update/', views.member_update, name='member_update'),
    path('admin-dashboard/users/list/<int:pk>/delete/', views.member_delete, name='member_delete'),
    path('admin-dashboard/users/api-test/', views.member_api_test, name='member_api_test'),
    
    # 會員 API 端點
    path('api/users/', views.member_api, name='member_api_list'),
    path('api/users/<int:member_id>/', views.member_api, name='member_api_detail'),
    path('api/member/profile/', views.profile_api, name='profile_api'),
    path('api/member/profile/update/', views.profile_update_api, name='profile_update_api'),
    
    # 商城系統
    path('admin-dashboard/shop/layout/', views.shop_layout, name='shop_layout'),
    path('admin-dashboard/shop/products/', views.product_list, name='product_list'),
    path('admin-dashboard/shop/products/create/', views.product_create, name='product_create'),
    path('admin-dashboard/shop/products/<int:pk>/', views.product_detail, name='product_detail'),
    path('admin-dashboard/shop/products/<int:pk>/update/', views.product_update, name='product_update'),
    path('admin-dashboard/shop/products/<int:pk>/delete/', views.product_delete, name='product_delete'),
    path('admin-dashboard/shop/api-test/', views.shop_api_test, name='shop_api_test'),
    
    # 商城 API 端點
    path('api/products/', views.product_api, name='product_api_list'),
    path('api/products/<int:product_id>/', views.product_api, name='product_api_detail'),
    
    path('members/', views.member_list, name='member_list'),
    path('members/<int:pk>/', views.member_detail, name='member_detail'),
    path('members/create/', views.member_create, name='member_create'),
    path('members/<int:pk>/update/', views.member_update, name='member_update'),
    path('members/<int:pk>/delete/', views.member_delete, name='member_delete'),
    path('set-admin/', views.set_admin, name='set_admin'),
    path('sweetalert/', views.sweetalert_view, name='sweetalert'),
    path('register-v2/', views.register_v2_view, name='register_v2'),
    path('messages/inbox/', views.inbox, name='inbox'),
    path('messages/sent/', views.sent_messages, name='sent_messages'),
    path('messages/compose/', views.compose_message, name='compose_message'),
    path('messages/<int:message_id>/', views.message_detail, name='message_detail'),
    path('messages/<int:message_id>/delete/', views.delete_message, name='delete_message'),
    path('api/user/register/', views.register_api, name='api-register'),
    path('api/user/signin/', views.signin, name='api-signin'),
    path('api/user/logout/', views.logout_api, name='api-logout'),
    path('api/user/check-auth/', views.check_auth, name='api-check-auth'),
    path('api/user/profile/', views.profile_api, name='api-profile'),
    path('api/posts/create/', views.create_post, name='create_post'),
]
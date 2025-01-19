from django.urls import path
from . import views

app_name = 'myapp'  # 添加應用程序命名空間

urlpatterns = [
    # API 路由
    path('register/', views.register_api, name='api-register'),
    path('signin/', views.signin, name='api-signin'),
    path('logout/', views.logout_api, name='api-logout'),
    path('check-auth/', views.check_auth, name='api-check-auth'),
    path('profile/', views.member_api, name='member-api'),
    
    # 頁面路由
    path('auth/login/', views.login_view, name='login-page'),
    path('auth/register/', views.register_view, name='register-page'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # 會員 API
    path('profile/<int:member_id>/', views.member_api, name='member_api_detail'),
    
    # 管理員路由
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/users/', views.member_list, name='member_list'),
    path('admin/users/<int:pk>/', views.member_detail, name='member_detail'),
    path('admin/users/<int:pk>/update/', views.member_update, name='member_update'),
    path('admin/users/<int:pk>/delete/', views.member_delete, name='member_delete'),
] 
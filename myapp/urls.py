from django.urls import path
from . import views

urlpatterns = [
    # 用戶認證相關
    path('api/user/check-auth/', views.check_auth, name='check-auth'),
    path('api/user/logout/', views.logout, name='api-logout'),
    path('api/user/register/', views.register, name='register'),
] 
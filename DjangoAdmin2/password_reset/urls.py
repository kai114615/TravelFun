from django.urls import path
from . import views

# 傳統網頁視圖 URL 配置
urlpatterns = [
    path('', views.password_reset_request, name='password_reset_request'),
    path('verify/', views.password_reset_verify, name='password_reset_verify'),
    path('confirm/', views.password_reset_confirm, name='password_reset_confirm'),
    
    # API 端點
    path('api/request/', views.password_reset_request_api, name='password_reset_request_api'),
    path('api/verify/', views.verify_code_api, name='verify_code_api'),
    path('api/reset/', views.reset_password_api, name='reset_password_api'),
] 
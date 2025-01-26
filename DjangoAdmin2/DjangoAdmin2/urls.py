from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

# 健康檢查視圖函數
@csrf_exempt
def health_check(request):
    return JsonResponse({'status': 'ok'})

# API 路由
urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API 路由
    path('', include('myapp.urls')),  # 包含 myapp 的所有 URLs
    path('restaurant/', include('restaurant_system.urls')),
    path('shop/', include('shopping_system.urls')),
    path('travel/', include('travel_app.urls')),
    path('theme/', include('theme_entertainment.urls')),
    path('', include('forum_system.urls')),
    path('admin-dashboard/travel_app/', include('travel_app.urls')),
    path('api/health-check/', health_check, name='health_check'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/v1/', include('myapp.urls_api')),
    
    # CKEditor 5 URLs
    path('ckeditor5/', include('django_ckeditor_5.urls')),
]

# 在開發環境中提供媒體文件服務
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# 添加 CORS 設定
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3333",
    "http://127.0.0.1:3333",
]
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
] 
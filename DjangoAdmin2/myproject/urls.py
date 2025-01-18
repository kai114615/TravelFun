from django.contrib import admin
from django.urls import path, include
from myapp import views
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

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('myapp.urls')),
    path('restaurant/', include('restaurant_system.urls')),
    path('shop/', include('shopping_system.urls')),
    path('travel/', include('travel_app.urls')),
    path('theme/', include('theme_entertainment.urls')),
    path('', include('forum_system.urls')),
    path('admin-dashboard/travel_app/', include('travel_app.urls')),
    path('api/health-check/', health_check, name='health_check'),
    # JWT 認證端點
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    # API v1 路由
    path('api/v1/', include('myapp.urls_api')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

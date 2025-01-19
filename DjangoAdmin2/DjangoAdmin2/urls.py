from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# API 路由
urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API 路由
    path('', include('myapp.urls')),  # 包含 myapp 的所有 URLs
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # 其他應用路由
    path('', include('forum_system.urls')),
    path('', include('shopping_system.urls')),
    path('', include('travel_app.urls')),
    
    # CKEditor 5 URLs
    path('ckeditor5/', include('django_ckeditor_5.urls')),
]

# 在開發環境中提供媒體文件服務
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 
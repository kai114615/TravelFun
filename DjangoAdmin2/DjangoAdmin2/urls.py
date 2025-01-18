from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('forum_system.urls')),
    path('', include('shopping_system.urls')),
    path('travel/', include('travel_app.urls')),
    path('admin-dashboard/travel_app/', include('travel_app.urls')),
    
    # JWT 認證
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # CKEditor 5 URLs
    path('ckeditor5/', include('django_ckeditor_5.urls')),
] 

# 在開發環境中提供媒體文件服務
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 
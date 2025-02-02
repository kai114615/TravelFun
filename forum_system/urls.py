from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# API路由
router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet)
router.register(r'posts', views.NewForumViewSet, basename='forum-posts')

# 後台API路由
admin_router = DefaultRouter()
admin_router.register(r'admin/posts', views.AdminPostViewSet)
admin_router.register(r'admin/categories', views.AdminCategoryViewSet)
admin_router.register(r'admin/comments', views.AdminCommentViewSet)

urlpatterns = [
    # API路由
    path('api/', include(router.urls)),
    path('api/', include(admin_router.urls)),
    
    # 後台管理頁面路由
    path('user-dashboard/forum/articles/', views.AdminPostListView.as_view(), name='forum_article_list'),
    path('user-dashboard/forum/categories/', views.AdminCategoryListView.as_view(), name='forum_category_list'),
    path('user-dashboard/forum/comments/', views.AdminCommentListView.as_view(), name='forum_comment_list'),
    
    # API測試頁面路由
    path('user-dashboard/forum/api-test/', views.AdminApiTestView.as_view(), name='forum_api_test'),
    
    # 公開測試 API 端點 - 不帶ID的路由
    path('api/public/posts/', views.PublicTestPostApiView.as_view(), name='public_test_post_api'),
    path('api/public/categories/', views.PublicTestCategoryApiView.as_view(), name='public_test_category_api'),
    
    # 公開測試 API 端點 - 帶ID的路由
    path('api/public/posts/<int:pk>/', views.PublicTestPostApiView.as_view(), name='public_test_post_api_detail'),
    path('api/public/categories/<int:pk>/', views.PublicTestCategoryApiView.as_view(), name='public_test_category_api_detail'),
] 
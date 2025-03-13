from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# API路由
router = DefaultRouter()
router.register(r'forum', views.PublicForumViewSet, basename='forum')
router.register(r'categories', views.CategoryViewSet)
router.register(r'posts', views.PostViewSet)
router.register(r'comments', views.CommentViewSet)
router.register(r'saved-posts', views.SavedPostViewSet, basename='saved-posts')
router.register(r'tags', views.TagViewSet, basename='tags')

# 後台API路由
admin_router = DefaultRouter()
admin_router.register(r'admin/posts', views.AdminPostViewSet)
admin_router.register(r'admin/categories', views.AdminCategoryViewSet)
admin_router.register(r'admin/comments', views.AdminCommentViewSet)
admin_router.register(r'admin/tags', views.TagViewSet)

# 公開API路由
public_router = DefaultRouter()
public_router.register(r'public/categories', views.PublicCategoryViewSet)
public_router.register(r'public/posts', views.PublicPostViewSet)
public_router.register(r'public/tags', views.TagViewSet)

urlpatterns = [
    # API路由
    path('api/', include(router.urls)),
    path('api/', include(admin_router.urls)),
    path('api/', include(public_router.urls)),
    
    # 後台管理頁面路由
    path('user-dashboard/forum/articles/', views.AdminPostListView.as_view(), name='forum_article_list'),
    path('user-dashboard/forum/articles/<int:pk>/', views.AdminPostDetailView.as_view(), name='admin-post-detail'),
    path('user-dashboard/forum/articles/<int:pk>/edit/', views.AdminPostEditView.as_view(), name='admin-post-edit'),
    path('user-dashboard/forum/categories/', views.AdminCategoryListView.as_view(), name='forum_category_list'),
    path('user-dashboard/forum/comments/', views.AdminCommentListView.as_view(), name='forum_comment_list'),
    path('user-dashboard/forum/tags/', views.AdminTagListView.as_view(), name='forum_tag_list'),
    
    # 文章刪除API端點
    path('api/forum/posts/<int:pk>/delete/', views.PublicForumViewSet.as_view({'post': 'delete_post'}), name='delete-post'),
    # 另一個刪除API端點 - 使用標準DELETE方法（會調用destroy方法）
    path('api/forum/posts/<int:pk>/', views.PublicForumViewSet.as_view({'delete': 'destroy'}), name='post-delete'),
    
    # API測試頁面路由
    path('user-dashboard/forum/api-test/', views.AdminApiTestView.as_view(), name='forum_api_test'),
    
    # API測試端點 - 不帶ID的路由
    path('api/test/posts/', views.TestPostApiView.as_view(), name='test_post_api'),
    path('api/test/categories/', views.TestCategoryApiView.as_view(), name='test_category_api'),
    path('api/test/comments/', views.TestCommentApiView.as_view(), name='test_comment_api'),
    
    # API測試端點 - 帶ID的路由
    path('api/test/posts/<int:pk>/', views.TestPostApiView.as_view(), name='test_post_api_detail'),
    path('api/test/categories/<int:pk>/', views.TestCategoryApiView.as_view(), name='test_category_api_detail'),
    path('api/test/comments/<int:pk>/', views.TestCommentApiView.as_view(), name='test_comment_api_detail'),
    
    # 測試無權限分類創建API
    path('api/test-create-category/', views.test_category_create, name='test_create_category'),
    
    # 測試無權限分類更新API
    path('api/test-update-category/', views.test_category_update, name='test_update_category'),
    
    # 測試無權限分類刪除API
    path('api/test-delete-category/', views.test_category_delete, name='test_delete_category'),
    
    # 測試無權限評論刪除API
    path('api/test-delete-comment/', views.test_comment_delete, name='test_delete_comment'),
    
    # 添加一個直接的評論刪除路由 (透過GET請求)
    path('api/direct-delete-comment/<int:comment_id>/', views.direct_comment_delete, name='direct_comment_delete'),
    
    # 評論相關的 API 端點
    path('api/forum/posts/<int:pk>/comments/', views.PostViewSet.as_view({'get': 'get_comments'}), name='post-comments'),
    path('api/forum/posts/<int:pk>/add_comment/', views.PostViewSet.as_view({'post': 'add_comment'}), name='add-comment'),
    path('api/forum/comments/<int:pk>/delete_comment/', views.CommentViewSet.as_view({'post': 'delete_comment'}), name='delete-comment'),
    
    # 增加觀看數 API 端點
    path('api/f/increment-views/<int:post_id>', views.increment_views, name='increment-views'),
]
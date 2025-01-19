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
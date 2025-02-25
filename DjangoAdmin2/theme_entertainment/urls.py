"""
主題育樂活動管理系統的 URL 配置

API 端點說明：
1. GET    /admin-dashboard/entertainment/activities/
   - 獲取活動列表
   - 返回所有活動數據

2. POST   /admin-dashboard/entertainment/activities/create/
   - 創建新活動
   - 需要提供必要的活動信息

3. PUT    /admin-dashboard/entertainment/activities/<event_id>/
   - 更新指定活動
   - 可以選擇性更新任何活動欄位

4. DELETE /admin-dashboard/entertainment/activities/<event_id>/delete/
   - 刪除指定活動
   - 永久刪除，請謹慎使用
"""

from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt

app_name = 'theme_entertainment'

urlpatterns = [
    # 前端 API 路由
    path('activities/api/list/',
         csrf_exempt(views.activity_list),
         name='activity_list'),

    # 新增用於更新本地數據的API
#     path('activities/api/sync/',
#          csrf_exempt(views.sync_activities),
#          name='sync_activities'),

    # 後台管理頁面路由
    path('activities/',
         views.activity_management,
         name='activity_management'),

    path('activities/create/',
         views.create_event,
         name='create_activity'),

    # 後台 API 路由 - 需要認證
    path('activities/list/',
         views.get_events,
         name='admin_events'),

    # 活動詳情 API 路由
    path('activities/api/<int:id>/',
         views.get_event_detail,
         name='event_detail'),

    path('activities/<int:event_id>/update/',
         views.update_event,
         name='update_event'),

    path('activities/<int:event_id>/delete/',
         views.delete_event,
         name='delete_event'),
]

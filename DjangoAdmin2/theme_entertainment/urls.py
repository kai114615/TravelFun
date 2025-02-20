from django.urls import path
from . import views

app_name = 'theme_entertainment'

urlpatterns = [
    path('list/', views.theme_list, name='theme_list'),
    path('create/', views.theme_create, name='theme_create'),
    path('activities/', views.activity_management, name='activity_management'),
    path('api/events/', views.ActivityListView.as_view(), name='activity-list'),
    path('api/events/<int:pk>/', views.ActivityDetailView.as_view(),
         name='activity-detail'),
]

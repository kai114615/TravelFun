from django.shortcuts import render
from rest_framework import viewsets, permissions, filters
from rest_framework.response import Response
from .models import CultureActivity, NewTaipeiActivity, TaipeiActivity, TFAMActivity
from rest_framework import serializers
from datetime import datetime
from .serializers import ActivitySerializer
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from itertools import chain
from rest_framework.generics import ListAPIView, RetrieveAPIView
from django.db import connection
import logging

logger = logging.getLogger(__name__)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100


class ActivityListView(ListAPIView):
    serializer_class = ActivitySerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            with connection.cursor() as cursor:
                # 檢查表是否存在
                cursor.execute("""
                    SELECT COUNT(*) FROM theme_events
                """)
                count = cursor.fetchone()[0]
                logger.info(f"Found {count} records in theme_events")

                cursor.execute("""
                    SELECT
                        id, uid, activity_name, description,
                        organizer, address, start_date, end_date,
                        location, latitude, longitude,
                        ticket_price, related_link, image_url,
                        created_at
                    FROM theme_events
                    WHERE end_date >= NOW()
                    ORDER BY start_date ASC
                """)

                columns = [col[0] for col in cursor.description]
                events = [
                    dict(zip(columns, row))
                    for row in cursor.fetchall()
                ]

                # 轉換日期格式
                for event in events:
                    if event['start_date']:
                        event['start_date'] = event['start_date'].strftime(
                            '%Y-%m-%d')
                    if event['end_date']:
                        event['end_date'] = event['end_date'].strftime(
                            '%Y-%m-%d')

                logger.info(f"Retrieved {len(events)} events")
                return events

        except Exception as e:
            logger.error(f"Database error: {str(e)}")
            return []

    def list(self, request, *args, **kwargs):
        try:
            events = self.get_queryset()
            return Response({
                'status': 'success',
                'results': events,
                'count': len(events)
            })
        except Exception as e:
            logger.error(f"API error: {str(e)}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=500)


class ActivityDetailView(RetrieveAPIView):
    serializer_class = ActivitySerializer
    permission_classes = [permissions.AllowAny]

    def get_object(self):
        pk = self.kwargs.get('pk')
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, uid, activity_name, description, organizer,
                       address, start_date, end_date, location,
                       latitude, longitude, ticket_price as ticket_info,
                       related_link, image_url, created_at
                FROM theme_events
                WHERE id = %s
            """, [pk])
            columns = [col[0] for col in cursor.description]
            event = dict(zip(columns, cursor.fetchone()))
            return event


def theme_list(request):
    """顯示主題育樂活動列表頁面"""
    return render(request, 'theme_entertainment/list.html', {
        'page_title': '主題育樂活動',
        'page_description': '探索精彩的文化、藝術與娛樂活動'
    })


def theme_create(request):
    """顯示創建活動頁面"""
    return render(request, 'theme_entertainment/create.html', {
        'page_title': '新增活動',
        'page_description': '創建新的主題育樂活動'
    })


def activity_management(request):
    """顯示活動管理頁面"""
    return render(request, 'theme_entertainment/activity_management.html', {
        'page_title': '活動管理',
        'page_description': '管理所有主題育樂活動'
    })

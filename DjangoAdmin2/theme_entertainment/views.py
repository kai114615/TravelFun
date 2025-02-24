"""
主題育樂活動管理系統的視圖模組
包含前端頁面渲染和 API 端點
"""

from django.shortcuts import render, redirect
from rest_framework import viewsets, permissions, filters
from rest_framework.response import Response
from rest_framework import serializers
from datetime import datetime
from .serializers import ActivitySerializer
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from itertools import chain
from rest_framework.generics import ListAPIView, RetrieveAPIView
from django.db import connection, transaction
import logging
from django.http import JsonResponse
from .models import Events
from django.core.serializers import serialize
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os

logger = logging.getLogger(__name__)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100


class ActivityListView(ListAPIView):
    """
    活動列表 API 視圖
    用於：
    1. 提供後台管理介面的數據
    2. 支持分頁和過濾功能
    """
    serializer_class = ActivitySerializer
    permission_classes = [permissions.IsAuthenticated]  # 需要登入才能訪問
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """
        返回所有活動數據，包括已結束的活動
        支持搜尋和過濾
        """
        with connection.cursor() as cursor:
            # 基礎查詢
            query = """
                SELECT *
                FROM theme_events
                WHERE 1=1
            """
            params = []

            # 搜尋條件
            search = self.request.query_params.get('search', '')
            if search:
                query += """
                    AND (
                        activity_name LIKE %s
                        OR organizer LIKE %s
                        OR location LIKE %s
                    )
                """
                search_param = f'%{search}%'
                params.extend([search_param, search_param, search_param])

            # 狀態過濾
            status = self.request.query_params.get('status', '')
            if status:
                today = datetime.now().date()
                if status == 'upcoming':
                    query += " AND start_date > %s"
                    params.append(today)
                elif status == 'ongoing':
                    query += " AND start_date <= %s AND end_date >= %s"
                    params.extend([today, today])
                elif status == 'ended':
                    query += " AND end_date < %s"
                    params.append(today)

            # 排序
            query += " ORDER BY start_date DESC"

            cursor.execute(query, params)
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def list(self, request, *args, **kwargs):
        """
        自定義響應格式
        """
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                'status': 'success',
                'data': serializer.data,
                'total': len(queryset)
            })

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'status': 'success',
            'data': serializer.data,
            'total': len(queryset)
        })


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


# 前端頁面路由（供一般用戶瀏覽）
@csrf_exempt
@require_http_methods(["GET"])
def activity_list(request):
    """獲取活動列表的API"""
    try:
        # 直接從 JSON 檔案讀取
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(current_dir, 'events_data.json')

        if not os.path.exists(json_path):
            # 如果檔案不存在，返回空列表
            return JsonResponse([], safe=False)

        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return JsonResponse(data, safe=False)

    except FileNotFoundError:
        # 如果找不到檔案，嘗試從資料庫獲取
        events = Events.objects.all().values()
        events_list = list(events)
        return JsonResponse(events_list, safe=False)

    except Exception as e:
        logger.error(f"Error in activity_list: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@csrf_exempt
def theme_create(request):
    """顯示創建活動頁面"""
    if request.method == "GET":
        return render(request, 'theme_entertainment/create.html', {
            'page_title': '新增活動',
            'page_description': '創建新的主題育樂活動'
        })
    elif request.method == "POST":
        try:
            data = json.loads(request.body)
            # 處理活動創建邏輯
            return JsonResponse({
                'status': 'success',
                'message': '活動創建成功'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)


def activity_management(request):
    """後台管理頁面"""
    return render(request, 'theme_entertainment/activity_management.html', {
        'page_title': '主題育樂活動管理',
        'page_description': '管理所有主題育樂活動資訊'
    })


# API 端點（供後台管理和前端 AJAX 調用）
@csrf_exempt
@require_http_methods(["GET"])
def get_events(request):
    """
    統一的活動列表 API
    根據請求來源提供不同的數據格式
    """
    try:
        # 判斷是否為管理介面的請求
        is_admin = request.GET.get('is_admin', 'false').lower() == 'true'

        with connection.cursor() as cursor:
            if is_admin:
                # 管理介面查詢（顯示所有活動）
                cursor.execute("""
                    SELECT *
                    FROM theme_events
                    ORDER BY start_date DESC
                """)
            else:
                # 前台查詢（只顯示未結束的活動）
                cursor.execute("""
                    SELECT id, activity_name, description,
                           start_date, end_date, location, image_url
                    FROM theme_events
                    WHERE end_date >= CURRENT_DATE
                    ORDER BY start_date ASC
                """)

            columns = [col[0] for col in cursor.description]
            events = [dict(zip(columns, row)) for row in cursor.fetchall()]

            # 格式化日期
            for event in events:
                if event.get('start_date'):
                    event['start_date'] = event['start_date'].strftime(
                        '%Y-%m-%d')
                if event.get('end_date'):
                    event['end_date'] = event['end_date'].strftime('%Y-%m-%d')

            return JsonResponse({
                'status': 'success',
                'data': events
            })
    except Exception as e:
        logger.error(f"Error in get_events: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def create_event(request):
    """
    創建新活動或顯示創建表單

    GET: 顯示創建活動的表單頁面
    POST: 處理活動創建請求

    返回格式：
    GET: 渲染表單頁面
    POST: {
        'status': 'success',
        'message': '活動創建成功',
        'id': int
    }
    """
    if request.method == "GET":
        context = {
            'page_title': '新增活動',
            'page_description': '建立新的主題育樂活動'
        }
        return render(request, 'theme_entertainment/create.html', context)

    try:
        logger.info("開始創建新活動")
        data = json.loads(request.body)
        required_fields = ['activity_name', 'organizer',
                           'start_date', 'end_date', 'location']

        # 檢查必填欄位
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({
                    'status': 'error',
                    'message': f'缺少必填欄位: {field}'
                }, status=400)

        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO theme_events (
                        activity_name, description, organizer,
                        address, start_date, end_date,
                        location, latitude, longitude,
                        ticket_price, source_url, image_url,
                        created_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW()
                    ) RETURNING id
                """, [
                    data.get('activity_name'),
                    data.get('description', ''),
                    data.get('organizer'),
                    data.get('address', ''),
                    data.get('start_date'),
                    data.get('end_date'),
                    data.get('location'),
                    data.get('latitude', 0),
                    data.get('longitude', 0),
                    data.get('ticket_info', ''),
                    data.get('source_url', ''),
                    data.get('image_url', '')
                ])

                new_id = cursor.fetchone()[0]

                return JsonResponse({
                    'status': 'success',
                    'message': '活動創建成功',
                    'id': new_id
                })
    except Exception as e:
        logger.error(f"Error in create_event: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["PUT"])
def update_event(request, event_id):
    """
    更新現有活動

    參數：
    - event_id: 活動ID

    可更新欄位：
    - 所有活動相關欄位都可選擇性更新
    - 使用 COALESCE 保留未提供的欄位原值

    特點：
    - 使用事務確保數據一致性
    - 先檢查活動是否存在
    - 只更新提供的欄位

    返回格式：
    {
        'status': 'success',
        'message': '活動更新成功'
    }
    """
    try:
        logger.info(f"開始更新活動 ID: {event_id}")
        data = json.loads(request.body)

        with transaction.atomic():
            with connection.cursor() as cursor:
                # 檢查活動是否存在
                cursor.execute(
                    "SELECT id FROM theme_events WHERE id = %s", [event_id])
                if not cursor.fetchone():
                    return JsonResponse({
                        'status': 'error',
                        'message': '活動不存在'
                    }, status=404)

                # 更新活動
                cursor.execute("""
                    UPDATE theme_events SET
                        activity_name = COALESCE(%s, activity_name),
                        description = COALESCE(%s, description),
                        organizer = COALESCE(%s, organizer),
                        address = COALESCE(%s, address),
                        start_date = COALESCE(%s, start_date),
                        end_date = COALESCE(%s, end_date),
                        location = COALESCE(%s, location),
                        latitude = COALESCE(%s, latitude),
                        longitude = COALESCE(%s, longitude),
                        ticket_price = COALESCE(%s, ticket_price),
                        source_url = COALESCE(%s, source_url),
                        image_url = COALESCE(%s, image_url)
                    WHERE id = %s
                """, [
                    data.get('activity_name'),
                    data.get('description'),
                    data.get('organizer'),
                    data.get('address'),
                    data.get('start_date'),
                    data.get('end_date'),
                    data.get('location'),
                    data.get('latitude'),
                    data.get('longitude'),
                    data.get('ticket_info'),
                    data.get('source_url'),
                    data.get('image_url'),
                    event_id
                ])

                return JsonResponse({
                    'status': 'success',
                    'message': '活動更新成功'
                })
    except Exception as e:
        logger.error(f"Error in update_event: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_event(request, event_id):
    """
    刪除指定活動

    參數：
    - event_id: 活動ID

    處理流程：
    1. 檢查活動是否存在
    2. 使用事務確保安全刪除
    3. 完整的錯誤處理

    返回格式：
    {
        'status': 'success',
        'message': '活動刪除成功'
    }
    """
    try:
        logger.info(f"開始刪除活動 ID: {event_id}")
        with transaction.atomic():
            with connection.cursor() as cursor:
                # 檢查活動是否存在
                cursor.execute(
                    "SELECT id FROM theme_events WHERE id = %s", [event_id])
                if not cursor.fetchone():
                    return JsonResponse({
                        'status': 'error',
                        'message': '活動不存在'
                    }, status=404)

                # 刪除活動
                cursor.execute(
                    "DELETE FROM theme_events WHERE id = %s", [event_id])

                return JsonResponse({
                    'status': 'success',
                    'message': '活動刪除成功'
                })
    except Exception as e:
        logger.error(f"Error in delete_event: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def sync_activities(request):
    """同步活動數據的API"""
    try:
        # 重新執行數據同步
        from .main import main
        main()

        return JsonResponse({'status': 'success', 'message': '數據同步完成'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

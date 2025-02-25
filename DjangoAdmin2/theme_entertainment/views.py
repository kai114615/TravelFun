"""
主題育樂活動管理系統的視圖模組
包含前端頁面渲染和 API 端點
"""

# Django 核心
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db import connection

# Django REST framework
from rest_framework import permissions
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

# 本地應用
from .models import Events
from .serializers import ActivitySerializer

# 工具
import json
import logging

# 設置日誌
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

# 後台管理頁面
def activity_management(request):
    return render(request, 'theme_entertainment/activity_management.html', {
        'page_title': '主題育樂活動管理',
        'page_description': '管理所有活動資訊'
    })


# 創建活動頁面
def create_event(request):
    if request.method == "POST":
        return render(request, 'theme_entertainment/create.html', {
            'page_title': '新增活動'
        })


# 前端頁面路由（供一般用戶瀏覽）
@csrf_exempt
@require_http_methods(["GET"])
def activity_list(request):
    """獲取活動列表的API"""
    try:
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))

        activities = Events.objects.all().order_by('id')
        paginator = Paginator(activities, page_size)

        current_page = paginator.page(page)

        data = [{
            'id': activity.id,
            'activity_name': activity.activity_name,
            'location': activity.location,
            'start_date': activity.start_date,
            'end_date': activity.end_date,
            'ticket_price': activity.ticket_price,
        } for activity in current_page]

        return JsonResponse({
            'status': 'success',
            'data': data,
            'total': paginator.count,
            'page': page,
            'total_pages': paginator.num_pages
        })

    except Exception as e:
        logger.error(f"Error in activity_list: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


# API 端點（供後台管理）
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
        sort_order = request.GET.get('sort', 'desc').lower()  # 預設降序

        # 設定排序方向
        order_by = 'DESC' if sort_order == 'desc' else 'ASC'

        with connection.cursor() as cursor:
            if is_admin:
                # 管理介面查詢（顯示所有活動）
                cursor.execute("""
                    SELECT *
                    FROM theme_events
                    ORDER BY id %s, start_date %s
                """ % (order_by, order_by))
            else:
                # 前台查詢（只顯示未結束的活動）
                cursor.execute("""
                    SELECT id, activity_name, description,
                           start_date, end_date, location, image_url
                    FROM theme_events
                    WHERE end_date >= CURRENT_DATE
                    ORDER BY id %s, start_date %s
                """ % (order_by, order_by))

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


# 創建活動（POST）
@csrf_exempt
@require_http_methods(["GET", "POST"])
def create_event(request):
    if request.method == "GET":
        return render(request, 'theme_entertainment/create.html', {
            'page_title': '新增活動',
            'page_description': '創建新的活動'
        })

    elif request.method == "POST":
        try:
            data = json.loads(request.body)

            # 驗證必要欄位
            required_fields = ['activity_name', 'description', 'location', 'start_date', 'end_date']
            for field in required_fields:
                if not data.get(field):
                    return JsonResponse({
                        'status': 'error',
                        'message': f'缺少必要欄位: {field}'
                    }, status=400)

            # 檢查 uid 是否存在
            if Events.objects.filter(uid=data.get('uid')).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': 'uid 已存在'
                }, status=400)

            # 創建新活動
            new_event = Events.objects.create(
                uid=data.get('uid'),
                activity_name=data.get('activity_name'),
                description=data.get('description'),
                organizer=data.get('organizer'),
                address=data.get('address'),
                start_date=data.get('start_date'),
                end_date=data.get('end_date'),
                location=data.get('location'),
                latitude=data.get('latitude'),
                longitude=data.get('longitude'),
                ticket_price=data.get('ticket_price'),
                source_url=data.get('source_url'),
                image_url=data.get('image_url', '')
            )

            return JsonResponse({
                'status': 'success',
                'message': '活動創建成功',
                'id': new_event.id
            })

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)


# 更新活動（PUT）
@csrf_exempt
@require_http_methods(["PUT"])
def update_event(request, event_id):
    try:
        data = json.loads(request.body)
        event = get_object_or_404(Events, id=event_id)

        # 更新提供的欄位
        fields_to_update = [
            'activity_name', 'description', 'organizer', 'address',
            'start_date', 'end_date', 'location', 'latitude',
            'longitude', 'ticket_price', 'source_url', 'image_url'
        ]

        for field in fields_to_update:
            if field in data:
                setattr(event, field, data[field])

        event.save()

        return JsonResponse({
            'status': 'success',
            'message': '活動更新成功'
        })

    except Events.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': '活動不存在'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


# 刪除活動（DELETE）
@csrf_exempt
@require_http_methods(["DELETE"])
def delete_event(request, event_id):
    try:
        event = get_object_or_404(Events, id=event_id)
        event.delete()

        return JsonResponse({
            'status': 'success',
            'message': '活動刪除成功'
        })

    except Events.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': '活動不存在'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_event_detail(request, event_id):
    """
    獲取單個活動的詳細資訊
    """
    try:
        # 使用 ORM 而不是原始 SQL，避免類型轉換問題
        event = get_object_or_404(Events, id=event_id)

        data = {
            'id': event.id,
            'uid': event.uid,
            'activity_name': event.activity_name,
            'description': event.description,
            'organizer': event.organizer,
            'address': event.address,
            'start_date': event.start_date.strftime('%Y-%m-%d') if event.start_date else None,
            'end_date': event.end_date.strftime('%Y-%m-%d') if event.end_date else None,
            'location': event.location,
            'latitude': float(event.latitude) if event.latitude else None,
            'longitude': float(event.longitude) if event.longitude else None,
            'ticket_price': event.ticket_price,
            'source_url': event.source_url,
            'image_url': event.image_url,
            'created_at': event.created_at.strftime('%Y-%m-%d') if event.created_at else None,
            'updated_at': event.updated_at.strftime('%Y-%m-%d') if event.updated_at else None
        }

        return JsonResponse({
            'status': 'success',
            'data': data
        })

    except Events.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': '找不到該活動'
        }, status=404)
    except Exception as e:
        logger.error(f"Error in get_event_detail: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

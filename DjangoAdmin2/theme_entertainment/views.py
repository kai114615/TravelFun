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
from django.http import Http404

# Django REST framework
from rest_framework import permissions
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

# 本地應用
from .models import Events
from .serializers import ActivitySerializer

# 工具
import json
import logging
import uuid
from django.utils import timezone
import pytz
from django.conf import settings

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


class ActivityDetailView(RetrieveAPIView):
    """活動詳情 API 視圖"""
    serializer_class = ActivitySerializer
    permission_classes = [permissions.AllowAny]

    def get_object(self):
        """獲取單個活動詳情"""
        uid = self.kwargs.get('id')  # 從 URL 參數獲取 uid
        try:
            # 使用 uid 查詢而不是 id
            event = get_object_or_404(Events, uid=uid)
            return {
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
        except Events.DoesNotExist:
            raise Http404("活動不存在")

    def retrieve(self, request, *args, **kwargs):
        """自定義回應格式"""
        try:
            instance = self.get_object()
            return Response({
                'status': 'success',
                'data': instance
            })
        except Http404:
            return Response({
                'status': 'error',
                'message': '找不到該活動'
            }, status=404)
        except Exception as e:
            logger.error(f"Error in ActivityDetailView: {str(e)}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=500)


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
                           start_date, end_date, location, image_url, ticket_price
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

            # 記錄接收到的數據，用於調試
            logger.info(f"接收到的活動數據: {data}")

            # 驗證必要欄位
            required_fields = ['activity_name', 'description', 'location', 'start_date', 'end_date']
            for field in required_fields:
                if not data.get(field):
                    return JsonResponse({
                        'status': 'error',
                        'message': f'缺少必要欄位: {field}'
                    }, status=400)

            # 如果沒有提供uid，則生成一個
            if not data.get('uid'):
                data['uid'] = f"manual-{uuid.uuid4()}"
            # 檢查 uid 是否存在
            elif Events.objects.filter(uid=data.get('uid')).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': 'uid 已存在'
                }, status=400)

            # 處理日期格式（確保是字符串格式的日期）
            for date_field in ['start_date', 'end_date']:
                if isinstance(data.get(date_field), list):
                    # 如果是時間戳列表，取第一個值
                    data[date_field] = data[date_field][0]

            # 因為 USE_TZ = False，所以 timezone.now() 直接返回台灣時間
            # 不需要額外的時區設置

            # 創建新活動
            new_event = Events.objects.create(
                uid=data.get('uid'),
                activity_name=data.get('activity_name'),
                description=data.get('description'),
                organizer=data.get('organizer', ''),
                address=data.get('address', ''),
                start_date=data.get('start_date'),
                end_date=data.get('end_date'),
                location=data.get('location'),
                latitude=data.get('latitude'),
                longitude=data.get('longitude'),
                ticket_price=data.get('ticket_price', ''),
                source_url=data.get('source_url', ''),
                image_url=data.get('image_url', '')
            )

            # 直接獲取創建時間（已經是台灣時間）
            current_time = new_event.created_at.strftime('%Y-%m-%d %H:%M:%S')

            # 直接輸出到終端，確保可見
            print(f"活動建立成功! 活動ID: {new_event.id}, 活動名稱: {new_event.activity_name}")
            print(f"建立時間: {current_time} (台灣時區 UTC+8)")
            logger.info(f"成功創建活動: {new_event.activity_name}, 活動ID: {new_event.id}, 建立時間: {current_time}")

            return JsonResponse({
                'status': 'success',
                'message': '活動創建成功',
                'id': new_event.id,
                'created_at': current_time
            })

        except Exception as e:
            # 直接輸出到終端，確保可見
            print(f"創建活動時發生錯誤: {str(e)}")
            logger.error(f"創建活動時出錯: {str(e)}")
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
def test_create_form(request):
    """
    測試活動創建表單的視圖
    僅用於開發階段測試表單提交
    """
    return render(request, 'theme_entertainment/create.html', {
        'page_title': '測試新增活動',
        'page_description': '測試創建新的活動（開發用）'
    })


@csrf_exempt
@require_http_methods(["GET"])
def test_timezone(request):
    """
    測試時區設置是否正確
    此視圖將顯示:
    1. 當前系統時間（台灣時間 UTC+8）
    2. 創建的活動時間（也應為台灣時間）
    """
    # 獲取當前時間（由於 USE_TZ = False，這將直接是台灣時間）
    now = timezone.now()

    # 創建一個測試活動
    test_event = Events.objects.create(
        uid=f"timezone-test-{uuid.uuid4()}",
        activity_name="時區測試活動",
        description="這是一個用於測試時區設置的活動",
        location="台北市",
        start_date=now.date(),
        end_date=now.date() + timezone.timedelta(days=7)
    )

    # 返回時間信息
    return JsonResponse({
        'system_time': now.strftime('%Y-%m-%d %H:%M:%S'),
        'event_created_at': test_event.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'settings_time_zone': settings.TIME_ZONE,
        'settings_use_tz': settings.USE_TZ,
        'note': 'USE_TZ = False 表示所有時間直接以台灣時區(UTC+8)存儲，無需轉換'
    })

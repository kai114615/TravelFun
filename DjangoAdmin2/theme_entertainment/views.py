"""
主題育樂活動管理系統的視圖模組
包含前端頁面渲染和 API 端點
"""

# Django 核心
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db import connection
from django.http import Http404
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect

# Django REST framework
from rest_framework import permissions
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

# 本地應用
from .models import Events, QueryResult, QueryEventRelation
from .serializers import ActivitySerializer

# 工具
import json
import logging
import uuid
from django.utils import timezone
import pytz
from django.conf import settings
import os
from datetime import time, datetime
import glob
from django.db.models import Q

# 設置日誌
logger = logging.getLogger(__name__)

# 媒體檔案設定
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(settings.BASE_DIR, 'media')


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


class ActivityDetailByIdView(RetrieveAPIView):
    """根據數據庫ID查詢活動詳情 API 視圖"""
    serializer_class = ActivitySerializer
    permission_classes = [permissions.AllowAny]

    def get_object(self):
        """根據數據庫ID獲取單個活動詳情"""
        event_id = self.kwargs.get('event_id')  # 從 URL 參數獲取數據庫 id
        try:
            # 使用數據庫 id 查詢
            event = get_object_or_404(Events, id=event_id)

            # 格式化日期時間
            start_datetime_str = None
            end_datetime_str = None

            if event.start_date:
                start_datetime_str = event.start_date.strftime('%Y-%m-%d %H:%M:%S')

            if event.end_date:
                end_datetime_str = event.end_date.strftime('%Y-%m-%d %H:%M:%S')

            return {
                'id': event.id,
                'uid': event.uid,
                'activity_name': event.activity_name,
                'description': event.description,
                'organizer': event.organizer,
                'address': event.address,
                'start_date': start_datetime_str,
                'end_date': end_datetime_str,
                'location': event.location,
                'latitude': float(event.latitude) if event.latitude else None,
                'longitude': float(event.longitude) if event.longitude else None,
                'ticket_price': event.ticket_price,
                'source_url': event.source_url,
                'image_url': event.image_url,
                'created_at': event.created_at.strftime('%Y-%m-%d %H:%M:%S') if event.created_at else None,
                'updated_at': event.updated_at.strftime('%Y-%m-%d %H:%M:%S') if event.updated_at else None
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
            logger.error(f"Error in ActivityDetailByIdView: {str(e)}")
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
                # 前台查詢（顯示所有活動）
                cursor.execute("""
                    SELECT id, activity_name, description,
                           start_date, end_date, location, image_url, ticket_price
                    FROM theme_events
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


# 抽取共用函數：處理圖片上傳
def handle_image_upload(image_file, event_id):
    """
    處理圖片上傳，並返回圖片URL

    參數:
        image_file: 上傳的圖片檔案
        event_id: 活動ID

    返回:
        image_url: 圖片存儲後的URL
    """
    try:
        # 設定儲存路徑
        upload_dir = os.path.join('theme_entertainment', 'activities', 'images')
        full_dir_path = os.path.join(settings.MEDIA_ROOT, upload_dir)

        # 確保目錄存在
        os.makedirs(full_dir_path, exist_ok=True)

        # 計算此活動已有的圖片數量
        existing_images = glob.glob(os.path.join(full_dir_path, f"{event_id}_*"))
        image_count = len(existing_images) + 1  # 新圖片的次序編號

        # 生成新檔名：活動ID_次序編號.副檔名
        file_extension = image_file.name.split('.')[-1].lower()
        new_filename = f"{event_id}_{image_count}.{file_extension}"

        # 完整檔案路徑
        file_path = os.path.join(full_dir_path, new_filename)

        # 儲存檔案
        with open(file_path, 'wb+') as destination:
            for chunk in image_file.chunks():
                destination.write(chunk)

        # 設定可訪問的 URL
        image_url = f"{settings.MEDIA_URL}{upload_dir}/{new_filename}"
        logger.info(f"圖片已保存到: {file_path}")
        logger.info(f"圖片 URL: {image_url}")

        return image_url
    except Exception as img_err:
        logger.error(f"保存圖片時出錯: {str(img_err)}")
        print(f"保存圖片時出錯: {str(img_err)}")
        return None


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
            # 依據不同內容類型處理請求資料
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                image_file = None
            else:  # 處理 multipart/form-data
                data = request.POST.dict()
                image_file = request.FILES.get('image')

                # 日期欄位可能需要特殊處理，因為通過表單提交時格式不同
                if 'date_range' in request.POST:
                    # 日期範圍可能需要從字串轉換
                    try:
                        date_range = json.loads(request.POST.get('date_range'))
                        if date_range and len(date_range) == 2:
                            data['start_date'] = date_range[0]
                            data['end_date'] = date_range[1]
                    except:
                        pass

            # 記錄接收到的數據，用於調試
            logger.info(f"接收到的活動數據: {data}")
            logger.info(f"提交的UID(原始): {data.get('uid', 'None')}")

            # 從請求中直接獲取 uid，避免可能的轉換問題
            submitted_uid = None
            if request.content_type == 'application/json':
                submitted_uid = json.loads(request.body).get('uid')
            else:  # multipart/form-data
                submitted_uid = request.POST.get('uid')

            logger.info(f"直接從請求中獲取的UID: {submitted_uid}")

            if image_file:
                logger.info(f"接收到的圖片: {image_file.name}, 大小: {image_file.size} bytes")

            # 驗證必要欄位
            required_fields = ['activity_name', 'description', 'location', 'start_date', 'end_date']
            for field in required_fields:
                if not data.get(field):
                    return JsonResponse({
                        'status': 'error',
                        'message': f'缺少必要欄位: {field}'
                    }, status=400)

            # 處理 UID - 優先使用直接從請求中獲取的 UID
            if submitted_uid and submitted_uid != 'undefined' and submitted_uid != 'null':
                # 確保使用前端提交的 UID，而不是從字典中獲取
                data['uid'] = submitted_uid
                logger.info(f"使用請求中的UID: {submitted_uid}")
            else:
                # 如果前端沒有提供有效的 UID，則生成一個新的
                generated_uid = f"{uuid.uuid4()}".replace('-', '')  # 生成不含連字符的UUID
                data['uid'] = generated_uid
                logger.info(f"生成新的UUID: {generated_uid}")

            # 檢查 uid 是否存在
            if Events.objects.filter(uid=data['uid']).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': 'uid 已存在'
                }, status=400)

            logger.info(f"最終使用的UUID: {data['uid']}")  # 記錄最終使用的UUID

            # 處理日期格式（確保是字符串格式的日期）
            for date_field in ['start_date', 'end_date']:
                if isinstance(data.get(date_field), list):
                    # 如果是時間戳列表，取第一個值
                    data[date_field] = data[date_field][0]

            # 處理經緯度欄位（確保正確的數值類型）
            latitude = data.get('latitude')
            longitude = data.get('longitude')

            # 將 "null" 字符串或空字符串轉換為 None
            if latitude == "null" or latitude == "" or latitude is None:
                latitude = None
            else:
                try:
                    latitude = float(latitude)  # 嘗試轉換為浮點數
                except (TypeError, ValueError):
                    latitude = None

            if longitude == "null" or longitude == "" or longitude is None:
                longitude = None
            else:
                try:
                    longitude = float(longitude)  # 嘗試轉換為浮點數
                except (TypeError, ValueError):
                    longitude = None

            # 處理票價欄位 (如果也是 decimal)
            ticket_price = data.get('ticket_price', '')
            if ticket_price == "null":
                ticket_price = ''

            # 處理圖片上傳
            image_url = data.get('image_url', '')

            # 先創建新活動以獲取活動ID (不管是否有圖片上傳)
            new_event = Events.objects.create(
                uid=data.get('uid'),
                activity_name=data.get('activity_name'),
                description=data.get('description'),
                organizer=data.get('organizer', ''),
                address=data.get('address', ''),
                start_date=data.get('start_date'),
                end_date=data.get('end_date'),
                location=data.get('location'),
                latitude=latitude,  # 使用處理後的經緯度值
                longitude=longitude,
                ticket_price=ticket_price,
                source_url=data.get('source_url', ''),
                image_url=image_url  # 先用預設值或傳入的URL
            )

            # 如果有上傳圖片，處理圖片並更新活動的圖片URL
            if image_file:
                uploaded_image_url = handle_image_upload(image_file, new_event.id)
                if uploaded_image_url:
                    new_event.image_url = uploaded_image_url
                    new_event.save()

            # 直接獲取創建時間（已經是台灣時間）
            current_time = new_event.created_at.strftime('%Y-%m-%d %H:%M:%S')

            # 直接輸出到終端，確保可見
            print(f"活動建立成功! 活動ID: {new_event.id}, 活動名稱: {new_event.activity_name}")
            print(f"建立時間: {current_time} (台灣時區 UTC+8)")
            logger.info(f"成功創建活動: {new_event.activity_name}, 活動ID: {new_event.id}, 建立時間: {current_time}")

            # 返回成功訊息，包含更多資訊以支援前端處理
            return JsonResponse({
                'status': 'success',
                'message': '活動創建成功',
                'id': new_event.id,
                'created_at': current_time,
                'activity_name': new_event.activity_name,
                'redirect_url': '/admin-dashboard/entertainment/activities/',
                'show_popup': True  # 標記前端需要顯示彈窗
            })

        except Exception as e:
            # 直接輸出到終端，確保可見
            print(f"創建活動時發生錯誤: {str(e)}")
            logger.error(f"創建活動時出錯: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)


# 更新活動（POST）
@csrf_exempt
@require_http_methods(["POST", "PUT"])
def update_event(request, event_id):
    try:
        # 檢查Content-Type頭部
        content_type = request.content_type or ''

        # 根據不同Content-Type處理數據
        if content_type.startswith('application/json'):
            data = json.loads(request.body)
            image = None
        else:
            data = {}
            for key, value in request.POST.items():
                data[key] = value
            image = request.FILES.get('image')

        # 獲取活動對象
        event = get_object_or_404(Events, id=event_id)

        # 處理經緯度欄位
        latitude = data.get('latitude')
        longitude = data.get('longitude')

        # 將 "null" 字符串或空字符串轉換為 None
        if latitude == "null" or latitude == "" or latitude is None:
            latitude = None
        else:
            try:
                latitude = float(latitude)  # 嘗試轉換為浮點數
            except (TypeError, ValueError):
                latitude = None

        if longitude == "null" or longitude == "" or longitude is None:
            longitude = None
        else:
            try:
                longitude = float(longitude)  # 嘗試轉換為浮點數
            except (TypeError, ValueError):
                longitude = None

        # 設置處理過的經緯度值
        event.latitude = latitude
        event.longitude = longitude

        # 處理圖片上傳
        if image:
            # 使用共用的圖片上傳處理函數
            uploaded_image_url = handle_image_upload(image, event_id)
            if uploaded_image_url:
                event.image_url = uploaded_image_url
        else:
            # 保留原始圖片URL或使用前端傳來的URL
            original_image_url = data.get('original_image_url')
            if original_image_url and original_image_url != "null":
                event.image_url = original_image_url

        # 處理日期時間
        # 從請求中獲取日期（YYYY-MM-DD）和時間（HH:MM）
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        start_time = data.get('start_time')
        end_time = data.get('end_time')

        logger.info(f"接收到日期時間參數 - 開始日期: {start_date}, 開始時間: {start_time}, 結束日期: {end_date}, 結束時間: {end_time}")

        # 組合日期和時間為完整的日期時間物件
        try:
            if start_date and start_time:
                # 如果日期時間已經是完整格式，直接使用
                if ' ' in start_date:
                    event.start_date = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
                else:
                    # 否則組合日期和時間
                    date_str = f"{start_date} {start_time}"
                    event.start_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M')
                logger.info(f"設置開始日期時間: {event.start_date}")
            elif start_date:
                # 如果只有日期，設置時間為預設值 (00:00)
                if ' ' in start_date:
                    event.start_date = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
                else:
                    event.start_date = datetime.strptime(f"{start_date} 00:00", '%Y-%m-%d %H:%M')
        except Exception as e:
            logger.error(f"解析開始日期時間出錯: {str(e)}")

        try:
            if end_date and end_time:
                # 如果日期時間已經是完整格式，直接使用
                if ' ' in end_date:
                    event.end_date = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')
                else:
                    # 否則組合日期和時間
                    date_str = f"{end_date} {end_time}"
                    event.end_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M')
                logger.info(f"設置結束日期時間: {event.end_date}")
            elif end_date:
                # 如果只有日期，設置時間為預設值 (23:59)
                if ' ' in end_date:
                    event.end_date = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')
                else:
                    event.end_date = datetime.strptime(f"{end_date} 23:59", '%Y-%m-%d %H:%M')
        except Exception as e:
            logger.error(f"解析結束日期時間出錯: {str(e)}")

        # 其他欄位更新（排除已處理的欄位）
        fields_to_update = [
            'activity_name', 'description', 'organizer', 'address',
            'location', 'ticket_price', 'source_url'
            # 不包含 'latitude', 'longitude', 'image_url'，因為已特別處理
        ]

        for field in fields_to_update:
            if field in data:
                setattr(event, field, data[field])

        # 保存活動
        event.save()

        # 格式化時間用於回應
        start_datetime_str = event.start_date.strftime('%Y-%m-%d %H:%M:%S') if event.start_date else None
        end_datetime_str = event.end_date.strftime('%Y-%m-%d %H:%M:%S') if event.end_date else None

        # 返回成功訊息，包含更新後的時間
        response_data = {
            'status': 'success',
            'message': '活動更新成功',
            'id': event.id,
            'start_date': start_datetime_str,
            'end_date': end_datetime_str,
            'activity_name': event.activity_name,
            'redirect_url': '/admin-dashboard/entertainment/activities/',
            'show_popup': True  # 標記前端需要顯示彈窗
        }

        return JsonResponse(response_data)
    except Events.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': '活動不存在'
        }, status=404)
    except Exception as e:
        logger.error(f"更新活動時出錯: {str(e)}")
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


# 編輯活動頁面視圖
@csrf_exempt
@require_http_methods(["GET"])
def edit_event(request, event_id):
    """
    活動編輯頁面

    用於顯示活動編輯表單，允許管理員修改現有活動資料
    """
    try:
        # 嘗試獲取活動資料
        event = Events.objects.get(id=event_id)

        # 渲染編輯頁面
        return render(request, 'theme_entertainment/edit.html', {
            'page_title': '編輯活動',
            'page_description': f'編輯「{event.activity_name}」活動資料',
            'event_id': event_id
        })
    except Events.DoesNotExist:
        # 如果活動不存在，重定向到活動列表頁面
        messages.error(request, f'找不到ID為 {event_id} 的活動')
        return redirect('theme_entertainment:activity_management')
    except Exception as e:
        # 其他未知錯誤
        logger.error(f"顯示編輯頁面時出錯: {str(e)}")
        messages.error(request, f'發生錯誤: {str(e)}')
        return redirect('theme_entertainment:activity_management')


@api_view(['GET'])
@permission_classes([AllowAny])
def get_entertainment_data_for_ai(request):
    """提供主題育樂資料給AI聊天機器人使用"""

    search_term = request.GET.get('q', '')
    limit = int(request.GET.get('limit', 20))

    # 獲取當前日期時間，用於時間分類
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)

    # 定義三天的時間範圍（毫秒）- 用於判斷即將開始和即將結束
    three_days = timezone.timedelta(days=3)

    # 基本查詢條件
    base_query = Q(activity_name__icontains=search_term) | Q(description__icontains=search_term)

    # 蒐集各個主題育樂資料
    # 1. 基本活動資料（依關鍵字搜尋）
    activities = list(Events.objects.filter(base_query)[:limit].values(
        'activity_name', 'description', 'address', 'start_date', 'end_date', 'location', 'ticket_price'))

    # 2. 已結束的活動 - 結束日期小於當前時間
    ended_activities = list(Events.objects.filter(
        end_date__lt=now
    )[:limit].values('activity_name', 'description', 'address', 'start_date', 'end_date', 'location', 'ticket_price'))

    # 3. 只限今日活動 - 開始和結束日期都在今天
    today_only_activities = list(Events.objects.filter(
        start_date__date=now.date(),
        end_date__date=now.date()
    )[:limit].values('activity_name', 'description', 'address', 'start_date', 'end_date', 'location', 'ticket_price'))

    # 4. 即將結束活動 - 結束日期在當前時間和3天內的時間之間
    ending_soon_activities = list(Events.objects.filter(
        end_date__gt=now,
        end_date__lte=now + three_days
    )[:limit].values('activity_name', 'description', 'address', 'start_date', 'end_date', 'location', 'ticket_price'))

    # 5. 進行中活動 - 開始日期小於當前時間，且結束日期大於當前時間
    ongoing_activities = list(Events.objects.filter(
        Q(start_date__lt=now) &
        Q(end_date__gt=now) &
        ~Q(start_date__gt=now - three_days)  # 排除最近三天內開始的活動
    )[:limit].values('activity_name', 'description', 'address', 'start_date', 'end_date', 'location', 'ticket_price'))

    # 6. 即將開始活動 - 開始日期在當前時間和3天內的時間之間
    upcoming_activities = list(Events.objects.filter(
        start_date__gt=now,
        start_date__lte=now + three_days
    )[:limit].values('activity_name', 'description', 'address', 'start_date', 'end_date', 'location', 'ticket_price'))

    # 7. 未開始活動 - 開始日期大於3天後的時間
    not_started_activities = list(Events.objects.filter(
        start_date__gt=now + three_days
    )[:limit].values('activity_name', 'description', 'address', 'start_date', 'end_date', 'location', 'ticket_price'))

    # 8. 其他分類 - 依關鍵字搜尋
    # 運動相關活動
    sports = list(Events.objects.filter(
        base_query &
        (Q(activity_name__icontains='運動') | Q(activity_name__icontains='體育') |
         Q(activity_name__icontains='球賽') | Q(activity_name__icontains='健身') |
         Q(description__icontains='運動') | Q(description__icontains='體育') |
         Q(description__icontains='球賽') | Q(description__icontains='健身'))
    )[:limit].values('activity_name', 'description', 'address', 'start_date', 'end_date', 'location', 'ticket_price'))

    # 宗教相關活動
    religions = list(Events.objects.filter(
        base_query &
        (Q(activity_name__icontains='宗教') | Q(activity_name__icontains='寺廟') |
         Q(activity_name__icontains='教堂') | Q(activity_name__icontains='廟宇') |
         Q(description__icontains='宗教') | Q(description__icontains='寺廟') |
         Q(description__icontains='教堂') | Q(description__icontains='廟宇'))
    )[:limit].values('activity_name', 'description', 'address', 'start_date', 'end_date', 'location', 'ticket_price'))

    # 表演相關活動
    shows = list(Events.objects.filter(
        base_query &
        (Q(activity_name__icontains='表演') | Q(activity_name__icontains='音樂會') |
         Q(activity_name__icontains='演唱會') | Q(activity_name__icontains='戲劇') |
         Q(description__icontains='表演') | Q(description__icontains='音樂會') |
         Q(description__icontains='演唱會') | Q(description__icontains='戲劇'))
    )[:limit].values('activity_name', 'description', 'address', 'start_date', 'end_date', 'location', 'ticket_price'))

    # 藝術相關活動
    arts = list(Events.objects.filter(
        base_query &
        (Q(activity_name__icontains='藝術') | Q(activity_name__icontains='展覽') |
         Q(activity_name__icontains='畫展') | Q(activity_name__icontains='美術') |
         Q(description__icontains='藝術') | Q(description__icontains='展覽') |
         Q(description__icontains='畫展') | Q(description__icontains='美術'))
    )[:limit].values('activity_name', 'description', 'address', 'start_date', 'end_date', 'location', 'ticket_price'))

    # 電影相關活動
    cinemas = list(Events.objects.filter(
        base_query &
        (Q(activity_name__icontains='電影') | Q(activity_name__icontains='影展') |
         Q(activity_name__icontains='放映') | Q(activity_name__icontains='院線') |
         Q(description__icontains='電影') | Q(description__icontains='影展') |
         Q(description__icontains='放映') | Q(description__icontains='院線'))
    )[:limit].values('activity_name', 'description', 'address', 'start_date', 'end_date', 'location', 'ticket_price'))

    # 處理日期時間格式化，方便前端使用
    activity_collections = [
        activities, ended_activities, today_only_activities, ending_soon_activities,
        ongoing_activities, upcoming_activities, not_started_activities,
        sports, religions, shows, arts, cinemas
    ]

    for items in activity_collections:
        for item in items:
            if item.get('start_date'):
                item['start_date'] = item['start_date'].strftime('%Y-%m-%d %H:%M:%S')
            if item.get('end_date'):
                item['end_date'] = item['end_date'].strftime('%Y-%m-%d %H:%M:%S')

    data = {
        'activities': activities,
        'ended_activities': ended_activities,
        'today_only_activities': today_only_activities,
        'ending_soon_activities': ending_soon_activities,
        'ongoing_activities': ongoing_activities,
        'upcoming_activities': upcoming_activities,
        'not_started_activities': not_started_activities,
        'sports': sports,
        'religions': religions,
        'shows': shows,
        'arts': arts,
        'cinemas': cinemas
    }

    return Response(data)

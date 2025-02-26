from django.shortcuts import render, redirect
from django.db.models import Q
from django.http import HttpResponse, JsonResponse, FileResponse
from .models import Travel,Taiwan,Counties,TravelClass
from datetime import datetime
import time
import json
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import SessionAuthentication
from .serializers import TravelSerializers,TravelClassSerializers,TaiwanSerializers,TravelFilterSerializer,CountrySerializers
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
import heapq
import math
from rest_framework.decorators import api_view, permission_classes, authentication_classes

# Create your views here.
from django.core.paginator import Paginator
from django.shortcuts import render
from .models import Travel

#讀取縣市資料
def region(request):
    regions = Counties.objects.values('name').distinct()
    regions = [item['name'] for item in regions]
    return JsonResponse(regions, safe=False)

# 讀取鄉鎮市區資料
def town(request, region_name):
    towns = Taiwan.objects.filter(region=region_name).values('town')
    towns = [item['town'] for item in towns]
    return JsonResponse(towns, safe=False)

# 顯示篩選資料
def show(request, region_name, town_name):
    travels = Travel.objects.filter(
        town=town_name,
        region__in=[region_name.replace('台', '臺'), region_name.replace('臺', '台')]  # 支援「台」和「臺」
    ).values()
    return JsonResponse(list(travels), safe=False)


def travel_main(request):
    travel_name = request.GET.get('name', '')
    page_number = request.GET.get('page', 1)
    region_name = request.GET.get('region_name', '')  
    town_name = request.GET.get('town_name', '')

    per_page = 30

    # 添加默認排序
    if travel_name:
        travels = Travel.objects.filter(
            travel_name__icontains=travel_name
        ).order_by('travel_id')  # 使用 travel_id 作為排序依據
    elif town_name and region_name:
        # 修改 show 函數返回的 QuerySet
        travels = Travel.objects.filter(
            town=town_name,
            region__in=[region_name.replace('台', '臺'), region_name.replace('臺', '台')]
        ).order_by('travel_id')
    else:
        travels = Travel.objects.all().order_by('travel_id')

    # 分頁處理
    paginator = Paginator(travels, per_page)
    page_obj = paginator.get_page(page_number)

    # 自定義分頁邏輯：顯示最多 10 個頁碼按鈕
    total_pages = paginator.num_pages
    current_page = page_obj.number

    # 計算分頁按鈕範圍
    start_page = max(1, current_page - 5)
    end_page = min(total_pages, current_page + 4)

    if end_page - start_page < 9:  # 確保顯示的按鈕數量不超過 10
        if start_page == 1:
            end_page = min(10, total_pages)
        elif end_page == total_pages:
            start_page = max(1, total_pages - 9)

    page_range = range(start_page, end_page + 1)

    return render(request, 'travel/travel.html', {
        "travel": page_obj,  # 分頁後的資料
        "page_obj": page_obj,  # 傳遞分頁物件到模板
        "page_range": page_range,  # 傳遞頁碼範圍到模板
        "total_pages": total_pages,  # 總頁數
        "travel_name": travel_name,  # 傳遞篩選條件
        "region": region_name,  # 傳遞region到模板
        "town": town_name,
    })



def register(request):
    
    return render(request, 'travel/register.html')

def edit(request, id):   
    travel = Travel.objects.get(travel_id=id)  
    return render(request, 'travel/edit.html',{'travel': travel})

#新增資料
def register01(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        txt = request.POST.get('txt')
        tel = request.POST.get('tel')
        address = request.POST.get('address')
        region = request.POST.get("region")
        town = request.POST.get('town')
        linginfo = request.POST.get('linginfo')
        opentime = request.POST.get('opentime')
        image1 = request.POST.get('image1')
        image2 = request.POST.get('image2')
        image3 = request.POST.get('image3')
        Px = request.POST.get('Px')
        Py = request.POST.get('Py')
        website = request.POST.get('website')
        tickinfo = request.POST.get('tickinfo')
        parkinfo = request.POST.get('parkinfo')

        #景點屬性
        class_list = request.POST.getlist("class")
        if not class_list:
            return HttpResponse("您好，請至少選一個類別", 'text/plain')
        class1=class_list[0]
        if len(class_list)>=2:
            class2=class_list[1]
        else:
            class2=None
        if len(class_list)>=3:
            class3=class_list[2]
        else:
            class3=None

    #確認景點名稱
    if not name:
       return HttpResponse("您好，景點名稱不能是空的", 'text/plain')
    if Travel.objects.filter(travel_name=name):
       return HttpResponse("您好，景點名稱已註冊", 'text/plain')

    #確認景點電話
    if tel and Travel.objects.filter(tel=tel):
       return HttpResponse("您好，此電話已註冊", 'text/plain')

    #確認景點地址
    if address and Travel.objects.filter(travel_address=address):
       return HttpResponse("您好，此地址已註冊", 'text/plain')

    #確認縣市
    if not region or not town:
        return HttpResponse("您好，縣市/鄉鎮市(區)欄位不能為空", 'text/plain')

    if region.startswith('臺') :
        if not Counties.objects.filter(name__contains=region[1:]):
            return HttpResponse("您好，此縣市不存在", 'text/plain')
    elif region.startswith('台'):
        return HttpResponse("您好，台請改成臺", 'text/plain')
    elif not Counties.objects.filter(name=region):
        return HttpResponse("您好，此縣市不存在", 'text/plain')

    if region.startswith('臺'):
        region_name = region[1:].strip()
        if not Counties.objects.filter(Q(name__iexact='台' + region_name)).exists():
            return HttpResponse("您好，此縣市不存在", 'text/plain')
    elif not Taiwan.objects.filter(region=region,town=town) :
        return HttpResponse("您好，這縣市，不存在此鄉鎮市", 'text/plain')

    #確認經緯度
    if not Px or not Py :
        return HttpResponse("您好，經/緯度不能是空的", 'text/plain')
    Px=float(Px)
    if  Px>125 or Px<121:
        return HttpResponse("您好，此經度不再臺灣範圍內", 'text/plain')
    Py=float(Py)
    if  Py>26 or Py<21:
        return HttpResponse("您好，此緯度不再臺灣範圍內", 'text/plain')
    
    Travel.objects.create(
        travel_name = name,
        travel_txt = txt,
        tel = tel,
        travel_address = address,
        region = region,
        town = town,
        travel_linginfo =linginfo,
        opentime = opentime,
        image1 = image1,
        image2 = image2,
        image3 = image3,
        px = Px,
        py = Py,
        class1_id = class1,
        class2_id = class2,
        class3_id = class3,
        website = website,
        ticketinfo = tickinfo,
        parkinginfo = parkinfo,
        upload = datetime.now()
    )
    content =  f"您好，景點:{name}，已加入資料庫  "
    return HttpResponse(content, 'text/plain')

def edit01(request,id):
    travel = Travel.objects.get(travel_id=id) 
    if request.method == 'POST':

        #確認景點名稱，並輸入
        if not travel.travel_name:
            return HttpResponse("您好，景點名稱不能是空的", 'text/plain')
        if travel.travel_name != request.POST.get('name'):
            if Travel.objects.filter(travel_name=request.POST.get('name')):
                return HttpResponse("您好，景點名稱已註冊", 'text/plain')
            else:
                travel.travel_name = request.POST.get('name')

        travel.travel_txt = request.POST.get('txt')
        
        #確認景點電話，並輸入
        if travel.tel != request.POST.get('tel') and  request.POST.get('tel'):
            if travel.tel and Travel.objects.filter(tel=travel.tel):
                return HttpResponse("您好，此電話已註冊", 'text/plain')
            else :
                travel.tel = request.POST.get('tel')

        #確認景點地址，並輸入
        if travel.travel_address != request.POST.get('address') and  request.POST.get('address'):
            if travel.travel_address and Travel.objects.filter(travel_address=travel.travel_address):
                return HttpResponse("您好，此地址已註冊", 'text/plain')
            else :
                travel.travel_address = request.POST.get('address')
        
        travel.region = request.POST.get("region")
        travel.town = request.POST.get('town')
        travel.travel_linginfo = request.POST.get('linginfo')
        travel.opentime = request.POST.get('opentime')
        travel.image1 = request.POST.get('image1')
        travel.image2 = request.POST.get('image2')
        travel.image3 = request.POST.get('image3')
        travel.px = request.POST.get('Px')
        travel.py = request.POST.get('Py')
        travel.website = request.POST.get('website')
        travel.ticketinfo = request.POST.get('tickinfo')
        travel.parkinginfo = request.POST.get('parkinfo')

        # 景點屬性處理
        class_list = request.POST.getlist("class")
        if not class_list:
            return HttpResponse("您好，請至少選一個類別", 'text/plain')
        
        # 先清空所有類別
        travel.class1 = None
        travel.class2 = None
        travel.class3 = None

        # 依序設置類別
        if len(class_list) >= 1:
            travel.class1 = TravelClass.objects.get(class_id=class_list[0])
        if len(class_list) >= 2:
            travel.class2 = TravelClass.objects.get(class_id=class_list[1])
        if len(class_list) >= 3:
            travel.class3 = TravelClass.objects.get(class_id=class_list[2])

            
    #確認景點縣市
    if not travel.region or not travel.town:
        return HttpResponse("您好，縣市/鄉鎮市(區)欄位不能為空", 'text/plain')

    if travel.region.startswith('臺') :
        region_name = travel.region[1:].strip()
        if not Counties.objects.filter(Q(name__iexact='台' + region_name)).exists():
            return HttpResponse("您好，此縣市不存在", 'text/plain')
    elif travel.region.startswith('台'):
        return HttpResponse("您好，台請改成臺", 'text/plain')
    elif not Counties.objects.filter(name=travel.region):
        return HttpResponse("您好，此縣市不存在", 'text/plain')

    if travel.region.startswith('臺'):
        if not Taiwan.objects.filter(region__contains=travel.region[1:],town=travel.town):
            return HttpResponse("您好，這縣市，不存在此鄉鎮市", 'text/plain')
    elif not Taiwan.objects.filter(region=travel.region,town=travel.town) :
        return HttpResponse("您好，這縣市，不存在此鄉鎮市", 'text/plain')

    #確認經緯度
    if not travel.px or not travel.py :
        return HttpResponse("您好，經/緯度不能是空的", 'text/plain')   
    Px = float(travel.px)
    if  Px>125 or Px<121:
        return HttpResponse("您好，此經度不再臺灣範圍內", 'text/plain')
    Py=float(travel.py)
    if  Py>26 or Py<21:
        return HttpResponse("您好，此緯度不再臺灣範圍內", 'text/plain')
    
    travel.save()
    content =  f"您好，景點資訊，已修改  "
    return HttpResponse(content, 'text/plain')
    


#刪除資料
def delete(request, id):   
    todo = Travel.objects.get(travel_id=id)  
    todo.delete()
    return redirect('travel:travel')

#預覽資料
def preview(request,id):
    travel = Travel.objects.get(travel_id=id) 
    class1 = TravelClass.objects.get(class_id = travel.class1_id)
    if travel.class2_id:
        class2 = TravelClass.objects.get(class_id = travel.class2_id)
    else : class2 = None
    if travel.class3_id:
        class3 = TravelClass.objects.get(class_id = travel.class3_id)
    else : class3 = None

    return render(request,"travel/preview.html",{'travel': travel,'class1': class1 ,'class2': class2 ,'class3': class3})




#確認景點名稱
def travelName(request):
    name = request.GET.get("name")
    result = {
        "name_exists": False,
    }

    if request.GET.get("travel_id"):
        id = request.GET.get("travel_id")
        if not Travel.objects.filter(travel_name=name,travel_id=id).exists():
            if Travel.objects.filter(travel_name=name).exists():
                result["name_exists"] = True
    
    elif Travel.objects.filter(travel_name=name).exists():
        result["name_exists"] = True
    return JsonResponse(result, safe=False)

#確認電話
def travelTel(request):
    tel = request.GET.get("tel")
    result = {
        "tel_exists": False,
    }

    if tel:
        if request.GET.get("travel_id"):
            id = request.GET.get("travel_id")
            if not Travel.objects.filter(tel=tel,travel_id=id).exists():
                if Travel.objects.filter(tel=tel).exists():
                    result["tel_exists"] = True
    
        elif Travel.objects.filter(tel=tel).exists():
            result["tel_exists"] = True
    return JsonResponse(result, safe=False)

#確認地址
def travelAddress(request):
    address = request.GET.get("address")
    travel_id = request.GET.get("travel_id")
    result = {
        "address_exists": False,
    }
    if address:
        if travel_id:
            if not Travel.objects.filter(travel_address=address, travel_id=travel_id).exists():
                if Travel.objects.filter(travel_address=address).exists():
                    result["address_exists"] = True
        else:  
            if Travel.objects.filter(travel_address=address).exists():
                result["address_exists"] = True
    
    return JsonResponse(result, safe=False)

#確認縣市
def travelRegion(request):
    region = request.GET.get("region")
    result = {
        "region_exists": False,
    }
    
    if region.startswith("台") or region.startswith("臺"):
        # 判斷以 "台" 或 "臺" 開頭時是否匹配
        region_name = region[1:].strip()
        if not (region.startswith("臺") and Counties.objects.filter(Q(name__iexact='台' + region_name)).exists()):
            result["region_exists"] = True
    else:
        if not Counties.objects.filter(name=region).exists():
            result["region_exists"] = True
    
    return JsonResponse(result, safe=False)
#確認鄉鎮市區
def travelTown(request):
    town = request.GET.get("town")
    region = request.GET.get("region")
    result = {
        "town_exists": False,
    }
    if region.startswith("臺"):
        region_name = region[1:].strip()
        if not Taiwan.objects.filter(Q(region__iexact='台' + region_name),town=town).exists():
            result["town_exists"] = True

    elif not Taiwan.objects.filter(town=town,region=region).exists():
        result["town_exists"] = True
    return JsonResponse(result, safe=False)


from rest_framework import viewsets, filters,status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend


class CountryViewSet(viewsets.ModelViewSet):
    queryset = Counties.objects.all()
    serializer_class = CountrySerializers
    permission_classes = [AllowAny]  # 允許公開訪問

class TravelViewSet(viewsets.ModelViewSet):
    queryset = Travel.objects.all().order_by('travel_id') 
    serializer_class = TravelSerializers
    permission_classes = [AllowAny]  # 允許公開訪問

class TravelClassViewSet(viewsets.ModelViewSet):
    queryset = TravelClass.objects.all()
    serializer_class = TravelClassSerializers
    permission_classes = [AllowAny]  # 允許公開訪問

class TaiwanViewSet(viewsets.ModelViewSet):
    queryset = Taiwan.objects.all()
    serializer_class = TaiwanSerializers
    permission_classes = [AllowAny]  # 允許公開訪問

class SpotimagesspotPagination(PageNumberPagination):
    page_size=9 # 一頁幾筆資料
    page_size_query_param = 'page_size' # ?page_size=20
    def get_paginated_response(self, data):
        return Response({
            'total_page':self.page.paginator.num_pages,
            'current_page':self.page.number,
            'results': data
        })

# Create your views here.
class TravelFilterViewSet(viewsets.ModelViewSet):
    queryset = Travel.objects.all()
    serializer_class = TravelFilterSerializer
    permission_classes = [AllowAny]  # 允許公開訪問
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['travel_name']
    filterset_fields = ['class1']
    pagination_class = SpotimagesspotPagination
    

import os
import faiss # type: ignore
from sentence_transformers import SentenceTransformer 
from django.conf import settings

# 初始化模型和索引
model_name = 'sentence-transformers/distiluse-base-multilingual-cased-v1'
bi_encoder = SentenceTransformer(model_name)

# 使用絕對路徑加載索引文件
index_path = os.path.join(settings.BASE_DIR, 'travel_app/travel_model/vector.index')

if not os.path.exists(index_path):
    raise FileNotFoundError(f"索引文件不存在：{index_path}")

index = faiss.read_index(index_path)

class QueryViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny] 
    def create(self, request):
        try:
            # 從請求中獲取查詢
            list_query = request.data.get('queries', [])
            if not list_query or not isinstance(list_query, list):
                return Response({"error": "請提供有效的查詢句子列表"}, status=status.HTTP_400_BAD_REQUEST)
            # 將查詢轉換為向量
            embeddings = bi_encoder.encode(
                list_query,
                batch_size=512,
                show_progress_bar=False,
                normalize_embeddings=False
            )

            # 在索引中進行查詢
            D, I = index.search(embeddings, k=5)

            # 將結果轉換為可讀格式
            results = []
            for i in range(len(list_query)):
                results.append({
                    "query": list_query[i],
                    "similarities": D[i].tolist(),
                    "document_ids": I[i].tolist()
                })

            return Response({"results": results}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def api_test(request):
    """
    顯示API測試頁面
    """
    return render(request, 'travel/api_test.html', {
        'title': 'API測試',
        'active_menu': 'travel'  # 設置active_menu為travel
    })

# Haversine公式，計算兩個經緯度點之間的距離
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # 地球半徑，單位：公里
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = math.sin(delta_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c  # 返回距離，單位：公里

def find_nearest_neighbor(points, start_point, distances):
    """使用最近鄰居算法找出一條路徑"""
    current = start_point
    unvisited = set(points) - {start_point}
    path = [current]
    total_distance = 0
    
    while unvisited:
        next_point = min(unvisited, key=lambda x: distances[(current, x)])
        total_distance += distances[(current, next_point)]
        current = next_point
        unvisited.remove(current)
        path.append(current)
    
    return path, total_distance

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
@authentication_classes([])
def find_path(request):
    """
    尋找最佳路徑的API endpoint
    支持 GET 和 POST 請求，允許未認證訪問
    
    POST 請求格式:
    {
        "path": [
            [latitude1, longitude1],
            [latitude2, longitude2],
            ...
        ],
        "start_point": [latitude, longitude],  # 可選
        "end_point": [latitude, longitude]     # 可選
    }
    """
    try:
        if request.method == 'GET':
            # 返回API使用說明
            return Response({
                'message': '請使用 POST 請求並提供以下格式的數據',
                'format': {
                    'path': [
                        [25.0330, 121.5654],
                        [25.0335, 121.5660],
                        [25.0340, 121.5665],
                        [25.0359, 121.5678]
                    ],
                    'start_point': [25.0330, 121.5654],  # 可選
                    'end_point': [25.0359, 121.5678]     # 可選
                },
                '說明': '提供一個路徑點列表，可選起點和終點，系統會計算出最佳遊覽順序'
            })
        
        # 驗證請求數據
        if not request.data:
            return Response({
                'error': '請求數據不能為空'
            }, status=400)
            
        if 'path' not in request.data:
            return Response({
                'error': '請求數據必須包含 "path" 欄位'
            }, status=400)
            
        path_points = request.data['path']
        start_point = request.data.get('start_point')
        end_point = request.data.get('end_point')
        
        # 驗證路徑點
        if not isinstance(path_points, list):
            return Response({
                'error': 'path 必須是一個列表'
            }, status=400)
            
        if len(path_points) < 2:
            return Response({
                'error': '至少需要提供兩個路徑點'
            }, status=400)
            
        # 驗證每個點的格式並轉換為元組
        validated_points = []
        for point in path_points:
            if not isinstance(point, list) or len(point) != 2:
                return Response({
                    'error': '每個路徑點必須是包含兩個數值的列表 [緯度, 經度]'
                }, status=400)
            try:
                lat, lon = float(point[0]), float(point[1])
                if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                    return Response({
                        'error': f'無效的經緯度值: [{lat}, {lon}]'
                    }, status=400)
                validated_points.append((lat, lon))  # 轉換為元組
            except (ValueError, TypeError):
                return Response({
                    'error': '路徑點的經緯度必須是數值'
                }, status=400)
        
        # 驗證起點和終點（如果有提供）
        start_index = None
        end_index = None
        
        if start_point:
            try:
                start_lat, start_lon = float(start_point[0]), float(start_point[1])
                if not (-90 <= start_lat <= 90) or not (-180 <= start_lon <= 180):
                    return Response({
                        'error': f'無效的起點經緯度值: [{start_lat}, {start_lon}]'
                    }, status=400)
                # 找到最接近起點的位置
                start_index = min(range(len(validated_points)), 
                                key=lambda i: haversine(start_lat, start_lon, 
                                                      validated_points[i][0], 
                                                      validated_points[i][1]))
            except (ValueError, TypeError, IndexError):
                return Response({
                    'error': '起點格式無效'
                }, status=400)
                
        if end_point:
            try:
                end_lat, end_lon = float(end_point[0]), float(end_point[1])
                if not (-90 <= end_lat <= 90) or not (-180 <= end_lon <= 180):
                    return Response({
                        'error': f'無效的終點經緯度值: [{end_lat}, {end_lon}]'
                    }, status=400)
                # 找到最接近終點的位置
                end_index = min(range(len(validated_points)), 
                              key=lambda i: haversine(end_lat, end_lon, 
                                                    validated_points[i][0], 
                                                    validated_points[i][1]))
            except (ValueError, TypeError, IndexError):
                return Response({
                    'error': '終點格式無效'
                }, status=400)
        
        # 計算所有點之間的距離矩陣
        n = len(validated_points)
        distances = [[0] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                if i != j:
                    distances[i][j] = haversine(
                        validated_points[i][0], validated_points[i][1],
                        validated_points[j][0], validated_points[j][1]
                    )
        
        # 使用最近鄰居算法找出最佳路徑
        def find_best_path():
            best_distance = float('inf')
            best_path = None
            
            # 確定起點範圍
            start_points = [start_index] if start_index is not None else range(n)
            
            # 嘗試每個可能的起點
            for start in start_points:
                unvisited = set(range(n))
                current = start
                path = [current]
                total_distance = 0
                unvisited.remove(current)
                
                # 如果有指定終點，確保它是最後訪問的
                if end_index is not None:
                    unvisited.remove(end_index)
                
                # 不斷找最近的下一個點
                while unvisited:
                    next_point = min(unvisited, key=lambda x: distances[current][x])
                    total_distance += distances[current][next_point]
                    current = next_point
                    path.append(current)
                    unvisited.remove(current)
                
                # 如果有指定終點，將其加入路徑末尾
                if end_index is not None:
                    total_distance += distances[current][end_index]
                    path.append(end_index)
                
                # 如果這條路徑更短，就更新最佳路徑
                if total_distance < best_distance:
                    best_distance = total_distance
                    best_path = path
        
            return best_path, best_distance
        
        # 計算最佳路徑
        best_path_indices, total_distance = find_best_path()
        
        if best_path_indices:
            # 將索引轉換回實際的路徑點
            optimal_path = [validated_points[i] for i in best_path_indices]
            
            return Response({
                'success': True,
                'path': [list(point) for point in optimal_path],  # 轉回列表以便 JSON 序列化
                'total_distance': round(total_distance, 2),  # 四捨五入到小數點後兩位
                'unit': 'kilometers'
            })
        else:
            return Response({
                'error': '無法找到有效路徑'
            }, status=404)
            
    except Exception as e:
        return Response({
            'error': f'處理請求時發生錯誤: {str(e)}'
        }, status=500)
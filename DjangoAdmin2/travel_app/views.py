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
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from .serializers import TravelSerializers,TravelClassSerializers,TaiwanSerializers,TravelFilterSerializer,CountrySerializers
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

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
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

class TravelViewSet(viewsets.ModelViewSet):
    queryset = Travel.objects.all()
    serializer_class = TravelSerializers
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

class TravelClassViewSet(viewsets.ModelViewSet):
    queryset = TravelClass.objects.all()
    serializer_class = TravelClassSerializers
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

class TaiwanViewSet(viewsets.ModelViewSet):
    queryset = Taiwan.objects.all()
    serializer_class = TaiwanSerializers
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

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
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter ]
    search_fields = ['travel_name']



    # # 過濾 where categoryid=1
    filterset_fields = ['class1']
    # # 分頁功能
    pagination_class= SpotimagesspotPagination
    

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


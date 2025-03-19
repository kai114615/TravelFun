from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
import json
from .models import Product, Carousel, CategoryDisplay, RecommendedProduct, Order, OrderItem
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
import uuid
from datetime import datetime
import urllib.parse
import re
import random
import time
from rest_framework.response import Response
from rest_framework import status

@login_required
@user_passes_test(lambda u: u.is_staff)
def shop_layout(request):
    """商城版面管理視圖"""
    carousels = Carousel.objects.all()
    categories = CategoryDisplay.objects.all()
    recommended_products = RecommendedProduct.objects.all()
    
    return render(request, 'admin-dashboard/shop/layout.html', {
        'title': '版面管理',
        'carousels': carousels,
        'categories': categories,
        'recommended_products': recommended_products
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def product_list(request):
    """商品列表視圖"""
    try:
        products = Product.objects.all()
        print("商品列表：", products.count(), "個商品")
        print("SQL查詢：", str(products.query))
        for product in products:
            print(f"商品ID: {product.id}, 名稱: {product.name}, 類別: {product.category}")
        
        context = {
            'title': '商品列表',
            'products': products
        }
        print("模板上下文：", context)
        
        response = render(request, 'admin-dashboard/shop/product_list.html', context)
        print("渲染的模板路徑：admin-dashboard/shop/product_list.html")
        return response
    except Exception as e:
        print("商品列表視圖出錯：", str(e))
        raise

@login_required
@user_passes_test(lambda u: u.is_staff)
def product_create(request):
    """新增商品視圖"""
    if request.method == 'POST':
        try:
            # 處理表單提交
            data = request.POST
            
            product = Product.objects.create(
                name=data['name'],
                category=data['category'],
                price=data['price'],
                description=data['description'],
                stock=int(data['stock']),
                is_active=data.get('is_active', False) == 'on',
                image_url=data.get('image_url', '')
            )
            
            return redirect('shopping_system:product_list')
        except Exception as e:
            print("創建商品時出錯：", str(e))
            return render(request, 'admin-dashboard/shop/product_form.html', {
                'title': '新增商品',
                'error': str(e)
            })
        
    return render(request, 'admin-dashboard/shop/product_form.html', {
        'title': '新增商品'
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def product_detail(request, pk):
    """商品詳情視圖"""
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'admin-dashboard/shop/product_detail.html', {
        'title': '商品詳情',
        'product': product
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def product_update(request, pk):
    """更新商品視圖"""
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        try:
            # 處理表單提交
            data = request.POST
            
            product.name = data['name']
            product.category = data['category']
            product.price = data['price']
            product.description = data['description']
            product.stock = int(data['stock'])
            product.is_active = data.get('is_active', '') == 'on'
            product.image_url = data.get('image_url', '')
                
            product.save()
            return redirect('shopping_system:product_detail', pk=product.id)
        except Exception as e:
            print("更新商品時出錯：", str(e))
            return render(request, 'admin-dashboard/shop/product_form.html', {
                'title': '編輯商品',
                'product': product,
                'error': str(e)
            })
        
    return render(request, 'admin-dashboard/shop/product_form.html', {
        'title': '編輯商品',
        'product': product
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def product_delete(request, pk):
    """刪除商品視圖"""
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('shopping_system:product_list')
    return render(request, 'admin-dashboard/shop/product_confirm_delete.html', {
        'title': '刪除商品',
        'product': product
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def shop_api_test(request):
    """API 測試頁面"""
    return render(request, 'admin-dashboard/shop/api_test.html', {
        'title': 'API 測試',
        'active_menu': 'shop_api_test'
    })

@csrf_exempt
@api_view(['GET', 'POST', 'PUT', 'DELETE'])
@permission_classes([AllowAny])  # 允許所有用戶訪問
def product_api(request, product_id=None):
    """商品 API 視圖"""
    print(f"收到 {request.method} 請求，product_id: {product_id}")  # 調試日誌
    
    if request.method == 'GET':
        try:
            if product_id:
                product = get_object_or_404(Product, pk=product_id)
                data = {
                    'id': product.id,
                    'name': product.name,
                    'category': product.category,
                    'price': str(product.price),
                    'description': product.description,
                    'stock': product.stock,
                    'is_active': product.is_active,
                    'image_url': product.get_image_url()
                }
            else:
                products = Product.objects.filter(is_active=True)  # 只返回已上架的商品
                print(f"找到 {products.count()} 個商品")  # 調試日誌
                data = [{
                    'id': p.id,
                    'name': p.name,
                    'category': p.category,
                    'price': str(p.price),
                    'description': p.description,
                    'stock': p.stock,
                    'is_active': p.is_active,
                    'image_url': p.get_image_url()
                } for p in products]
            print("返回數據：", data)  # 調試日誌
            return JsonResponse(data, safe=False)
        except Exception as e:
            print("API錯誤：", str(e))  # 調試日誌
            return JsonResponse({'error': str(e)}, status=500)
    
    elif request.method == 'POST':
        data = json.loads(request.body)
        product = Product.objects.create(
            name=data['name'],
            category=data['category'],
            price=data['price'],
            description=data.get('description', ''),
            stock=data.get('stock', 0),
            is_active=data.get('is_active', True),
            image_url=data.get('image_url', '')
        )
        return JsonResponse({
            'id': product.id,
            'name': product.name,
            'category': product.category,
            'price': str(product.price),
            'description': product.description,
            'stock': product.stock,
            'is_active': product.is_active,
            'image_url': product.get_image_url()
        }, status=201)
    
    elif request.method == 'PUT':
        product = get_object_or_404(Product, pk=product_id)
        data = json.loads(request.body)
        
        product.name = data.get('name', product.name)
        product.category = data.get('category', product.category)
        product.price = data.get('price', product.price)
        product.description = data.get('description', product.description)
        product.stock = data.get('stock', product.stock)
        product.is_active = data.get('is_active', product.is_active)
        product.image_url = data.get('image_url', product.image_url)
        
        product.save()
        return JsonResponse({
            'id': product.id,
            'name': product.name,
            'category': product.category,
            'price': str(product.price),
            'description': product.description,
            'stock': product.stock,
            'is_active': product.is_active,
            'image_url': product.get_image_url()
        })
    
    elif request.method == 'DELETE':
        product = get_object_or_404(Product, pk=product_id)
        product.delete()
        return JsonResponse({'message': '商品已刪除'})

# 版面管理相關的 API
@require_http_methods(['GET', 'POST', 'PUT', 'DELETE'])
def carousel_api(request, carousel_id=None):
    """輪播圖 API"""
    if request.method == 'GET':
        if carousel_id:
            carousel = get_object_or_404(Carousel, pk=carousel_id)
            data = {
                'id': carousel.id,
                'title': carousel.title,
                'url': carousel.url,
                'order': carousel.order,
                'is_active': carousel.is_active,
                'image_url': carousel.get_image_url()
            }
        else:
            carousels = Carousel.objects.all()
            data = [{
                'id': c.id,
                'title': c.title,
                'url': c.url,
                'order': c.order,
                'is_active': c.is_active,
                'image_url': c.get_image_url()
            } for c in carousels]
        return JsonResponse(data, safe=False)

@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def category_display_api(request, category_id=None):
    """分類 API 視圖"""
    try:
        if category_id:
            category = get_object_or_404(CategoryDisplay, pk=category_id, is_active=True)
            data = {
                'id': category.id,
                'name': category.category,
                'description': category.description,
                'icon': category.icon
            }
        else:
            categories = CategoryDisplay.objects.filter(is_active=True).order_by('order')
            data = [{
                'id': c.id,
                'name': c.category,
                'description': c.description,
                'icon': c.icon
            } for c in categories]
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(['GET', 'POST', 'PUT', 'DELETE'])
def recommended_product_api(request, recommended_id=None):
    """推薦商品 API"""
    if request.method == 'GET':
        if recommended_id:
            recommended = get_object_or_404(RecommendedProduct, pk=recommended_id)
            data = {
                'id': recommended.id,
                'product': {
                    'id': recommended.product.id,
                    'name': recommended.product.name
                },
                'position': recommended.position,
                'order': recommended.order,
                'is_active': recommended.is_active,
                'start_time': recommended.start_time.isoformat() if recommended.start_time else None,
                'end_time': recommended.end_time.isoformat() if recommended.end_time else None
            }
        else:
            recommended_products = RecommendedProduct.objects.all()
            data = [{
                'id': r.id,
                'product': {
                    'id': r.product.id,
                    'name': r.product.name
                },
                'position': r.position,
                'order': r.order,
                'is_active': r.is_active,
                'start_time': r.start_time.isoformat() if r.start_time else None,
                'end_time': r.end_time.isoformat() if r.end_time else None
            } for r in recommended_products]
        return JsonResponse(data, safe=False)

@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def export_mall_products_json(request):
    """
    導出商城商品資料到JSON檔案
    此API不會影響現有的商品API功能
    """
    try:
        # 獲取所有商品資料
        products = Product.objects.all()
        
        # 準備JSON資料
        products_data = []
        for product in products:
            product_data = {
                'id': product.id,
                'name': product.name,
                'category': product.category,
                'price': str(product.price),
                'description': product.description,
                'stock': product.stock,
                'is_active': product.is_active,
                'image_url': product.get_image_url(),
                'created_at': product.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': product.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            products_data.append(product_data)
        
        # 將資料寫入JSON檔案
        import os
        json_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                    'src', 'views', 'front', 'Mall', 'data', 'MallProduct.json')
        
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(products_data, f, ensure_ascii=False, indent=2)
        
        return JsonResponse({
            'status': 'success',
            'message': f'成功導出 {len(products_data)} 筆商品資料到 MallProduct.json',
            'total_products': len(products_data)
        })
        
    except Exception as e:
        print("導出商品資料時發生錯誤：", str(e))
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def add_to_cart(request):
    """加入購物車 API"""
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)
        
        # 檢查商品是否存在
        product = get_object_or_404(Product, id=product_id)
        
        # 檢查庫存
        if product.stock < quantity:
            return JsonResponse({
                'success': False,
                'message': '商品庫存不足'
            }, status=400)
        
        # TODO: 這裡應該實現購物車功能
        # 暫時直接返回成功
        return JsonResponse({
            'success': True,
            'message': '成功加入購物車'
        })
        
    except Product.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': '商品不存在'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)

@csrf_exempt
@api_view(['GET', 'POST', 'OPTIONS'])  # 新增OPTIONS方法以支持跨域預檢請求
@permission_classes([AllowAny])  # 允許未認證用戶創建訂單
def create_order(request):
    """創建訂單API"""
    # 如果是OPTIONS請求（跨域預檢請求），直接返回成功
    if request.method == 'OPTIONS':
        return Response(status=status.HTTP_200_OK)
        
    # 打印完整請求信息用於調試
    print("=" * 80)
    print(f"收到訂單請求 - 方法: {request.method}, 路徑: {request.path}")
    print(f"請求頭: {request.headers}")
    print(f"請求數據: {request.data}")
    print(f"請求來源: {request.META.get('HTTP_ORIGIN', '未知')}")
    print(f"請求IP: {request.META.get('REMOTE_ADDR', '未知')}")
    print("=" * 80)
    
    # 測試響應 - 返回一個簡單的成功消息，測試API是否可訪問
    if request.method == 'GET':
        return JsonResponse({
            'success': True,
            'message': '訂單API可正常訪問',
            'method': 'GET',
            'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
    # 處理POST請求 - 創建訂單
    if request.method == 'POST':
        try:
            # 獲取請求數據
            data = request.data
            
            # 獲取用戶信息
            user = None
            if request.user.is_authenticated:
                user = request.user
                print(f"認證用戶: {user.username}")
            else:
                print("未認證用戶")
                # 嘗試從請求頭中獲取token
                auth_header = request.headers.get('Authorization', '')
                if auth_header.startswith('Bearer '):
                    token = auth_header.split(' ')[1]
                    try:
                        from django.contrib.auth.models import User
                        from rest_framework_simplejwt.tokens import AccessToken
                        token_obj = AccessToken(token)
                        user_id = token_obj['user_id']
                        user = User.objects.get(id=user_id)
                        print(f"通過token找到用戶: {user.username}")
                    except Exception as e:
                        print(f"Token解析錯誤: {str(e)}")
            
            # 取得訂單數據
            payment_method = data.get('payment_method', 'cash_on_delivery')
            
            # 嘗試獲取收件人信息 - 支持兩種格式
            shipping_info = data.get('shipping_info', {})
            if shipping_info:
                # 如果使用shipping_info格式
                shipping_name = shipping_info.get('name')
                shipping_phone = shipping_info.get('phone')
                shipping_address = shipping_info.get('address')
                shipping_note = shipping_info.get('note', '')
            else:
                # 如果直接使用shipping_name等格式
                shipping_name = data.get('shipping_name')
                shipping_phone = data.get('shipping_phone')
                shipping_address = data.get('shipping_address')
                shipping_note = data.get('shipping_note', '')
            
            print(f"處理的收件人信息: 姓名={shipping_name}, 電話={shipping_phone}, 地址={shipping_address}")
            
            # 驗證訂單必填字段
            if not shipping_name or not shipping_phone or not shipping_address:
                print(f"收件人信息不完整: 姓名={shipping_name}, 電話={shipping_phone}, 地址={shipping_address}")
                return JsonResponse({
                    'success': False,
                    'message': '請提供完整的收件人信息'
                }, status=400)
            
            # 從請求中提取items數據
            items_data = data.get('items', [])
            
            print(f"訂單項目數據: {items_data}")
            
            # 如果沒有商品項目，返回錯誤
            if not items_data:
                return JsonResponse({
                    'success': False,
                    'message': '訂單中沒有商品項目'
                }, status=400)
        
            # 生成訂單編號
            import datetime
            import random
            current_date = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            random_suffix = ''.join([str(random.randint(0, 9)) for _ in range(4)])
            order_number = f"ORD{current_date}{random_suffix}"
            
            # 計算訂單總金額並處理訂單項目
            total_amount = 0
            order_items = []
            
            for item_data in items_data:
                try:
                    product_id = item_data.get('product_id')
                    quantity = int(item_data.get('quantity', 1))
                    
                    # 獲取商品
                    try:
                        product = Product.objects.get(id=product_id)
                        item_price = product.price
                    except Product.DoesNotExist:
                        print(f"商品不存在(ID: {product_id})，使用默認價格")
                        product = None
                        item_price = 100  # 默認價格
                    
                    # 計算小計
                    item_total = item_price * quantity
                    total_amount += item_total
                    
                    # 添加訂單項目
                    order_items.append({
                        'product': product,
                        'product_id': product_id,
                        'quantity': quantity,
                        'price': item_price
                    })
                    
                    print(f"添加訂單項目: 商品ID={product_id}, 數量={quantity}, 單價={item_price}, 小計={item_total}")
                    
                except Exception as e:
                    print(f"處理訂單項目時出錯: {str(e)}")
                    # 繼續處理其他項目
            
            if not order_items:
                return JsonResponse({
                    'success': False,
                    'message': '無法處理任何訂單項目'
                }, status=400)
        
            # 創建訂單記錄
            try:
                order = Order.objects.create(
                    user=user,
                    order_number=order_number,
                    total_amount=total_amount,
                    status='pending',
                    payment_method=payment_method,
                    shipping_name=shipping_name,
                    shipping_phone=shipping_phone,
                    shipping_address=shipping_address,
                    shipping_note=shipping_note
                )
                
                # 創建訂單項目記錄
                for item in order_items:
                    if item['product']:
                        OrderItem.objects.create(
                            order=order,
                            product=item['product'],
                            quantity=item['quantity'],
                            price=item['price']
                        )
                    else:
                        # 如果產品不存在，使用ID創建
                        OrderItem.objects.create(
                            order=order,
                            product_id=item['product_id'],
                            quantity=item['quantity'],
                            price=item['price']
                        )
                
                print(f"成功創建訂單: {order_number}, 總金額: {total_amount}")
            
                # 返回成功訊息
                return JsonResponse({
                    'success': True,
                    'message': '訂單創建成功',
                    'order_id': order.id,
                    'order_number': order_number,
                    'total_amount': str(total_amount)
                })
            
            except Exception as e:
                import traceback
                traceback.print_exc()
                print(f"創建訂單記錄時出錯: {str(e)}")
                return JsonResponse({
                    'success': False,
                    'message': f'創建訂單失敗: {str(e)}'
                }, status=500)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"處理訂單請求時出錯: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': f'處理訂單時出錯: {str(e)}'
            }, status=500)

@login_required
@user_passes_test(lambda u: u.is_staff)
def order_list(request):
    """訂單列表視圖"""
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'admin-dashboard/shop/order_list.html', {
        'title': '訂單列表',
        'orders': orders
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def order_detail(request, pk):
    """訂單詳情視圖"""
    order = get_object_or_404(Order, pk=pk)
    order_items = OrderItem.objects.filter(order=order)
    
    return render(request, 'admin-dashboard/shop/order_detail.html', {
        'title': '訂單詳情',
        'order': order,
        'order_items': order_items
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def order_update_status(request, pk):
    """更新訂單狀態"""
    if request.method == 'POST':
        try:
            order = get_object_or_404(Order, pk=pk)
            data = json.loads(request.body)
            new_status = data.get('status')
            
            if new_status:
                order.status = new_status
                order.save()
                return JsonResponse({'success': True, 'message': f'訂單狀態已更新為 {new_status}'})
            else:
                return JsonResponse({'success': False, 'message': '未提供狀態參數'}, status=400)
                
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'message': '僅支持POST請求'}, status=405)

@login_required
@user_passes_test(lambda u: u.is_staff)
def order_delete(request, pk):
    """刪除訂單"""
    order = get_object_or_404(Order, pk=pk)
    
    if request.method == 'POST':
        try:
            order.delete()
            return redirect('shopping_system:order_list')
        except Exception as e:
            return render(request, 'admin-dashboard/shop/order_list.html', {
                'title': '訂單列表',
                'orders': Order.objects.all().order_by('-created_at'),
                'error': f'刪除訂單時出錯: {e}'
            })
    
    return render(request, 'admin-dashboard/shop/order_confirm_delete.html', {
        'title': '確認刪除訂單',
        'order': order
    })

@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def all_orders(request):
    """獲取所有訂單API - 如果用戶已登入則返回該用戶的訂單，否則返回空列表
    
    這個API端點主要用於前端訂單管理頁面顯示訂單列表
    API路徑: /api/shopping/orders/
    
    參數:
    - page: 頁碼，預設為1
    - per_page: 每頁數量，預設為10
    - order_by: 排序欄位，預設為'-created_at'
    - status: 訂單狀態過濾，可選
    
    返回:
    {
        'success': True/False,
        'message': '成功/錯誤訊息',
        'data': [...訂單數據...],
        'pagination': {
            'total': 總數,
            'page': 當前頁,
            'per_page': 每頁數量,
            'total_pages': 總頁數
        }
    }
    """
    try:
        # 獲取當前用戶 - 可以是登入用戶或匿名用戶
        user = request.user
        
        # 獲取分頁和排序參數
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))
        order_by = request.GET.get('order_by', '-created_at')
        status = request.GET.get('status', None)
        order_number = request.GET.get('order_number', None)
        
        # 如果提供了訂單號，優先查詢該訂單
        if order_number:
            query = Order.objects.filter(order_number=order_number)
            if not query.exists():
                return JsonResponse({
                    'success': False,
                    'message': f'找不到訂單號: {order_number}',
                    'data': [],
                    'pagination': {
                        'total': 0,
                        'page': 1,
                        'per_page': per_page,
                        'total_pages': 0
                    }
                })
        # 如果用戶已登入，則返回該用戶的訂單，否則返回空列表
        elif user.is_authenticated:
            # 建立基本查詢
            query = Order.objects.filter(user=user)
        else:
            # 未登入用戶返回空列表
            return JsonResponse({
                'success': True,
                'message': '未登入，無法查看訂單',
                'data': [],
                'pagination': {
                    'total': 0,
                    'page': 1,
                    'per_page': per_page,
                    'total_pages': 0
                }
            })
            
        # 添加狀態過濾
        if status:
            query = query.filter(status=status)
        
        # 添加排序
        query = query.order_by(order_by)
        
        # 計算總數
        total = query.count()
        
        # 計算分頁
        start = (page - 1) * per_page
        end = start + per_page
        orders = query[start:end]
        
        # 構建響應數據
        orders_data = []
        for order in orders:
            # 獲取訂單項目
            items = OrderItem.objects.filter(order=order)
            items_data = []
            for item in items:
                # 檢查 product 是否存在，因為可能已被刪除
                product_name = item.product.name if item.product else "商品已下架"
                product_image = item.product.get_image_url() if item.product else None
                items_data.append({
                    'id': item.id,
                    'product_id': item.product.id if item.product else None,
                    'product_name': product_name,
                    'product_image': product_image,
                    'price': str(item.price),
                    'quantity': item.quantity,
                })
            
            # 獲取物流資訊，如果有的話
            logistics_data = None
            if order.logistics_info:
                try:
                    logistics_data = json.loads(order.logistics_info)
                except:
                    logistics_data = None
            
            orders_data.append({
                'id': order.id,
                'order_number': order.order_number,
                'status': order.status,
                'payment_method': order.payment_method,
                'total_amount': str(order.total_amount),
                'shipping_name': order.shipping_name,
                'shipping_phone': order.shipping_phone,
                'shipping_address': order.shipping_address,
                'shipping_note': order.shipping_note,
                'created_at': order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': order.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                'logistics_id': order.logistics_id,
                'logistics_status': order.logistics_status,
                'logistics_info': logistics_data,
                'items': items_data
            })
        
        return JsonResponse({
            'success': True,
            'message': '成功獲取訂單',
            'data': orders_data,
            'pagination': {
                'total': total,
                'page': page,
                'per_page': per_page,
                'total_pages': (total + per_page - 1) // per_page
            }
        })
    except Exception as e:
        print(f"獲取訂單列表出錯: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'獲取訂單失敗: {str(e)}'
        }, status=500)

@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def user_orders(request):
    """獲取用戶的訂單列表 - 與all_orders提供相同功能，為了兼容性保留"""
    return all_orders(request)

@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def order_api_detail(request, order_id):
    """獲取訂單詳情API"""
    try:
        print(f"=== 獲取訂單詳情 ID: {order_id} ===")
        
        # 檢查用戶是否登入
        user = request.user
        if not user.is_authenticated:
            # 嘗試從請求中獲取 token
            auth_header = request.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
                try:
                    from django.contrib.auth.models import User
                    from rest_framework_simplejwt.tokens import AccessToken
                    token_obj = AccessToken(token)
                    user_id = token_obj['user_id']
                    user = User.objects.get(id=user_id)
                    print(f"通過token找到用戶: {user.username}")
                except Exception as e:
                    print(f"從token獲取用戶失敗: {str(e)}")
                    return JsonResponse({
                        'success': False,
                        'message': '用戶未登入或Token無效'
                    }, status=401)
            else:
                print("未提供授權頭或非Bearer格式")
                return JsonResponse({
                    'success': False,
                    'message': '未提供有效的授權資訊'
                }, status=401)
        
        # 查詢訂單
        try:
            # 嘗試先用ID找訂單
            try:
                order = Order.objects.get(id=order_id)
            except (Order.DoesNotExist, ValueError):
                # 如果ID找不到，嘗試用訂單號找
                print(f"用ID找不到訂單，嘗試用訂單號...")
                try:
                    order = Order.objects.get(order_number=order_id)
                except Order.DoesNotExist:
                    print(f"找不到訂單: {order_id}")
                    return JsonResponse({
                        'success': False,
                        'message': f'找不到訂單: {order_id}'
                    }, status=404)
            
            # 檢查是否為訂單所有者
            if order.user and order.user != user and not user.is_staff:
                print(f"用戶 {user.username} 嘗試查看不屬於他的訂單")
                return JsonResponse({
                    'success': False,
                    'message': '無權查看此訂單'
                }, status=403)
            
            # 獲取訂單項目
            order_items = OrderItem.objects.filter(order=order)
            items_data = []
            
            for item in order_items:
                # 檢查product是否還存在
                if item.product:
                    product_name = item.product.name
                    product_image = item.product.get_image_url()
                    product_id = item.product.id
                else:
                    product_name = "商品已下架"
                    product_image = None
                    product_id = None
                    
                items_data.append({
                    'id': item.id,
                    'product_id': product_id,
                    'product_name': product_name,
                    'product_image': product_image,
                    'price': str(item.price),
                    'quantity': item.quantity,
                    'subtotal': str(item.price * item.quantity)
                })
            
            # 獲取物流信息
            logistics_data = None
            if order.logistics_info:
                try:
                    logistics_data = json.loads(order.logistics_info)
                except json.JSONDecodeError:
                    print(f"解析物流信息失敗: {order.logistics_info}")
                    logistics_data = None
            
            # 構建訂單詳情
            order_data = {
                'id': order.id,
                'order_number': order.order_number,
                'status': order.status,
                'payment_method': order.payment_method,
                'total_amount': str(order.total_amount),
                'recipient_name': order.shipping_name,
                'recipient_phone': order.shipping_phone,
                'shipping_address': order.shipping_address,
                'shipping_note': order.shipping_note,
                'order_date': order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': order.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                'logistics_id': order.logistics_id,
                'logistics_status': order.logistics_status,
                'logistics_info': logistics_data,
                'items': items_data
            }
            
            print(f"成功獲取訂單詳情: {order.order_number}")
            
            # 返回訂單詳情
            return JsonResponse({
                'success': True,
                'message': '成功獲取訂單詳情',
                'data': order_data
            })
            
        except Exception as e:
            print(f"查詢訂單詳情失敗: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': f'查詢訂單失敗: {str(e)}'
            }, status=500)
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"處理訂單詳情請求發生錯誤: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'處理請求時發生錯誤: {str(e)}'
        }, status=500)

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def ecpay_payment(request):
    """綠界金流付款處理"""
    try:
        # 獲取訂單資訊
        order_id = request.data.get('order_id')
        
        # 記錄請求
        print(f"收到綠界金流請求: order_id={order_id}, 資料={request.data}")
        
        # 查詢訂單
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': '找不到訂單資訊'
            }, status=404)
        
        # 檢查訂單狀態
        if order.status != 'pending':
            return JsonResponse({
                'success': False,
                'message': '訂單狀態不正確，無法進行支付'
            }, status=400)
        
        # 導入綠界金流SDK
        import importlib.util
        import sys
        import os
        
        # 取得SDK路徑
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sdk_path = os.path.join(base_dir, 'ECPayAIO_Python-master', 'sdk', 'ecpay_payment_sdk.py')
        
        print(f"綠界SDK路徑: {sdk_path}")
        
        # 檢查SDK是否存在
        if not os.path.exists(sdk_path):
            print(f"警告: 找不到綠界SDK文件於 {sdk_path}")
            return JsonResponse({
                'success': False,
                'message': '找不到綠界金流SDK，請確認系統設定'
            }, status=500)
        
        # 動態導入SDK
        spec = importlib.util.spec_from_file_location("ecpay_payment_sdk", sdk_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # 建立綠界金流實例
        ecpay_payment_sdk = module.ECPayPaymentSdk(
            MerchantID='2000132',  # 綠界測試環境特店編號
            HashKey='5294y06JbISpM5x9',  # 綠界測試環境HashKey
            HashIV='v77hoKGq4kWxNNIS'  # 綠界測試環境HashIV
        )
        
        # 使用原訂單編號作為綠界訂單編號 (但確保不超過20字元)
        # 綠界規定MerchantTradeNo長度不能超過20且只能包含英數字
        merchant_trade_no = order.order_number
        
        # 確保訂單編號只包含英數字且長度不超過20
        if len(merchant_trade_no) > 20 or not re.match(r'^[a-zA-Z0-9]+$', merchant_trade_no):
            print(f"警告: 訂單編號 {merchant_trade_no} 不符合綠界規範，進行修正")
            # 保留前15位，再加上當前時間戳的後5位，確保唯一性
            timestamp = str(int(time.time()))[-5:]
            merchant_trade_no = re.sub(r'[^a-zA-Z0-9]', '', merchant_trade_no)[:15] + timestamp
            
            # 儲存修改後的訂單編號回資料庫，確保一致性
            order.order_number = merchant_trade_no
            order.save()
            
            print(f"修正後的訂單編號: {merchant_trade_no}")
        
        print(f"綠界訂單編號: {merchant_trade_no}")
        print(f"綠界訂單編號長度: {len(merchant_trade_no)}")
        
        # 取得商品名稱 (最多三項商品，超過的合併為其他商品)
        items = OrderItem.objects.filter(order=order)
        item_names = []
        for idx, item in enumerate(items[:3]):
            item_names.append(f"{item.product.name} x {item.quantity}")
        
        if items.count() > 3:
            item_names.append(f"其他商品 x {items.count() - 3}")
        
        # 組合商品名稱
        item_name = "#".join(item_names)
        
        # 取得前端網址域名
        frontend_domain = request.data.get('frontend_domain', 'http://localhost:3333')
        
        print(f"前端域名: {frontend_domain}")
        print(f"當前後端URL: {request.build_absolute_uri('/')}")
        
        # 組建完整的API回調URL (確保URL包含域名和完整路徑)
        backend_base_url = request.build_absolute_uri('/').rstrip('/')
        notify_url = f"{backend_base_url}/api/ecpay/notify/"
        payment_info_url = f"{backend_base_url}/api/ecpay/payment_info/"
        
        print(f"付款通知URL: {notify_url}")
        print(f"付款資訊URL: {payment_info_url}")
        
        # 設定綠界金流參數 (嚴格按照API規格)
        order_params = {
            'MerchantID': '2000132',  # 綠界測試環境特店編號 (必填)
            'MerchantTradeNo': merchant_trade_no,  # 特店訂單編號 (必填)
            'MerchantTradeDate': datetime.now().strftime("%Y/%m/%d %H:%M:%S"),  # 特店交易時間 (必填)
            'PaymentType': 'aio',  # 交易類型 (必填)
            'TotalAmount': str(int(order.total_amount)),  # 交易金額 (必填) - 轉為字串
            'TradeDesc': '訂單購物',  # 交易描述 (必填) - 避免使用特殊字元，使用簡單描述
            'ItemName': item_name,  # 商品名稱 (必填)
            'ReturnURL': notify_url,  # 付款完成通知回傳網址 (必填)
            'ChoosePayment': 'ALL',  # 選擇預設付款方式 (必填)
            'EncryptType': '1',  # CheckMacValue加密類型 (必填) - 1代表SHA256
            
            # 以下為選填參數
            'ClientBackURL': f"{frontend_domain}/#/order-complete/{order.order_number}",  # 消費者付款完成後返回的網址
            'ItemURL': f"{frontend_domain}/#/member/orders",  # 商品資訊網址
            'OrderResultURL': f"{frontend_domain}/#/order-complete/{order.order_number}",  # 消費者付款完成後的轉導網址
            'NeedExtraPaidInfo': 'Y',  # 是否需要額外的付款資訊
        }
        
        # 加入延伸參數 (ATM, CVS, BARCODE)
        extend_params = {
            'ExpireDate': '7',  # ATM繳費期限 (計算單位為天) - 改為字串
            'PaymentInfoURL': payment_info_url,  # 取得額外付款資訊，回傳位址
            'ClientRedirectURL': '',  # 付款完成後的轉導位址
            'StoreExpireDate': '15',  # 超商繳費期限 (計算單位為天) - 改為字串
        }
        
        # 合併參數
        order_params.update(extend_params)
        
        try:
            # 產生綠界訂單所需參數
            final_order_params = ecpay_payment_sdk.create_order(order_params)
            
            # 產生 html 的 form 格式
            action_url = 'https://payment-stage.ecpay.com.tw/Cashier/AioCheckOut/V5'  # 測試環境
            # action_url = 'https://payment.ecpay.com.tw/Cashier/AioCheckOut/V5'  # 正式環境
            
            html = ecpay_payment_sdk.gen_html_post_form(action_url, final_order_params)
            
            print("已成功生成綠界金流表單HTML")
            
            # 更新訂單狀態
            order.payment_method = 'ecpay'
            order.save()
            
            # 返回 HTML 表單
            return JsonResponse({
                'success': True,
                'message': '訂單建立成功，正在導向到綠界金流付款頁面',
                'html_form': html,
                'order_id': order.id,
                'order_number': order.order_number
            })
            
        except Exception as error:
            print(f"綠界金流建立訂單失敗: {str(error)}")
            return JsonResponse({
                'success': False,
                'message': f'建立綠界金流訂單失敗: {str(error)}'
            }, status=500)
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': f'處理訂單時發生錯誤: {str(e)}'
        }, status=500)

@csrf_exempt
def ecpay_notify(request):
    """綠界金流付款結果通知處理"""
    try:
        # 取得所有回傳參數
        post_data = request.POST.dict()
        
        print("綠界付款通知接收到的資料:", post_data)
        
        # 驗證回傳的資料是否正確
        import importlib.util
        import os
        
        # 取得SDK路徑
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sdk_path = os.path.join(base_dir, 'ECPayAIO_Python-master', 'sdk', 'ecpay_payment_sdk.py')
        
        # 動態導入SDK
        spec = importlib.util.spec_from_file_location("ecpay_payment_sdk", sdk_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # 建立綠界金流實例 (使用測試環境參數，與支付時使用的參數一致)
        ecpay_payment_sdk = module.ECPayPaymentSdk(
            MerchantID='2000132',  # 綠界測試環境特店編號
            HashKey='5294y06JbISpM5x9',  # 綠界測試環境HashKey
            HashIV='v77hoKGq4kWxNNIS'  # 綠界測試環境HashIV
        )
        
        # 檢查交易狀態
        if post_data.get('RtnCode') == '1':  # 若交易成功
            # 從MerchantTradeNo取得訂單編號
            merchant_trade_no = post_data.get('MerchantTradeNo', '')
            
            print(f"處理訂單編號: {merchant_trade_no}")
            
            try:
                # 直接使用完整的MerchantTradeNo搜尋訂單
                order = Order.objects.get(order_number=merchant_trade_no)
                
                # 更新訂單狀態
                order.status = 'paid'
                
                # 記錄支付資訊
                order.payment_info = {
                    'payment_type': post_data.get('PaymentType', ''),
                    'trade_no': post_data.get('TradeNo', ''),
                    'paid_amount': post_data.get('TradeAmt', ''),
                    'payment_date': post_data.get('PaymentDate', ''),
                    'payment_method': 'ecpay',
                    'rtn_code': post_data.get('RtnCode', ''),
                    'rtn_msg': post_data.get('RtnMsg', '')
                }
                
                order.save()
                
                print(f"訂單 {merchant_trade_no} 支付成功，已更新訂單狀態: {order.status}")
                
                # 支付成功，回覆綠界金流
                return HttpResponse('1|OK')
            except Order.DoesNotExist:
                # 嘗試通過模糊匹配找出訂單
                print(f"無法直接匹配訂單編號 {merchant_trade_no}，嘗試模糊匹配")
                
                # 查找所有包含該模式的訂單
                from django.db.models import Q
                matching_orders = Order.objects.filter(
                    Q(order_number__iexact=merchant_trade_no) | 
                    Q(order_number__contains=merchant_trade_no) |
                    Q(order_number__endswith=merchant_trade_no)
                ).order_by('-created_at')
                
                if matching_orders.exists():
                    order = matching_orders.first()
                    
                    print(f"找到匹配訂單: {order.order_number}, ID: {order.id}")
                    
                    # 更新訂單狀態
                    order.status = 'paid'
                    
                    # 記錄支付資訊
                    order.payment_info = {
                        'payment_type': post_data.get('PaymentType', ''),
                        'trade_no': post_data.get('TradeNo', ''),
                        'paid_amount': post_data.get('TradeAmt', ''),
                        'payment_date': post_data.get('PaymentDate', ''),
                        'payment_method': 'ecpay',
                        'rtn_code': post_data.get('RtnCode', ''),
                        'rtn_msg': post_data.get('RtnMsg', '')
                    }
                    
                    order.save()
                    
                    print(f"訂單 {order.order_number} 支付成功，已更新訂單狀態: {order.status}")
                    
                    # 支付成功，回覆綠界金流
                    return HttpResponse('1|OK')
                else:
                    print(f"警告: 無法找到匹配訂單編號 {merchant_trade_no} 的訂單")
                    # 在找不到訂單的情況下仍然回覆成功，避免綠界重複通知
                    return HttpResponse('1|OK')
                    
        else:  # 交易失敗
            rtn_code = post_data.get('RtnCode', '')
            rtn_msg = post_data.get('RtnMsg', '')
            merchant_trade_no = post_data.get('MerchantTradeNo', '')
            
            print(f"訂單 {merchant_trade_no} 支付失敗: {rtn_code} - {rtn_msg}")
            
            # 嘗試找到對應訂單並更新狀態
            try:
                order = Order.objects.get(order_number=merchant_trade_no)
                order.status = 'payment_failed'
                order.payment_info = {
                    'error_code': rtn_code,
                    'error_msg': rtn_msg,
                    'payment_method': 'ecpay'
                }
                order.save()
                
                print(f"已將訂單 {merchant_trade_no} 狀態更新為支付失敗")
            except Order.DoesNotExist:
                print(f"警告: 無法找到訂單編號 {merchant_trade_no} 的訂單，無法更新狀態")
            
            # 交易失敗也回覆成功，避免綠界重複通知
            return HttpResponse('1|OK')
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"處理綠界金流通知時發生錯誤: {str(e)}")
        # 即使處理失敗也回覆成功，避免綠界重複通知
        return HttpResponse('1|OK')

@csrf_exempt
def ecpay_payment_info(request):
    """綠界金流付款資訊通知處理"""
    try:
        # 取得所有回傳參數
        post_data = request.POST.dict()
        
        print("綠界付款資訊通知接收到的資料:", post_data)
        
        # 這裡可以記錄繳費資訊，例如：繳費代碼、繳費期限等
        merchant_trade_no = post_data.get('MerchantTradeNo', '')
        
        if merchant_trade_no.startswith('EC'):
            # 找出對應的訂單
            order_number_pattern = merchant_trade_no[2:]  # 去掉EC前綴
            
            # 查找所有包含該模式的訂單
            from django.db.models import Q
            matching_orders = Order.objects.filter(
                Q(order_number__endswith=order_number_pattern) | 
                Q(order_number__contains=order_number_pattern)
            ).order_by('-created_at')
            
            if matching_orders.exists():
                order = matching_orders.first()
                
                # 記錄支付資訊
                payment_info = order.payment_info if hasattr(order, 'payment_info') and order.payment_info else {}
                
                # 更新支付資訊
                payment_info.update({
                    'payment_type': post_data.get('PaymentType', ''),
                    'trade_no': post_data.get('TradeNo', ''),
                    'atm_info': post_data.get('vAccount', ''),  # ATM轉帳帳號
                    'cvs_info': post_data.get('PaymentNo', ''),  # 超商代碼繳費資訊
                    'expire_date': post_data.get('ExpireDate', ''),  # 繳費期限
                    'barcode_info': {
                        'barcode1': post_data.get('Barcode1', ''),
                        'barcode2': post_data.get('Barcode2', ''),
                        'barcode3': post_data.get('Barcode3', ''),
                    }
                })
                
                order.payment_info = payment_info
                order.save()
                
                print(f"訂單 {order.order_number} 的付款資訊已更新")
                
                return HttpResponse('1|OK')  # 通知綠界處理成功
            else:
                print(f"找不到對應的訂單: {merchant_trade_no}")
                return HttpResponse('0|找不到對應的訂單')
        else:
            print(f"訂單編號格式不符: {merchant_trade_no}")
            return HttpResponse('0|訂單編號格式不符')
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"處理綠界支付資訊通知時發生錯誤: {str(e)}")
        return HttpResponse(f"0|處理綠界支付資訊通知時發生錯誤: {str(e)}")

# 新增綠界物流 API 函數
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def create_shipping_order(request):
    """建立物流訂單 API"""
    try:
        # 解析請求參數
        data = request.data
        order_id = data.get('order_id')
        
        # 記錄請求數據
        print(f"收到建立物流訂單請求，訂單ID: {order_id}")
        
        # 獲取訂單
        try:
            order = Order.objects.get(id=order_id)
            print(f"成功找到訂單: {order.order_number}")
        except Order.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': f'訂單ID {order_id} 不存在'
            }, status=404)
            
        # 匯入綠界物流 SDK
        import importlib.util
        import sys
        import os
        from datetime import datetime
        
        # 動態載入 SDK
        sdk_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                             'Logistic_Python-master', 'sdk', 'ecpay_logistic_sdk.py')
        
        spec = importlib.util.spec_from_file_location("ecpay_logistic_sdk", sdk_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # 建立物流訂單參數
        create_shipping_order_params = {
            'MerchantTradeNo': order.order_number,
            'MerchantTradeDate': datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
            'LogisticsType': module.LogisticsType['HOME'],  # 宅配
            'LogisticsSubType': module.LogisticsSubType['TCAT'],  # 黑貓
            'GoodsAmount': int(order.total_amount),  # 商品金額
            'CollectionAmount': int(order.total_amount),  # 代收金額
            'IsCollection': module.IsCollection['YES'],  # 貨到付款
            'GoodsName': '網路購物商品',
            'SenderName': '我的網路商店',
            'SenderPhone': '0226550115',
            'SenderCellPhone': '0911222333',
            'ReceiverName': order.shipping_name,
            'ReceiverPhone': order.shipping_phone,
            'ReceiverCellPhone': order.shipping_phone,
            'ReceiverEmail': order.user.email if order.user and order.user.email else '',
            'TradeDesc': f'訂單編號: {order.order_number}',
            'ServerReplyURL': request.build_absolute_uri('/api/logistics/callback/'),
            'ClientReplyURL': '',
            'Remark': order.shipping_note,
            'PlatformID': '',
            'LogisticsC2CReplyURL': '',
        }
        
        # 宅配參數
        shipping_home_params = {
            'SenderZipCode': '11560',
            'SenderAddress': '台北市南港區三重路19-2號10樓D棟',
            'ReceiverZipCode': '',  # 可以為空
            'ReceiverAddress': order.shipping_address,
            'Temperature': module.Temperature['ROOM'],  # 常溫
            'Distance': module.Distance['SAME'],  # 同縣市
            'Specification': module.Specification['CM_60'],  # 60cm
            'ScheduledPickupTime': module.ScheduledPickupTime['UNLIMITED'],  # 不限時
            'ScheduledDeliveryTime': module.ScheduledDeliveryTime['UNLIMITED'],  # 不限時
            'ScheduledDeliveryDate': '',
            'PackageCount': '1',  # 包裹數
        }
        
        # 更新及合併參數
        create_shipping_order_params.update(shipping_home_params)
        
        # 建立 SDK 實體
        ecpay_logistic_sdk = module.ECPayLogisticSdk(
            MerchantID='2000132',  # 測試用編號
            HashKey='5294y06JbISpM5x9',  # 測試用 HashKey
            HashIV='v77hoKGq4kWxNNIS'  # 測試用 HashIV
        )
        
        # 介接路徑 (測試環境)
        action_url = 'https://logistics-stage.ecpay.com.tw/Express/Create'
        
        # 建立物流訂單並接收回應訊息
        reply_result = ecpay_logistic_sdk.create_shipping_order(
            action_url=action_url,
            client_parameters=create_shipping_order_params
        )
        
        print(f"綠界物流回應: {reply_result}")
        
        # 更新訂單物流資訊
        if reply_result.get('RtnCode') == '1':
            order.shipping_method = 'home_delivery'
            order.logistics_id = reply_result.get('AllPayLogisticsID', '')
            order.logistics_status = 'created'
            order.logistics_info = str(reply_result)
            order.save()
            
            return JsonResponse({
                'success': True,
                'message': '物流訂單建立成功',
                'logistics_id': reply_result.get('AllPayLogisticsID', ''),
                'data': reply_result
            })
        else:
            return JsonResponse({
                'success': False,
                'message': f"物流訂單建立失敗: {reply_result.get('RtnMsg', '未知錯誤')}",
                'data': reply_result
            }, status=400)
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"處理物流訂單請求時發生錯誤: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)

# 物流回呼 API
@csrf_exempt
def logistics_callback(request):
    """綠界物流回呼 API"""
    try:
        if request.method == 'POST':
            print(f"收到物流回呼通知: {request.POST}")
            
            # 取得物流回呼參數
            logistics_id = request.POST.get('AllPayLogisticsID', '')
            logistics_status = request.POST.get('RtnCode', '')
            
            # 嘗試更新訂單狀態
            try:
                order = Order.objects.get(logistics_id=logistics_id)
                
                # 根據回傳碼更新物流狀態
                if logistics_status == '300':  # 訂單建立成功
                    order.logistics_status = 'created'
                elif logistics_status == '2063':  # 物流狀態已變更
                    # 關於物流狀態的解釋，請參考綠界物流文件
                    order.logistics_status = 'shipping'
                elif logistics_status == '2067':  # 商品已送達
                    order.logistics_status = 'delivered'
                    order.status = 'completed'  # 訂單完成
                
                # 儲存完整回呼資訊
                order.logistics_info = str(dict(request.POST.items()))
                order.save()
                
                return HttpResponse('1|OK')
            except Order.DoesNotExist:
                print(f"找不到對應物流編號的訂單: {logistics_id}")
                return HttpResponse('0|找不到對應訂單')
        
        return HttpResponse('0|僅接受POST請求')
        
    except Exception as e:
        print(f"處理物流回呼時發生錯誤: {str(e)}")
        return HttpResponse(f"0|{str(e)}")

# 修改 create_order 函數，以更好支持貨到付款方式
def update_create_order():
    """
    這個函數在views.py中沒有實際被調用
    僅作為修改create_order函數的示範
    此段程式碼應加入到create_order函數結尾，訂單創建成功後
    """
    # 當訂單創建成功且付款方式為貨到付款時，自動創建物流訂單
    if order.payment_method == 'cash_on_delivery':
        try:
            # 在建立訂單後，直接建立物流訂單
            # 這個過程可以在前端透過AJAX調用，或者在後端直接處理
            # 這裡示範後端處理方式
            from django.test import RequestFactory
            from django.urls import reverse
            import json
            
            # 建立假請求來調用物流API
            factory = RequestFactory()
            logistics_data = {
                'order_id': order.id
            }
            logistics_request = factory.post(
                reverse('create_shipping_order'),
                data=json.dumps(logistics_data),
                content_type='application/json'
            )
            
            # 設置用戶身份
            logistics_request.user = request.user
            
            # 調用物流API
            logistics_response = create_shipping_order(logistics_request)
            
            # 如果需要，處理響應
            print(f"物流訂單建立結果: {logistics_response.content}")
        except Exception as e:
            print(f"自動建立物流訂單失敗: {str(e)}")
            # 繼續處理，不要因為物流訂單建立失敗而中斷整個訂單流程
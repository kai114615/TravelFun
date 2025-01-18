from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
import json
from .models import Product, Carousel, CategoryDisplay, RecommendedProduct
from django.views.decorators.csrf import csrf_exempt

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
@require_http_methods(['GET', 'POST', 'PUT', 'DELETE'])
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
                products = Product.objects.all()
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

@require_http_methods(['GET', 'POST', 'PUT', 'DELETE'])
def category_display_api(request, category_id=None):
    """分類展示 API"""
    if request.method == 'GET':
        if category_id:
            category = get_object_or_404(CategoryDisplay, pk=category_id)
            data = {
                'id': category.id,
                'category': category.category,
                'order': category.order,
                'is_active': category.is_active,
                'icon': category.icon,
                'description': category.description
            }
        else:
            categories = CategoryDisplay.objects.all()
            data = [{
                'id': c.id,
                'category': c.category,
                'order': c.order,
                'is_active': c.is_active,
                'icon': c.icon,
                'description': c.description
            } for c in categories]
        return JsonResponse(data, safe=False)

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
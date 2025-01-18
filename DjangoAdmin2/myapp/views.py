from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import CustomUserCreationForm, MemberForm, ProfileUpdateForm, MessageForm, CustomPasswordChangeForm, ProductReviewForm, ArticleReviewForm, RestaurantReviewForm
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from .models import Member, Article, Message, Product, Restaurant
import logging
import requests
from django.db.models import Count
from django.db.models.functions import TruncDate
import json
from datetime import timedelta
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.core.serializers import serialize
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)

User = get_user_model()

def home(request):
    return render(request, 'home.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        print(f"嘗試登入: username={username}, password={password}")  # 調試信息
        
        # 檢查用戶是否存在
        try:
            member = Member.objects.get(username=username)
            print(f"找到用戶: {member.username}, ID: {member.id}, 級別: {member.level}")
        except Member.DoesNotExist:
            print(f"用戶 {username} 不存在")
            messages.error(request, "用戶名或密碼不正確")
            return render(request, 'login.html')
            
        user = authenticate(request, username=username, password=password)
        print(f"認證結果: user={user}")  # 調試信息
        
        if user is not None:
            login(request, user)
            print(f"用戶已登入，準備重定向")  # 調試信息
            if user.level == 'admin':
                print("重定向到管理員儀表板")  # 調試信息
                return redirect('admin_dashboard')
            else:
                print("重定向到用戶儀表板")  # 調試信息
                return redirect('user_dashboard')
        else:
            print("密碼驗證失敗")  # 調試信息
            messages.error(request, "用戶名或密碼不正確")
    return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "註冊成功！")
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

@login_required
def dashboard(request):
    if request.user.level == 'admin':
        return redirect('admin_dashboard')
    else:
        return redirect('user_dashboard')

def is_admin(user):
    return user.level == 'admin'

@login_required
@user_passes_test(lambda u: u.level == 'admin')
def admin_dashboard(request):
    users = Member.objects.all().order_by('-date_joined')
    # 獲取最新收到的訊息
    latest_messages = Message.objects.filter(recipient=request.user).order_by('-created_at')[:5]

    # 獲取最近發送的訊息
    sent_messages = Message.objects.filter(sender=request.user).order_by('-created_at')[:5]

    context = {
        'users': users,
        'latest_messages': latest_messages,
        'sent_messages': sent_messages,
    }
    return render(request, 'admin-dashboard/dashboard.html', context)

@login_required
def user_dashboard(request):
    # 獲取天氣資訊（這裡使用 OpenWeatherMap API 作為示例）
    api_key = "YOUR_API_KEY"  # 替換為您的 API 密鑰
    city = "Taipei"  # 可以根據用戶的位置動態設置
    weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    
    try:
        weather_response = requests.get(weather_url)
        weather_data = weather_response.json()
    except requests.RequestException:
        weather_data = {"name": "N/A", "main": {"temp": "N/A"}, "weather": [{"description": "N/A"}]}

    # 獲取用戶的文章
    user_articles = Article.objects.filter(author=request.user).order_by('-pub_date')[:5]

    # 獲取新消息數量
    new_messages_count = Message.objects.filter(recipient=request.user, is_read=False).count()

    # 這裡您需要根據實際情況獲取新歌曲的數量
    new_songs_count = 0  # 示例值，請根據實際情況修改

    # 獲取喜好的餐廳（假設您有一個 Restaurant 模型和相關的 ManyToMany 關係）
    favorite_restaurants = request.user.favorite_restaurants.all()[:5] if hasattr(request.user, 'favorite_restaurants') else []

    # 獲取喜愛的商品（假設您有一個 Product 模型和相關的 ManyToMany 關係）
    favorite_products = request.user.favorite_products.all()[:5] if hasattr(request.user, 'favorite_products') else []

    # 獲取最新收到的訊息
    latest_messages = Message.objects.filter(recipient=request.user).order_by('-created_at')[:5]

    # 獲取最近發送的訊息
    sent_messages = Message.objects.filter(sender=request.user).order_by('-created_at')[:5]

    # 獲取新通知數量（如果您有通知系統）
    new_notifications_count = 0  # 替換為實際的通知計數邏輯

    context = {
        'weather': weather_data,
        'user_articles': user_articles,
        'new_messages_count': new_messages_count,
        'new_songs_count': new_songs_count,
        'favorite_restaurants': favorite_restaurants,
        'favorite_products': favorite_products,
        'latest_messages': latest_messages,
        'new_notifications_count': new_notifications_count,
        'sent_messages': sent_messages,
    }
    return render(request, 'user_dashboard.html', context)

@login_required
def profile_update(request):
    if request.method == 'POST':
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        password_form = CustomPasswordChangeForm(request.user, request.POST)
        
        # 檢查是否有密碼相關的數據
        has_password_data = any([
            request.POST.get('old_password'),
            request.POST.get('new_password1'),
            request.POST.get('new_password2')
        ])

        if profile_form.is_valid():
            profile_form.save()
            
            # 只有當提交了密碼數據時才驗證密碼表單
            if has_password_data:
                if password_form.is_valid():
                    password_form.save()
                    update_session_auth_hash(request, request.user)
                    messages.success(request, '您的個人資料和密碼已更新！')
                else:
                    messages.error(request, '個人資料已更新，但密碼更新失敗！')
                    return render(request, 'profile_update.html', {
                        'profile_form': profile_form,
                        'password_form': password_form
                    })
            else:
                messages.success(request, '您的個人資料已更新！')
            
            # 檢查用戶來源頁面
            referer = request.META.get('HTTP_REFERER', '')
            if 'admin-dashboard' in referer:
                return redirect('admin_dashboard')
            else:
                return redirect('user_dashboard')
    else:
        profile_form = ProfileUpdateForm(instance=request.user)
        password_form = CustomPasswordChangeForm(request.user)
    
    context = {
        'profile_form': profile_form,
        'password_form': password_form,
    }
    return render(request, 'profile_update.html', context)

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
@user_passes_test(lambda u: u.level == 'admin')
def member_list(request):
    members = Member.objects.all().order_by('-date_joined')
    return render(request, 'member_list.html', {'users': members})

@login_required
@user_passes_test(lambda u: u.level == 'admin')
def member_detail(request, pk):
    member = get_object_or_404(Member, pk=pk)
    return render(request, 'member_detail.html', {'member': member})

@login_required
@user_passes_test(lambda u: u.level == 'admin')
def member_create(request):
    if request.method == 'POST':
        form = MemberForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, '用戶創建成功')
            return redirect('member_list')
    else:
        form = MemberForm()
    return render(request, 'member_form.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.level == 'admin')
def member_update(request, pk):
    member = get_object_or_404(Member, pk=pk)
    if request.method == 'POST':
        form = MemberForm(request.POST, request.FILES, instance=member)
        if form.is_valid():
            form.save()
            messages.success(request, '用戶資訊更新成功')
            return redirect('member_list')
    else:
        form = MemberForm(instance=member)
    return render(request, 'member_form.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.level == 'admin')
def member_delete(request, pk):
    member = get_object_or_404(Member, pk=pk)
    if request.method == 'POST':
        member.delete()
        messages.success(request, '用戶刪除成功')
        return redirect('member_list')
    return render(request, 'member_confirm_delete.html', {'member': member})

def set_admin(request):
    username = 'admin'
    password = 'admin'
    email = 'admin@example.com'
    
    try:
        # 檢查現有用戶
        user = Member.objects.get(username=username)
        print(f"找到現有用戶: {user.username}")
        print(f"用戶ID: {user.id}")
        print(f"用戶級別: {user.level}")
        print(f"當前密碼哈希: {user.password}")  # 打印當前密碼哈希
        
        # 使用 set_password 方法設置新密碼
        user.set_password(password)
        user.save()  # 記得保存更改
        print(f"新密碼哈希: {user.password}")  # 打印新的密碼哈希
        
    except Member.DoesNotExist:
        # 創建新用戶
        user = Member.objects.create_user(
            username=username,
            email=email,
            password=password  # create_user 會自動處理密碼哈希
        )
        print(f"創建新用戶: {username}")
        print(f"密碼哈希: {user.password}")  # 打印密碼哈希
    
    # 設置管理員權限
    user.level = 'admin'
    user.is_staff = True
    user.is_superuser = True
    user.save()
    print(f"已設置用戶 {username} 為管理員")
    
    return HttpResponse(
        f'管理員帳號設置成功！<br>'
        f'用戶名: {username}<br>'
        f'密碼: {password}<br>'
        f'<a href="/login/">點擊這裡登入</a>'
    )

def index(request):
    return render(request, 'home.html')

def sweetalert_view(request):
    return render(request, 'sweetalert.html')

def register_v2_view(request):
    return render(request, 'register_v2.html')

# 為其他 H-v4 HTML 文件添加類似的視圖函數

@login_required
def inbox(request):
    received_messages = Message.objects.filter(recipient=request.user).order_by('-created_at')
    unread_count = received_messages.filter(is_read=False).count()
    return render(request, 'messages/inbox.html', {
        'messages': received_messages,
        'unread_count': unread_count
    })

@login_required
def sent_messages(request):
    sent_messages = Message.objects.filter(sender=request.user).order_by('-created_at')
    return render(request, 'messages/sent.html', {'messages': sent_messages})

@login_required
def compose_message(request):
    reply_to_id = request.GET.get('reply_to')
    quote = request.GET.get('quote') == 'true'
    
    if request.method == 'POST':
        form = MessageForm(request.POST, sender=request.user)
        if form.is_valid():
            recipient_email = form.cleaned_data['recipient_email']
            if recipient_email == 'admin':
                admin_recipients = Member.objects.filter(level='admin')
                for admin in admin_recipients:
                    Message.objects.create(
                        sender=request.user,
                        recipient=admin,
                        subject=form.cleaned_data['subject'],
                        content=form.cleaned_data['content']
                    )
                messages.success(request, '訊息已成功發送給所有管理員。')
            else:
                message = form.save(commit=False)
                message.sender = request.user
                recipient = Member.objects.get(email=recipient_email)
                message.recipient = recipient
                if reply_to_id and quote:
                    quoted_message = Message.objects.get(id=reply_to_id)
                    message.quoted_message = quoted_message
                message.save()
                messages.success(request, '訊息已成功發送。')
            return redirect('inbox')
    else:
        initial = {}
        if reply_to_id:
            replied_message = Message.objects.get(id=reply_to_id)
            initial['recipient_email'] = '管理員' if replied_message.sender.level == 'admin' else replied_message.sender.email
            initial['subject'] = f"Re: {replied_message.subject}"
            if quote:
                initial['content'] = f"\n\n--- 原始訊息 ---\n{replied_message.content}"
        form = MessageForm(initial=initial, sender=request.user)
    
    return render(request, 'messages/compose.html', {'form': form})

@login_required
def message_detail(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    if message.recipient == request.user and not message.is_read:
        message.is_read = True
        message.save()
    return render(request, 'messages/detail.html', {'message': message})

@login_required
def delete_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    if message.recipient == request.user or message.sender == request.user:
        message.delete()
        messages.success(request, '訊息已成功刪除。')
    else:
        messages.error(request, '您沒有權限刪除這條訊息。')
    return redirect('inbox')

@login_required
def some_view_function(request):
    # 獲取最新的5條訊息
    latest_messages = Message.objects.filter(recipient=request.user).order_by('-created_at')[:5]
    new_messages_count = Message.objects.filter(recipient=request.user, is_read=False).count()
    
    # 其他視圖邏輯...
    
    context = {
        'latest_messages': latest_messages,
        'new_messages_count': new_messages_count,
        # 其他上下文數據...
    }
    return render(request, 'some_template.html', context)

@login_required
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = product.reviews.all().order_by('-created_at')
    if request.method == 'POST':
        form = ProductReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
            return redirect('product_detail', product_id=product.id)
    else:
        form = ProductReviewForm()
    return render(request, 'product_detail.html', {'product': product, 'reviews': reviews, 'form': form})

@login_required
def article_detail(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    reviews = article.reviews.all().order_by('-created_at')
    if request.method == 'POST':
        form = ArticleReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.article = article
            review.save()
            return redirect('article_detail', article_id=article.id)
    else:
        form = ArticleReviewForm()
    return render(request, 'article_detail.html', {'article': article, 'reviews': reviews, 'form': form})

@login_required
def restaurant_detail(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    reviews = restaurant.reviews.all().order_by('-created_at')
    if request.method == 'POST':
        form = RestaurantReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.restaurant = restaurant
            review.save()
            return redirect('restaurant_detail', restaurant_id=restaurant.id)
    else:
        form = RestaurantReviewForm()
    return render(request, 'restaurant_detail.html', {'restaurant': restaurant, 'reviews': reviews, 'form': form})

@login_required
@user_passes_test(lambda u: u.level == 'admin')
def member_api_test(request):
    """會員系統API測試頁面"""
    return render(request, 'admin-dashboard/users/api_test.html')

@login_required
@user_passes_test(lambda u: u.level == 'admin')
@require_http_methods(["GET", "POST", "PUT", "DELETE"])
def member_api(request, member_id=None):
    """會員API處理函數"""
    if request.method == 'GET':
        if member_id:
            try:
                member = Member.objects.get(id=member_id)
                data = {
                    'id': member.id,
                    'username': member.username,
                    'email': member.email,
                    'level': member.level,
                    'date_joined': member.date_joined.strftime('%Y-%m-%d %H:%M:%S'),
                    'is_active': member.is_active
                }
                return JsonResponse(data)
            except Member.DoesNotExist:
                return JsonResponse({'error': '找不到指定會員'}, status=404)
        else:
            members = Member.objects.all()
            data = [{
                'id': member.id,
                'username': member.username,
                'email': member.email,
                'level': member.level,
                'date_joined': member.date_joined.strftime('%Y-%m-%d %H:%M:%S'),
                'is_active': member.is_active
            } for member in members]
            return JsonResponse(data, safe=False)

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            member = Member.objects.create(
                username=data.get('username'),
                email=data.get('email'),
                level=data.get('level', 'user')
            )
            member.set_password(data.get('password', '123456'))
            member.save()
            return JsonResponse({
                'message': '會員創建成功',
                'id': member.id
            }, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    elif request.method == 'PUT':
        if not member_id:
            return JsonResponse({'error': '需要指定會員ID'}, status=400)
        try:
            member = Member.objects.get(id=member_id)
            data = json.loads(request.body)
            
            if 'username' in data:
                member.username = data['username']
            if 'email' in data:
                member.email = data['email']
            if 'level' in data:
                member.level = data['level']
            if 'password' in data:
                member.set_password(data['password'])
            
            member.save()
            return JsonResponse({'message': '會員資料更新成功'})
        except Member.DoesNotExist:
            return JsonResponse({'error': '找不到指定會員'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    elif request.method == 'DELETE':
        if not member_id:
            return JsonResponse({'error': '需要指定會員ID'}, status=400)
        try:
            member = Member.objects.get(id=member_id)
            member.delete()
            return JsonResponse({'message': '會員刪除成功'})
        except Member.DoesNotExist:
            return JsonResponse({'error': '找不到指定會員'}, status=404)

@login_required
@user_passes_test(lambda u: u.is_staff)
def shop_layout(request):
    """商城版面管理視圖"""
    return render(request, 'admin-dashboard/shop/layout.html', {
        'title': '版面管理'
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def product_list(request):
    """商品列表視圖"""
    products = Product.objects.all()
    return render(request, 'admin-dashboard/shop/product_list.html', {
        'title': '商品列表',
        'products': products
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def product_create(request):
    """新增商品視圖"""
    if request.method == 'POST':
        # 處理表單提交
        pass
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
        # 處理表單提交
        pass
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
        return redirect('product_list')
    return render(request, 'admin-dashboard/shop/product_confirm_delete.html', {
        'title': '刪除商品',
        'product': product
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def shop_api_test(request):
    """商城 API 測試視圖"""
    return render(request, 'admin-dashboard/shop/api_test.html', {
        'title': 'API測試'
    })

@require_http_methods(['GET', 'POST'])
def product_api(request, product_id=None):
    """商品 API 視圖"""
    if request.method == 'GET':
        if product_id:
            product = get_object_or_404(Product, pk=product_id)
            data = {
                'id': product.id,
                'name': product.name,
                'price': str(product.price),
                'description': product.description
            }
        else:
            products = Product.objects.all()
            data = [{
                'id': p.id,
                'name': p.name,
                'price': str(p.price),
                'description': p.description
            } for p in products]
        return JsonResponse(data, safe=False)
    
    elif request.method == 'POST':
        data = json.loads(request.body)
        if product_id:
            product = get_object_or_404(Product, pk=product_id)
            # 更新商品
            product.name = data.get('name', product.name)
            product.price = data.get('price', product.price)
            product.description = data.get('description', product.description)
            product.save()
        else:
            # 創建新商品
            product = Product.objects.create(
                name=data['name'],
                price=data['price'],
                description=data.get('description', '')
            )
        return JsonResponse({
            'id': product.id,
            'name': product.name,
            'price': str(product.price),
            'description': product.description
        })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_auth(request):
    """
    檢查用戶的認證狀態
    """
    try:
        # 獲取用戶信息
        user = request.user
        
        # 構建用戶數據
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'full_name': f"{user.first_name} {user.last_name}".strip(),
            'last_login': user.last_login,
            'updated_at': user.date_joined,
        }
        
        return Response({
            'success': True,
            'isAuthenticated': True,
            'user': user_data
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'isAuthenticated': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@require_http_methods(["POST"])
def logout(request):
    """
    登出視圖 - 不需要驗證，因為即使 token 無效也應該允許登出
    """
    try:
        # 執行 Django 的登出
        django_logout(request)
    except Exception as e:
        print(f"Logout warning: {str(e)}")  # 僅記錄警告，不返回錯誤
    
    # 無論如何都返回成功
    response = Response({
        'success': True,
        'message': '登出成功'
    }, status=status.HTTP_200_OK)
    
    # 清除相關的 cookies
    response.delete_cookie('token')
    response.delete_cookie('refresh_token')
    response.delete_cookie('sessionid')
    
    return response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, logout as django_logout
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods
from django.shortcuts import render

@api_view(['POST'])
@permission_classes([AllowAny])  # 允許未認證用戶訪問
def signin(request):
    """
    登入視圖
    """
    try:
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({
                'success': False,
                'message': '請提供用戶名和密碼'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 驗證用戶
        user = authenticate(username=username, password=password)
        
        if user is not None:
            # 生成 JWT token
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'success': True,
                'message': '登入成功',
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'full_name': f"{user.first_name} {user.last_name}".strip() or user.username
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': '用戶名或密碼錯誤'
            }, status=status.HTTP_401_UNAUTHORIZED)

    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@require_http_methods(["POST"])
def logout_api(request):
    """
    登出 API 視圖
    """
    try:
        # 執行 Django 的登出
        django_logout(request)
        
        # 準備響應
        response = Response({
            'success': True,
            'message': '登出成功'
        }, status=status.HTTP_200_OK)
        
        # 清除相關的 cookies
        response.delete_cookie('token')
        response.delete_cookie('refresh_token')
        response.delete_cookie('sessionid')  # 清除 Django session cookie
        
        return response
        
    except Exception as e:
        print(f"Logout error: {str(e)}")
        return Response({
            'success': False,
            'message': f'登出時發生錯誤: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_auth(request):
    """
    檢查用戶認證狀態
    """
    try:
        if request.user.is_authenticated:
            return Response({
                'success': True,
                'isAuthenticated': True,
                'user': {
                    'id': request.user.id,
                    'username': request.user.username,
                    'email': request.user.email,
                    'full_name': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username
                }
            })
        return Response({
            'success': False,
            'isAuthenticated': False
        })
    except Exception as e:
        print(f"Check auth error: {str(e)}")  # 添加日誌
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])  # 允許未認證用戶訪問
def register_api(request):
    """
    註冊 API 視圖
    """
    print('收到註冊請求:', {
        'data': request.data,
        'headers': dict(request.headers),
        'method': request.method
    })

    try:
        username = request.data.get('username')
        password = request.data.get('password')
        password2 = request.data.get('password2')
        email = request.data.get('email')
        full_name = request.data.get('full_name', '')

        print('註冊數據:', {
            'username': username,
            'email': email,
            'full_name': full_name,
            'has_password': bool(password),
            'has_password2': bool(password2)
        })

        # 驗證必要字段
        if not username or not password or not password2 or not email:
            print('缺少必要字段')
            return Response({
                'success': False,
                'message': '請提供所有必要信息'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 驗證密碼是否匹配
        if password != password2:
            print('密碼不匹配')
            return Response({
                'success': False,
                'message': '兩次輸入的密碼不一致'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 檢查用戶名是否已存在
        if User.objects.filter(username=username).exists():
            print(f'用戶名已存在: {username}')
            return Response({
                'success': False,
                'message': '用戶名已存在'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 檢查郵箱是否已存在
        if User.objects.filter(email=email).exists():
            print(f'郵箱已被使用: {email}')
            return Response({
                'success': False,
                'message': '郵箱已被使用'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 創建新用戶
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # 如果提供了全名，分割並設置
        if full_name:
            name_parts = full_name.split(' ', 1)
            user.first_name = name_parts[0]
            if len(name_parts) > 1:
                user.last_name = name_parts[1]
            user.save()

        print(f'用戶創建成功: {user.username}')

        # 生成 JWT token
        refresh = RefreshToken.for_user(user)

        response_data = {
            'success': True,
            'message': '註冊成功',
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': f"{user.first_name} {user.last_name}".strip() or user.username
            }
        }

        print('註冊成功，返回數據:', response_data)
        return Response(response_data, status=status.HTTP_201_CREATED)

    except Exception as e:
        print(f"註冊錯誤: {str(e)}")
        import traceback
        print('錯誤詳情:', traceback.format_exc())
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

def register_view(request):
    """
    註冊頁面視圖
    """
    return render(request, 'register.html')

# ... 其他視圖函數 ... 
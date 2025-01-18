from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, logout as django_logout
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods

@api_view(['POST'])
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
def logout(request):
    """
    登出視圖 - 不需要驗證，因為即使 token 無效也應該允許登出
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

# ... 其他視圖函數 ... 
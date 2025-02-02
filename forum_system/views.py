from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from django.shortcuts import get_object_or_404
from django.db.models import Count
from .models import Category, Post, Comment, SavedPost
from .serializers import (
    CategorySerializer,
    PostSerializer,
    CommentSerializer,
    SavedPostSerializer
)
from .permissions import IsAuthorOrReadOnly, IsAdminOrReadOnly
from django.views.generic import ListView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.views import APIView

class CategoryViewSet(viewsets.ModelViewSet):
    """討論區分類視圖集"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

class PostViewSet(viewsets.ModelViewSet):
    """文章視圖集"""
    queryset = Post.objects.filter(is_deleted=False)
    serializer_class = PostSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

class CommentViewSet(viewsets.ModelViewSet):
    """評論視圖集"""
    queryset = Comment.objects.filter(is_deleted=False)
    serializer_class = CommentSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

class SavedPostViewSet(viewsets.ModelViewSet):
    """收藏文章視圖集"""
    serializer_class = SavedPostSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

class AdminPostViewSet(viewsets.ModelViewSet):
    """後台文章管理視圖集"""
    queryset = Post.objects.filter(is_deleted=False)
    serializer_class = PostSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

class AdminCategoryViewSet(viewsets.ModelViewSet):
    """後台分類管理視圖集"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

class AdminCommentViewSet(viewsets.ModelViewSet):
    """後台評論管理視圖集"""
    queryset = Comment.objects.filter(is_deleted=False)
    serializer_class = CommentSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

class TestPostApiView(APIView):
    """文章API測試"""
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk=None):
        if pk:
            return Response({
                'status': 'success',
                'message': f'獲取ID為{pk}的文章',
                'data': {
                    'id': pk,
                    'title': '測試文章',
                    'content': '這是一篇測試文章的內容'
                }
            })
        return Response({
            'status': 'success',
            'message': '獲取文章列表',
            'data': [
                {'id': 1, 'title': '文章1'},
                {'id': 2, 'title': '文章2'}
            ]
        })

    def post(self, request):
        return Response({
            'status': 'success',
            'message': '創建文章成功',
            'data': request.data
        })

    def put(self, request, pk=None):
        if not pk:
            return Response({'error': '需要指定文章ID'}, status=400)
        return Response({
            'status': 'success',
            'message': f'更新ID為{pk}的文章成功',
            'data': request.data
        })

    def delete(self, request, pk=None):
        if not pk:
            return Response({'error': '需要指定文章ID'}, status=400)
        return Response({
            'status': 'success',
            'message': f'刪除ID為{pk}的文章成功'
        })

class TestCategoryApiView(APIView):
    """分類API測試"""
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk=None):
        if pk:
            return Response({
                'status': 'success',
                'message': f'獲取ID為{pk}的分類',
                'data': {
                    'id': pk,
                    'name': '測試分類',
                    'description': '這是一個測試分類'
                }
            })
        return Response({
            'status': 'success',
            'message': '獲取分類列表',
            'data': [
                {'id': 1, 'name': '分類1'},
                {'id': 2, 'name': '分類2'}
            ]
        })

    def post(self, request):
        return Response({
            'status': 'success',
            'message': '創建分類成功',
            'data': request.data
        })

    def put(self, request, pk=None):
        if not pk:
            return Response({'error': '需要指定分類ID'}, status=400)
        return Response({
            'status': 'success',
            'message': f'更新ID為{pk}的分類成功',
            'data': request.data
        })

    def delete(self, request, pk=None):
        if not pk:
            return Response({'error': '需要指定分類ID'}, status=400)
        return Response({
            'status': 'success',
            'message': f'刪除ID為{pk}的分類成功'
        })

class TestCommentApiView(APIView):
    """評論API測試"""
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk=None):
        if pk:
            return Response({
                'status': 'success',
                'message': f'獲取ID為{pk}的評論',
                'data': {
                    'id': pk,
                    'content': '這是一條測試評論'
                }
            })
        return Response({
            'status': 'success',
            'message': '獲取評論列表',
            'data': [
                {'id': 1, 'content': '評論1'},
                {'id': 2, 'content': '評論2'}
            ]
        })

    def post(self, request):
        return Response({
            'status': 'success',
            'message': '創建評論成功',
            'data': request.data
        })

    def put(self, request, pk=None):
        if not pk:
            return Response({'error': '需要指定評論ID'}, status=400)
        return Response({
            'status': 'success',
            'message': f'更新ID為{pk}的評論成功',
            'data': request.data
        })

    def delete(self, request, pk=None):
        if not pk:
            return Response({'error': '需要指定評論ID'}, status=400)
        return Response({
            'status': 'success',
            'message': f'刪除ID為{pk}的評論成功'
        })

class AdminApiTestView(LoginRequiredMixin, TemplateView):
    """API測試頁面"""
    template_name = 'admin-dashboard/forum/api_test.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'API 測試'
        context['active_menu'] = 'forum_api_test'
        return context 

class PublicTestPostApiView(APIView):
    """公開的文章API測試"""
    authentication_classes = []
    permission_classes = []
    
    def get(self, request, pk=None):
        if pk:
            return Response({
                'status': 'success',
                'message': f'獲取ID為{pk}的文章',
                'data': {
                    'id': pk,
                    'title': '測試文章',
                    'content': '這是一篇測試文章的內容'
                }
            })
        return Response({
            'status': 'success',
            'message': '獲取文章列表',
            'data': [
                {'id': 1, 'title': '文章1'},
                {'id': 2, 'title': '文章2'}
            ]
        })

    def post(self, request):
        return Response({
            'status': 'success',
            'message': '創建文章成功',
            'data': request.data
        })

class PublicTestCategoryApiView(APIView):
    """公開的分類API測試"""
    authentication_classes = []
    permission_classes = []
    
    def get(self, request, pk=None):
        if pk:
            return Response({
                'status': 'success',
                'message': f'獲取ID為{pk}的分類',
                'data': {
                    'id': pk,
                    'name': '測試分類',
                    'description': '這是一個測試分類'
                }
            })
        return Response({
            'status': 'success',
            'message': '獲取分類列表',
            'data': [
                {'id': 1, 'name': '分類1'},
                {'id': 2, 'name': '分類2'}
            ]
        })

    def post(self, request):
        return Response({
            'status': 'success',
            'message': '創建分類成功',
            'data': request.data
        }) 
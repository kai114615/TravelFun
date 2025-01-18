from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
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
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['get'])
    def posts(self, request, pk=None):
        """獲取特定分類下的所有文章"""
        category = self.get_object()
        posts = Post.objects.filter(category=category, is_deleted=False)
        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = PostSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def menu(self, request):
        """獲取討論區菜單"""
        categories = self.get_queryset()
        menu_data = []
        for category in categories:
            post_count = Post.objects.filter(category=category, is_deleted=False).count()
            menu_item = {
                'id': category.id,
                'name': category.name,
                'description': category.description,
                'post_count': post_count,
                'created_at': category.created_at
            }
            menu_data.append(menu_item)
        return Response(menu_data)

class PostViewSet(viewsets.ModelViewSet):
    """文章視圖集"""
    queryset = Post.objects.filter(is_deleted=False)
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """按讚/取消按讚"""
        post = self.get_object()
        user = request.user
        if post.likes.filter(id=user.id).exists():
            post.likes.remove(user)
            return Response({'detail': '已取消按讚'})
        post.likes.add(user)
        return Response({'detail': '已按讚'})

    @action(detail=True, methods=['post'])
    def save_post(self, request, pk=None):
        """收藏/取消收藏文章"""
        post = self.get_object()
        user = request.user
        saved_post, created = SavedPost.objects.get_or_create(user=user, post=post)
        if not created:
            saved_post.delete()
            return Response({'detail': '已取消收藏'})
        return Response({'detail': '已收藏'})

    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        """添加評論"""
        post = self.get_object()
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user, post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        """獲取文章詳情時增加瀏覽次數"""
        instance = self.get_object()
        instance.views += 1
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class CommentViewSet(viewsets.ModelViewSet):
    """評論視圖集"""
    queryset = Comment.objects.filter(is_deleted=False)
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class SavedPostViewSet(viewsets.ModelViewSet):
    """收藏文章視圖集"""
    serializer_class = SavedPostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SavedPost.objects.filter(user=self.request.user)

class AdminPostViewSet(viewsets.ModelViewSet):
    """後台文章管理視圖集"""
    queryset = Post.objects.filter(is_deleted=False)
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]  # 後續可以改為自定義的管理員權限

    def get_queryset(self):
        """獲取文章列表，包含統計數據"""
        return Post.objects.filter(is_deleted=False).annotate(
            like_count=Count('likes'),
            save_count=Count('saved_by'),
            comment_count=Count('comments')
        ).order_by('-created_at')

    @action(detail=True, methods=['post'])
    def delete_post(self, request, pk=None):
        """軟刪除文章"""
        post = self.get_object()
        post.is_deleted = True
        post.save()
        return Response({'detail': '文章已刪除'})

class AdminCategoryViewSet(viewsets.ModelViewSet):
    """後台分類管理視圖集"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]  # 後續可以改為自定義的管理員權限

    @action(detail=True, methods=['get'])
    def category_stats(self, request, pk=None):
        """獲取分類統計信息"""
        category = self.get_object()
        posts = Post.objects.filter(category=category, is_deleted=False)
        stats = {
            'total_posts': posts.count(),
            'total_views': sum(post.views for post in posts),
            'total_likes': sum(post.likes.count() for post in posts),
            'total_comments': sum(post.comments.count() for post in posts)
        }
        return Response(stats)

class AdminCommentViewSet(viewsets.ModelViewSet):
    """後台評論管理視圖集"""
    queryset = Comment.objects.filter(is_deleted=False)
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]  # 後續可以改為自定義的管理員權限

    def get_queryset(self):
        """可以根據文章ID篩選評論"""
        queryset = Comment.objects.filter(is_deleted=False)
        post_id = self.request.query_params.get('post_id', None)
        if post_id is not None:
            queryset = queryset.filter(post_id=post_id)
        return queryset

    @action(detail=True, methods=['post'])
    def delete_comment(self, request, pk=None):
        """軟刪除評論"""
        comment = self.get_object()
        comment.is_deleted = True
        comment.save()
        return Response({'detail': '評論已刪除'})

    @action(detail=False, methods=['get'])
    def post_comments(self, request):
        """獲取指定文章的所有評論"""
        post_id = request.query_params.get('post_id')
        if not post_id:
            return Response({'error': '需要提供文章ID'}, status=400)
        
        comments = Comment.objects.filter(
            post_id=post_id,
            is_deleted=False
        ).select_related('author', 'post')
        
        serializer = self.get_serializer(comments, many=True)
        return Response(serializer.data)

# 後台管理頁面視圖
class AdminPostListView(LoginRequiredMixin, ListView):
    """文章列表頁面"""
    model = Post
    template_name = 'admin-dashboard/forum/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.filter(is_deleted=False).annotate(
            like_count=Count('likes'),
            save_count=Count('saved_by'),
            comment_count=Count('comments')
        ).order_by('-created_at')

class AdminCategoryListView(LoginRequiredMixin, ListView):
    """分類管理頁面"""
    model = Category
    template_name = 'admin-dashboard/forum/category_list.html'
    context_object_name = 'categories'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for category in context['categories']:
            posts = Post.objects.filter(category=category, is_deleted=False)
            category.stats = {
                'total_posts': posts.count(),
                'total_views': sum(post.views for post in posts),
                'total_likes': sum(post.likes.count() for post in posts),
                'total_comments': sum(post.comments.count() for post in posts)
            }
        return context

class AdminCommentListView(LoginRequiredMixin, ListView):
    """評論管理頁面"""
    model = Comment
    template_name = 'admin-dashboard/forum/comment_list.html'
    context_object_name = 'comments'
    paginate_by = 20

    def get_queryset(self):
        queryset = Comment.objects.filter(is_deleted=False)
        post_id = self.request.GET.get('post_id')
        if post_id:
            queryset = queryset.filter(post_id=post_id)
        return queryset.select_related('author', 'post')

class AdminApiTestView(TemplateView):
    """API測試頁面"""
    template_name = 'admin-dashboard/forum/api_test.html'

class TestPostApiView(APIView):
    """文章API測試"""
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
            'data': {'id': 3, 'title': '新文章'}
        })

    def put(self, request, pk):
        return Response({
            'status': 'success',
            'message': f'更新ID為{pk}的文章成功'
        })

    def delete(self, request, pk):
        return Response({
            'status': 'success',
            'message': f'刪除ID為{pk}的文章成功'
        })

class TestCategoryApiView(APIView):
    """分類API測試"""
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
            'data': {'id': 3, 'name': '新分類'}
        })

    def put(self, request, pk):
        return Response({
            'status': 'success',
            'message': f'更新ID為{pk}的分類成功'
        })

    def delete(self, request, pk):
        return Response({
            'status': 'success',
            'message': f'刪除ID為{pk}的分類成功'
        })

class TestCommentApiView(APIView):
    """評論API測試"""
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
            'data': {'id': 3, 'content': '新評論'}
        })

    def put(self, request, pk):
        return Response({
            'status': 'success',
            'message': f'更新ID為{pk}的評論成功'
        })

    def delete(self, request, pk):
        return Response({
            'status': 'success',
            'message': f'刪除ID為{pk}的評論成功'
        })
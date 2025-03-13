from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404, redirect
from django.db.models import Count
from .models import Category, Post, Comment, SavedPost, Tag, Member
from .serializers import (
    CategorySerializer,
    PostSerializer,
    CommentSerializer,
    SavedPostSerializer,
    TagSerializer
)
from .permissions import IsAuthorOrReadOnly, IsAdminOrReadOnly
from django.views.generic import ListView, TemplateView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.contrib import messages

class CategoryViewSet(viewsets.ModelViewSet):
    """討論區分類視圖集"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

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
    permission_classes = [IsAuthenticatedOrReadOnly]  # 修改權限設置

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

    @action(detail=True, methods=['get'])
    def get_comments(self, request, pk=None):
        """獲取文章評論"""
        post = self.get_object()
        comments = Comment.objects.filter(post=post, is_deleted=False).order_by('created_at')
        serializer = CommentSerializer(comments, many=True)
        return Response({
            'status': 'success',
            'message': '獲取評論成功',
            'data': serializer.data
        })

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def add_comment(self, request, pk=None):
        """添加評論"""
        post = self.get_object()
        content = request.data.get('content')
        
        if not content:
            return Response({'error': '評論內容不能為空'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            comment = Comment.objects.create(
                post=post,
                author=request.user,
                content=content
            )
            serializer = CommentSerializer(comment)
            return Response({
                'status': 'success',
                'message': '評論發表成功',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

    @action(detail=True, methods=['post'])
    def delete_comment(self, request, pk=None):
        """軟刪除評論"""
        try:
            comment = self.get_object()
            
            # 記錄被刪除的評論信息
            comment_content = comment.content
            post_title = comment.post.title if comment.post else "未知文章"
            user_name = request.user.username
            
            # 執行軟刪除
            comment.is_deleted = True
            comment.save()
            
            print(f"評論已刪除：ID={comment.id}, 由用戶={user_name} 刪除")
            
            return Response({
                'status': 'success',
                'message': '評論已刪除',
                'data': {
                    'comment_id': comment.id,
                    'content': comment_content[:100] + ('...' if len(comment_content) > 100 else ''),
                    'post_title': post_title
                }
            })
        except Exception as e:
            print(f"刪除評論時出錯: {str(e)}")
            return Response({
                'status': 'error',
                'message': f'刪除評論時出錯: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    def destroy(self, request, *args, **kwargs):
        """重寫刪除方法，實現軟刪除"""
        try:
            comment = self.get_object()
            
            # 記錄被刪除的評論信息
            comment_content = comment.content
            post_title = comment.post.title if comment.post else "未知文章"
            user_name = request.user.username
            
            # 執行軟刪除
            comment.is_deleted = True
            comment.save()
            
            print(f"評論已軟刪除：ID={comment.id}, 由用戶={user_name} 刪除")
            
            return Response({
                'status': 'success',
                'message': '評論已刪除',
                'data': {
                    'comment_id': comment.id,
                    'content': comment_content[:100] + ('...' if len(comment_content) > 100 else ''),
                    'post_title': post_title
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"刪除評論時出錯: {str(e)}")
            return Response({
                'status': 'error',
                'message': f'刪除評論時出錯: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
        try:
            post = self.get_object()
            
            # 記錄被刪除的文章信息
            post_title = post.title
            post_id = post.id
            
            # 執行軟刪除
            post.is_deleted = True
            post.save()
            
            print(f"文章已刪除：ID={post_id}, 標題={post_title}")
            
            return Response({
                'status': 'success',
                'message': '文章已刪除',
                'data': {
                    'post_id': post_id,
                    'title': post_title
                }
            })
        except Exception as e:
            print(f"刪除文章時出錯: {str(e)}")
            return Response({
                'status': 'error',
                'message': f'刪除文章時出錯: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
        """獲取所有非刪除的評論，可以按照文章進行過濾"""
        queryset = Comment.objects.filter(is_deleted=False)
        post_id = self.request.query_params.get('post_id')
        if post_id:
            queryset = queryset.filter(post_id=post_id)
        
        # 使用 select_related 提前獲取 post 和 author 信息以提高性能
        return queryset.select_related('author', 'post').order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def delete_comment(self, request, pk=None):
        """軟刪除評論"""
        try:
            comment = self.get_object()
            
            # 記錄被刪除的評論信息
            comment_content = comment.content
            post_title = comment.post.title if comment.post else "未知文章"
            user_name = request.user.username
            
            # 執行軟刪除
            comment.is_deleted = True
            comment.save()
            
            print(f"評論已刪除：ID={comment.id}, 由用戶={user_name} 刪除")
            
            return Response({
                'status': 'success',
                'message': '評論已刪除',
                'data': {
                    'comment_id': comment.id,
                    'content': comment_content[:100] + ('...' if len(comment_content) > 100 else ''),
                    'post_title': post_title
                }
            })
        except Exception as e:
            print(f"刪除評論時出錯: {str(e)}")
            return Response({
                'status': 'error',
                'message': f'刪除評論時出錯: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    def destroy(self, request, *args, **kwargs):
        """重寫刪除方法，實現軟刪除"""
        try:
            comment = self.get_object()
            
            # 記錄被刪除的評論信息
            comment_content = comment.content
            post_title = comment.post.title if comment.post else "未知文章"
            user_name = request.user.username
            
            # 執行軟刪除而不是真正刪除
            comment.is_deleted = True
            comment.save()
            
            print(f"評論已軟刪除：ID={comment.id}, 由用戶={user_name} 刪除")
            
            return Response({
                'status': 'success',
                'message': '評論已刪除',
                'data': {
                    'comment_id': comment.id,
                    'content': comment_content[:100] + ('...' if len(comment_content) > 100 else ''),
                    'post_title': post_title
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"刪除評論時出錯: {str(e)}")
            return Response({
                'status': 'error',
                'message': f'刪除評論時出錯: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AdminCommentListView(LoginRequiredMixin, ListView):
    """評論管理頁面"""
    model = Comment
    template_name = 'admin-dashboard/forum/comment_list.html'
    context_object_name = 'comments'

    def get_queryset(self):
        """獲取所有非刪除的評論"""
        queryset = Comment.objects.filter(is_deleted=False)
        post_id = self.request.GET.get('post_id')
        if post_id:
            queryset = queryset.filter(post_id=post_id)
        
        # 打印評論總數，用於調試
        total_comments = queryset.count()
        print(f"找到 {total_comments} 條非刪除評論")
        
        # 使用 select_related 提前獲取 post 和 author 信息以提高性能
        return queryset.select_related('author', 'post').order_by('-created_at')

class AdminApiTestView(TemplateView):
    """API測試頁面"""
    template_name = 'admin-dashboard/forum/api_test.html'

class TestPostApiView(APIView):
    """文章API測試"""
    authentication_classes = [SessionAuthentication]  # 添加認證
    permission_classes = [IsAuthenticated]  # 需要登入
    
    def get(self, request, pk=None):
        """獲取文章列表或單篇文章"""
        if pk:
            try:
                post = Post.objects.get(pk=pk)
                return Response({
                    'status': 'success',
                    'message': f'獲取ID為{pk}的文章',
                    'data': {
                        'id': post.id,
                        'title': post.title,
                        'content': post.content,
                        'category_id': post.category_id,
                        'author': {
                            'id': post.author.id,
                            'username': post.author.username
                        },
                        'created_at': post.created_at,
                        'views': post.views,
                        'likes_count': post.likes.count(),
                        'comments_count': post.comments.count()
                    }
                })
            except Post.DoesNotExist:
                return Response({
                    'status': 'error',
                    'message': '文章不存在'
                }, status=status.HTTP_404_NOT_FOUND)
                
        # 獲取所有非刪除的文章
        posts = Post.objects.filter(is_deleted=False).select_related('author', 'category')
        posts_data = [{
            'id': post.id,
            'title': post.title,
            'content': post.content,
            'category_id': post.category_id,
            'author': {
                'id': post.author.id,
                'username': post.author.username
            },
            'created_at': post.created_at,
            'views': post.views,
            'likes_count': post.likes.count(),
            'comments_count': post.comments.count()
        } for post in posts]
        
        return Response({
            'status': 'success',
            'message': '獲取文章列表',
            'data': posts_data
        })

    def post(self, request):
        try:
            # 驗證必填欄位
            title = request.data.get('title')
            content = request.data.get('content')
            category_id = request.data.get('category_id')
            
            if not all([title, content, category_id]):
                return Response({
                    'status': 'error',
                    'message': '請填寫所有必填欄位'
                }, status=status.HTTP_400_BAD_REQUEST)
                
            # 檢查分類是否存在
            try:
                category = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                return Response({
                    'status': 'error',
                    'message': '分類不存在'
                }, status=status.HTTP_400_BAD_REQUEST)
                
            # 創建新文章，使用當前登入用戶作為作者
            post = Post.objects.create(
                title=title,
                content=content,
                category=category,
                author=request.user  # 使用當前登入用戶
            )
            
            # 返回成功響應
            return Response({
                'status': 'success',
                'message': '文章發表成功',
                'data': {
                    'id': post.id,
                    'title': post.title,
                    'content': post.content,
                    'category_id': post.category_id,
                    'author': {
                        'id': post.author.id,
                        'username': post.author.username
                    },
                    'created_at': post.created_at,
                    'views': post.views,
                    'likes_count': 0,
                    'comments_count': 0
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

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
    authentication_classes = []  # 移除認證要求
    permission_classes = []  # 移除權限要求
    
    def get(self, request, pk=None):
        if pk:
            try:
                category = Category.objects.get(pk=pk)
                post_count = Post.objects.filter(category=category, is_deleted=False).count()
                return Response({
                    'status': 'success',
                    'message': f'獲取ID為{pk}的分類',
                    'data': {
                        'id': category.id,
                        'name': category.name,
                        'description': category.description,
                        'post_count': post_count,
                        'created_at': category.created_at
                    }
                })
            except Category.DoesNotExist:
                return Response({
                    'status': 'error',
                    'message': '分類不存在'
                }, status=status.HTTP_404_NOT_FOUND)
                
        # 獲取所有分類
        categories = Category.objects.all()
        categories_data = []
        for category in categories:
            post_count = Post.objects.filter(category=category, is_deleted=False).count()
            categories_data.append({
                'id': category.id,
                'name': category.name,
                'description': category.description,
                'post_count': post_count,
                'created_at': category.created_at
            })
            
        return Response({
            'status': 'success',
            'message': '獲取分類列表',
            'data': categories_data
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

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_post(request):
    try:
        # 獲取分類
        category_id = request.data.get('category_id')
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return Response({'success': False, 'message': '無效的分類'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 創建文章
        post = Post.objects.create(
            title=request.data.get('title'),
            content=request.data.get('content'),
            category=category,
            author=request.user
        )
        
        # 處理標籤
        tags = request.data.get('tags', [])
        if tags:
            # 確保所有標籤都存在
            valid_tags = Tag.objects.filter(id__in=tags)
            if len(valid_tags) != len(tags):
                return Response({
                    'success': False,
                    'message': '部分標籤不存在'
                }, status=status.HTTP_400_BAD_REQUEST)
            post.tags.set(valid_tags)
        
        serializer = PostSerializer(post)
        return Response({
            'success': True,
            'message': '文章發表成功',
            'post': serializer.data
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

class PublicPostViewSet(viewsets.ModelViewSet):
    """公開的文章視圖集，允許已登入用戶發文"""
    queryset = Post.objects.filter(is_deleted=False)
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # 允許未登入用戶讀取，但需要登入才能發文

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response({
                'status': 'success',
                'message': '文章發表成功',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class PublicCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """公開的分類視圖集，不需要登入即可訪問"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = []  # 不需要任何權限

    def list(self, request, *args, **kwargs):
        """獲取分類列表"""
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                'status': 'success',
                'message': '獲取分類列表成功',
                'data': serializer.data
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        """獲取單個分類"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response({
                'status': 'success',
                'message': '獲取分類詳情成功',
                'data': serializer.data
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def menu(self, request):
        """獲取討論區菜單"""
        try:
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
            return Response({
                'status': 'success',
                'message': '獲取討論區菜單成功',
                'data': menu_data
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class PublicForumViewSet(viewsets.ModelViewSet):
    """公開的討論區 API"""
    queryset = Post.objects.filter(is_deleted=False)
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # 恢復原始權限設定
    
    def get_queryset(self):
        """獲取文章列表，包含作者和分類信息"""
        return Post.objects.filter(is_deleted=False).select_related('author', 'category')
    
    def perform_create(self, serializer):
        """創建文章時自動設置作者"""
        serializer.save(author=self.request.user)
    
    def get_serializer_context(self):
        """添加 request 到序列化器上下文"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def list(self, request, *args, **kwargs):
        """獲取文章列表"""
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                'status': 'success',
                'message': '獲取文章列表成功',
                'data': serializer.data
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """按讚/取消按讚"""
        try:
            post = self.get_object()
            user = request.user
            
            # 檢查用戶是否已經按讚
            if post.likes.filter(id=user.id).exists():
                post.likes.remove(user)
                return Response({
                    'status': 'success',
                    'message': '已取消按讚',
                    'data': {
                        'is_liked': False,
                        'like_count': post.likes.count()
                    }
                })
            else:
                post.likes.add(user)
                return Response({
                    'status': 'success',
                    'message': '已按讚',
                    'data': {
                        'is_liked': True,
                        'like_count': post.likes.count()
                    }
                })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def moderators(self, request):
        """獲取版務人員（管理員）資訊"""
        try:
            # 只獲取管理員權限的用戶
            moderators = Member.objects.filter(
                is_staff=True,  # 是管理員
                is_active=True  # 帳號啟用中
            ).values(
                'id', 
                'username', 
                'avatar',
                'last_login'
            )
            
            # 處理每個管理員的狀態
            moderator_list = []
            for mod in moderators:
                status = '在線' if mod['last_login'] and (timezone.now() - mod['last_login']).seconds < 3600 else '離線'
                
                # 處理頭像路徑
                avatar_url = mod['avatar']
                if avatar_url:
                    # 移除開頭的 media/ 如果存在
                    avatar_url = avatar_url.replace('media/', '', 1) if avatar_url.startswith('media/') else avatar_url
                    # 移除開頭的 /media/ 如果存在
                    avatar_url = avatar_url.replace('/media/', '', 1) if avatar_url.startswith('/media/') else avatar_url
                
                moderator_list.append({
                    'id': mod['id'],
                    'username': mod['username'],
                    'avatar': avatar_url,
                    'status': status
                })
            
            return Response({
                'status': 'success',
                'message': '獲取版務人員資訊成功',
                'data': moderator_list
            })
        except Exception as e:
            print(f"獲取版務人員資訊錯誤: {str(e)}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete', 'post'], permission_classes=[IsAuthenticated])
    def delete_post(self, request, pk=None):
        """刪除文章（軟刪除）"""
        try:
            post = self.get_object()
            
            # 檢查權限 - 只有作者或管理員可以刪除
            if not (request.user.id == post.author.id or request.user.is_staff):
                return Response({
                    'status': 'error',
                    'message': '您沒有權限刪除此文章'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # 記錄被刪除的文章信息
            post_title = post.title
            post_id = post.id
            
            # 執行軟刪除
            post.is_deleted = True
            post.save()
            
            print(f"文章已刪除：ID={post_id}, 標題={post_title}, 刪除者={request.user.username}")
            
            return Response({
                'status': 'success',
                'message': '文章已成功刪除',
                'data': {
                    'post_id': post_id,
                    'title': post_title
                }
            })
        except Exception as e:
            print(f"刪除文章時出錯: {str(e)}")
            return Response({
                'status': 'error',
                'message': f'刪除文章時出錯: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    def destroy(self, request, *args, **kwargs):
        """重寫標準的destroy方法，改為軟刪除"""
        try:
            instance = self.get_object()
            
            # 檢查權限 - 只有作者或管理員可以刪除
            if not (request.user.id == instance.author.id or request.user.is_staff):
                return Response({
                    'status': 'error',
                    'message': '您沒有權限刪除此文章'
                }, status=status.HTTP_403_FORBIDDEN)
                
            # 記錄被刪除的文章信息
            post_title = instance.title
            post_id = instance.id
            
            # 執行軟刪除而不是真正刪除
            instance.is_deleted = True
            instance.save()
            
            print(f"文章已刪除：ID={post_id}, 標題={post_title}, 刪除者={request.user.username}")
            
            return Response({
                'status': 'success',
                'message': '文章已成功刪除',
                'data': {
                    'post_id': post_id,
                    'title': post_title
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"刪除文章時出錯: {str(e)}")
            return Response({
                'status': 'error',
                'message': f'刪除文章時出錯: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class NewForumViewSet(viewsets.ModelViewSet):
    """新的論壇 API 視圖集"""
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        """獲取文章列表，包含作者和分類信息"""
        print("正在獲取文章列表...")  # 添加調試信息
        queryset = Post.objects.filter(is_deleted=False).select_related('author', 'category')
        print(f"找到 {queryset.count()} 篇文章")  # 添加調試信息
        return queryset
    
    def list(self, request, *args, **kwargs):
        """獲取文章列表"""
        try:
            print("開始處理文章列表請求...")  # 添加調試信息
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            response_data = {
                'status': 'success',
                'message': '獲取文章列表成功',
                'data': serializer.data
            }
            print(f"成功序列化 {len(serializer.data)} 篇文章")  # 添加調試信息
            return Response(response_data)
        except Exception as e:
            print(f"獲取文章列表錯誤: {str(e)}")  # 添加調試信息
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def create(self, request, *args, **kwargs):
        """發表文章"""
        try:
            print("開始處理發文請求...")  # 添加調試信息
            # 檢查用戶是否登入
            if not request.user.is_authenticated:
                return Response({
                    'status': 'error',
                    'message': '請先登入'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # 檢查必要欄位
            required_fields = ['title', 'content', 'category_id']
            if not all(field in request.data for field in required_fields):
                return Response({
                    'status': 'error',
                    'message': '缺少必要欄位'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 創建文章
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(author=request.user)
            
            print(f"成功創建文章: {serializer.data.get('title')}")  # 添加調試信息
            return Response({
                'status': 'success',
                'message': '發文成功',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            print(f"發文錯誤: {str(e)}")  # 添加調試信息
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class TagViewSet(viewsets.ModelViewSet):
    """標籤管理視圖集"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # 修改權限設置
    
    def get_queryset(self):
        """獲取標籤列表"""
        print("正在獲取標籤列表...")
        queryset = Tag.objects.all()
        print(f"找到 {queryset.count()} 個標籤")
        return queryset
    
    def list(self, request, *args, **kwargs):
        """獲取標籤列表"""
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)  # 直接返回序列化後的數據
        except Exception as e:
            print(f"獲取標籤列表錯誤: {str(e)}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def create(self, request, *args, **kwargs):
        """創建標籤"""
        try:
            print("開始創建標籤...")
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            print(f"成功創建標籤: {serializer.data.get('name')}")
            return Response({
                'status': 'success',
                'message': '創建標籤成功',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(f"創建標籤錯誤: {str(e)}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        """更新標籤"""
        try:
            print("開始更新標籤...")
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            print(f"成功更新標籤: {serializer.data.get('name')}")
            return Response({
                'status': 'success',
                'message': '更新標籤成功',
                'data': serializer.data
            })
        except Exception as e:
            print(f"更新標籤錯誤: {str(e)}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        """刪除標籤"""
        try:
            print("開始刪除標籤...")
            instance = self.get_object()
            tag_name = instance.name
            self.perform_destroy(instance)
            print(f"成功刪除標籤: {tag_name}")
            return Response({
                'status': 'success',
                'message': '刪除標籤成功'
            }, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            print(f"刪除標籤錯誤: {str(e)}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class AdminTagListView(LoginRequiredMixin, ListView):
    """後台標籤管理視圖"""
    model = Tag
    template_name = 'forum_system/admin/tag_list.html'
    context_object_name = 'tags'
    paginate_by = 10

    def get_queryset(self):
        print("正在獲取標籤列表...")
        return Tag.objects.all().order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = '標籤管理'
        context['total_tags'] = Tag.objects.count()
        return context

    def post(self, request, *args, **kwargs):
        print("收到標籤新增請求...")
        try:
            name = request.POST.get('name')
            icon = request.POST.get('icon')
            description = request.POST.get('description')

            if not name:
                return JsonResponse({'status': 'error', 'message': '標籤名稱為必填項'})

            # 檢查標籤名稱是否已存在
            if Tag.objects.filter(name=name).exists():
                return JsonResponse({'status': 'error', 'message': '此標籤名稱已存在'})

            # 創建新標籤
            tag = Tag.objects.create(
                name=name,
                icon=icon if icon else 'fa fa-tag',
                description=description
            )
            print(f"標籤創建成功: {tag.name}")

            # 返回成功訊息
            return JsonResponse({
                'status': 'success',
                'message': '標籤新增成功',
                'tag': {
                    'id': tag.id,
                    'name': tag.name,
                    'icon': tag.icon,
                    'description': tag.description,
                    'created_at': tag.created_at.strftime('%Y-%m-%d %H:%M')
                }
            })

        except Exception as e:
            print(f"標籤創建失敗: {str(e)}")
            return JsonResponse({'status': 'error', 'message': f'標籤創建失敗: {str(e)}'})

class AdminCategoryListView(LoginRequiredMixin, ListView):
    """分類管理頁面"""
    model = Category
    template_name = 'admin-dashboard/forum/category_list.html'
    context_object_name = 'categories'
    
    def get_queryset(self):
        """獲取所有分類"""
        queryset = Category.objects.all().order_by('-created_at')
        
        # 打印分類總數，用於調試
        total_categories = queryset.count()
        print(f"找到 {total_categories} 個分類")
        
        # 為每個分類添加統計數據
        for category in queryset:
            posts = Post.objects.filter(category=category, is_deleted=False)
            category.stats = {
                'total_posts': posts.count(),
                'total_views': sum(post.views for post in posts),
                'total_likes': sum(post.likes.count() for post in posts),
                'total_comments': sum(post.comments.count() for post in posts)
            }
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = '分類管理'
        return context
    
    def get(self, request, *args, **kwargs):
        """處理編輯和刪除分類的請求"""
        # 處理編輯分類請求
        edit_id = request.GET.get('edit')
        if edit_id:
            try:
                category = Category.objects.get(id=edit_id)
                # 返回包含分類信息的JSON響應
                return JsonResponse({
                    'status': 'success',
                    'category': {
                        'id': category.id,
                        'name': category.name,
                        'description': category.description
                    }
                })
            except Category.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': '找不到指定的分類'})
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': f'獲取分類信息時出錯: {str(e)}'})
        
        # 處理刪除分類請求
        delete_id = request.GET.get('delete')
        if delete_id:
            try:
                category = Category.objects.get(id=delete_id)
                
                # 檢查該分類是否有文章
                post_count = Post.objects.filter(category=category).count()
                if post_count > 0:
                    return JsonResponse({
                        'status': 'error', 
                        'message': f'無法刪除此分類「{category.name}」，因為它包含 {post_count} 篇文章'
                    })
                
                category_name = category.name
                category.delete()
                
                return JsonResponse({
                    'status': 'success',
                    'message': f'已成功刪除分類「{category_name}」'
                })
            except Category.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': '找不到指定的分類'})
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': f'刪除分類時出錯: {str(e)}'})
        
        # 如果沒有特殊操作，就顯示列表頁面
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        """處理表單提交 - 創建或更新分類"""
        try:
            # 獲取表單數據
            category_id = request.POST.get('id')
            name = request.POST.get('name')
            description = request.POST.get('description', '')
            
            if not name:
                return JsonResponse({'status': 'error', 'message': '分類名稱不能為空'})
            
            # 如果有分類ID，則是更新操作
            if category_id:
                try:
                    category = Category.objects.get(id=category_id)
                    
                    # 檢查名稱是否已存在（且不是當前分類）
                    if Category.objects.filter(name=name).exclude(id=category_id).exists():
                        return JsonResponse({'status': 'error', 'message': f'分類「{name}」已存在'})
                    
                    # 更新分類
                    category.name = name
                    category.description = description
                    category.save()
                    
                    # 添加統計數據
                    posts = Post.objects.filter(category=category, is_deleted=False)
                    category.stats = {
                        'total_posts': posts.count(),
                        'total_views': sum(post.views for post in posts),
                        'total_likes': sum(post.likes.count() for post in posts),
                        'total_comments': sum(post.comments.count() for post in posts)
                    }
                    
                    # 返回成功信息
                    return JsonResponse({
                        'status': 'success',
                        'message': f'分類「{name}」更新成功',
                        'category': {
                            'id': category.id,
                            'name': category.name,
                            'description': category.description,
                            'created_at': category.created_at.strftime('%Y-%m-%d %H:%M'),
                            'stats': category.stats
                        }
                    })
                except Category.DoesNotExist:
                    return JsonResponse({'status': 'error', 'message': '找不到指定的分類'})
            
            # 否則是創建操作
            else:
                # 檢查分類名稱是否已存在
                if Category.objects.filter(name=name).exists():
                    return JsonResponse({'status': 'error', 'message': f'分類「{name}」已存在'})
                
                # 創建新分類
                category = Category.objects.create(
                    name=name,
                    description=description
                )
                
                # 添加統計數據
                category.stats = {
                    'total_posts': 0,
                    'total_views': 0,
                    'total_likes': 0,
                    'total_comments': 0
                }
                
                # 返回成功信息
                return JsonResponse({
                    'status': 'success',
                    'message': f'分類「{name}」創建成功',
                    'category': {
                        'id': category.id,
                        'name': category.name,
                        'description': category.description,
                        'created_at': category.created_at.strftime('%Y-%m-%d %H:%M'),
                        'stats': category.stats
                    }
                })
        except Exception as e:
            print(f"處理分類時出錯: {str(e)}")
            return JsonResponse({'status': 'error', 'message': f'處理分類時出錯: {str(e)}'})

class AdminPostListView(LoginRequiredMixin, ListView):
    """文章列表管理頁面"""
    model = Post
    template_name = 'admin-dashboard/forum/post_list.html'
    context_object_name = 'posts'

    def get_queryset(self):
        """獲取所有非刪除的文章"""
        queryset = Post.objects.filter(is_deleted=False)
        category_id = self.request.GET.get('category_id')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # 打印文章總數，用於調試
        total_posts = queryset.count()
        print(f"找到 {total_posts} 篇非刪除文章")
        
        # 使用 select_related 提前獲取 author 和 category 信息以提高性能
        # 使用 annotate 添加統計數據
        return queryset.select_related('author', 'category').prefetch_related('tags').annotate(
            likes_total=Count('likes', distinct=True),
            comments_total=Count('comments', distinct=True),
            saves_total=Count('saved_by', distinct=True)
        ).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = '文章管理'
        context['total_posts'] = self.get_queryset().count()
        context['categories'] = Category.objects.all()
        return context

    def get(self, request, *args, **kwargs):
        # 處理刪除文章的請求
        delete_id = request.GET.get('delete')
        if delete_id:
            try:
                post = Post.objects.get(id=delete_id)
                post.is_deleted = True
                post.save()
                messages.success(request, f'已成功刪除文章「{post.title}」')
                return redirect('forum_article_list')
            except Post.DoesNotExist:
                messages.error(request, '找不到指定的文章')
            except Exception as e:
                messages.error(request, f'刪除文章時出錯：{str(e)}')
        
        # 處理編輯文章的請求
        edit_id = request.GET.get('edit')
        if edit_id:
            try:
                return redirect('admin-post-edit', pk=edit_id)
            except Exception as e:
                messages.error(request, f'跳轉編輯頁面時出錯：{str(e)}')
        
        # 正常顯示文章列表
        return super().get(request, *args, **kwargs)

class AdminPostDetailView(LoginRequiredMixin, DetailView):
    """文章詳情頁面"""
    model = Post
    template_name = 'admin-dashboard/forum/post_detail.html'
    context_object_name = 'post'

    def get_queryset(self):
        return Post.objects.filter(is_deleted=False).select_related(
            'author', 'category'
        ).prefetch_related(
            'likes', 'comments', 'saved_by', 'tags'
        ).annotate(
            likes_total=Count('likes', distinct=True),
            comments_total=Count('comments', distinct=True),
            saves_total=Count('saved_by', distinct=True)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.filter(is_deleted=False).select_related('author').order_by('created_at')
        return context

class AdminPostEditView(LoginRequiredMixin, UpdateView):
    """文章編輯頁面"""
    model = Post
    template_name = 'admin-dashboard/forum/post_edit.html'
    fields = ['title', 'content', 'category', 'tags']
    context_object_name = 'post'
    
    def get_queryset(self):
        return Post.objects.filter(is_deleted=False)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['tags'] = Tag.objects.all()
        return context
    
    def get_success_url(self):
        return reverse('admin-post-detail', kwargs={'pk': self.object.pk})

@api_view(['POST'])
@permission_classes([])  # 不需要任何權限
def test_category_create(request):
    """測試創建分類的API - 無需權限驗證"""
    try:
        print("收到測試分類創建請求:", request.data)
        
        # 檢查請求數據
        if not request.data.get('name'):
            return Response({"success": False, "message": "分類名稱不能為空"}, status=400)
        
        # 創建分類
        category = Category.objects.create(
            name=request.data.get('name'),
            description=request.data.get('description', '')
        )
        
        print(f"成功創建分類: ID={category.id}, 名稱={category.name}")
        
        return Response({
            "success": True, 
            "message": "分類創建成功", 
            "data": {
                "id": category.id,
                "name": category.name,
                "description": category.description,
                "created_at": category.created_at
            }
        })
    except Exception as e:
        print("測試創建分類時出錯:", str(e))
        return Response({"success": False, "message": f"創建失敗: {str(e)}"}, status=500)

@api_view(['POST'])
@permission_classes([])  # 不需要任何權限
def test_category_update(request):
    """測試更新分類的API - 無需權限驗證"""
    try:
        print("收到測試分類更新請求:", request.data)
        
        # 檢查請求數據
        category_id = request.data.get('id')
        name = request.data.get('name')
        description = request.data.get('description', '')
        
        if not category_id:
            return Response({"success": False, "message": "分類ID不能為空"}, status=400)
        
        if not name:
            return Response({"success": False, "message": "分類名稱不能為空"}, status=400)
        
        # 嘗試查找分類
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return Response({"success": False, "message": "找不到指定的分類"}, status=404)
        
        # 更新分類
        category.name = name
        category.description = description
        category.save()
        
        print(f"成功更新分類: ID={category.id}, 名稱={category.name}")
        
        return Response({
            "success": True, 
            "message": "分類更新成功", 
            "data": {
                "id": category.id,
                "name": category.name,
                "description": category.description,
                "updated_at": timezone.now()
            }
        })
    except Exception as e:
        print("測試更新分類時出錯:", str(e))
        return Response({"success": False, "message": f"更新失敗: {str(e)}"}, status=500)

@api_view(['POST'])
@permission_classes([])  # 不需要任何權限
def test_category_delete(request):
    """測試刪除分類的API - 無需權限驗證"""
    try:
        print("收到測試分類刪除請求")
        
        # 檢查請求數據
        category_id = request.data.get('id')
        if not category_id:
            return Response({"success": False, "message": "分類ID不能為空"}, status=400)
        
        # 嘗試查找分類
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return Response({"success": False, "message": "找不到指定的分類"}, status=404)
        
        # 檢查是否有關聯的文章
        posts_count = Post.objects.filter(category=category).count()
        if posts_count > 0:
            return Response({
                "success": False, 
                "message": f"無法刪除此分類，因為它包含 {posts_count} 篇文章"
            }, status=400)
        
        # 刪除分類
        category_name = category.name
        category.delete()
        
        print(f"成功刪除分類: ID={category_id}, 名稱={category_name}")
        
        return Response({
            "success": True, 
            "message": "分類刪除成功"
        })
    except Exception as e:
        print("測試刪除分類時出錯:", str(e))
        return Response({"success": False, "message": f"刪除失敗: {str(e)}"}, status=500)

@api_view(['POST'])
@permission_classes([])  # 不需要任何權限
def test_comment_delete(request):
    """測試刪除評論的API - 無需權限驗證"""
    try:
        print("收到測試評論刪除請求內容:")
        print(f"- 請求內容類型: {request.content_type}")
        print(f"- 請求方法: {request.method}")
        print(f"- 請求數據: {request.data}")
        print(f"- 請求體: {request.body}")
        
        # 嘗試解析請求數據 (處理不同的內容類型和數據格式)
        comment_id = None
        
        # 方法1: 從URL參數獲取
        comment_id_from_url = request.GET.get('id')
        if comment_id_from_url:
            print(f"從URL參數獲取ID: {comment_id_from_url}")
            comment_id = comment_id_from_url
        
        # 方法2: 從請求體中解析JSON數據
        if not comment_id and request.content_type == 'application/json':
            try:
                import json
                if isinstance(request.data, dict):
                    comment_id = request.data.get('id')
                    print(f"從request.data字典獲取ID: {comment_id}")
                elif request.body:
                    json_data = json.loads(request.body)
                    comment_id = json_data.get('id')
                    print(f"從JSON主體獲取ID: {comment_id}")
            except Exception as e:
                print(f"解析JSON數據時出錯: {str(e)}")
        
        # 方法3: 從表單數據獲取
        if not comment_id:
            comment_id = request.POST.get('id')
            print(f"從表單數據獲取ID: {comment_id}")
            
        # 方法4: 從請求體直接解析
        if not comment_id and request.body:
            try:
                # 嘗試作為URL編碼形式解析
                from urllib.parse import parse_qs
                body_str = request.body.decode('utf-8')
                if '=' in body_str:
                    parsed_data = parse_qs(body_str)
                    if 'id' in parsed_data:
                        comment_id = parsed_data['id'][0]
                        print(f"從URL編碼主體獲取ID: {comment_id}")
            except Exception as e:
                print(f"解析請求體時出錯: {str(e)}")
                
        # 轉換為整數類型
        if comment_id:
            try:
                comment_id = int(comment_id)
                print(f"已將評論ID轉換為整數: {comment_id}")
            except (ValueError, TypeError) as e:
                print(f"無法將評論ID轉換為整數: {comment_id}, 錯誤: {str(e)}")
        
        print(f"最終解析出的評論ID: {comment_id}")
        
        # 檢查請求數據
        if not comment_id:
            return Response({
                "success": False, 
                "message": "評論ID不能為空，請提供有效的評論ID",
                "debug_info": {
                    "content_type": request.content_type,
                    "method": request.method,
                    "data": str(request.data),
                    "body": str(request.body)
                }
            }, status=400)
        
        # 嘗試查找評論
        try:
            comment = Comment.objects.get(id=comment_id)
            print(f"成功找到評論: ID={comment_id}, 內容={comment.content[:30]}...")
        except Comment.DoesNotExist:
            print(f"找不到評論: ID={comment_id}")
            return Response({"success": False, "message": "找不到指定的評論"}, status=404)
        except Exception as e:
            print(f"查詢評論時出錯: {str(e)}")
            return Response({"success": False, "message": f"查詢評論時出錯: {str(e)}"}, status=500)
        
        # 記錄被刪除的評論信息
        comment_content = comment.content
        post_title = comment.post.title if comment.post else "未知文章"
        
        # 執行軟刪除
        try:
            comment.is_deleted = True
            comment.save()
            print(f"成功標記評論為已刪除: ID={comment_id}")
        except Exception as e:
            print(f"保存評論時出錯: {str(e)}")
            return Response({"success": False, "message": f"保存評論時出錯: {str(e)}"}, status=500)
        
        print(f"成功刪除評論: ID={comment_id}, 內容={comment_content[:30]}...")
        
        return Response({
            "success": True, 
            "message": "評論刪除成功", 
            "data": {
                "id": comment.id,
                "content": comment_content[:100] + ('...' if len(comment_content) > 100 else ''),
                "post_title": post_title
            }
        })
    except Exception as e:
        print("測試刪除評論時出錯:", str(e))
        import traceback
        traceback.print_exc()
        
        # 如果是GET請求，返回簡單的HTML錯誤頁面
        if request.method == 'GET':
            from django.http import HttpResponse
            return HttpResponse(f'<html><body><h1>刪除評論時出錯</h1><p>{str(e)}</p><p><a href="/user-dashboard/forum/comments/">返回評論列表</a></p></body></html>')
        
        # 否則返回JSON錯誤響應
        return Response({"success": False, "message": f"刪除失敗: {str(e)}"}, status=500)

@api_view(['GET', 'POST'])
@permission_classes([])  # 不需要任何權限
def direct_comment_delete(request, comment_id):
    """直接透過URL刪除評論 - 簡化版本"""
    try:
        print(f"收到直接評論刪除請求: ID={comment_id}, Method={request.method}")
        
        # 嘗試查找評論
        try:
            comment = Comment.objects.get(id=comment_id)
            print(f"成功找到評論: ID={comment_id}, 內容={comment.content[:30]}...")
        except Comment.DoesNotExist:
            print(f"找不到評論: ID={comment_id}")
            from django.http import HttpResponse
            if request.method == 'GET':
                return HttpResponse(f'<html><body><h1>錯誤</h1><p>找不到ID={comment_id}的評論</p><p><a href="/user-dashboard/forum/comments/">返回評論列表</a></p></body></html>')
            return Response({"success": False, "message": "找不到指定的評論"}, status=404)
        
        # 記錄被刪除的評論信息
        comment_content = comment.content
        post_title = comment.post.title if comment.post else "未知文章"
        
        # 執行軟刪除
        comment.is_deleted = True
        comment.save()
        
        print(f"成功刪除評論: ID={comment_id}, 內容={comment_content[:30]}...")
        
        # 如果是GET請求，重定向回評論列表頁面
        if request.method == 'GET':
            from django.shortcuts import redirect
            from django.contrib import messages
            # 添加一個成功消息
            try:
                messages.success(request, f'評論已成功刪除：{comment_content[:50]}...')
            except:
                pass  # 忽略消息添加錯誤
            return redirect('forum_comment_list')
        
        # 否則返回JSON響應
        return Response({
            "success": True, 
            "message": "評論直接刪除成功", 
            "data": {
                "id": comment.id,
                "content": comment_content[:100] + ('...' if len(comment_content) > 100 else ''),
                "post_title": post_title
            }
        })
    except Exception as e:
        print(f"直接刪除評論時出錯: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # 如果是GET請求，返回簡單的HTML錯誤頁面
        if request.method == 'GET':
            from django.http import HttpResponse
            return HttpResponse(f'<html><body><h1>刪除評論時出錯</h1><p>{str(e)}</p><p><a href="/user-dashboard/forum/comments/">返回評論列表</a></p></body></html>')
        
        # 否則返回JSON錯誤響應
        return Response({"success": False, "message": f"刪除失敗: {str(e)}"}, status=500)

@csrf_exempt  # 允許跨域請求
def increment_views(request, post_id):
    """增加文章觀看數的 API"""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': '只接受 POST 請求'}, status=405)
    
    try:
        # 查找文章
        post = Post.objects.get(pk=post_id)
        
        # 增加文章的觀看數
        post.views += 1
        post.save()
        
        # 返回更新後的數據
        return JsonResponse({
            'status': 'success',
            'message': '觀看數已增加',
            'data': {
                'id': post.id,
                'views': post.views,
            }
        })
    except Post.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': '文章不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
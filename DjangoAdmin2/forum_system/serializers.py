from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Category, Post, Comment, SavedPost

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class CategorySerializer(serializers.ModelSerializer):
    post_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'post_count', 'created_at']

    def get_post_count(self, obj):
        return Post.objects.filter(category=obj, is_deleted=False).count()

class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'content', 'created_at', 'updated_at']
        read_only_fields = ['author']

class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    like_count = serializers.IntegerField(read_only=True)
    comment_count = serializers.IntegerField(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    is_liked = serializers.SerializerMethodField()
    is_saved = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'content', 'author', 'category', 'category_id',
            'views', 'like_count', 'comment_count', 'comments',
            'is_liked', 'is_saved', 'created_at', 'updated_at'
        ]
        read_only_fields = ['author', 'views', 'like_count', 'comment_count']

    def get_is_liked(self, obj):
        user = self.context['request'].user
        return user.is_authenticated and obj.likes.filter(id=user.id).exists()

    def get_is_saved(self, obj):
        user = self.context['request'].user
        return user.is_authenticated and SavedPost.objects.filter(user=user, post=obj).exists()

class SavedPostSerializer(serializers.ModelSerializer):
    post = PostSerializer(read_only=True)
    post_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = SavedPost
        fields = ['id', 'user', 'post', 'post_id', 'created_at']
        read_only_fields = ['user'] 
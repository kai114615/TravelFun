from rest_framework import serializers
from .models import Product, Cart, Category, Post

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'category', 'image', 'created_at', 'updated_at']

class CartSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Cart
        fields = ['id', 'user', 'product', 'product_id', 'quantity', 'created_at', 'updated_at']
        read_only_fields = ['user']
        
    def create(self, validated_data):
        user = self.context['request'].user
        return Cart.objects.create(user=user, **validated_data)

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'created_at', 'updated_at']

class PostSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'content', 'author', 'author_name',
            'category', 'category_name', 'created_at', 'updated_at',
            'views', 'likes_count', 'tags', 'is_deleted'
        ]
        read_only_fields = ['author', 'views', 'likes_count', 'created_at', 'updated_at']

    def get_author_name(self, obj):
        return obj.author.username if obj.author else None

    def get_category_name(self, obj):
        return obj.category.name if obj.category else None

    def get_likes_count(self, obj):
        return obj.get_likes_count()

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['author'] = request.user
        return super().create(validated_data) 
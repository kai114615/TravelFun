from django.db import models
from django.conf import settings
from django.utils import timezone
from django_ckeditor_5.fields import CKEditor5Field
from myapp.models import Member  # 引入 Member 模型
from django.contrib.auth import get_user_model

User = get_user_model()

class Category(models.Model):
    """討論區分類"""
    name = models.CharField('分類名稱', max_length=50)
    description = models.TextField('分類描述', blank=True, null=True)
    created_at = models.DateTimeField('建立時間', default=timezone.now)
    updated_at = models.DateTimeField('更新時間', auto_now=True)

    class Meta:
        verbose_name = '討論區分類'
        verbose_name_plural = '討論區分類'
        ordering = ['created_at']

    def __str__(self):
        return self.name

class Post(models.Model):
    """討論文章"""
    title = models.CharField('標題', max_length=200)
    content = CKEditor5Field('內容', config_name='default', blank=True, null=True)
    author = models.ForeignKey(
        Member,  # 改為使用 Member 模型
        on_delete=models.CASCADE,
        related_name='forum_posts',  # 改名以避免衝突
        verbose_name='作者'
    )
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='posts', verbose_name='分類')
    views = models.PositiveIntegerField('瀏覽次數', default=0)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_posts', blank=True, verbose_name='按讚')
    tags = models.ManyToManyField('Tag', related_name='posts', blank=True, verbose_name='標籤')
    allow_comments = models.BooleanField('允許評論', default=True)
    is_published = models.BooleanField('是否發布', default=True)
    created_at = models.DateTimeField('發布時間', default=timezone.now)
    updated_at = models.DateTimeField('更新時間', auto_now=True)
    is_deleted = models.BooleanField('是否刪除', default=False)

    class Meta:
        verbose_name = '討論文章'
        verbose_name_plural = '討論文章'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_like_count(self):
        return self.likes.count()

    def get_comment_count(self):
        return self.comments.count()

class Comment(models.Model):
    """文章評論"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name='文章')
    author = models.ForeignKey(
        Member,  # 改為使用 Member 模型
        on_delete=models.CASCADE,
        related_name='forum_comments',  # 改名以避免衝突
        verbose_name='作者'
    )
    content = models.TextField('評論內容', blank=True)
    created_at = models.DateTimeField('評論時間', default=timezone.now)
    updated_at = models.DateTimeField('更新時間', auto_now=True)
    is_deleted = models.BooleanField('是否刪除', default=False)

    class Meta:
        verbose_name = '評論'
        verbose_name_plural = '評論'
        ordering = ['created_at']

    def __str__(self):
        return f'{self.author.username} 評論 {self.post.title}'

class SavedPost(models.Model):
    """收藏的文章"""
    user = models.ForeignKey(
        Member,  # 改為使用 Member 模型
        on_delete=models.CASCADE,
        related_name='forum_saved_posts',  # 改名以避免衝突
        verbose_name='用戶'
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='saved_by', verbose_name='文章')
    created_at = models.DateTimeField('收藏時間', default=timezone.now)

    class Meta:
        verbose_name = '收藏文章'
        verbose_name_plural = '收藏文章'
        unique_together = ['user', 'post']
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} 收藏 {self.post.title}'

class Carousel(models.Model):
    """輪播圖"""
    title = models.CharField('標題', max_length=100)
    image = models.ImageField('圖片', upload_to='carousel/', blank=True, null=True)
    description = models.TextField('描述', blank=True, null=True)
    url = models.URLField('連結', blank=True, null=True)
    order = models.IntegerField('排序', default=0)
    is_active = models.BooleanField('是否啟用', default=True)
    created_at = models.DateTimeField('建立時間', default=timezone.now)
    updated_at = models.DateTimeField('更新時間', auto_now=True)

    class Meta:
        verbose_name = '輪播圖'
        verbose_name_plural = '輪播圖'
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title

class FeaturedArticle(models.Model):
    """精選文章"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='featured', verbose_name='文章')
    order = models.IntegerField('排序', default=0)
    is_active = models.BooleanField('是否啟用', default=True)
    created_at = models.DateTimeField('建立時間', default=timezone.now)
    updated_at = models.DateTimeField('更新時間', auto_now=True)

    class Meta:
        verbose_name = '精選文章'
        verbose_name_plural = '精選文章'
        ordering = ['order', '-created_at']

    def __str__(self):
        return f'精選: {self.post.title}'

class ProductRanking(models.Model):
    """產品排名"""
    title = models.CharField('標題', max_length=100)
    image = models.ImageField('圖片', upload_to='products/', blank=True, null=True)
    description = models.TextField('描述', blank=True, null=True)
    price = models.DecimalField('價格', max_digits=10, decimal_places=2, default=0)
    ranking = models.IntegerField('排名', default=0)
    is_active = models.BooleanField('是否啟用', default=True)
    created_at = models.DateTimeField('建立時間', default=timezone.now)
    updated_at = models.DateTimeField('更新時間', auto_now=True)

    class Meta:
        verbose_name = '產品排名'
        verbose_name_plural = '產品排名'
        ordering = ['ranking', '-created_at']

    def __str__(self):
        return self.title

class Tag(models.Model):
    """文章標籤模型"""
    name = models.CharField('標籤名稱', max_length=50, unique=True)
    icon = models.CharField('標籤圖標', max_length=50, blank=True)
    description = models.TextField('標籤描述', blank=True)
    created_at = models.DateTimeField('創建時間', default=timezone.now)
    updated_at = models.DateTimeField('更新時間', auto_now=True)
    
    class Meta:
        verbose_name = '標籤'
        verbose_name_plural = '標籤管理'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
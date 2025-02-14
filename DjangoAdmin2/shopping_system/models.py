from django.db import models
from django.utils import timezone
from django.templatetags.static import static
from ckeditor.fields import RichTextField
from myapp.models import Member
import json
import os
from .tasks import update_json_file_async

class Product(models.Model):
    """商品模型"""
    name = models.CharField(max_length=200, verbose_name='名稱')
    category = models.CharField(max_length=100, verbose_name='類別')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='價格')
    description = RichTextField(blank=True, verbose_name='描述')
    image_url = models.URLField(max_length=500, blank=True, null=True, verbose_name='商品圖片網址')
    stock = models.PositiveIntegerField(default=0, verbose_name='庫存')
    is_active = models.BooleanField(default=True, verbose_name='是否上架')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='創建時間')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新時間')

    def __str__(self):
        return self.name

    def get_image_url(self):
        if self.image_url:
            return self.image_url
        return static('img/no-image.jpg')

    def save(self, *args, **kwargs):
        # 先保存商品
        super().save(*args, **kwargs)
        # 非阻塞式呼叫更新JSON檔案
        update_json_file_async.delay()

    def delete(self, *args, **kwargs):
        # 先刪除商品
        super().delete(*args, **kwargs)
        # 非阻塞式呼叫更新JSON檔案
        update_json_file_async.delay()

    @classmethod
    def update_json_file(cls):
        try:
            # 獲取所有商品資料
            products = cls.objects.all()
            products_data = []
            for product in products:
                products_data.append({
                    'id': product.id,
                    'name': product.name,
                    'category': product.category,
                    'price': str(product.price),
                    'description': product.description,
                    'stock': product.stock,
                    'is_active': product.is_active,
                    'image_url': product.get_image_url(),
                    'created_at': product.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'updated_at': product.updated_at.strftime('%Y-%m-%d %H:%M:%S')
                })

            # 構建JSON檔案路徑
            json_file_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'src', 'views', 'front', 'Mall', 'data', 'MallProduct.json'
            )

            # 寫入JSON檔案
            with open(json_file_path, 'w', encoding='utf-8') as f:
                json.dump(products_data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"更新JSON檔案時發生錯誤：{str(e)}")

    class Meta:
        verbose_name = '商品'
        verbose_name_plural = '商品'
        ordering = ['-created_at']

class ProductReview(models.Model):
    """商品評論"""
    RATING_CHOICES = (
        (1, '1星'),
        (2, '2星'),
        (3, '3星'),
        (4, '4星'),
        (5, '5星'),
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', verbose_name='商品')
    user = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='shopping_product_reviews',
        verbose_name='用戶'
    )
    content = models.TextField(verbose_name='內容')
    rating = models.IntegerField(choices=RATING_CHOICES, verbose_name='評分')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='創建時間')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新時間')

    class Meta:
        verbose_name = '商品評論'
        verbose_name_plural = '商品評論'
        ordering = ['-created_at']

class Carousel(models.Model):
    """輪播圖模型"""
    title = models.CharField(max_length=100, verbose_name='標題')
    image = models.ImageField(upload_to='carousel/', verbose_name='圖片')
    url = models.URLField(verbose_name='鏈接', blank=True)
    order = models.IntegerField(default=0, verbose_name='排序')
    is_active = models.BooleanField(default=True, verbose_name='是否啟用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='創建時間')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新時間')

    class Meta:
        verbose_name = '輪播圖'
        verbose_name_plural = '輪播圖'
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title

    def get_image_url(self):
        if self.image:
            return self.image.url
        return static('img/no-image.jpg')

class CategoryDisplay(models.Model):
    """分類展示設置模型"""
    category = models.CharField(max_length=100, verbose_name='分類名稱')
    order = models.IntegerField(default=0, verbose_name='排序')
    is_active = models.BooleanField(default=True, verbose_name='是否顯示')
    icon = models.CharField(max_length=50, blank=True, verbose_name='圖標')
    description = models.TextField(blank=True, verbose_name='描述')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='創建時間')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新時間')

    class Meta:
        verbose_name = '分類展示'
        verbose_name_plural = '分類展示'
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.category

class RecommendedProduct(models.Model):
    """推薦商品設置模型"""
    POSITION_CHOICES = (
        ('home', '首頁推薦'),
        ('hot', '熱門商品'),
        ('new', '新品上市'),
    )

    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='商品')
    position = models.CharField(max_length=20, choices=POSITION_CHOICES, verbose_name='推薦位置')
    order = models.IntegerField(default=0, verbose_name='排序')
    is_active = models.BooleanField(default=True, verbose_name='是否顯示')
    start_time = models.DateTimeField(null=True, blank=True, verbose_name='開始時間')
    end_time = models.DateTimeField(null=True, blank=True, verbose_name='結束時間')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='創建時間')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新時間')

    class Meta:
        verbose_name = '推薦商品'
        verbose_name_plural = '推薦商品'
        ordering = ['position', 'order', '-created_at']
        unique_together = ['product', 'position']  # 同一個商品在同一個位置只能推薦一次

    def __str__(self):
        return f'{self.get_position_display()} - {self.product.name}'

    def is_valid(self):
        """檢查推薦是否在有效期內"""
        now = timezone.now()
        if self.start_time and self.end_time:
            return self.start_time <= now <= self.end_time
        return True 

class Order(models.Model):
    """訂單"""
    ORDER_STATUS = (
        ('pending', '待付款'),
        ('paid', '已付款'),
        ('shipped', '已出貨'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    )
    
    user = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='shopping_orders',
        verbose_name='購買者'
    )
    order_number = models.CharField('訂單編號', max_length=20, unique=True)
    total_amount = models.DecimalField('總金額', max_digits=10, decimal_places=2)
    status = models.CharField('訂單狀態', max_length=20, choices=ORDER_STATUS)
    shipping_address = models.TextField('收貨地址')
    contact_phone = models.CharField('聯絡電話', max_length=20)
    created_at = models.DateTimeField('建立時間', auto_now_add=True)
    updated_at = models.DateTimeField('更新時間', auto_now=True)

    class Meta:
        verbose_name = '訂單'
        verbose_name_plural = '訂單'
        ordering = ['-created_at']

    def __str__(self):
        return f'訂單 {self.order_number}'

class OrderItem(models.Model):
    """訂單項目"""
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='訂單'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        related_name='order_items',
        verbose_name='商品'
    )
    quantity = models.PositiveIntegerField('數量')
    price = models.DecimalField('購買價格', max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = '訂單項目'
        verbose_name_plural = '訂單項目'

    def __str__(self):
        return f'{self.order.order_number} - {self.product.name}' 
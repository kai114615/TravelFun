from django.db import models
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class ImportDate(models.Model):
    import_date = models.DateTimeField(null=False)
    timezone_type = models.IntegerField(null=False)
    timezone = models.CharField(max_length=50, null=False)

    class Meta:
        db_table = 'theme_import_dates'
        verbose_name = '資料匯入時間'
        verbose_name_plural = '資料匯入時間'
        app_label = 'theme_entertainment'


class Events(models.Model):
    """活動基本模型"""
    id = models.BigAutoField(primary_key=True)
    uid = models.CharField('唯一識別碼', max_length=100, unique=True, db_index=True)
    activity_name = models.CharField('活動名稱', max_length=500)
    description = models.TextField('活動描述', null=True, blank=True)
    organizer = models.CharField('主辦單位', max_length=200, null=True, blank=True)
    address = models.TextField('地址', null=True, blank=True)
    start_date = models.DateTimeField('開始時間', null=True, blank=True)
    end_date = models.DateTimeField('結束時間', null=True, blank=True)
    location = models.CharField('地點', max_length=200, null=True, blank=True)
    latitude = models.FloatField('緯度', null=True, blank=True)
    longitude = models.FloatField('經度', null=True, blank=True)
    ticket_info = models.TextField('票價資訊', null=True, blank=True)
    image_url = models.URLField('圖片網址', max_length=500, null=True, blank=True)
    created_at = models.DateTimeField('建立時間', auto_now_add=True, db_index=True)

    class Meta:
        abstract = True
        ordering = ['-start_date']
        app_label = 'theme_entertainment'

    def __str__(self):
        return self.activity_name


class CultureActivity(Events):
    """文化部活動"""
    performer = models.CharField('演出單位', max_length=200, blank=True)
    venue_name = models.CharField('場地名稱', max_length=200, blank=True)
    is_free = models.BooleanField('是否免費', default=True)
    source = models.CharField('資料來源', max_length=50, default='文化部')

    class Meta:
        db_table = 'theme_culture_activities'
        verbose_name = '文化部活動'
        verbose_name_plural = '文化部活動'
        app_label = 'theme_entertainment'


class NewTaipeiActivity(Events):
    """新北市活動"""
    activity_id = models.CharField('活動ID', max_length=100, unique=True)
    category = models.CharField('活動類別', max_length=100, blank=True)
    venue_phone = models.CharField('場地電話', max_length=50, blank=True)
    transportation = models.TextField('交通說明', blank=True)
    related_link = models.URLField('相關連結', max_length=500, blank=True)
    source = models.CharField('資料來源', max_length=50, default='新北市')

    class Meta:
        db_table = 'theme_newtaipei_activities'
        verbose_name = '新北市活動'
        verbose_name_plural = '新北市活動'
        app_label = 'theme_entertainment'


class TaipeiActivity(Events):
    """台北市活動"""
    data_sn = models.CharField('資料序號', max_length=100, unique=True)
    contact_person = models.CharField('聯絡人', max_length=100, blank=True)
    contact_phone = models.CharField('聯絡電話', max_length=50, blank=True)
    contact_email = models.EmailField('聯絡Email', blank=True)
    registration_method = models.CharField('報名方式', max_length=200, blank=True)
    participant_limit = models.CharField('人數限制', max_length=100, blank=True)
    categories = models.JSONField('活動類別', default=list, blank=True)
    source = models.CharField('資料來源', max_length=50, default='台北市')

    class Meta:
        db_table = 'theme_taipei_activities'
        verbose_name = '台北市活動'
        verbose_name_plural = '台北市活動'
        app_label = 'theme_entertainment'


class TFAMActivity(Events):
    """台北市立美術館活動與展覽"""
    ACTIVITY_TYPE_CHOICES = [
        ('activity', '一般活動'),
        ('exhibition', '展覽'),
    ]

    activity_type = models.CharField(
        '活動類型',
        max_length=20,
        choices=ACTIVITY_TYPE_CHOICES,
        default='activity'
    )
    content = models.TextField('內容')
    link = models.URLField('連結', max_length=500)
    publishing_unit = models.CharField('發布單位', max_length=100)
    source = models.CharField('資料來源', max_length=50, default='北美館')

    class Meta:
        db_table = 'theme_tfam_activities'
        verbose_name = '北美館活動'
        verbose_name_plural = '北美館活動'
        app_label = 'theme_entertainment'
        indexes = [
            models.Index(fields=['activity_type']),
        ]

    def save(self, *args, **kwargs):
        if self.activity_type == 'exhibition':
            self.activity_name = self.content[:500]
        super().save(*args, **kwargs)


class QueryResult(models.Model):
    query_timestamp = models.CharField(max_length=50, null=False)
    limit_count = models.IntegerField(null=False)
    offset_count = models.IntegerField(null=False)
    total_count = models.IntegerField(null=False)
    sort_order = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'theme_query_results'
        verbose_name = '查詢結果'
        verbose_name_plural = '查詢結果'
        app_label = 'theme_entertainment'


class QueryEventRelation(models.Model):
    query = models.ForeignKey(QueryResult, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    event = GenericForeignKey('content_type', 'object_id')
    display_order = models.IntegerField(null=False)

    class Meta:
        db_table = 'theme_query_event_relations'
        unique_together = ('query', 'content_type', 'object_id')
        verbose_name = '查詢結果與活動關聯'
        verbose_name_plural = '查詢結果與活動關聯'
        app_label = 'theme_entertainment'

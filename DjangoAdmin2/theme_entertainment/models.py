from django.db import models
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class ImportDate(models.Model):
    import_date = models.DateTimeField()
    timezone_type = models.IntegerField()
    timezone = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'theme_import_dates'
        managed = True


class Events(models.Model):
    """活動基本模型"""
    uid = models.CharField(max_length=255, unique=True)
    activity_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    organizer = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=8, blank=True, null=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, blank=True, null=True)
    ticket_price = models.TextField(blank=True, null=True)
    source_url = models.TextField(blank=True, null=True)
    image_url = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'theme_events'
        managed = True


class QueryResult(models.Model):
    query_timestamp = models.DateTimeField(blank=True, null=True)
    limit_count = models.IntegerField(blank=True, null=True)
    offset_count = models.IntegerField(blank=True, null=True)
    total_count = models.IntegerField(blank=True, null=True)
    sort_order = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'theme_query_results'
        verbose_name = '查詢結果'
        verbose_name_plural = '查詢結果'
        app_label = 'theme_entertainment'
        managed = True


class QueryEventRelation(models.Model):
    query = models.ForeignKey(QueryResult, on_delete=models.CASCADE)
    event = models.ForeignKey(Events, on_delete=models.CASCADE)
    display_order = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'theme_query_event_relations'
        managed = True

from django.db import models

class Festival(models.Model):
    id = models.AutoField(primary_key=True)
    activity_name = models.CharField(max_length=255, verbose_name="活動名稱")
    description = models.TextField(verbose_name="簡介說明", blank=True, null=True)
    location = models.CharField(max_length=255, verbose_name="活動地點")
    phone = models.CharField(max_length=50, verbose_name="電話", blank=True, null=True)
    organizer = models.CharField(max_length=255, verbose_name="主辦單位", blank=True, null=True)
    start_time = models.DateTimeField(verbose_name="活動起始時間", blank=True, null=True)
    end_time = models.DateTimeField(verbose_name="活動結束時間", blank=True, null=True)
    url = models.URLField(verbose_name="活動網址", blank=True, null=True)
    latitude = models.FloatField(verbose_name="緯度", blank=True, null=True)
    longitude = models.FloatField(verbose_name="經度", blank=True, null=True)
    transport_info = models.TextField(verbose_name="交通資訊", blank=True, null=True)
    parking_info = models.TextField(verbose_name="停車資訊", blank=True, null=True)
    cost = models.CharField(max_length=100, verbose_name="費用", blank=True, null=True)
    remarks = models.TextField(verbose_name="備註", blank=True, null=True)
    region = models.CharField(max_length=255, verbose_name="所在區域", blank=True, null=True)
    image_url = models.URLField(verbose_name="圖片連結", blank=True, null=True)

    def __str__(self):
        return self.activity_name

class ArtCultureActivity(models.Model):
    uid = models.CharField(max_length=50, primary_key=True, verbose_name="活動唯一識別碼")
    activity_name = models.CharField(max_length=255, verbose_name="活動名稱")
    performer = models.CharField(max_length=255, verbose_name="演出單位", blank=True, null=True)
    description = models.TextField(verbose_name="簡介說明", blank=True, null=True)
    image_url = models.URLField(verbose_name="圖片連結", blank=True, null=True)
    organizer = models.CharField(max_length=255, verbose_name="主辦單位", blank=True, null=True)
    start_date = models.DateField(verbose_name="活動起始日期", blank=True, null=True)
    end_date = models.DateField(verbose_name="活動結束日期", blank=True, null=True)
    address = models.CharField(max_length=255, verbose_name="地址", blank=True, null=True)
    venue_name = models.CharField(max_length=255, verbose_name="場地名稱", blank=True, null=True)
    is_ticketed = models.CharField(max_length=1, verbose_name="是否售票", choices=[('Y', 'Yes'), ('N', 'No')], blank=True, null=True)
    latitude = models.FloatField(verbose_name="緯度", blank=True, null=True)
    longitude = models.FloatField(verbose_name="經度", blank=True, null=True)
    ticket_price = models.CharField(max_length=100, verbose_name="票價", blank=True, null=True)

    def __str__(self):
        return self.activity_name

class CulturalActivity(models.Model):
    uid = models.CharField(max_length=50, primary_key=True, verbose_name="活動唯一識別碼")
    activity_name = models.CharField(max_length=255, verbose_name="活動名稱")
    performer = models.CharField(max_length=255, verbose_name="演出單位", blank=True, null=True)
    description = models.TextField(verbose_name="簡介說明", blank=True, null=True)
    image_url = models.URLField(verbose_name="圖片連結", blank=True, null=True)
    organizer = models.CharField(max_length=255, verbose_name="主辦單位", blank=True, null=True)
    start_date = models.DateField(verbose_name="活動起始日期", blank=True, null=True)
    end_date = models.DateField(verbose_name="活動結束日期", blank=True, null=True)
    address = models.CharField(max_length=255, verbose_name="地址", blank=True, null=True)
    venue_name = models.CharField(max_length=255, verbose_name="場地名稱", blank=True, null=True)
    is_ticketed = models.CharField(max_length=1, verbose_name="是否售票", choices=[('Y', 'Yes'), ('N', 'No')], blank=True, null=True)
    latitude = models.FloatField(verbose_name="緯度", blank=True, null=True)
    longitude = models.FloatField(verbose_name="經度", blank=True, null=True)
    ticket_price = models.CharField(max_length=100, verbose_name="票價", blank=True, null=True)

    def __str__(self):
        return self.activity_name

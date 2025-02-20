from rest_framework import serializers
from .models import CultureActivity, NewTaipeiActivity, TaipeiActivity, TFAMActivity


class ActivitySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    uid = serializers.CharField()
    activity_name = serializers.CharField()
    description = serializers.CharField(allow_null=True)
    organizer = serializers.CharField(allow_null=True)
    address = serializers.CharField(allow_null=True)
    start_date = serializers.DateTimeField(allow_null=True)
    end_date = serializers.DateTimeField(allow_null=True)
    location = serializers.CharField(allow_null=True)
    latitude = serializers.FloatField(allow_null=True)
    longitude = serializers.FloatField(allow_null=True)
    ticket_info = serializers.CharField(allow_null=True)
    related_link = serializers.CharField(allow_null=True)
    image_url = serializers.CharField(allow_null=True)
    created_at = serializers.DateTimeField()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # 添加來源標籤
        data['source'] = '主題育樂'
        return data

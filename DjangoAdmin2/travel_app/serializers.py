from rest_framework import serializers
from .models import Travel,TravelClass,Taiwan,Counties

class CountrySerializers(serializers.ModelSerializer):
    class Meta:
        model = Counties
        fields = '__all__'

class TravelSerializers(serializers.ModelSerializer):
    class Meta:
        model = Travel
        fields = '__all__'     

class TravelClassSerializers(serializers.ModelSerializer):
    class Meta:
        model = TravelClass
        fields = '__all__'

class TaiwanSerializers(serializers.ModelSerializer):
    class Meta:
        model = Taiwan
        fields = '__all__'

class TravelFilterSerializer(serializers.ModelSerializer):
    # 添加一个自定义字段，例如完整的描述
    
    class Meta:
        model = Travel
        fields = '__all__'  




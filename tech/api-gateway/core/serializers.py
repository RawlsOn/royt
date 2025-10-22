from rest_framework import serializers
from django.urls import reverse

import core.models as core_models

class 토지Serializer(serializers.ModelSerializer):
    class Meta:
        model = core_models.토지
        fields = '__all__'

class 토지매물Serializer(serializers.ModelSerializer):
    토지_data = 토지Serializer(source='토지', read_only= True)
    기준월 = serializers.ReadOnlyField()
    class Meta:
        model = core_models.토지매물
        fields = '__all__'

class 건물Serializer(serializers.ModelSerializer):
    class Meta:
        model = core_models.건물
        fields = '__all__'

class 건물매물Serializer(serializers.ModelSerializer):
    건물_data = 건물Serializer(source='건물', read_only= True)
    기준월 = serializers.ReadOnlyField()
    class Meta:
        model = core_models.건물매물
        fields = '__all__'

class 상가Serializer(serializers.ModelSerializer):
    class Meta:
        model = core_models.상가
        fields = '__all__'

class 상가매물Serializer(serializers.ModelSerializer):
    상가_data = 상가Serializer(source='상가', read_only= True)
    기준월 = serializers.ReadOnlyField()
    class Meta:
        model = core_models.상가매물
        fields = '__all__'
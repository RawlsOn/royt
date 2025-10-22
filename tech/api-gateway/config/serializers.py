
from rest_framework import serializers

from config.models import *


class SEOSerializer(serializers.ModelSerializer):
    image_url_wo_expire = serializers.ReadOnlyField()
    class Meta:
        model = SEO
        fields = '__all__'

class BaseSettingSerializer(serializers.ModelSerializer):
    image_url_wo_expire = serializers.ReadOnlyField()
    class Meta:
        model = BaseSetting
        fields = '__all__'
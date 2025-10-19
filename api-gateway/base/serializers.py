from rest_framework import serializers
from django.urls import reverse

import base.models as base_models


class FrontendVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = base_models.FrontendVersion
        fields = '__all__'
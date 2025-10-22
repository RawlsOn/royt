import importlib

from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions, serializers

from common.util import model_util, datetime_util

from common.util.model_util import get_or_none
import user.models as user_models

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = user_models.UserProfile
        fields = '__all__'

class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = user_models.UserInfo
        fields = '__all__'

class UserSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = user_models.UserSetting
        fields = '__all__'

class UserCustomSerializer(serializers.ModelSerializer):
    usercss_wo_exp = serializers.ReadOnlyField()
    class Meta:
        model = user_models.UserCustom
        fields = '__all__'

class CustomUserSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    info = serializers.SerializerMethodField()
    setting = serializers.SerializerMethodField()
    custom = serializers.SerializerMethodField()

    def get_profile(self, obj):
        return UserProfileSerializer(
            user_models.UserProfile.objects.get(user_id= obj.id)
        ).data

    def get_info(self, obj):
        return UserInfoSerializer(
            user_models.UserInfo.objects.get(user_id= obj.id)
        ).data

    def get_setting(self, obj):
        return UserSettingSerializer(
            user_models.UserSetting.objects.get(user_id= obj.id)
        ).data

    def get_custom(self, obj):
        return UserCustomSerializer(
            user_models.UserCustom.objects.get(user_id= obj.id)
        ).data

    class Meta:
        model = user_models.CustomUser
        fields = ('id', 'email', 'joined_at', 'profile', 'info', 'setting', 'custom')

class PublicUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = user_models.UserProfile
        fields = ('id', 'nickname', 'bio', 'userimage',)

class CustomPublicUserSerializer(serializers.ModelSerializer):
    joined_at = serializers.SerializerMethodField()
    profile = serializers.SerializerMethodField()

    def get_profile(self, obj):
        profile = get_or_none(user_models.UserProfile, user_id= obj.id)
        if profile is not None:
            return PublicUserProfileSerializer(profile).data

    def get_joined_at(self, obj):
        user = get_or_none(user_models.CustomUser, id= obj.id)
        return datetime_util.pretty_date(user.date_joined)

    class Meta:
        model = user_models.CustomUser
        fields = ('id', 'profile', 'joined_at')

class RegistrateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = user_models.CustomUser
        fields = '__all__'

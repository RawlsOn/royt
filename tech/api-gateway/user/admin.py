from django.contrib import admin
from django.utils.safestring import mark_safe

import user.models as user_models

@admin.register(user_models.CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    ordering = ['-date_joined',]
    search_fields = [field.name for field in user_models.CustomUser._meta.fields]
    list_display = [field.name for field in user_models.CustomUser._meta.fields]
    list_display.insert(1, 'profile')
    list_display.remove('password')
    list_display = list_display[::-1]
    readonly_fields= ('password', )
    def profile(self, obj):
        user_profile = user_models.UserProfile.objects.get(user_id= obj.id)
        html = f"""
            <a href='/adminachy/user/userprofile/{user_profile.id}/change/'>보기</a>
        """
        url = ('/')
        return mark_safe(html)

@admin.register(user_models.UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    ordering = ['-created_at']
    search_fields = [field.name for field in user_models.UserProfile._meta.fields]
    list_display = [field.name for field in user_models.UserProfile._meta.fields]

@admin.register(user_models.UserInfo)
class UserInfoAdmin(admin.ModelAdmin):
    ordering = ['-created_at']
    search_fields = [field.name for field in user_models.UserInfo._meta.fields]
    list_display = [field.name for field in user_models.UserInfo._meta.fields]

@admin.register(user_models.UserSystem)
class Admin(admin.ModelAdmin):
    ordering = ['-created_at']
    search_fields = [field.name for field in user_models.UserSystem._meta.fields]
    list_display = [field.name for field in user_models.UserSystem._meta.fields]

@admin.register(user_models.UserCustom)
class UserCustomAdmin(admin.ModelAdmin):
    ordering = ['-created_at']
    search_fields = [field.name for field in user_models.UserCustom._meta.fields]
    list_display = [field.name for field in user_models.UserCustom._meta.fields]

# @admin.register(user_models.UserSystemInfo)
# class UserSystemInfoAdmin(admin.ModelAdmin):
#     ordering = ['-created_at']
#     search_fields = [field.name for field in user_models.UserSystemInfo._meta.fields]
#     list_display = [field.name for field in user_models.UserSystemInfo._meta.fields]

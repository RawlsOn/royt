from django.contrib import admin
from roemail.models import *

@admin.register(SendJob)
class Admin(admin.ModelAdmin):
    ordering = ['-created_at']
    # search_fields = [field.name for field in user_models.UserProfile._meta.fields]
    list_display = [field.name for field in SendJob._meta.fields]
    list_display = ['created_at', 'to', 'subject', 'content_type', 'send_type']

@admin.register(SendLog)
class Admin(admin.ModelAdmin):
    ordering = ['-created_at']
    # search_fields = [field.name for field in user_models.UserProfile._meta.fields]
    list_display = [field.name for field in SendLog._meta.fields]

@admin.register(Invitation)
class Admin(admin.ModelAdmin):
    ordering = ['-created_at']
    # search_fields = [field.name for field in user_models.UserProfile._meta.fields]
    list_display = [field.name for field in Invitation._meta.fields]

@admin.register(EmailLoginjoinCode)
class Admin(admin.ModelAdmin):
    ordering = ['-created_at']
    # search_fields = [field.name for field in user_models.UserProfile._meta.fields]
    list_display = [field.name for field in EmailLoginjoinCode._meta.fields]
